"""
Scraper de leads B2B — Prospection PME françaises
Génère un fichier leads.csv compatible avec campagne_emails_auto.py.

Source des entreprises : API officielle "Recherche d'entreprises"
(recherche-entreprises.api.gouv.fr), qui interroge le registre SIRENE/RNE.
Données publiques d'entreprises (pas de données personnelles au sens RGPD
hors nom du dirigeant, publié légalement au RNE) — gratuit, sans clé API,
aucun scraping de plateforme tierce (Google/LinkedIn/Pages Jaunes non utilisés).

Enrichissement email (optionnel, --enrichir) : devine le nom de domaine du
site de l'entreprise, puis lit UNIQUEMENT les pages publiques de ce site
(accueil, /contact, /mentions-legales) pour y trouver une adresse de contact
via regex. Aucun compte, aucune connexion, aucun contournement d'accès.

⚠️ Toujours relire manuellement les emails/prénoms avant un envoi de masse,
et respecter le droit d'opposition (lien de désabonnement dans les templates).

Usage :
    python scraper_leads_pme.py --q "cabinet comptable" --departement 33 --limit 30
    python scraper_leads_pme.py --naf 69.20Z,70.22Z --departement 75,92,93,94 --effectif-max 49 --limit 50 --enrichir
    python scraper_leads_pme.py --q "agence immobilière" --departement 69 --limit 20 --out leads_immo.csv
"""

import argparse
import csv
import re
import sys
import time
import unicodedata
from urllib.parse import quote

import requests

API_URL = "https://recherche-entreprises.api.gouv.fr/search"

# Codes INSEE tranche_effectif_salarie -> (min, max) salariés
TRANCHES_EFFECTIF = {
    "00": (0, 0), "01": (1, 2), "02": (3, 5), "03": (6, 9),
    "11": (10, 19), "12": (20, 49), "21": (50, 99), "22": (100, 199),
    "31": (200, 249), "32": (250, 499), "41": (500, 999), "42": (1000, 1999),
    "51": (2000, 4999), "52": (5000, 9999), "53": (10000, 999999),
}

SUFFIXES_LEGAUX = [
    "sarl", "sas", "sasu", "eurl", "sa", "sci", "scop", "ei", "eirl",
    "entreprise individuelle", "et associes", "et fils", "groupe",
]

HEADERS_HTTP = {"User-Agent": "Mozilla/5.0 (prospection B2B; contact manuel avant envoi)"}
EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}")
DOMAINES_EXCLUS = ("sentry.io", "wixpress.com", "example.com", "w3.org",
                    "godaddy.com", "cloudflare.com", "schema.org", ".png", ".jpg", ".svg")


# ─── Récupération des entreprises (API officielle) ─────────────────────────

def rechercher_entreprises(q, naf, departement, effectif_min, effectif_max, limit):
    """Interroge l'API recherche-entreprises.api.gouv.fr et retourne une liste d'entreprises actives."""
    resultats = []
    page = 1
    per_page = min(25, limit)

    while len(resultats) < limit:
        params = {
            "etat_administratif": "A",
            "per_page": per_page,
            "page": page,
        }
        if q:
            params["q"] = q
        if naf:
            params["activite_principale"] = naf
        if departement:
            params["departement"] = departement

        resp = requests.get(API_URL, params=params, headers=HEADERS_HTTP, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        page_resultats = data.get("results", [])
        if not page_resultats:
            break

        for ent in page_resultats:
            tranche = ent.get("tranche_effectif_salarie") or "NN"
            bornes = TRANCHES_EFFECTIF.get(tranche)
            if bornes and (bornes[1] < effectif_min or bornes[0] > effectif_max):
                continue
            resultats.append(ent)
            if len(resultats) >= limit:
                break

        if len(page_resultats) < per_page:
            break
        page += 1
        time.sleep(0.3)  # usage raisonnable de l'API publique

    return resultats


def extraire_ligne(ent):
    """Transforme une entrée de l'API en ligne de lead exploitable."""
    siege = ent.get("siege", {})
    dirigeants = ent.get("dirigeants", [])
    prenom = ""
    for d in dirigeants:
        if d.get("type_dirigeant") == "personne physique" and d.get("prenoms"):
            prenom = d["prenoms"].split(",")[0].strip().title()
            break

    tranche = ent.get("tranche_effectif_salarie") or "NN"
    bornes = TRANCHES_EFFECTIF.get(tranche, (0, 0))
    effectif_moyen = (bornes[0] + bornes[1]) / 2 if bornes[1] < 999999 else bornes[0]
    ca_estime = int(effectif_moyen * 90000) if effectif_moyen else 0  # heuristique ~90k€ CA/salarié, à affiner

    return {
        "societe": ent.get("nom_complet", "").title(),
        "prenom": prenom,
        "email": "",
        "site_web": "",
        "secteur": ent.get("activite_principale", ""),
        "ca_estime": ca_estime,
        "effectif": f"{bornes[0]}-{bornes[1]}" if bornes[1] < 999999 else f"{bornes[0]}+",
        "ville": siege.get("libelle_commune", ""),
        "code_postal": siege.get("code_postal", ""),
        "siret": siege.get("siret", ""),
        "siren": ent.get("siren", ""),
    }


# ─── Enrichissement email (best-effort, sur le site propre de l'entreprise) ─

DNS_LABEL_MAX = 63  # limite RFC 1035 pour un label de domaine


def slugifier(nom):
    nom = re.sub(r"\(.*?\)", "", nom)  # retire les compléments entre parenthèses (souvent redondants)
    nom = unicodedata.normalize("NFKD", nom).encode("ascii", "ignore").decode()
    nom = nom.lower()
    for suf in SUFFIXES_LEGAUX:
        nom = re.sub(rf"\b{re.escape(suf)}\b", "", nom)
    nom = re.sub(r"[^a-z0-9]", "", nom)
    return nom[:DNS_LABEL_MAX]


def deviner_site(societe):
    """Teste quelques variantes de domaine plausibles et retourne la première qui répond."""
    slug = slugifier(societe)
    if not slug:
        return None
    for domaine in (f"{slug}.fr", f"{slug}.com", f"www.{slug}.fr", f"www.{slug}.com"):
        url = f"https://{domaine}"
        try:
            r = requests.get(url, headers=HEADERS_HTTP, timeout=6, allow_redirects=True)
            if r.status_code == 200 and len(r.text) > 200:
                return r.url.rstrip("/")
        except Exception:
            # Domaine invalide, DNS KO, TLS KO, timeout... on essaie juste la variante suivante.
            continue
    return None


def extraire_email(url_base):
    """Cherche un email de contact sur la page d'accueil, /contact et /mentions-legales."""
    for chemin in ("", "/contact", "/mentions-legales", "/contact-us", "/nous-contacter"):
        try:
            r = requests.get(url_base + chemin, headers=HEADERS_HTTP, timeout=6)
            if r.status_code != 200:
                continue
            matches = EMAIL_RE.findall(r.text)
            candidats = [m for m in matches if not any(d in m.lower() for d in DOMAINES_EXCLUS)]
            if candidats:
                # Priorité aux adresses génériques de contact
                for prefixe in ("contact@", "info@", "bonjour@", "hello@"):
                    for c in candidats:
                        if c.lower().startswith(prefixe):
                            return c
                return candidats[0]
        except Exception:
            continue
    return ""


def enrichir_ligne(ligne):
    site = deviner_site(ligne["societe"])
    if not site:
        return ligne
    ligne["site_web"] = site
    ligne["email"] = extraire_email(site)
    return ligne


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Scraper de leads B2B — PME françaises (API officielle SIRENE)")
    parser.add_argument("--q", default="", help="Recherche libre (ex: 'cabinet comptable', 'agence immobilière')")
    parser.add_argument("--naf", default="", help="Codes NAF/APE séparés par virgule (ex: 69.20Z,70.22Z)")
    parser.add_argument("--departement", default="", help="Département(s) séparés par virgule (ex: 75,92,93,94)")
    parser.add_argument("--effectif-min", type=int, default=0, help="Effectif salarié minimum")
    parser.add_argument("--effectif-max", type=int, default=49, help="Effectif salarié maximum (défaut 49 = TPE/PME)")
    parser.add_argument("--limit", type=int, default=30, help="Nombre de leads à récupérer")
    parser.add_argument("--enrichir", action="store_true", help="Tente de deviner site web + email (plus lent, ~2-4s/entreprise)")
    parser.add_argument("--out", default="leads.csv", help="Fichier CSV de sortie")
    args = parser.parse_args()

    if not args.q and not args.naf:
        print("⚠️  Précisez au moins --q (recherche libre) ou --naf (codes NAF).")
        sys.exit(1)

    print(f"[INFO] Recherche en cours (q='{args.q}', naf='{args.naf}', departement='{args.departement}')...")
    entreprises = rechercher_entreprises(
        q=args.q, naf=args.naf, departement=args.departement,
        effectif_min=args.effectif_min, effectif_max=args.effectif_max, limit=args.limit,
    )
    print(f"[INFO] {len(entreprises)} entreprise(s) trouvée(s).")

    lignes = [extraire_ligne(e) for e in entreprises]

    if args.enrichir:
        print("[INFO] Enrichissement site web + email (best-effort)...")
        for i, ligne in enumerate(lignes):
            enrichir_ligne(ligne)
            statut = ligne["email"] or "— pas trouvé"
            print(f"  [{i+1}/{len(lignes)}] {ligne['societe'][:40]:40s} -> {statut}")

    champs = ["email", "prenom", "societe", "secteur", "ca_estime",
              "effectif", "ville", "code_postal", "site_web", "siret", "siren"]
    with open(args.out, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=champs)
        writer.writeheader()
        writer.writerows(lignes)

    avec_email = sum(1 for l in lignes if l["email"])
    print(f"\n[OK] Fichier écrit : {args.out}")
    print(f"[OK] {avec_email}/{len(lignes)} lead(s) avec email trouvé automatiquement.")
    if avec_email < len(lignes):
        print("[INFO] Complétez manuellement les emails manquants (LinkedIn, site web, annuaire) avant l'envoi.")


if __name__ == "__main__":
    main()

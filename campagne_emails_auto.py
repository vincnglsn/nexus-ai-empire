"""
Campagne Cold Emails Automatisée
Envoie les emails de prospection via Gmail SMTP avec rate limiting
et suivi de campagne. 100% automatique.

Couvre deux campagnes :
- InvoiceGuard AI (templates pme / pme_btp / ec)
- AI Automation Done-For-You (templates auto_sav / auto_prospection / auto_contenu
  + séquence de relance à 4 touches J0/J3/J7/J14)

Usage:
    python campagne_emails_auto.py --liste prospects.csv --template pme
    python campagne_emails_auto.py --liste experts.csv --template ec
    python campagne_emails_auto.py --demo   # Simule sans envoyer

    # Séquence "AI Automation" (même --liste à chaque étape, l'état est suivi automatiquement) :
    python campagne_emails_auto.py --liste leads.csv --template auto_sav --etape 1
    python campagne_emails_auto.py --liste leads.csv --etape 2   # relance J3
    python campagne_emails_auto.py --liste leads.csv --etape 3 --exemple-client "un cabinet comptable a réduit de 60% le temps passé sur les relances clients"   # relance J7
    python campagne_emails_auto.py --liste leads.csv --etape 4   # clôture J14

Formats CSV acceptés:
    email, prenom, societe, secteur, ca_estime (optionnel)
"""

import smtplib
import csv
import time
import os
import sys
import json
import argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import make_msgid
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ─── Templates ────────────────────────────────────────────────────────────────

TEMPLATES = {
    "pme": {
        "sujet": "Vos factures impayées vous coûtent {montant_estime}€ par an — solution IA",
        "corps": """Bonjour {prenom},

Je développe InvoiceGuard AI, un outil qui récupère automatiquement les factures impayées des PME françaises via l'intelligence artificielle.

En 30 secondes, l'IA génère la relance parfaite : bon ton, bonne urgence, conforme Loi LME — et l'envoie directement à votre client.

Résultat : -40% de DSO en 60 jours pour nos premiers utilisateurs.

Seriez-vous partant pour un essai gratuit de 14 jours ?
→ https://baby-rss-textile-rap.trycloudflare.com

(Aucune carte bancaire requise, 5 minutes pour importer vos factures)

Bonne journée,
Vincent
InvoiceGuard AI — Recouvrement intelligent pour PME françaises

P.S. : Si ce n'est pas votre problème prioritaire, pas de souci — mais si vos impayés dépassent 2% de votre CA, on peut récupérer la quasi-totalité en quelques semaines.
""",
    },
    "pme_btp": {
        "sujet": "BTP : 1 PME sur 3 dépose le bilan à cause des impayés — comment éviter ça",
        "corps": """Bonjour {prenom},

Le BTP est le secteur où les impayés font le plus de dégâts : délais de paiement non respectés, sous-traitants en attente, trésorerie sous tension.

J'ai construit InvoiceGuard AI spécialement pour ce contexte :
• Détection automatique des retards (Loi LME BTP)
• Relances calibrées selon l'ancienneté du chantier
• Mise en demeure juridique en 1 clic
• Rapport mensuel pour votre expert-comptable

Essai 14 jours gratuit → https://baby-rss-textile-rap.trycloudflare.com

Vincent | InvoiceGuard AI
""",
    },
    "ec": {
        "sujet": "Partenariat Expert-Comptable — 20% de commission récurrente sur vos clients PME",
        "corps": """Bonjour {prenom},

Je lance InvoiceGuard AI, un SaaS de recouvrement d'impayés pour PME françaises (IA + Loi LME).

Je recherche des experts-comptables partenaires pour recommander l'outil à leurs clients.

Ce que vous y gagnez :
• 20% de commission récurrente sur chaque abonnement souscrit
→ 1 client Pro (149€/mois) = 29,80€/mois à vie
→ 10 clients = 298€/mois passifs, sans effort

Ce que vos clients y gagnent :
• DSO réduit de 40% en 60 jours
• Rapport mensuel prêt à intégrer à votre reporting
• Conformité Loi LME garantie

Je peux vous montrer l'outil en 15 minutes en visio.
Créneau disponible cette semaine ?

Vincent | InvoiceGuard AI
→ https://baby-rss-textile-rap.trycloudflare.com
""",
    },
    # ─── AI Automation Done-For-You ────────────────────────────────────────
    "auto_sav": {
        "sujet": "{societe}, une question sur votre SAV",
        "corps": """{salutation}

Question directe : combien de temps passez-vous chaque semaine à répondre
aux mêmes questions par email chez {societe} — suivi de commande, FAQ,
relances clients ?

Je mets en place des agents IA qui traitent ça automatiquement, branchés
directement sur votre boîte mail. Livré en 5 jours, pas d'abonnement
logiciel supplémentaire à gérer.

15 min cette semaine pour voir si ça a du sens pour vous ?

Vinc
""",
    },
    "auto_prospection": {
        "sujet": "{societe}, une question sur votre prospection",
        "corps": """{salutation}

Question directe : combien de leads qualifiés {societe} pourrait traiter
en plus par mois si la recherche et le premier contact étaient automatisés ?

Je mets en place un pipeline qui scrape les prospects correspondant à votre
cible, lance une séquence de cold email automatisée, et vous remonte
uniquement les réponses. Livré en 5 jours.

15 min cette semaine pour voir si ça a du sens pour vous ?

Vinc
""",
    },
    "auto_contenu": {
        "sujet": "{societe}, une question sur votre contenu",
        "corps": """{salutation}

Question directe : combien de temps {societe} passe chaque semaine à
produire et publier du contenu sur LinkedIn/Instagram ?

Je mets en place un système qui génère et publie vos posts automatiquement
à partir de votre activité. Livré en 5 jours.

15 min cette semaine pour voir si ça a du sens pour vous ?

Vinc
""",
    },
    "auto_relance_j3": {
        "corps": """{salutation}

Je me permets de relancer — je sais que ça part vite dans les priorités.

Pour être concret : ça se livre en 5 jours, sans engagement long, et vous
testez avec vos propres données avant de valider quoi que ce soit.

Un créneau de 15 min cette semaine ou la suivante ?

Vinc
""",
    },
    "auto_relance_j7": {
        "corps": """{salutation}

Pas de réponse, ce n'est pas grave — je me doute que ce n'est peut-être pas
le bon moment ou pas la bonne priorité.

{exemple_client}

Si ça peut être utile pour {societe}, je vous montre en 15 min comment
ça marcherait avec votre cas précis. Sinon, dites-moi et je n'insiste pas.

Vinc
""",
    },
    "auto_relance_j14": {
        "corps": """{salutation}

Je vais arrêter de vous solliciter sur ce sujet — si le besoin revient
({offre_label} qui prend trop de temps), vous avez mon mail.

Bonne continuation à {societe}.

Vinc
""",
    },
}

# ─── Identité d'envoi par famille de campagne ──────────────────────────────────

MARQUES = {
    "invoiceguard": (
        "Vincent — InvoiceGuard AI",
        'InvoiceGuard AI · <a href="https://invoiceguard.fr">invoiceguard.fr</a> · Se désabonner',
    ),
    "auto": (
        "Vinc",
        "Automatisation IA sur-mesure · Se désabonner",
    ),
}

FAMILLE_TEMPLATE = {
    "pme": "invoiceguard", "pme_btp": "invoiceguard", "ec": "invoiceguard",
    "auto_sav": "auto", "auto_prospection": "auto", "auto_contenu": "auto",
    "auto_relance_j3": "auto", "auto_relance_j7": "auto", "auto_relance_j14": "auto",
}

OFFRE_LABEL = {
    "auto_sav": "SAV", "auto_prospection": "prospection", "auto_contenu": "contenu",
}

# Étape de séquence -> template de relance à utiliser (étape 1 = mail initial, template au choix)
ETAPE_TEMPLATE_RELANCE = {2: "auto_relance_j3", 3: "auto_relance_j7", 4: "auto_relance_j14"}

# ─── Envoi SMTP ───────────────────────────────────────────────────────────────

def envoyer_email_smtp(
    to: str,
    sujet: str,
    corps: str,
    gmail_user: str,
    gmail_password: str,
    expediteur_nom: str = "Vincent — InvoiceGuard AI",
    footer_html: str = 'InvoiceGuard AI · <a href="https://invoiceguard.fr">invoiceguard.fr</a> · Se désabonner',
    in_reply_to: str = "",
    references: str = "",
    mode_demo: bool = False,
) -> dict:
    """Envoie un email via Gmail SMTP avec App Password.

    Retourne le Message-ID utilisé, pour pouvoir y répondre (même fil de
    discussion) lors de la relance suivante de la séquence.
    """
    domaine = gmail_user.split("@")[-1] if gmail_user and "@" in gmail_user else None
    message_id = make_msgid(domain=domaine)

    if mode_demo:
        return {"success": True, "mode": "DEMO", "to": to, "message_id": message_id}

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"]    = sujet
        msg["From"]       = f"{expediteur_nom} <{gmail_user}>"
        msg["To"]         = to
        msg["Message-ID"] = message_id
        if in_reply_to:
            msg["In-Reply-To"] = in_reply_to
        if references:
            msg["References"] = references

        # Corps texte brut
        msg.attach(MIMEText(corps, "plain", "utf-8"))

        # Corps HTML minimal
        html_corps = corps.replace("\n", "<br>")
        html = f"""<html><body style="font-family:Arial,sans-serif;line-height:1.6;color:#333;max-width:600px">
{html_corps}
<br><br>
<hr style="border:1px solid #eee">
<small style="color:#888">{footer_html}</small>
</body></html>"""
        msg.attach(MIMEText(html, "html", "utf-8"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user, [to], msg.as_bytes())

        return {"success": True, "to": to, "message_id": message_id}
    except Exception as e:
        return {"success": False, "to": to, "error": str(e), "message_id": message_id}


# ─── Personnalisation ─────────────────────────────────────────────────────────

def personnaliser(template: str, contact: dict) -> tuple[str, str]:
    ca = float(contact.get("ca_estime", 500000))
    montant_estime = int(ca * 0.035)  # 3.5% de taux d'impayés moyen

    variables = {
        "prenom":          contact.get("prenom", ""),
        "societe":         contact.get("societe", "votre entreprise"),
        "secteur":         contact.get("secteur", ""),
        "montant_estime":  f"{montant_estime:,}".replace(",", " "),
    }

    # Choisit le bon template
    tpl_key = template
    secteur = contact.get("secteur", "").lower()
    if template == "pme" and "btp" in secteur:
        tpl_key = "pme_btp"

    tpl = TEMPLATES.get(tpl_key, TEMPLATES["pme"])
    sujet = tpl["sujet"].format(**variables)
    corps = tpl["corps"].format(**variables)
    return sujet, corps


def personnaliser_auto(template: str, contact: dict, exemple_client: str = "") -> tuple[str, str]:
    """Personnalise les templates de la séquence 'AI Automation Done-For-You'."""
    prenom = (contact.get("prenom") or "").strip()
    societe = contact.get("societe") or "votre entreprise"
    secteur = contact.get("secteur") or ""
    offre_label = OFFRE_LABEL.get(template, "automatisation")

    variables = {
        "salutation":     f"Bonjour {prenom}," if prenom else "Bonjour,",
        "societe":        societe,
        "secteur":        secteur,
        "offre_label":    offre_label,
        # Si aucun exemple réel n'est fourni (--exemple-client), on reste volontairement
        # générique plutôt que d'inventer un chiffre ou un témoignage client fictif.
        "exemple_client": exemple_client or (
            f"Je travaille actuellement avec plusieurs entreprises du secteur "
            f"{secteur or 'similaire au vôtre'} sur ce type d'automatisation — "
            f"si vous voulez, je vous montre concrètement à quoi ça ressemblerait "
            f"pour {societe}."
        ),
    }
    tpl = TEMPLATES[template]
    sujet = tpl["sujet"].format(**variables) if "sujet" in tpl else ""
    corps = tpl["corps"].format(**variables)
    return sujet, corps


# ─── Suivi de campagne ────────────────────────────────────────────────────────

def log_campagne(result: dict, log_path: str):
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps({**result, "timestamp": datetime.now().isoformat()}, ensure_ascii=False) + "\n")


# ─── Suivi de séquence (relances J3/J7/J14) ────────────────────────────────────

def charger_etat_sequence(path: str) -> dict:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def sauver_etat_sequence(etat: dict, path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(etat, f, ensure_ascii=False, indent=2)


# ─── Main ─────────────────────────────────────────────────────────────────────

def lancer_campagne(
    liste_csv: str,
    template: str,
    gmail_user: str,
    gmail_password: str,
    etape: int = 1,
    etat_path: str = "",
    exemple_client: str = "",
    mode_demo: bool = False,
    delai_secondes: float = 45.0,
    max_emails: int = 50,
):
    etat_path = etat_path or f"etat_sequence_{os.path.splitext(os.path.basename(liste_csv))[0]}.json"
    etat = charger_etat_sequence(etat_path)

    # À partir de l'étape 2, le template est celui de la relance correspondante
    # (le mail initial peut être auto_sav / auto_prospection / auto_contenu, la
    # relance qui suit est la même pour tous — --template est alors ignoré).
    if etape > 1:
        template = ETAPE_TEMPLATE_RELANCE[etape]

    famille = FAMILLE_TEMPLATE.get(template, "invoiceguard")
    expediteur_nom, footer_html = MARQUES[famille]

    log_path = f"campagne_{template}_{datetime.now().strftime('%Y%m%d_%H%M')}.log"
    envoyes, erreurs, ignores = 0, 0, 0

    sep = "=" * 60
    print(f"\n{sep}")
    print(f"  Campagne '{template.upper()}' — Étape {etape}")
    print(f"  Mode : {'DEMO' if mode_demo else 'PRODUCTION'}")
    print(f"  Liste : {liste_csv}")
    print(f"  État séquence : {etat_path}")
    print(f"  Delai inter-email : {delai_secondes}s | Max : {max_emails}")
    print(f"{sep}\n")

    with open(liste_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        contacts = list(reader)

    total = min(len(contacts), max_emails)
    print(f"[INFO] {total} contacts a traiter\n")

    for i, contact in enumerate(contacts[:max_emails]):
        email = contact.get("email", "").strip()
        if not email or "@" not in email:
            print(f"  [{i+1}/{total}] SKIP Email invalide : '{email}'")
            continue

        etat_contact = etat.get(email, {})
        sujet_original = etat_contact.get("sujet", "")

        if etape == 1:
            # Protection anti-doublon : si ce contact a déjà été contacté (même lors
            # d'un run précédent, ex. interrompu par --max), on ne renvoie pas un
            # second mail initial identique.
            if etat_contact.get("etape"):
                ignores += 1
                print(f"  [{i+1}/{total}] SKIP {email} -- deja contacte le {etat_contact.get('date','?')}")
                continue
            if template in ("pme", "pme_btp", "ec"):
                sujet, corps = personnaliser(template, contact)
            else:
                sujet, corps = personnaliser_auto(template, contact, exemple_client)
            in_reply_to = references = ""
        else:
            # On ne relance que les contacts arrivés au bon stade de la séquence.
            # Un contact absent de l'état (jamais contacté) ou resté à une étape
            # antérieure (retiré manuellement après une réponse, par ex.) est ignoré.
            if etat_contact.get("etape") != etape - 1:
                ignores += 1
                print(f"  [{i+1}/{total}] SKIP {email} -- pas au stade {etape-1} de la sequence")
                continue
            _, corps = personnaliser_auto(template, contact, exemple_client)
            sujet = sujet_original if sujet_original.startswith("Re: ") else f"Re: {sujet_original}"
            in_reply_to = references = etat_contact.get("message_id", "")

        result = envoyer_email_smtp(
            email, sujet, corps, gmail_user, gmail_password,
            expediteur_nom=expediteur_nom, footer_html=footer_html,
            in_reply_to=in_reply_to, references=references,
            mode_demo=mode_demo,
        )
        log_campagne({**result, "sujet": sujet, "etape": etape, "contact": contact}, log_path)

        icone = "OK " if result["success"] else "ERR"
        mode_txt = " [DEMO]" if mode_demo else ""
        print(f"  [{i+1}/{total}] {icone}{mode_txt} {email} -- {contact.get('prenom','')} {contact.get('societe','')}")

        if result["success"]:
            envoyes += 1
            # Un envoi DEMO ne part réellement à personne : l'état de séquence ne
            # doit avancer que sur un vrai envoi, sinon un dry-run bloquerait ensuite
            # le vrai envoi via la protection anti-doublon.
            if not mode_demo:
                etat[email] = {
                    "etape": etape,
                    "sujet": sujet if etape == 1 else sujet_original,
                    "message_id": result["message_id"],
                    "date": datetime.now().isoformat(),
                }
        else:
            erreurs += 1
            print(f"     Erreur : {result.get('error','?')}")

        if i < total - 1 and not mode_demo:
            print(f"     Pause {delai_secondes}s...")
            time.sleep(delai_secondes)

    sauver_etat_sequence(etat, etat_path)

    print(f"\n{sep}")
    print(f"  Campagne terminee")
    print(f"  Envoyes : {envoyes} | Erreurs : {erreurs} | Ignores (mauvais stade) : {ignores}")
    print(f"  Log : {log_path}")
    print(f"  Etat sequence : {etat_path}")
    print(f"{sep}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Campagne emails — InvoiceGuard AI & AI Automation Done-For-You")
    parser.add_argument("--liste",    default="prospects_pme.csv", help="Fichier CSV de prospects (ex: leads.csv genere par scraper_leads_pme.py)")
    parser.add_argument("--template", default="pme",
                         choices=["pme", "pme_btp", "ec", "auto_sav", "auto_prospection", "auto_contenu"],
                         help="Template du mail initial (etape 1 uniquement — ignore si --etape > 1)")
    parser.add_argument("--etape",    type=int, default=1, choices=[1, 2, 3, 4],
                         help="Etape de la sequence AI Automation : 1=mail initial (J0), 2=relance J3, 3=relance J7, 4=cloture J14")
    parser.add_argument("--etat",     default="", help="Fichier JSON de suivi de sequence (defaut : etat_sequence_<liste>.json)")
    parser.add_argument("--exemple-client", default="", dest="exemple_client",
                         help="Exemple client reel a citer en relance J7 (sinon formulation generique, sans chiffre invente)")
    parser.add_argument("--demo",     action="store_true", help="Mode démonstration (ne pas envoyer)")
    parser.add_argument("--max",      type=int, default=20, help="Nombre max d'emails")
    parser.add_argument("--delai",    type=float, default=45.0, help="Délai entre emails (secondes)")
    args = parser.parse_args()

    gmail_user     = os.environ.get("GMAIL_USER", "")
    gmail_password = os.environ.get("GMAIL_APP_PASSWORD", "")

    if not args.demo and (not gmail_user or not gmail_password):
        print("\n⚠️  Configuration email manquante !")
        print("\nAjoutez dans votre fichier .env :")
        print("  GMAIL_USER=votre@gmail.com")
        print("  GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx  (App Password Gmail)")
        print("\nComment créer un App Password Gmail :")
        print("  1. Allez sur myaccount.google.com/security")
        print("  2. Activez la validation en 2 étapes")
        print("  3. Cherchez 'Mots de passe d'application'")
        print("  4. Créez un mot de passe pour 'Courrier'")
        print("\nOu lancez en mode démo d'abord :")
        print("  python campagne_emails_auto.py --demo")
        sys.exit(1)

    if not os.path.exists(args.liste):
        if args.etape > 1:
            print(f"\n⚠️  Fichier introuvable : {args.liste}")
            print("Les relances (etape > 1) doivent utiliser la meme liste que l'etape 1.")
            sys.exit(1)
        # Crée un fichier de demo
        demo_csv = args.liste
        with open(demo_csv, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["email", "prenom", "societe", "secteur", "ca_estime"])
            if args.template == "ec":
                w.writerows([
                    ["ec1@cabinet-dupont.fr", "Jean", "Cabinet Dupont", "Expert-Comptable", ""],
                    ["direction@leblanc-ec.fr", "Sophie", "Leblanc & Associés", "Expert-Comptable", ""],
                    ["contact@cabinet-martin.fr", "Pierre", "Cabinet Martin EC", "Expert-Comptable", ""],
                ])
            else:
                w.writerows([
                    ["daf@techsolutions.fr", "Marie", "TechSolutions SAS", "IT", "800000"],
                    ["contact@btprenov.fr", "Luc", "BTP Renov & Co", "BTP", "1200000"],
                    ["admin@logisticsexpress.fr", "Karim", "Logistics Express", "Transport", "2000000"],
                    ["direction@imprimerie-centrale.fr", "Anne", "Imprimerie Centrale", "Industrie", "400000"],
                    ["compta@gis.fr", "Thomas", "Groupe Immobilier Sud", "Immobilier", "5000000"],
                ])
        print(f"📄 Fichier exemple créé : {demo_csv}")

    lancer_campagne(
        liste_csv=args.liste,
        template=args.template,
        gmail_user=gmail_user,
        gmail_password=gmail_password,
        etape=args.etape,
        etat_path=args.etat,
        exemple_client=args.exemple_client,
        mode_demo=args.demo,
        delai_secondes=args.delai,
        max_emails=args.max,
    )

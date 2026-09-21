# 🛡️ Nexus AI (Supply Chain Shield) — Guide de Déploiement & Mise en Vente
# Objectif : encaisser les premiers euros cette semaine, en surfant sur la crise géopolitique en cours

## ════════════════════════════════════════════════════════════
## ÉTAPE 0 — VÉRIFIER CE QUI EXISTE DÉJÀ (5 minutes)
## ════════════════════════════════════════════════════════════

Contrairement à InvoiceGuard, Nexus AI (`crisis_dashboard.py`) a déjà :
- [x] Un paywall Stripe fonctionnel (49€/mois, abonnement) → lien déjà dans le code — ⚠️ vérifié le 21/09 : le lien pointe vers un produit Stripe nommé "Accès API OSINT Premium" plutôt que "Nexus AI"/"Supply Chain Shield". Ça fonctionne pour encaisser, mais le nom du produit sur le relevé/reçu du client ne matchera pas la marque — à renommer côté Stripe (Produits > ce produit > Modifier) dès que possible pour éviter la confusion/les contestations de paiement.
- [x] Le moteur IA (analyse fichier + génération de plan de continuité, Gemini)
- [x] L'accroche mise à jour aujourd'hui avec la vraie crise en cours (Mer Rouge/Ormuz/Mer Noire, au lieu de l'ancien exemple "Détroit de Malacca")

Ce qui manque encore, c'est uniquement la mise en avant publique + la prospection. C'est plus rapide à lancer qu'InvoiceGuard : pas de nouveau compte Stripe à créer.

---

## ════════════════════════════════════════════════════════════
## ÉTAPE 1 — DÉPLOIEMENT PUBLIC : STREAMLIT COMMUNITY CLOUD
## ════════════════════════════════════════════════════════════

### Ce qui est déjà en place (vérifié le 21/09)
- Le repo a déjà DEUX remotes Git configurés :
  - `invoiceguard` → github.com/vincnglsn/invoiceguard-ai.git (déploiement InvoiceGuard, `streamlit_app.py`)
  - `origin` → github.com/vincnglsn/nexus-ai-empire.git — **c'est celui-ci qu'il faut utiliser pour Nexus**
- `origin/main` a déjà eu un déploiement Streamlit Cloud connecté par le passé (dernier commit dessus : "Update links to Streamlit Cloud", 19/09/2026)
- **10 commits locaux ne sont pas encore poussés sur `origin`** (du travail sur InvoiceGuard des 2 derniers jours + mes changements Nexus d'aujourd'hui). Le déploiement `nexus-ai-empire` actuellement en ligne, s'il existe encore, est donc figé au 19/09 et ne contient PAS le hook Mer Rouge/Ormuz du jour.
- `crisis_dashboard.py` a été rendu compatible Streamlit Cloud aujourd'hui : la clé Gemini se lit maintenant via `st.secrets["GEMINI_API_KEY"]` en priorité (avant, le code lisait un `.env` situé hors repo, `../worldmonitor_test/.env`, qui n'existe pas sur le Cloud).
- `requirements.txt` couvre déjà toutes les dépendances de `crisis_dashboard.py` (streamlit, google-genai, python-dotenv, pandas, requests, openpyxl).

### Ce qu'il reste à faire (nécessite ton compte, je ne peux pas le faire à ta place)
1. **Vérifier si une app Streamlit Cloud existe déjà** pour `nexus-ai-empire` sur https://share.streamlit.io (onglet "Your apps"). Si oui, note son "Main file path" actuel.
2. **Si elle pointe déjà sur `crisis_dashboard.py`** : il suffit de pousser (voir plus bas) → redéploiement automatique.
3. **Sinon, créer une nouvelle app** : "Create app" → repo `vincnglsn/nexus-ai-empire` → branche `main` → main file path : `crisis_dashboard.py` → Deploy.
4. **Secrets** (Settings de l'app → Secrets) : coller `GEMINI_API_KEY = "ta_cle"` (même valeur que celle utilisée en local).
5. ✅ Fait le 21/09 : l'app est en ligne à **https://nexus-ai-empire-6yrflyffrz2l6jxaxtk9gf.streamlit.app** (déjà reliée à `origin/main`, redéploiement automatique confirmé après le push). Vérifié : paywall à jour, alerte Mer Rouge/Ormuz visible. URL déjà intégrée dans `VENTE_KIT_NEXUS.md`.

### Pousser le code (à valider par toi avant que je le fasse)
```bash
git push origin main
```
⚠️ Ça pousse les 10 commits en attente d'un coup (InvoiceGuard + Nexus), sur un repo dont le comment dans `streamlit_app.py` indique explicitement qu'il est **public**. Dis-moi si je peux lancer ce push, ou si tu préfères le faire toi-même après relecture.

### Option B : Tunnel local immédiat (0 min setup, démo live en attendant)
`tunnel_public.py` est prêt dans le repo pour exposer `crisis_dashboard.py` en public le temps d'une démo — mais sa création est bloquée dans cette session (politique de sécurité de l'environnement sur les tunnels d'accès entrant). Lance-le toi-même : `python tunnel_public.py` (adapté au port 8502).

---

## ════════════════════════════════════════════════════════════
## ÉTAPE 2 — RAFRAÎCHIR LE HOOK CHAQUE SEMAINE (5 minutes/semaine)
## ════════════════════════════════════════════════════════════

La force du pitch Nexus AI, c'est qu'il colle à l'actualité géopolitique réelle. Chaque lundi :
1. Ouvrez https://www.worldmonitor.app/dashboard (couches : conflicts, sanctions, waterways, military)
2. Notez les 2-3 signaux "Élevé/Critique" du panneau "Posture Stratégique IA" et les probabilités du panneau "AI Forecasts"
3. Mettez à jour l'alert-box dans `crisis_dashboard.py` (lignes ~56-61) et le prompt IA (lignes ~101-108) avec les nouveaux signaux
4. Réutilisez ces mêmes chiffres dans le post LinkedIn de la semaine (voir `VENTE_KIT_NEXUS.md`)

Un pitch daté de la veille convertit mieux qu'un cas d'école générique — c'est le seul entretien régulier nécessaire.

---

## ════════════════════════════════════════════════════════════
## ÉTAPE 3 — CALENDLY (5 minutes)
## ════════════════════════════════════════════════════════════

1. Événement "Démo Nexus AI 15 min" sur Calendly (réutilisez le compte InvoiceGuard si vous en avez un)
2. Description : "Je croise votre fichier fournisseurs avec les alertes géopolitiques en direct et je vous montre votre score d'exposition"
3. Remplacez le lien dans les emails du kit de vente

---

## ════════════════════════════════════════════════════════════
## ÉTAPE 4 — LANCEMENT (aujourd'hui / cette semaine)
## ════════════════════════════════════════════════════════════

### Aujourd'hui (1h) :
[x] `crisis_dashboard.py` déployé publiquement : https://nexus-ai-empire-6yrflyffrz2l6jxaxtk9gf.streamlit.app
[x] Lien Stripe vérifié le 21/09 : checkout fonctionnel, 49€/mois (abonnement, pas un achat unique) — renommer le produit Stripe "Accès API OSINT Premium" → "Nexus AI - Supply Chain Shield"
[ ] Publier le POST LINKEDIN n°1 de `VENTE_KIT_NEXUS.md` (daté aujourd'hui dans `linkedin_posts.csv`)
[x] 5 cold emails envoyés le 21/09 (FE Components, Dynasource, Terre Exotique, Beasy World Sourcing, Darriah Company) — depuis vinc.nglsn@gmail.com

### Cette semaine :
[ ] POST LINKEDIN n°2 et n°3 (voir dates disponibles dans `linkedin_posts.csv`, déjà mis à jour avec 3 nouveaux posts datés du crise du jour)
[x] 2 emails partenaires en brouillon (vinc.nglsn@gmail.com) : GFSLogistics (Marseille, commercial@gfslogistics.fr) et IdrisMans Transit (Paris, idris@idrismans.com) — à valider/envoyer
[ ] 15-20 cold emails PME supplémentaires (5 déjà envoyés le 21/09)

### Objectif J+7 :
→ 10 démos/tests avec fichier réel
→ 3-5 abonnements à 49€/mois = premiers euros encaissés (+ MRR récurrent)
→ 1 partenaire transitaire intéressé = pipeline de prospects récurrent

---

## ════════════════════════════════════════════════════════════
## RESSOURCES
## ════════════════════════════════════════════════════════════

| Fichier | Usage |
|---------|-------|
| `VENTE_KIT_NEXUS.md` | LinkedIn posts + cold emails + email partenaire + copy Product Hunt |
| `crisis_dashboard.py` | Le produit (dashboard + paywall Stripe + moteur IA), hook mis à jour |
| `linkedin_posts.csv` | File d'attente de publication (3 nouveaux posts Nexus ajoutés) |
| `tunnel_public.py` | Exposer l'app en public pour une démo live immédiate |

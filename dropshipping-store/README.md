# CURVÉA — boutique dropshipping mono-produit (0€ de frais fixes)

Landing page statique (HTML/CSS/JS, aucun backend) pour vendre un seul produit en dropshipping :
legging sculptant taille haute, effet push-up.

## Stack

- Site statique (pas de framework, pas de build) → hébergeable gratuitement sur Vercel/Netlify/GitHub Pages
- Paiement : **Stripe Payment Link** (aucun code serveur, aucun abonnement — juste la commission Stripe par vente)
- Fournisseur : AliExpress, commande manuelle à réception de chaque paiement (voir [FULFILLMENT.md](FULFILLMENT.md))

## Avant la mise en ligne publique

1. ✅ **Stripe Payment Link créé** : https://buy.stripe.com/00w8wP6AU5TJ6Id2Cp87K03
   (produit "Legging Sculptant Push-Up Taille Haute", 34,90€, livraison France, champ Taille en liste déroulante,
   collecte nom + adresse de facturation/livraison). Déjà intégré dans `index.html`.
2. **Compléter les mentions légales** (`mentions-legales.html`) : les champs `[À COMPLÉTER]` (SIRET, statut juridique, adresse)
   sont obligatoires légalement en France avant d'ouvrir la boutique à de vrais clients.
3. **Déployer** : créer un nouveau projet Vercel pointant sur ce dépôt avec comme "Root Directory" `dropshipping-store/`
   (projet séparé du reste du repo, qui héberge déjà Nexus AI). Aucune configuration de build nécessaire (site statique).
4. Optionnel : domaine personnalisé (~10€/an) une fois que le produit se vend, sinon le sous-domaine `*.vercel.app` gratuit suffit.

## Structure

```
dropshipping-store/
  index.html            page produit (hero, bénéfices, FAQ, CTA Stripe)
  mentions-legales.html
  cgv.html
  politique-retour.html
  assets/style.css
  assets/script.js
  FULFILLMENT.md        mode d'emploi de traitement des commandes
```

## Marge

Coût fournisseur ~14,79€ / prix de vente 34,90€ → ~20€ de marge brute avant frais Stripe (~1,5% + 0,25€) et budget pub éventuel.

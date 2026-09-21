# CURVÉA — boutique dropshipping mono-produit (0€ de frais fixes)

Landing page statique (HTML/CSS/JS, aucun backend) pour vendre un seul produit en dropshipping :
legging sculptant taille haute, effet push-up.

## Stack

- Site statique (pas de framework, pas de build) → hébergeable gratuitement sur Vercel/Netlify/GitHub Pages
- Paiement : **Stripe Payment Link** (aucun code serveur, aucun abonnement — juste la commission Stripe par vente)
- Fournisseur : AliExpress, commande manuelle à réception de chaque paiement (voir [FULFILLMENT.md](FULFILLMENT.md))

## Avant la mise en ligne publique

1. **Créer le Stripe Payment Link** pour "Legging Sculptant Push-Up" à 34,90€, avec collecte d'adresse de livraison et
   des variantes taille (S/M/L/XL/XXL) activée. Remplacer `#STRIPE_PAYMENT_LINK_ICI` dans `index.html` (bouton "Je commande maintenant")
   par l'URL réelle du Payment Link.
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

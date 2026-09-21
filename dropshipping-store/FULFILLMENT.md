# Traitement des commandes — CURVÉA

Boutique mono-produit sans backend : chaque vente arrive via Stripe, le traitement se fait à la main. Compter ~2 minutes par commande.

## Produit vendu

- **Produit fournisseur** : Legging de sport taille haute, effet push-up fessier
- **Lien fournisseur (AliExpress)** : https://fr.aliexpress.com/item/1005010759421776.html
- **Coût d'achat** : ~14,79€ / pièce (livraison gratuite vers la France incluse côté fournisseur)
- **Prix de vente boutique** : 34,90€
- **Marge brute avant frais Stripe/pub** : ~20€/vente

## À chaque commande

1. **Notification** : un email Stripe arrive à chaque paiement réussi (adresse configurée dans le compte Stripe "What else by Vinc"). Le tableau de bord Stripe (dashboard.stripe.com → Paiements) donne aussi : nom du client, adresse de livraison, taille/coloris choisis (si collectés via le Payment Link), montant.
2. **Commander chez le fournisseur** : aller sur le lien produit AliExpress ci-dessus, choisir la taille et le coloris indiqués par le client, renseigner l'adresse de livraison **du client** (pas la tienne) comme adresse de destination, payer avec ta carte/le solde du compte AliExpress.
3. **Récupérer le numéro de suivi** : une fois la commande AliExpress expédiée (généralement sous 1 à 3 jours), copier le numéro de suivi depuis AliExpress.
4. **Prévenir le client** : lui envoyer un email (depuis vinc.nglsn@gmail.com) avec le numéro de suivi et le lien de suivi colis.
5. **Suivi** : en cas de souci (retard, colis perdu, produit défectueux), voir la politique de retour du site — AliExpress rembourse aussi le vendeur si le colis n'arrive pas sous 35 jours, ce qui te couvre.

## Notes

- Ce flux est 100% manuel : pas d'abonnement à un outil de fulfillment automatique (DSers, Zendrop...). Si le volume de commandes augmente, ça vaudra le coup d'automatiser — mais pas nécessaire pour démarrer à 0€.
- Le produit encaissé par Stripe est réglé immédiatement ; l'achat côté AliExpress se fait donc avec ta propre carte, remboursé par la marge de la vente.

import streamlit as st
import pandas as pd
import os
import requests
from dotenv import load_dotenv

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

# Chargement de la clé API : Streamlit Cloud (st.secrets) en priorité, sinon .env local
try:
    if "GEMINI_API_KEY" in st.secrets:
        os.environ["GEMINI_API_KEY"] = str(st.secrets["GEMINI_API_KEY"])
except Exception:
    pass

if "GEMINI_API_KEY" not in os.environ:
    load_dotenv("../worldmonitor_test/.env")

api_key = os.environ.get("GEMINI_API_KEY")

st.set_page_config(page_title="Nexus AI - SaaS Logistique", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    .alert-box { padding: 20px; background-color: #ff4b4b; color: white; border-radius: 5px; margin-bottom: 25px; }
    .paywall { padding: 40px; background-color: #1e1e1e; border: 2px solid #3b82f6; border-radius: 10px; text-align: center; margin-top: 50px;}
</style>
""", unsafe_allow_html=True)

# --- SYSTEME DE PAYWALL (STRIPE) ---
st.sidebar.title("🔐 Accès Logiciel")
st.sidebar.markdown("Veuillez entrer le mot de passe VIP reçu après votre paiement Stripe.")
license_key = st.sidebar.text_input("Mot de passe d'accès", type="password")

# Fonction de vérification Stripe (Mot de passe universel ou admin)
def verify_license(key):
    if key in ["DEMO123", "NEXUS-PRO-2026"]: 
        return True
    return False

if not verify_license(license_key):
    st.markdown("""
    <div class="paywall">
        <h2>🔒 Logiciel Verrouillé</h2>
        <p>Abonnez-vous à 49€/mois (résiliable à tout moment) pour débloquer l'Intelligence Artificielle et analyser vos fichiers Excel.</p>
        <a href="https://buy.stripe.com/8x2aEX6AU1Dt8Qldh387K00" target="_blank" style="background-color: #635bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">Payer de manière sécurisée avec Stripe</a>
        <p style="font-size: 12px; margin-top: 15px; color: gray;">Le mot de passe VIP vous sera envoyé par email après votre paiement.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop() # Arrête l'exécution ici si pas de licence

st.sidebar.success("✅ Licence Valide. Accès autorisé.")

# --- APPLICATION SAAS ---
st.title("🛡️ Supply Chain AI Shield - Espace Client")
st.markdown("Importez votre fichier d'inventaire. L'IA va croiser vos données avec les alertes mondiales en cours.")
st.divider()

# Alerte Worldmonitor en direct
st.markdown("""
<div class="alert-box">
    <h4 style="margin-top:0; color:white;">🚨 ALERTE OSINT EN COURS : ORMUZ ET BAB EL-MANDEB TOUS DEUX SOUS TENSION</h4>
    Les Houthis contrôlent désormais les deux chenaux du détroit de Bab el-Mandeb (îles Mayun/Perim puis Hanish, prises les 11-12/09) : la Mer Rouge/Suez n'est plus une route de repli fiable face à Ormuz, les deux corridors sont contestés simultanément.
    Brouillage GPS actif en Mer Noire, Baltique et Golfe Persique. Arrêt de l'oléoduc Est-Ouest saoudien. Probabilité de perturbation du trafic Détroit d'Ormuz : 35-40% (marché).
    Conséquence directe : le fret aérien Chine→Europe dépasse 4,80 $/kg (+75% vs avant-conflit), avec 13-15% de la capacité aérienne mondiale clouée au sol.
</div>
""", unsafe_allow_html=True)

# Fourchettes publiques des surcharges conflit par corridor (USD par conteneur).
# Montants issus des avis transporteurs publiés ; à réviser dès qu'un transporteur les modifie.
WAR_RISK_RANGES = {
    "Golfe Persique (EAU, Qatar, Arabie saoudite, Koweït, Bahreïn, Irak, Oman)": {
        "date": "mars 2026",
        "sources": [
            ("Hapag-Lloyd — War Risk Surcharge : 1 500 USD/TEU, 3 500 USD reefer", "https://www.ttl-co.com/en/blog/war-risk-surcharge-gulf-shipping-2026"),
            ("CMA CGM — Emergency Conflict Surcharge : 2 000 / 3 000 / 4 000 USD", "https://www.ttl-co.com/en/blog/war-risk-surcharge-gulf-shipping-2026"),
            ("Maersk — Emergency Freight Rate : 1 800 / 3 000 / 3 800 USD", "https://www.ttl-co.com/en/blog/war-risk-surcharge-gulf-shipping-2026"),
        ],
        "types": {
            "20' dry": (1500, 2000),
            "40' dry": (3000, 3000),
            "Reefer / équipement spécial": (3500, 4000),
        },
    },
    "Mer Rouge (Djeddah, King Abdullah, Jordanie)": {
        "date": "août 2026",
        "sources": [
            ("Maersk — surcharge Mer Rouge (Océanie-Moyen-Orient) : 1 800 / 3 000 USD, jusqu'à 100% de plus que le Golfe", "https://www.indoneo.com/capital/maersk-red-sea-surcharge-oceania-middle-east-august-2026/"),
            ("MSC — Péninsule arabique vers Afrique/Océan Indien : 2 000 / 3 000 / 4 000 USD", "https://www.yqn.com/intro/blog/post/war_risk_surcharge"),
        ],
        "types": {
            "20' dry": (1800, 2000),
            "40' dry": (3000, 3000),
            "Reefer / équipement spécial": (1900, 3800),
        },
    },
}


def auditer_surcharge(montant, bas, haut):
    if montant > haut:
        return "haut", montant - haut
    if montant < bas:
        return "bas", bas - montant
    return "ok", 0


st.subheader("🔎 Audit de surcharge « war risk »")
st.markdown("Votre transporteur vous facture une surcharge conflit ? Vérifiez qu'elle correspond aux montants publiés par les grands armateurs.")

col_a, col_b, col_c = st.columns(3)
with col_a:
    corridor = st.selectbox("Corridor", list(WAR_RISK_RANGES.keys()))
with col_b:
    type_conteneur = st.selectbox("Type de conteneur", list(WAR_RISK_RANGES[corridor]["types"].keys()))
with col_c:
    montant_facture = st.number_input("Surcharge facturée (USD / conteneur)", min_value=0, step=50, value=0)

if montant_facture > 0:
    bas, haut = WAR_RISK_RANGES[corridor]["types"][type_conteneur]
    fourchette = f"{bas:,} USD" if bas == haut else f"{bas:,} – {haut:,} USD"
    verdict, ecart = auditer_surcharge(montant_facture, bas, haut)
    if verdict == "haut":
        st.error(f"⚠️ Au-dessus des montants publiés ({fourchette}) : {ecart:,} USD de plus par conteneur. Demandez à votre transporteur le détail et la justification de cette surcharge.")
    elif verdict == "bas":
        st.success(f"✅ En dessous des montants publiés ({fourchette}), {ecart:,} USD de moins par conteneur.")
    else:
        st.info(f"Dans la fourchette publiée par les grands armateurs ({fourchette}).")

    infos = WAR_RISK_RANGES[corridor]
    st.caption(
        f"Références : avis transporteurs publiés en {infos['date']}, relayés par la presse spécialisée accessible gratuitement. "
        "Les montants évoluent avec la situation : vérifiez toujours auprès de votre transporteur. "
        "Une surcharge carburant d'urgence (EBS/EFS) peut s'ajouter séparément."
    )
    for libelle, url in infos["sources"]:
        st.caption(f"• [{libelle}]({url})")

st.divider()

# Import du fichier Excel par le client
st.subheader("1. Importez vos données (Bring Your Own Excel)")
uploaded_file = st.file_uploader("Glissez votre fichier Excel ou CSV ici", type=["csv", "xlsx"])

if uploaded_file is None:
    st.info("💡 En attente de votre fichier. Si vous n'en avez pas, créez un fichier Excel simple avec 3 colonnes : Fournisseur, Marchandise, Valeur.")
else:
    # Lecture du fichier
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, sep=None, engine='python') # Tente de détecter le délimiteur
        else:
            df = pd.read_excel(uploaded_file)
            
        st.success("Fichier importé avec succès !")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        total_value = 0
        if "Valeur" in df.columns:
            total_value = df["Valeur"].sum()
            
    except Exception as e:
        st.error(f"Erreur de lecture du fichier : {e}")
        st.stop()

    st.divider()

    # Moteur de Résolution IA
    st.subheader("2. 🧠 Génération du Rapport de Continuité")
    
    if st.button("⚡ Analyser et Générer le Plan de Sauvetage", type="primary"):
        if not api_key or not genai:
            st.error("Erreur : Clé API Gemini manquante.")
        else:
            with st.spinner("Analyse de votre fichier en cours... Recherche d'alternatives mondiales..."):
                try:
                    client = genai.Client(api_key=api_key)
                    
                    prompt = f"""
                    Tu es une IA de crise Supply Chain (SaaS).
                    Contexte de crise actuel : les Houthis contrôlent les deux chenaux du détroit de Bab el-Mandeb depuis le 11-12/09 (îles Mayun/Perim puis Hanish) — la Mer Rouge/Suez n'est PAS une route de repli fiable, ce corridor est aussi contesté qu'Ormuz (35-40% de probabilité de perturbation, marché). Brouillage GPS en Mer Noire/Baltique/Golfe Persique, arrêt de l'oléoduc Est-Ouest saoudien.
                    Le fret aérien Chine→Europe dépasse 4,80 $/kg (+75% vs avant-conflit), 13-15% de la capacité aérienne mondiale est clouée au sol : l'alternative aérienne coûte cher elle aussi.
                    Voici les données extraites du fichier Excel du client :
                    {df.to_json()}

                    Rédige un plan de sauvetage (Contingency Plan) direct et professionnel.
                    NE PROPOSE PAS le contournement par Suez/Bab el-Mandeb comme solution sûre — les deux corridors maritimes sont contestés simultanément. Trouve des fournisseurs alternatifs fictifs mais réalistes en Europe/US pour remplacer ces marchandises, chiffre l'arbitrage réel entre surcoût de fret aérien (au tarif actuel ~4,80 $/kg) et le coût du retard maritime, et donne une marche à suivre claire.
                    """
                    
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt,
                        config=types.GenerateContentConfig(temperature=0.3)
                    )
                    
                    st.success("✅ Rapport généré.")
                    with st.expander("📄 TÉLÉCHARGER LE RAPPORT PDF (Simulation)", expanded=True):
                        st.markdown(response.text)
                        
                except Exception as e:
                    st.error(f"Erreur IA : {e}")

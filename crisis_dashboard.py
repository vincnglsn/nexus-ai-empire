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
    <h4 style="margin-top:0; color:white;">🚨 ALERTE OSINT EN COURS : DÉTROIT D'ORMUZ & MER ROUGE</h4>
    Posture "Élevée" sur Mer Rouge/Yémen et Mer de Chine méridionale. Brouillage GPS actif en Mer Noire, Baltique et Golfe Persique.
    Arrêt de l'oléoduc Est-Ouest saoudien. Probabilité de perturbation du trafic Détroit d'Ormuz : 35-40% (marché). Risque élevé de surcoût fret et délais pour les flux Asie/Moyen-Orient-Europe.
</div>
""", unsafe_allow_html=True)

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
                    Contexte de crise actuel : posture "Élevée" sur Mer Rouge/Yémen et Mer de Chine méridionale, brouillage GPS en Mer Noire/Baltique/Golfe Persique,
                    arrêt de l'oléoduc Est-Ouest saoudien, et probabilité de 35-40% de perturbation du trafic au Détroit d'Ormuz. Voici les données extraites du fichier Excel du client :
                    {df.to_json()}

                    Rédige un plan de sauvetage (Contingency Plan) direct et professionnel.
                    Trouve des fournisseurs alternatifs fictifs mais réalistes en Europe/US pour remplacer ces marchandises, estime le surcoût de fret aérien, et donne une marche à suivre claire.
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

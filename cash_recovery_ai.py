import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

# Chargement de la clé API
load_dotenv("../worldmonitor_test/.env")
api_key = os.environ.get("GEMINI_API_KEY")

st.set_page_config(page_title="Cash-Flow AI | Recouvrement", page_icon="💸", layout="wide")

# --- SYSTEME DE PAYWALL ---
st.sidebar.title("🔐 Accès Logiciel")
st.sidebar.markdown("Saisissez votre clé de licence pour utiliser l'Agent de Recouvrement.")
license_key = st.sidebar.text_input("Clé d'accès", type="password")

if license_key not in ["DEMO123", "CASHFLOW-2026"]:
    st.markdown("""
    <div style="padding: 40px; background-color: #1e1e1e; border: 2px solid #22c55e; border-radius: 10px; text-align: center; margin-top: 50px;">
        <h2>💸 Cash-Flow AI Verrouillé</h2>
        <p>Récupérez la trésorerie bloquée chez vos clients retardataires. L'IA génère des relances et mises en demeure intraîtables.</p>
        <a href="https://buy.stripe.com/cNieVd0cwgyn2rXgtf87K02" style="background-color: #22c55e; color: black; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">Acheter une Licence (99€/mois)</a>
        <p style="font-size: 12px; margin-top: 15px; color: gray;">Votre clé d'accès vous sera envoyée par email après votre paiement.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

st.title("💸 Cash-Flow AI - Agent de Recouvrement")
st.markdown("Importez la liste de vos factures impayées. Notre Agent IA va rédiger des emails de relance psychologiquement et juridiquement calibrés pour forcer le paiement.")

# Données d'exemple intégrées pour faciliter la démo
st.info("💡 Chargez votre fichier CSV ou utilisez les données de test ci-dessous.")
demo_data = pd.DataFrame({
    "Client": ["Entreprise Alpha", "Boutique Beta", "Gamma Industries"],
    "Facture": ["F-2026-001", "F-2026-042", "F-2025-999"],
    "Montant (€)": [1500, 450, 12400],
    "Jours_Retard": [12, 45, 95]
})

uploaded_file = st.file_uploader("Fichier des impayés (CSV, Excel)", type=["csv", "xlsx"])

if uploaded_file is not None:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file, sep=None, engine='python')
    else:
        df = pd.read_excel(uploaded_file)
else:
    st.warning("Aucun fichier détecté. Utilisation des données de démonstration.")
    df = demo_data

st.dataframe(df, use_container_width=True)

if st.button("⚡ Générer les Emails de Recouvrement", type="primary"):
    if not api_key or not genai:
        st.error("Erreur : Clé API Gemini manquante.")
    else:
        with st.spinner("L'Agent IA rédige les mises en demeure..."):
            client = genai.Client(api_key=api_key)
            
            st.divider()
            st.subheader("📬 Vos Relances Prêtes à l'Envoi")
            
            for index, row in df.iterrows():
                client_name = row.get("Client", "Client Inconnu")
                montant = row.get("Montant (€)", 0)
                retard = row.get("Jours_Retard", 0)
                facture = row.get("Facture", "N/A")
                
                # Le Prompt IA s'adapte à la gravité du retard
                prompt = f"""
                Tu es un expert en recouvrement de créances en France.
                Rédige un e-mail de relance à l'entreprise '{client_name}'.
                La facture {facture} d'un montant de {montant}€ est en retard de {retard} jours.
                
                Règles de ton :
                - Moins de 15 jours de retard : Ton très poli, rappel amical ("un simple oubli").
                - Entre 15 et 60 jours : Ton ferme, insistance sur les pénalités de retard légales (taux BCE + 10 points, indemnité forfaitaire de 40€).
                - Plus de 60 jours de retard : Mise en demeure formelle avant action en justice (injonction de payer au tribunal de commerce).
                
                Ne génère que l'objet et le corps de l'e-mail. Utilise le vouvoiement. Pas de bla-bla.
                """
                
                try:
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt,
                        config=types.GenerateContentConfig(temperature=0.3)
                    )
                    
                    # Interface UI : Un accordéon par client
                    color = "red" if retard > 60 else "orange" if retard > 15 else "green"
                    with st.expander(f"✉️ Relance {client_name} - {montant}€ ({retard} jours de retard)"):
                        st.markdown(response.text)
                        
                except Exception as e:
                    st.error(f"Erreur pour {client_name}: {e}")

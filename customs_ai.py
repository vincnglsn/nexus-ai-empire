import streamlit as st
import os
import tempfile
from dotenv import load_dotenv

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

# Chargement de la clé API
load_dotenv("../worldmonitor_test/.env")
api_key = os.environ.get("GEMINI_API_KEY")

st.set_page_config(page_title="Customs Document AI", page_icon="🛂", layout="centered")

# --- SYSTEME DE PAYWALL (UPSELL) ---
st.sidebar.title("🔐 Accès Premium")
st.sidebar.markdown("Veuillez entrer le mot de passe reçu après l'achat de l'extension Douane.")
license_key = st.sidebar.text_input("Mot de passe", type="password")

if license_key not in ["DEMO123", "NEXUS-CUSTOMS-2026"]:
    st.markdown("""
    <div style="padding: 40px; background-color: #1e1e1e; border: 2px solid #eab308; border-radius: 10px; text-align: center; margin-top: 50px;">
        <h2>🔒 Module Premium Verrouillé</h2>
        <p>L'intelligence artificielle d'analyse douanière est une extension (99€).</p>
        <a href="https://buy.stripe.com/14A8wPf7q81R0jP4Kx87K01" target="_blank" style="background-color: #eab308; color: black; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">Débloquer le Module Douane (99€)</a>
        <p style="font-size: 12px; margin-top: 15px; color: gray;">Le mot de passe VIP vous sera envoyé par email après votre paiement.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

st.sidebar.success("✅ Accès Premium Autorisé.")

# --- APPLICATION SAAS ---
st.title("🛂 Customs Document AI")
st.markdown("### Évitez les blocages aux frontières européennes.")
st.markdown("Glissez votre document logistique (Bill of Lading, Facture Proforma, Packing List). L'IA Vision va le scanner et détecter toute anomalie juridique ou mention manquante (Code HS, EORI, Incoterms).")

st.info("💡 Formats acceptés : PDF, JPG, PNG.")

uploaded_file = st.file_uploader("Document Douanier", type=["pdf", "jpg", "jpeg", "png"])

if uploaded_file is not None:
    if st.button("🔍 Lancer l'Audit Douanier", type="primary"):
        if not api_key or not genai:
            st.error("Erreur : Clé API Gemini manquante.")
        else:
            with st.spinner("Numérisation et analyse du document par Gemini Vision..."):
                try:
                    # Sauvegarde temporaire du fichier pour l'envoi à l'API Gemini
                    ext = uploaded_file.name.split('.')[-1]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
                        tmp.write(uploaded_file.getvalue())
                        tmp_path = tmp.name
                    
                    client = genai.Client(api_key=api_key)
                    
                    # Upload sécurisé vers Gemini
                    gemini_file = client.files.upload(file=tmp_path)
                    
                    prompt = """
                    Tu es un Expert Déclarant en Douane Européenne ultra-compétent.
                    Analyse ce document logistique scanné.
                    
                    Structure obligatoire de ta réponse :
                    1. 📄 **Type de Document identifié** (Facture, Connaissement maritime, etc.)
                    2. ✅ **Mentions valides** (Ce qui est correct).
                    3. ❌ **MENTIONS MANQUANTES ET RISQUES** (Analyse minutieusement s'il manque le Code HS, le numéro EORI, le Poids brut/net, le pays d'origine, l'Incoterm).
                    4. ⚖️ **Verdict final :** La marchandise passera-t-elle la douane ? (Oui/Non/Risque de blocage).
                    
                    Sois très direct, professionnel et orienté conformité douanière (Compliance).
                    """
                    
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[gemini_file, prompt]
                    )
                    
                    st.divider()
                    st.success("✅ Audit Douanier Terminé.")
                    st.markdown(response.text)
                    
                    # Nettoyage du fichier temporaire
                    os.remove(tmp_path)
                    
                except Exception as e:
                    st.error(f"Une erreur s'est produite lors de l'analyse : {e}")

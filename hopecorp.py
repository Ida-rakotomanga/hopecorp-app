import streamlit as st
import datetime
from fpdf import FPDF

# Configuration
st.set_page_config(page_title="HOPECORP", layout="centered", page_icon="🧵")

# --- DONNÉES ---
standards = {
    "Femme": {"34 (XS)": {"Poitrine": 80, "Taille": 62}, "36 (S)": {"Poitrine": 84, "Taille": 66}, "38 (M)": {"Poitrine": 92, "Taille": 74}},
    "Homme": {"44 (XS)": {"Poitrine": 88, "Taille": 76}, "46 (S)": {"Poitrine": 92, "Taille": 80}}
}

categories = {
    "IDENTITE": ["Nom Complet", "Date de mesure", "Notes"],
    "1. LES TOURS": ["Tour de cou", "Tour de poitrine", "Tour de taille", "Bassin (Gdes hanches)", "Tour de bras", "Tour de cuisse"],
    "2. LES LONGUEURS": ["Hauteur totale", "Epaule-taille", "Hauteur poitrine", "Jambe (Ext)", "Longueur de bras"],
    "3. SPECIFIQUES": ["Largeur epaule", "Carrure devant", "Carrure dos", "Enfourchure"],
    "4. PROJET (Photo/Tissu)": []
}

# --- INITIALISATION ---
if "data" not in st.session_state:
    st.session_state.data = {}

# Nettoyage et initialisation forcée
for cat_list in categories.values():
    for m in cat_list:
        if m not in st.session_state.data:
            st.session_state.data[m] = 0.0 if "Tour" in m or "Hauteur" in m or "Jambe" in m else ""

if not isinstance(st.session_state.data.get("Date de mesure"), datetime.date):
    st.session_state.data["Date de mesure"] = datetime.date.today()

# --- INTERFACE ---
st.title("🧵 HOPECORP")
page = st.sidebar.radio("Navigation", list(categories.keys()))

if page == "4. PROJET (Photo/Tissu)":
    st.header("📸 Projet")
    st.info("Section photo et métrage active.")
else:
    st.header(page)
    for label in categories[page]:
        if label == "Date de mesure":
            st.session_state.data[label] = st.date_input(label, value=st.session_state.data[label])
        elif label in ["Notes", "Nom Complet"]:
            st.session_state.data[label] = st.text_input(label, value=str(st.session_state.data.get(label, "")))
        else:
            val = st.session_state.data.get(label, 0.0)
            st.session_state.data[label] = st.number_input(label, min_value=0.0, value=float(val) if isinstance(val, (int,float)) else 0.0, step=0.5)

# --- TAILLE ESTIMÉE ---
st.sidebar.divider()
p = st.session_state.data.get("Tour de poitrine", 0.0)
if isinstance(p, (int, float)) and p > 40:
    st.sidebar.success(f"Taille : {p} cm détectés")

# --- GÉNÉRATEUR PDF ULTRA-ROBUSTE ---
def generate_pdf(data):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "FICHE DE MESURE - HOPECORP", ln=True, align="C")
        pdf.ln(10)
        
        pdf.set_font("Arial", "B", 12)
        nom_client = str(data.get('Nom Complet', '-'))
        date_m = str(data.get('Date de mesure', '-'))
        
        pdf.cell(0, 10, f"Client : {nom_client if nom_client.strip() else '-'}", ln=True)
        pdf.cell(0, 10, f"Date : {date_m}", ln=True)
        pdf.ln(5)
        
        pdf.set_font("Arial", "", 10)
        # On trie les données pour un PDF propre
        for k, v in data.items():
            if k not in ["Nom Complet", "Date de mesure", "image_modele"]:
                valeur = str(v) if v not in [0.0, "", 0] else "-"
                pdf.cell(90, 8, f"{str(k)}:", border=1)
                pdf.cell(0, 8, valeur, border=1, ln=True)
        
        return pdf.output()
    except Exception as e:
        return None

# --- BOUTON DE TÉLÉCHARGEMENT ---
st.sidebar.divider()
pdf_file = generate_pdf(st.session_state.data)

if pdf_file:
    st.sidebar.download_button(
        label="📥 Télécharger le PDF",
        data=bytes(pdf_file),
        file_name=f"Fiche_HOPECORP.pdf",
        mime="application/pdf"
    )
else:
    st.sidebar.error("Erreur de création PDF")

import streamlit as st
import datetime
from fpdf import FPDF

# Configuration
st.set_page_config(page_title="HOPECORP - Mesures Pro", layout="centered", page_icon="🧵")

# --- CATÉGORIES DÉTAILLÉES ---
categories = {
    "IDENTITE": ["Nom Complet", "Date de mesure", "Notes"],
    "1. LES TOURS": [
        "Tour de cou", "Tour de poitrine (Plein)", "Haut de poitrine", "Dessous de poitrine", 
        "Tour de taille", "Petites hanches", "Bassin (Grandes hanches)", 
        "Tour de bras (Biceps)", "Tour de poignet", "Tour de cuisse", "Tour de genou", "Tour de cheville"
    ],
    "2. LES LONGUEURS": [
        "Hauteur totale", "Epaule - Taille (Devant)", "Epaule - Taille (Dos)", 
        "Hauteur poitrine", "Ecartement poitrine", "Longueur épaule",
        "Longueur manche", "Longueur bras (plié)", "Longueur jupe/pantalon",
        "Entrejambe", "Montante (Fourche)"
    ],
    "3. CARRURES & LARGUEURS": [
        "Carrure devant", "Carrure dos", "Largeur dos", 
        "Largeur d'épaule à épaule", "Profondeur d'encolure"
    ],
    "4. PROJET (Photo/Tissu)": []
}

# --- INITIALISATION ---
if "data" not in st.session_state:
    st.session_state.data = {}

for cat_list in categories.values():
    for m in cat_list:
        if m not in st.session_state.data:
            st.session_state.data[m] = 0.0 if m not in ["Nom Complet", "Notes"] else ""

if not isinstance(st.session_state.data.get("Date de mesure"), datetime.date):
    st.session_state.data["Date de mesure"] = datetime.date.today()

# --- INTERFACE ---
st.title("🧵 HOPECORP")
page = st.sidebar.radio("Navigation", list(categories.keys()))
st.header(page)

if page == "4. PROJET (Photo/Tissu)":
    st.info("Section dédiée au suivi du modèle et métrage.")
else:
    for label in categories[page]:
        if label == "Date de mesure":
            st.session_state.data[label] = st.date_input(label, value=st.session_state.data[label])
        elif label in ["Notes", "Nom Complet"]:
            st.session_state.data[label] = st.text_input(label, value=str(st.session_state.data.get(label, "")))
        else:
            val = st.session_state.data.get(label, 0.0)
            st.session_state.data[label] = st.number_input(label, min_value=0.0, value=float(val), step=0.5)

# --- GÉNÉRATEUR PDF ---
def generate_pdf(data):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "FICHE TECHNIQUE - HOPECORP", ln=True, align="C")
        pdf.ln(5)
        
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 10, f"CLIENT : {str(data.get('Nom Complet', '-'))}", ln=True)
        pdf.cell(0, 10, f"DATE : {str(data.get('Date de mesure', '-'))}", ln=True)
        pdf.ln(3)
        
        pdf.set_font("Arial", "", 9)
        # Organisation par colonnes pour ne pas avoir un PDF trop long
        for k, v in data.items():
            if k not in ["Nom Complet", "Date de mesure", "image_modele"]:
                valeur = str(v) if v not in [0.0, "", 0] else "-"
                pdf.cell(80, 7, f"{str(k)}", border=1)
                pdf.cell(30, 7, f"{valeur} cm" if v not in [0.0, "", 0] else "-", border=1, ln=True)
        return pdf.output()
    except: return None

# --- BOUTON PDF ---
st.sidebar.divider()
pdf_file = generate_pdf(st.session_state.data)
if pdf_file:
    st.sidebar.download_button("📥 Télécharger PDF Complet", data=bytes(pdf_file), file_name="Fiche_Mesures.pdf", mime="application/pdf")

import streamlit as st
import datetime
from fpdf import FPDF

# Configuration
st.set_page_config(page_title="HOPECORP - Mesures Pro", layout="centered", page_icon="🧵")

# --- TOUTES LES MESURES DÉTAILLÉES ---
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
    "4. PROJET": ["Type de vêtement", "Métrage estimé (m)", "Laize tissu (cm)"]
}

# --- INITIALISATION & NETTOYAGE CRITIQUE ---
if "data" not in st.session_state:
    st.session_state.data = {}

# Cette boucle répare les erreurs de type (ex: du texte là où on veut un chiffre)
for cat, items in categories.items():
    for item in items:
        if item not in st.session_state.data:
            if item in ["Nom Complet", "Notes", "Type de vêtement"]:
                st.session_state.data[item] = ""
            elif item == "Date de mesure":
                st.session_state.data[item] = datetime.date.today()
            else:
                st.session_state.data[item] = 0.0
        else:
            # Vérification de sécurité pour éviter les plantages st.number_input
            if item not in ["Nom Complet", "Notes", "Date de mesure", "Type de vêtement"]:
                try:
                    st.session_state.data[item] = float(st.session_state.data[item])
                except:
                    st.session_state.data[item] = 0.0

# --- INTERFACE ---
st.title("🧵 HOPECORP")
page = st.sidebar.radio("Navigation", list(categories.keys()))
st.header(page)

# Formulaire dynamique
for label in categories[page]:
    if label == "Date de mesure":
        st.session_state.data[label] = st.date_input(label, value=st.session_state.data[label])
    elif label in ["Notes", "Nom Complet", "Type de vêtement"]:
        st.session_state.data[label] = st.text_input(label, value=str(st.session_state.data[label]))
    else:
        # number_input est très sensible : on s'assure que value est bien un float
        val_actuelle = float(st.session_state.data.get(label, 0.0))
        st.session_state.data[label] = st.number_input(label, min_value=0.0, value=val_actuelle, step=0.5)

# --- GÉNÉRATEUR PDF (SANS ERREUR) ---
def generate_pdf(data):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "FICHE TECHNIQUE - HOPECORP", ln=True, align="C")
        pdf.ln(5)
        
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, f"CLIENT : {str(data.get('Nom Complet', '-'))}", ln=True)
        pdf.cell(0, 8, f"DATE : {str(data.get('Date de mesure', '-'))}", ln=True)
        pdf.ln(5)
        
        pdf.set_font("Arial", "", 10)
        for k, v in data.items():
            if k not in ["Nom Complet", "Date de mesure"]:
                # Affichage propre des mesures remplies
                txt_v = str(v) if v not in [0.0, "", 0] else "-"
                pdf.cell(90, 7, f"{str(k)}", border=1)
                pdf.cell(40, 7, f"{txt_v}", border=1, ln=True)
        return pdf.output()
    except:
        return None

# --- BOUTON DE TÉLÉCHARGEMENT ---
st.sidebar.divider()
try:
    pdf_out = generate_pdf(st.session_state.data)
    if pdf_out:
        st.sidebar.download_button(
            "📥 Télécharger PDF", 
            data=bytes(pdf_out), 
            file_name=f"Fiche_{st.session_state.data['Nom Complet']}.pdf", 
            mime="application/pdf"
        )
except:
    st.sidebar.warning("Remplissez le nom pour le PDF")

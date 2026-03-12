import streamlit as st
import datetime
from fpdf import FPDF

# Configuration
st.set_page_config(page_title="HOPECORP - Atelier Pro", layout="centered", page_icon="🧵")

# --- PARAMÈTRES MÉTRAGE ---
metrage_base = {
    "Robe simple": 2.5, "Robe de soirée": 4.0, "Jupe": 1.5,
    "Pantalon": 2.0, "Veste/Blazer": 2.5, "Chemise/Chemisier": 2.0
}

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
    "4. PROJET (Photo/Métrage)": []
}

# --- INITIALISATION ROBUSTE ---
if "data" not in st.session_state:
    st.session_state.data = {}

# On s'assure que chaque champ existe pour éviter les erreurs de type (TypeError)
for items in categories.values():
    for item in items:
        if item not in st.session_state.data:
            if item == "Date de mesure": st.session_state.data[item] = datetime.date.today()
            elif item in ["Nom Complet", "Notes"]: st.session_state.data[item] = ""
            else: st.session_state.data[item] = 0.0

if "image_modele" not in st.session_state.data: st.session_state.data["image_modele"] = None

# --- INTERFACE ---
st.title("🧵 HOPECORP")
page = st.sidebar.radio("Navigation", list(categories.keys()))
st.header(page)

if page == "4. PROJET (Photo/Métrage)":
    # --- SECTION PHOTO ---
    st.subheader("📸 Modèle")
    uploaded_file = st.file_uploader("Prendre ou charger une photo", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        st.session_state.data["image_modele"] = uploaded_file.read()
    if st.session_state.data.get("image_modele"):
        st.image(st.session_state.data["image_modele"], width=300)
    
    st.divider()
    
    # --- SECTION MÉTRAGE ---
    st.subheader("📏 Calcul du Métrage")
    choix = st.selectbox("Type de vêtement", list(metrage_base.keys()))
    laize = st.select_slider("Laize du tissu (cm)", options=[90, 110, 140, 150], value=140)
    
    besoin = metrage_base[choix]
    if laize < 130: besoin *= 1.3 # Majoration pour tissu étroit
    
    st.session_state.data["Projet"] = choix
    st.session_state.data["Métrage estimé"] = f"{besoin:.1f} m"
    st.metric("Tissu recommandé", f"{besoin:.1f} mètres")

else:
    # --- FORMULAIRE DES MESURES ---
    for label in categories[page]:
        if label == "Date de mesure":
            st.session_state.data[label] = st.date_input(label, value=st.session_state.data[label])
        elif label in ["Notes", "Nom Complet"]:
            st.session_state.data[label] = st.text_input(label, value=str(st.session_state.data.get(label, "")))
        else:
            # Sécurité number_input pour éviter ValueError
            val = st.session_state.data.get(label, 0.0)
            try:
                f_val = float(val)
            except:
                f_val = 0.0
            st.session_state.data[label] = st.number_input(label, min_value=0.0, value=f_val, step=0.5)

# --- GÉNÉRATEUR PDF PROFESSIONNEL ---
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
        if "Projet" in data:
            pdf.cell(0, 8, f"PROJET : {data['Projet']} (Besoin: {data.get('Métrage estimé', '-')})", ln=True)
        pdf.ln(5)
        
        pdf.set_font("Arial", "", 9)
        # Liste des mesures dans le PDF
        for k, v in data.items():
            if k not in ["Nom Complet", "Date de mesure", "image_modele", "Projet", "Métrage estimé"]:
                txt_v = f"{v} cm" if (isinstance(v, float) and v > 0) else "-"
                pdf.cell(90, 7, f"{str(k)}", border=1)
                pdf.cell(40, 7, f"{txt_v}", border=1, ln=True)
        return pdf.output()
    except: return None

# --- BOUTON DE TÉLÉCHARGEMENT ---
st.sidebar.divider()
pdf_file = generate_pdf(st.session_state.data)
if pdf_file:
    st.sidebar.download_button(
        "📥 Télécharger PDF Complet", 
        data=bytes(pdf_file), 
        file_name=f"Fiche_{st.session_state.data.get('Nom Complet', 'Client')}.pdf", 
        mime="application/pdf"
    )

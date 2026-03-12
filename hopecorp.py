import streamlit as st
import datetime
from PIL import Image
import io
from fpdf import FPDF

# Configuration
st.set_page_config(page_title="HOPECORP", layout="centered", page_icon="🧵")

# --- DONNÉES ---
standards = {
    "Femme": {"34 (XS)": {"Poitrine": 80, "Taille": 62, "Bassin": 86}, "36 (S)": {"Poitrine": 84, "Taille": 66, "Bassin": 90}, "38 (S/M)": {"Poitrine": 88, "Taille": 70, "Bassin": 94}, "40 (M)": {"Poitrine": 92, "Taille": 74, "Bassin": 98}},
    "Homme": {"44 (XS)": {"Poitrine": 88, "Taille": 76}, "46 (S)": {"Poitrine": 92, "Taille": 80}, "48 (M)": {"Poitrine": 96, "Taille": 84}}
}
metrage_base = {"Robe": 2.5, "Jupe": 1.5, "Pantalon": 2.0, "Veste": 2.5, "Chemise": 2.0}

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

# On pré-remplit pour éviter les erreurs de clés manquantes (KeyError)
for cat_list in categories.values():
    for m in cat_list:
        if m not in st.session_state.data: st.session_state.data[m] = 0.0

if "Nom Complet" not in st.session_state.data: st.session_state.data["Nom Complet"] = ""
if "Notes" not in st.session_state.data: st.session_state.data["Notes"] = ""
if "Date de mesure" not in st.session_state.data: st.session_state.data["Date de mesure"] = datetime.date.today()
if "image_modele" not in st.session_state.data: st.session_state.data["image_modele"] = None

# --- INTERFACE ---
st.title("🧵 HOPECORP")
page = st.sidebar.radio("Navigation", list(categories.keys()))
st.header(page)

if page == "4. PROJET (Photo/Tissu)":
    st.subheader("📸 Modèle")
    uploaded_file = st.file_uploader("Ajouter une photo", type=["jpg", "png", "jpeg"])
    if uploaded_file: st.session_state.data["image_modele"] = uploaded_file.read()
    if st.session_state.data.get("image_modele"): st.image(st.session_state.data["image_modele"], width=300)
    st.divider()
    st.subheader("📏 Métrage")
    choix = st.selectbox("Vêtement", list(metrage_base.keys()))
    laize = st.select_slider("Laize (cm)", options=[90, 110, 140, 150], value=140)
    besoin = metrage_base[choix]
    if laize < 130: besoin *= 1.3
    st.metric("Tissu estimé", f"{besoin:.1f} m")
else:
    for label in categories[page]:
        if label == "Date de mesure":
            st.session_state.data[label] = st.date_input(label, value=st.session_state.data[label])
        elif label == "Notes":
            st.session_state.data[label] = st.text_area(label, value=str(st.session_state.data[label]))
        elif label == "Nom Complet":
            st.session_state.data[label] = st.text_input(label, value=str(st.session_state.data[label]))
        else:
            val = st.session_state.data.get(label, 0.0)
            st.session_state.data[label] = st.number_input(label, min_value=0.0, value=float(val), step=0.5)

# --- TAILLE ---
st.sidebar.divider()
p = st.session_state.data.get("Tour de poitrine", 0.0)
if p > 40:
    genre = st.sidebar.selectbox("Référence", list(standards.keys()))
    tab = standards[genre]
    best_t = min(tab.keys(), key=lambda n: abs(p - tab[n]["Poitrine"]))
    st.sidebar.success(f"Taille : {best_t}")

# --- GÉNÉRATEUR PDF SÉCURISÉ ---
def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "FICHE DE MESURE - HOPECORP", ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("helvetica", "B", 12)
    # Si le nom est vide, on met "Client Inconnu"
    nom = data.get('Nom Complet', '').strip()
    pdf.cell(0, 10, f"Client : {nom if nom else '-'}", ln=True)
    pdf.cell(0, 10, f"Date : {data.get('Date de mesure')}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("helvetica", "", 10)
    for k, v in data.items():
        if k not in ["image_modele", "Nom Complet", "Date de mesure"]:
            # On transforme tout en texte proprement pour éviter les erreurs de type
            valeur_texte = str(v) if (v != 0.0 and v != "") else "-"
            pdf.cell(90, 8, f"{k}:", border=1)
            pdf.cell(0, 8, valeur_texte, border=1, ln=True)
    return pdf.output()

# --- BOUTON DE TÉLÉCHARGEMENT ---
st.sidebar.divider()
try:
    pdf_bytes = generate_pdf(st.session_state.data)
    st.sidebar.download_button(
        label="📥 Télécharger le PDF",
        data=pdf_bytes,
        file_name=f"Fiche_{st.session_state.data['Nom Complet']}.pdf",
        mime="application/pdf"
    )
except Exception:
    st.sidebar.warning("Erreur lors de la préparation du PDF.")

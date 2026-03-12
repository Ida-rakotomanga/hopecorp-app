import streamlit as st
import datetime
from PIL import Image
import io
from fpdf import FPDF

# Configuration pour smartphone
st.set_page_config(page_title="HOPECORP", layout="centered", page_icon="🧵")

# --- DONNÉES DE RÉFÉRENCE ---
standards = {
    "Femme": {
        "34 (XS)":  {"Poitrine": 80, "Taille": 62, "Bassin": 86},
        "36 (S)":   {"Poitrine": 84, "Taille": 66, "Bassin": 90},
        "38 (S/M)": {"Poitrine": 88, "Taille": 70, "Bassin": 94},
        "40 (M)":   {"Poitrine": 92, "Taille": 74, "Bassin": 98},
        "42 (M/L)": {"Poitrine": 96, "Taille": 78, "Bassin": 102},
        "44 (L)":   {"Poitrine": 100, "Taille": 82, "Bassin": 106},
        "46 (XL)":  {"Poitrine": 104, "Taille": 86, "Bassin": 110},
        "48 (XXL)": {"Poitrine": 110, "Taille": 92, "Bassin": 116}
    },
    "Homme": {
        "44 (XS)": {"Poitrine": 88, "Taille": 76},
        "46 (S)":  {"Poitrine": 92, "Taille": 80},
        "48 (M)":  {"Poitrine": 96, "Taille": 84},
        "50 (M/L)":{"Poitrine": 100, "Taille": 88},
        "52 (L)":  {"Poitrine": 104, "Taille": 92}
    }
}

metrage_base = {
    "Robe simple": 2.5, "Robe de soirée": 4.0, "Jupe": 1.5,
    "Pantalon": 2.0, "Veste/Blazer": 2.5, "Chemise/Chemisier": 2.0
}

# --- CATÉGORIES ---
categories = {
    "IDENTITE": ["Nom Complet", "Date de mesure", "Notes"],
    "1. LES TOURS": ["Tour de cou", "Tour de poitrine", "Tour de taille", "Bassin (Gdes hanches)", "Tour de bras", "Tour de cuisse"],
    "2. LES LONGUEURS": ["Hauteur totale", "Epaule-taille", "Hauteur poitrine", "Jambe (Ext)", "Longueur de bras"],
    "3. SPECIFIQUES": ["Largeur epaule", "Carrure devant", "Carrure dos", "Enfourchure"],
    "4. PROJET (Photo/Tissu)": []
}

# --- INITIALISATION ROBUSTE ---
if "data" not in st.session_state:
    st.session_state.data = {}

# Correction forcée des types pour éviter les erreurs StreamlitAPIException
if not isinstance(st.session_state.data.get("Date de mesure"), datetime.date):
    st.session_state.data["Date de mesure"] = datetime.date.today()
if not isinstance(st.session_state.data.get("Nom Complet"), str):
    st.session_state.data["Nom Complet"] = ""
if not isinstance(st.session_state.data.get("Notes"), str):
    st.session_state.data["Notes"] = ""

# --- INTERFACE ---
st.title("🧵 HOPECORP")
page = st.sidebar.radio("Navigation", list(categories.keys()))
st.header(page)

if page == "4. PROJET (Photo/Tissu)":
    st.subheader("📸 Modèle")
    uploaded_file = st.file_uploader("Prendre une photo", type=["jpg", "png", "jpeg"])
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
            st.session_state.data[label] = st.text_area(label, value=st.session_state.data[label])
        elif label == "Nom Complet":
            st.session_state.data[label] = st.text_input(label, value=st.session_state.data[label])
        else:
            val = st.session_state.data.get(label, 0.0)
            if not isinstance(val, (int, float)): val = 0.0
            st.session_state.data[label] = st.number_input(label, min_value=0.0, value=float(val), step=0.5)

# --- ANALYSE TAILLE (SIDEBAR) ---
st.sidebar.divider()
p = st.session_state.data.get("Tour de poitrine", 0.0)
t = st.session_state.data.get("Tour de taille", 0.0)
if isinstance(p, (int, float)) and p > 40:
    genre = st.sidebar.selectbox("Référence", list(standards.keys()))
    tab = standards[genre]; best_t, score = "", 1000
    for n, m in tab.items():
        d = abs(p - m["Poitrine"]) + abs(t - m["Taille"])
        if d < score: score, best_t = d, n
    st.sidebar.success(f"Taille estimée : {best_t}")

# --- FONCTION PDF ---
def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "FICHE DE MESURE - HOPECORP", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, f"Client : {data.get('Nom Complet', 'Non renseigné')}", ln=True)
    pdf.cell(0, 10, f"Date : {data.get('Date de mesure')}", ln=True)
    pdf.ln(5)
    pdf.set_font("helvetica", "", 10)
    for k, v in data.items():
        if k not in ["image_modele", "Nom Complet", "Date de mesure"]:
            pdf.cell(90, 8, f"{k}:", border=1)
            pdf.cell(0, 8, f"{v}", border=1, ln=True)
    return pdf.output()

st.sidebar.divider()
if st.sidebar.button("📄 Préparer PDF"):
    pdf_bytes = generate_pdf(st.session_state.data)
    st.sidebar.download_button(
        "⬇️ Télécharger le PDF",
        data=pdf_bytes,
        file_name=f"Fiche_{st.session_state.data['Nom Complet']}.pdf",
        mime="application/pdf"
    )

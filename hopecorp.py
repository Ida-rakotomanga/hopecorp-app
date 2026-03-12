import streamlit as st
import datetime
from PIL import Image
import io

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
        "48 (XXL)": {"Poitrine": 110, "Taille": 92, "Bassin": 116},
        "50 (3XL)": {"Poitrine": 116, "Taille": 98, "Bassin": 122},
        "52 (4XL)": {"Poitrine": 122, "Taille": 104, "Bassin": 128}
    },
    "Homme": {
        "44 (XS)": {"Poitrine": 88, "Taille": 76},
        "46 (S)":  {"Poitrine": 92, "Taille": 80},
        "48 (M)":  {"Poitrine": 96, "Taille": 84},
        "50 (M/L)":{"Poitrine": 100, "Taille": 88},
        "52 (L)":  {"Poitrine": 104, "Taille": 92},
        "54 (XL)": {"Poitrine": 108, "Taille": 96},
        "56 (XXL)":{"Poitrine": 112, "Taille": 100}
    }
}

metrage_base = {
    "Robe simple": 2.5,
    "Robe de soirée": 4.0,
    "Jupe": 1.5,
    "Pantalon": 2.0,
    "Veste/Blazer": 2.5,
    "Chemise/Chemisier": 2.0
}

# --- TES CATÉGORIES ---
categories = {
    "IDENTITE": ["Nom Complet", "Date de mesure", "Notes"],
    "1. LES TOURS": [
        "Tour de cou", "Tour de poitrine", "Dessous de poitrine", 
        "Tour de taille", "Petites hanches", "Bassin (Gdes hanches)", 
        "Tour de bras", "Tour de poignet", "Tour de cuisse"
    ],
    "2. LES LONGUEURS": [
        "Hauteur totale", "Epaule-taille (Dev)", "Hauteur poitrine", 
        "Hauteur hanches", "Jambe (Ext)", "Jambe (Int)", "Longueur de bras"
    ],
    "3. SPECIFIQUES": [
        "Largeur epaule", "Carrure devant", "Carrure dos", 
        "Ecartement poitrine", "Enfourchure"
    ],
    "4. PROJET (Photo/Tissu)": []
}

# Initialisation propre des données
if "data" not in st.session_state:
    st.session_state.data = {}
    for cat_list in categories.values():
        for m in cat_list:
            st.session_state.data[m] = 0.0
    st.session_state.data["Nom Complet"] = ""
    st.session_state.data["Notes"] = ""
    st.session_state.data["Date de mesure"] = datetime.date.today()
    st.session_state.data["image_modele"] = None

# --- INTERFACE ---
st.title("🧵 HOPECORP")
page = st.sidebar.radio("Navigation", list(categories.keys()))

st.header(page)

if page == "4. PROJET (Photo/Tissu)":
    st.subheader("📸 Modèle")
    uploaded_file = st.file_uploader("Prendre une photo ou charger un modèle", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.session_state.data["image_modele"] = uploaded_file.read()
    
    if st.session_state.data["image_modele"]:
        st.image(st.session_state.data["image_modele"], width=300)

    st.divider()
    st.subheader("📏 Calculateur de Tissu")
    choix = st.selectbox("Type de vêtement", list(metrage_base.keys()))
    laize = st.select_slider("Laize du tissu (cm)", options=[90, 110, 140, 150], value=140)
    
    besoin = metrage_base[choix]
    if laize < 130: besoin *= 1.3
    st.metric("Tissu à prévoir", f"{besoin:.1f} mètres")

else:
    for label in categories[page]:
        if label == "Date de mesure":
            st.session_state.data[label] = st.date_input(label, value=st.session_state.data[label])
        elif label == "Notes":
            st.session_state.data[label] = st.text_area(label, value=st.session_state.data[label])
        elif label == "Nom Complet":
            st.session_state.data[label] = st.text_input(label, value=st.session_state.data[label])
        else:
            # Sécurité pour les nombres
            val_actuelle = st.session_state.data.get(label, 0.0)
            if not isinstance(val_actuelle, (int, float)): val_actuelle = 0.0
            st.session_state.data[label] = st.number_input(label, min_value=0.0, value=float(val_actuelle), step=0.5)

# --- ANALYSE DE TAILLE (Sidebar) ---
st.sidebar.divider()
genre = st.sidebar.selectbox("Référence", list(standards.keys()))
p = st.session_state.data.get("Tour de poitrine", 0.0)
t = st.session_state.data.get("Tour de taille", 0.0)

if isinstance(p, (int, float)) and p > 40:
    tab = standards[genre]
    meilleure, score = "", 1000
    for nom, m in tab.items():
        diff = abs(p - m["Poitrine"]) + abs(t - m["Taille"])
        if diff < score: score, meilleure = diff, nom
    st.sidebar.success(f"Taille recommandée : {meilleure}")

# --- EXPORT ---
st.divider()
if st.button("💾 Préparer la fiche pour téléchargement"):
    fiche = f"HOPECORP - {st.session_state.data['Nom Complet']}\n" + "-"*20 + "\n"
    for k, v in st.session_state.data.items():
        if k != "image_modele": fiche += f"{k}: {v}\n"
    st.download_button("⬇️ Télécharger maintenant", fiche, f"Fiche_{st.session_state.data['Nom Complet']}.txt")

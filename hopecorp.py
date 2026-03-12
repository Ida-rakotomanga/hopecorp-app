import streamlit as st
import datetime

# Configuration pour smartphone
st.set_page_config(page_title="HOPECORP", layout="centered")

# --- DONNÉES DE RÉFÉRENCE (Issues de ton script original) ---
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
    },
    "Enfant": {
        "116 (6a)": {"Poitrine": 60, "Taille": 56, "Bassin": 64},
        "128 (8a)": {"Poitrine": 64, "Taille": 58, "Bassin": 70},
        "140 (10a)":{"Poitrine": 70, "Taille": 62, "Bassin": 76},
        "152 (12a)":{"Poitrine": 76, "Taille": 66, "Bassin": 82}
    }
}

# --- TES CATÉGORIES DE MESURES ORIGINALES ---
categories = {
    "IDENTITE": ["Nom Complet", "Date de mesure", "Notes"],
    "1. LES TOURS": [
        "Tour de cou", "Tour de poitrine", "Dessous de poitrine", 
        "Tour de taille", "Petites hanches", "Bassin (Gdes hanches)", 
        "Tour de bras", "Tour de poignet", "Tour de cuisse",
        "Tour de genou", "Mollet", "Cheville"
    ],
    "2. LES LONGUEURS": [
        "Hauteur totale", "Epaule-taille (Dev)", "Epaule-taille (Dos)", 
        "Hauteur poitrine", "Hauteur hanches", "Montant (assis)", 
        "Jambe (Ext)", "Jambe (Int)", "Longueur de bras"
    ],
    "3. SPECIFIQUES": [
        "Largeur epaule", "Carrure devant", "Carrure dos", 
        "Ecartement poitrine", "Enfourchure", 
        "Profondeur emmanchure", "Inclinaison epaule"
    ]
}

if "data" not in st.session_state:
    st.session_state.data = {m: "" for cat in categories.values() for m in cat}
    st.session_state.data["Date de mesure"] = datetime.date.today()

# --- INTERFACE ---
st.title("🧵 HOPECORP")
page = st.sidebar.radio("Navigation", list(categories.keys()))

st.header(page)
for label in categories[page]:
    if label == "Date de mesure":
        st.session_state.data[label] = st.date_input(label, value=st.session_state.data[label])
    elif label == "Notes":
        st.session_state.data[label] = st.text_area(label, value=st.session_state.data[label])
    elif label == "Nom Complet":
        st.session_state.data[label] = st.text_input(label, value=st.session_state.data[label])
    else:
        # Valeur numérique avec gestion des virgules pour mobile
        current_val = st.session_state.data.get(label, 0.0)
        try:
            initial_val = float(current_val) if current_val != "" else 0.0
        except:
            initial_val = 0.0
        st.session_state.data[label] = st.number_input(label, min_value=0.0, value=initial_val, step=0.5)

# --- ANALYSE DE TAILLE ---
st.sidebar.divider()
genre = st.sidebar.selectbox("Genre de référence", list(standards.keys()))

p = st.session_state.data.get("Tour de poitrine", 0.0)
t = st.session_state.data.get("Tour de taille", 0.0)
b = st.session_state.data.get("Bassin (Gdes hanches)", 0.0)

if p > 40:
    tab = standards[genre]
    meilleure, score_mini = "", 1000
    for nom_t, m in tab.items():
        diff = abs(p - m["Poitrine"]) + abs(t - m["Taille"])
        if "Bassin" in m: diff += abs(b - m["Bassin"])
        if diff < score_mini:
            score_mini, meilleure = diff, nom_t
    
    st.sidebar.success(f"Taille recommandée : **{meilleure}**")
    st.sidebar.info(f"Écart total : {score_mini:.1f} cm")

# --- EXPORT ---
fiche_txt = f"FICHE HOPECORP - {st.session_state.data['Nom Complet']}\n" + "="*30 + "\n"
for k, v in st.session_state.data.items():
    fiche_txt += f"{k}: {v}\n"

st.download_button(
    label="💾 Télécharger la fiche",
    data=fiche_txt,
    file_name=f"Fiche_{st.session_state.data['Nom Complet']}.txt",
    mime="text/plain"
)

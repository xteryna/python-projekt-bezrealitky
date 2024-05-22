import streamlit as st
import pandas as pd

# Vytvoření dataframe pro příklad
data = {
    "Kraj": ["Kraj 1", "Kraj 1", "Kraj 2", "Kraj 2", "Kraj 3", "Kraj 3"],
    "Okres": ["Okres 1", "Okres 2", "Okres 3", "Okres 4", "Okres 5", "Okres 6"],
    "Cena": [1000000, 1500000, 2000000, 2500000, 3000000, 3500000]
}

df = pd.DataFrame(data)

# Inicializace session state pro vybraný kraj a okres
if "vybrany_kraj" not in st.session_state:
    st.session_state.vybrany_kraj = df["Kraj"].iloc[0]

if "vybrany_okres" not in st.session_state:
    st.session_state.vybrany_okres = df[df["Kraj"] == st.session_state.vybrany_kraj]["Okres"].iloc[0]

# Seznam krajů pro selectbox
kraje = df["Kraj"].unique().tolist()

# Funkce pro nastavení vybraného kraje
def set_kraj():
    st.session_state.vybrany_kraj = st.session_state.kraj
    st.session_state.vybrany_okres = df[df["Kraj"] == st.session_state.vybrany_kraj]["Okres"].iloc[0]

# Selectbox pro výběr kraje
st.selectbox("Vyber kraj:", kraje, key='kraj', index=kraje.index(st.session_state.vybrany_kraj), on_change=set_kraj)

# Filtrace okresů podle vybraného kraje
okresy = df[df["Kraj"] == st.session_state.vybrany_kraj]["Okres"].unique().tolist()

# Selectbox pro výběr okresu
st.session_state.vybrany_okres = st.selectbox("Vyber okres:", okresy, key='okres', index=okresy.index(st.session_state.vybrany_okres))

# Výpis vybraného kraje a okresu
st.write(f"Vybraný kraj: {st.session_state.vybrany_kraj}")
st.write(f"Vybraný okres: {st.session_state.vybrany_okres}")

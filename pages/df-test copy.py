import json
import pandas as pd
import streamlit as st
import plotly.express as px

# Načtení dat
with open("properties.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Vytvoření DataFrame
df = pd.DataFrame(data)

# Dropping nežádoucí sloupce
nechceme_sloupce = [
    "Městská část", "Stav", "Číslo inzerátu", "Vlastnictví", "Rizika", 
    "Vybaveno", "Podlaží", "URL", "Popis", "Dostupné od", "PENB", 
    "Pošta (metry)", "Pošta (minuty)", "Banka (metry)", "Banka (minuty)", 
    "Restaurace (metry)", "Restaurace (minuty)", "Lékárna (metry)", 
    "Lékárna (minuty)", "Sportoviště (metry)", "Sportoviště (minuty)", 
    "Provedení", "Stáří", "Vytápění", "Rekonstrukce", "Plocha pozemku", 
    "Typ pozemku", "Odpad", "Voda"
]
df = df.drop(nechceme_sloupce, axis=1)

# Přidání sloupce Cena za m2
df["Cena za m2"] = df["Cena"] / df["Užitná plocha"]

# Mapování dispozice na kategorie
def mapuj_dispozici(dispozice):
    if ('1+' in dispozice) or ("Garsoniéra" in dispozice):
        return '1+1 a 1+kk'
    elif '2+' in dispozice:
        return '2+1 a 2+kk'
    elif '3+' in dispozice:
        return '3+1 a 3+kk'
    elif '4+' in dispozice:
        return '4+1 a 4+kk'
    else:
        return 'Ostatní'

df['Dispozice_kategorie'] = df['Dispozice'].apply(mapuj_dispozici)

# Inicializace session state
if "zobrazit_uvodni_obrazovku" not in st.session_state:
    st.session_state["zobrazit_uvodni_obrazovku"] = True
if "vybrany_kraj" not in st.session_state:
    st.session_state.vybrany_kraj = ""
if "vybrany_okres" not in st.session_state:
    st.session_state.vybrany_okres = ""

# Funkce pro zobrazení obsahu
def zobraz_obsah():
    st.session_state["zobrazit_uvodni_obrazovku"] = False
    st.experimental_rerun()

# Získání prvního kraje a okresu
prvni_kraj = df["Kraj"].iloc[0]
prvni_okres = df[df["Kraj"] == prvni_kraj]["Okres"].iloc[0]

# Záložky
tab1, tab2 = st.tabs(["Analýza v rámci ČR", "Analýza pro vybraný kraj"])

# ZALOZKA1 - ANALYZA V RAMCI CR
with tab1:
    st.subheader("Analýza v rámci ČR - ceny bytů")  
    # Zobrazení obsahu na první kliknutí na tlačítko
    if st.session_state["zobrazit_uvodni_obrazovku"]:
        st.subheader("Projekt Python Como")
        st.title("Analýza bytů k prodeji - Bezrealitky.cz")
        if st.button("Procházet analýzu", key="btn_prochazet_analyzu"):
            zobraz_obsah()
    else:
        # Vyber kraje
        kraje = df["Kraj"].unique().tolist()
        vybrany_kraj = st.sidebar.selectbox("Vyber kraj, ke kterému se bude vztahovat analýza", kraje, index=kraje.index(prvni_kraj), key="vybrany_kraj")
        
        # Reset vybraného okresu při změně kraje
        if vybrany_kraj != st.session_state.vybrany_kraj:
            st.session_state.vybrany_kraj = vybrany_kraj
            st.session_state.vybrany_okres = ""
            st.experimental_rerun()
        
        # Zjištění okresů v daném kraji
        df_kraj = df[df["Kraj"] == st.session_state.vybrany_kraj]
        okresy = df_kraj["Okres"].unique().tolist()

        if st.session_state.vybrany_okres in okresy:
            vybrany_okres_index = okresy.index(st.session_state.vybrany_okres)
        else:
            vybrany_okres_index = 0
            if okresy:  # Check if okresy list is not empty
                st.session_state.vybrany_okres = okresy[0]

        # Vyber okresu
        vybrany_okres = st.sidebar.selectbox("Vyber okres, ke kterému se bude vztahovat analýza", okresy, index=vybrany_okres_index, key="vybrany_okres")

        # Zobrazí vybraný okres
        st.write(f"Vybraný okres: {vybrany_okres}")

# ZALOZKA2 - ANALYZA PRO VYBRANY KRAJ
with tab2:
    st.subheader("Analýza v rámci jednotlivých krajů - ceny bytů")
    df_kraj = df[df["Kraj"]==st.session_state.vybrany_kraj]

    vybrany_okres = "Most"
    df_groupby_okresy_cena_za_m2 = df.groupby("Okres")[["Užitná plocha", "Cena", "Cena za m2"]].mean().round({"Užitná plocha":0, "Cena": -5,"Cena za m2": -2}).reset_index().sort_values(by= "Cena za m2")
    num_rows = df_groupby_okresy_cena_za_m2.shape[0]
    styled_df = df_groupby_okresy_cena_za_m2.style.apply(zvyrazni_radek, axis=1, kategorie="Okres", vybrana_hodnota=vybrany_okres)
    st.write("Cena bytů za m2 pro jednotlivé kraje")
    st.dataframe(styled_df, height=(num_rows+1)*35+3, hide_index=True)
    #barchart
    st.write("Cena bytů za m2 pro jednotlivé okresy")
    st.bar_chart(df_groupby_okresy_cena_za_m2.sort_values(by="Cena za m2", ascending=False), x="Okres", y="Cena za m2")

    #BARCHART PLOTLY
    sorted_df = df_groupby_okresy_cena_za_m2.sort_values(by="Cena za m2")
    # Definice barev
    sorted_df["barva"] = sorted_df["Okres"].apply(lambda x: "lightblue" if x == vybrany_okres else "blue")
    # Vytvoření sloupcového grafu pomocí Plotly
    fig = px.bar(sorted_df, y="Okres", x="Cena za m2", color="barva",
                color_discrete_map={"lightblue": "lightblue", "blue": "blue"},
                category_orders={"Okres": sorted_df["Okres"].tolist()},
                title="Cena za m2 podle kraje")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig)



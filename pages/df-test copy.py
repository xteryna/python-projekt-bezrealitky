import json
import pandas as pd
import streamlit as st
import plotly.express as px

with open("properties.json", "r", encoding="utf-8") as file:
    data = json.load(file)

df = pd.DataFrame(data)
df = df.drop(["Městská část", "Stav", "Číslo inzerátu", "Vlastnictví", "Rizika", "Vybaveno", "Podlaží", "URL", "Popis", "Dostupné od", "PENB", "Pošta (metry)", "Pošta (minuty)", "Banka (metry)", "Banka (minuty)", "Restaurace (metry)", "Restaurace (minuty)", "Lékárna (metry)", "Lékárna (minuty)", "Sportoviště (metry)", "Sportoviště (minuty)", "Provedení", "Stáří", "Vytápění", "Rekonstrukce", "Plocha pozemku", "Typ pozemku", "Odpad", "Voda"], axis=1)
df["Cena za m2"] = df["Cena"] / df["Užitná plocha"]

def map_dispozice(dispozice):
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

df['Dispozice_kategorie'] = df['Dispozice'].apply(map_dispozice)

if "zobrazit_uvodni_obrazovku" not in st.session_state:
    st.session_state["zobrazit_uvodni_obrazovku"] = True
if "vybrany_kraj" not in st.session_state:
    st.session_state.vybrany_kraj = ""
if "vybrany_okres" not in st.session_state:
    st.session_state.vybrany_okres = ""

def show_content():
    st.session_state["zobrazit_uvodni_obrazovku"] = False
    st.experimental_rerun()  # Okamžitě obnoví skript pro zobrazení dalšího obsahu

if st.session_state["zobrazit_uvodni_obrazovku"]:
    st.subheader("Projekt Python Como")
    st.title("Analýza bytů k prodeji - Bezrealitky.cz")
    if st.button("Procházet analýzu", key="btn_prochazet_analyzu"):
        st.session_state["zobrazit_uvodni_obrazovku"] = False
        st.experimental_rerun()  # Okamžitě obnoví skript pro zobrazení dalšího obsahu
else:
    kraje = df["Kraj"].unique().tolist()
    vybrany_kraj = st.sidebar.selectbox("Vyber kraj, ke kterému se bude vztahovat analýza", kraje, index=0  , key="vybrany_kraj")
    
    if vybrany_kraj != st.session_state.vybrany_kraj:
        st.session_state.vybrany_kraj = vybrany_kraj
        st.session_state.vybrany_okres = ""  # Reset vybraného okresu při změně kraje
        st.experimental_rerun()  # Okamžitě obnoví skript pro aktualizaci okresu
#XXXXXXXXXXXXXXX
    df_kraj = df[df["Kraj"] == st.session_state.vybrany_kraj]
    okresy = df_kraj["Okres"].unique().tolist()
#XXXXXXXXXXXXXXX definovat okresy dřív
    st.write(okresy)
    
    if st.session_state.vybrany_okres in okresy:
        vybrany_okres_index = okresy.index(st.session_state.vybrany_okres)
    else:
        vybrany_okres_index = 0
        if okresy:  # Check if okresy list is not empty
            st.session_state.vybrany_okres = okresy[0]

    vybrany_okres = st.sidebar.selectbox("Vyber okres, ke kterému se bude vztahovat analýza", okresy, index=vybrany_okres_index, key="vybrany_okres")

    # Zbytek kódu



    # funkce pro podmíněné formátování
    def zvyrazni_radek(radek, kategorie, vybrana_hodnota):
        if radek[kategorie] == vybrana_hodnota:
            return ["background-color: blue"] * len(radek)
        else:
            return [""] * len(radek)

    def vypocti_vysku(df):
        num_rows = df.shape[0]
        table_height = (num_rows+1)*35+3
        return vypocti_vysku

    st.title("Analýza bytů k prodeji - Bezrealitky.cz")
    #ZALOZKY
    tab1, tab2 =st.tabs(["Analýza v rámci ČR", "Analýza pro vybraný kraj"])
    #ZALOZKA1 - ANALYZA V RAMCI CR
    with tab1:
        st.subheader("Analýza v rámci ČR - ceny bytů")  
        df_groupby_kraje_cena_za_m2 = df.groupby("Kraj")[["Užitná plocha", "Cena", "Cena za m2"]].mean().round({"Užitná plocha":0, "Cena": -5,"Cena za m2": -2}).reset_index().sort_values(by= "Cena za m2")
        num_rows = df_groupby_kraje_cena_za_m2.shape[0]

        styled_df = df_groupby_kraje_cena_za_m2.style.apply(zvyrazni_radek, axis=1, kategorie="Kraj", vybrana_hodnota=vybrany_kraj)


        st.write("Cena bytů za m2 pro jednotlivé kraje")
        st.dataframe(styled_df, height=(num_rows+1)*35+3, hide_index=True)
        # #barchart
        # st.write("Cena bytů za m2 pro jednotlivé kraje")
        # st.bar_chart(df_groupby_kraje_cena_za_m2.sort_values(by="Cena za m2", ascending=False), x="Kraj", y="Cena za m2")

        #BARCHART PLOTLY
        sorted_df = df_groupby_kraje_cena_za_m2.sort_values(by="Cena za m2")
        # Definice barev
        sorted_df["barva"] = sorted_df["Kraj"].apply(lambda x: "lightblue" if x == vybrany_kraj else "blue")
        # Vytvoření sloupcového grafu pomocí Plotly
        fig = px.bar(sorted_df, y="Kraj", x="Cena za m2", color="barva",
                    color_discrete_map={"lightblue": "lightblue", "blue": "blue"},
                    category_orders={"Kraj": sorted_df["Kraj"].tolist()},
                    title="Cena za m2 podle kraje")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig)

        #DISPOZICE ANALÝZA
        st.subheader("Analýza v rámci ČR - dispozice") 
        col1, col2 = st.columns(2)
        with col1:
            df_groupby_dispozice_cena_m2 = df.groupby("Dispozice_kategorie")["Cena za m2"].mean().reset_index().sort_values(by="Cena za m2")
            st.write("Dispozice bytů - cena za m2")
            num_rows = df_groupby_dispozice_cena_m2.shape[0]
            st.dataframe(df_groupby_dispozice_cena_m2, height=(num_rows+1)*35+3)    

        with col2:
            # st.bar_chart(df_groupby_dispozice_cena_m2)

            #BARCHART PLOTLY
            sorted_df = df_groupby_dispozice_cena_m2.sort_values(by="Cena za m2", ascending=False)
            # Vytvoření sloupcového grafu pomocí Plotly
            fig = px.bar(sorted_df, y="Dispozice_kategorie", x="Cena za m2",
                        category_orders={"Dispozice_kategorie": sorted_df["Dispozice_kategorie"].tolist()},
                        title="Cena za m2 dle dispozice bytu")
            fig.update_layout(showlegend=False, height=300, width=300, bargap=0.1)

            st.plotly_chart(fig)






        st.write("Nejčetnější dispozice bytů dle krajů")
        df_groupby_kraje_dispozice = df.groupby(["Kraj", "Dispozice_kategorie"]).size().reset_index(name="Počet")
        sorted_df_groupby_kraje_dispozice = df_groupby_kraje_dispozice.sort_values(by=["Kraj", "Počet"], ascending=[True, False])
        result_df = sorted_df_groupby_kraje_dispozice.groupby("Kraj").head(1).reset_index(drop=True)
        styled_df = result_df.style.apply(zvyrazni_radek, axis=1, kategorie="Kraj", vybrana_hodnota=vybrany_kraj)
        num_rows = result_df.shape[0]
        st.dataframe(styled_df, hide_index=True, height=(num_rows+1)*35+3)

    #ZALOZKA2 - ANALYZA PRO VYBRANY KRAJ
    with tab2:
        st.subheader("Analýza v rámci jednotlivých krajů - ceny bytů")
        df_kraj = df[df["Kraj"]==vybrany_kraj]

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
        






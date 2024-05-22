import json
import pandas as pd
import streamlit as st

with open("properties.json", "r", encoding="utf-8") as file:
    data = json.load(file)

df = pd.DataFrame(data)
df = df.drop(["Městská část","Stav", "Číslo inzerátu", "Vlastnictví", "Rizika", "Vybaveno", "Podlaží", "URL", "Popis", "Dostupné od", "PENB", "Pošta (metry)", "Pošta (minuty)", "Banka (metry)", "Banka (minuty)", "Restaurace (metry)", "Restaurace (minuty)", "Lékárna (metry)", "Lékárna (minuty)", "Sportoviště (metry)", "Sportoviště (minuty)", "Provedení", "Stáří", "Vytápění", "Rekonstrukce", "Plocha pozemku", "Typ pozemku", "Odpad", "Voda"],axis=1)
df["Cena za m2"] = df["Cena"]/df["Užitná plocha"]

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
if "vztah_kraj" not in st.session_state:
    st.session_state.vztah_kraj = "Ústecký kraj"

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
   


    vztah_kraj = "Ústecký kraj"

    # funkce pro podmíněné formátování
    def zvyrazni_radek(radek):
        if radek["Kraj"] == vztah_kraj:
            return ["background-color: yellow"] * len(radek)
        else:
            return [""] * len(radek)

    def vypocti_vysku(df):
        num_rows = df.shape[0]
        table_height = (num_rows+1)*35+3
        return vypocti_vysku


    #ZALOZKY
    tab1, tab2 =st.tabs(["Analýza v rámci ČR", "Analýza pro vybraný kraj"])
    #ZALOZKA1 - ANALYZA V RAMCI CR
    with tab1:
        st.subheader("Analýza v rámci ČR")  
        df_groupby_kraje_cena_za_m2 = df.groupby("Kraj")[["Užitná plocha", "Cena", "Cena za m2"]].mean().round({"Užitná plocha":0, "Cena": -5,"Cena za m2": -2}).reset_index().sort_values(by= "Cena za m2")
        num_rows = df_groupby_kraje_cena_za_m2.shape[0]
        styled_df = df_groupby_kraje_cena_za_m2.style.apply(zvyrazni_radek, axis=1)
        st.write("Cena bytů za m2 pro jednotlivé kraje")
        st.dataframe(styled_df, height=(num_rows+1)*35+3, hide_index=True)
        #barchart
        st.write("Cena bytů za m2 pro jednotlivé kraje")
        st.bar_chart(df_groupby_kraje_cena_za_m2.sort_values(by="Cena za m2", ascending=False), x="Kraj", y="Cena za m2")

        col1, col2 = st.columns(2)
        with col1:
            df_groupby_dispozice_cena_m2 = df.groupby("Dispozice_kategorie")["Cena za m2"].mean()
            st.write("Dispozice bytů - cena za m2")
            num_rows = df_groupby_dispozice_cena_m2.shape[0]
            st.dataframe(df_groupby_dispozice_cena_m2, height=(num_rows+1)*35+3)    

        with col2:
            st.write("Nejčetnější dispozice bytů dle krajů")
            df_groupby_kraje_dispozice = df.groupby(["Kraj", "Dispozice_kategorie"]).size().reset_index(name="Počet")
            sorted_df_groupby_kraje_dispozice = df_groupby_kraje_dispozice.sort_values(by=["Kraj", "Počet"], ascending=[True, False])
            result_df = sorted_df_groupby_kraje_dispozice.groupby("Kraj").head(1).reset_index(drop=True)
            styled_df = result_df.style.apply(zvyrazni_radek, axis=1)
            num_rows = result_df.shape[0]
            st.dataframe(styled_df, hide_index=True, height=(num_rows+1)*35+3)

    #ZALOZKA2 - ANALYZA PRO VYBRANY KRAJ
    with tab2:
        kraje = df['Kraj'].unique().tolist()
        vybrany_kraj = st.selectbox("Vyber kraj, ke kterému se bude vztahovat analýza", kraje)
import json
import pandas as pd
import streamlit as st
import plotly.express as px

#načíst soubor s daty z bezrealitky.cz
with open("properties.json", "r", encoding="utf-8") as file:
    data = json.load(file)

#pandas - vytvoření dataframe z dat v json
df = pd.DataFrame(data)
#odstranit z df nepotřebné sloupce
df = df.drop(["Městská část", "Stav", "Číslo inzerátu", "Vlastnictví", "Rizika", "Vybaveno", "Podlaží", "URL", "Popis", "Dostupné od", "PENB", "Pošta (metry)", "Pošta (minuty)", "Banka (metry)", "Banka (minuty)", "Restaurace (metry)", "Restaurace (minuty)", "Lékárna (metry)", "Lékárna (minuty)", "Sportoviště (metry)", "Sportoviště (minuty)", "Provedení", "Stáří", "Vytápění", "Rekonstrukce", "Plocha pozemku", "Typ pozemku", "Odpad", "Voda"], axis=1)
#výpočet nového sloupce - cena za m2
df["Cena za m2"] = df["Cena"] / df["Užitná plocha"]

#funkce pro sloučení hodnot  dispozic bytů
def map_dispozice(dispozice):
    if ("1+" in dispozice) or ("Garsoniéra" in dispozice):
        return "1+1/1+kk"
    elif "2+" in dispozice:
        return "2+1/2+kk"
    elif "3+" in dispozice:
        return "3+1/3+kk"
    elif "4+" in dispozice:
        return "4+1/4+kk"
    else:
        return 'Ostatní'
#nový sloupec s přemapovanými dispozicemi
df["Dispozice_kategorie"] = df["Dispozice"].apply(map_dispozice)

#------------ÚVODNÍ OBRAZOVKA------------------------------------------------------------------
#inicializace session state pro úvodní obrazovku
if "zobrazit_uvodni_obrazovku" not in st.session_state:
    st.session_state["zobrazit_uvodni_obrazovku"] = True

#na začátku se zobrazí úvodní obrazovka (true), pak je deaktivována stisknutím tlačítka
if st.session_state["zobrazit_uvodni_obrazovku"]:
    st.subheader("Projekt Python Como")
    st.title("Analýza bytů k prodeji - Bezrealitky.cz")
    st.title("Autor: Tereza Beránková")
    if st.button("Procházet analýzu", key="btn_prochazet_analyzu"):
        st.session_state["zobrazit_uvodni_obrazovku"] = False #deaktivace úvodní obrazovky
        st.experimental_rerun()  # Okamžitě obnoví skript pro zobrazení dalšího obsahu
else:
    #------------SELECTBOXY: VÝBĚR KRAJE A OKRESU------------------------------------------------------------------
    def nastav_ss_kraj():
        if "Ústecký kraj" in df["Kraj"].tolist():
            st.session_state.vybrany_kraj = "Ústecký kraj" #primárně Ústecký kraj
        else:
            st.session_state.vybrany_kraj = df["Kraj"].iloc[0] #- první řádek v df
    
    # Inicializace session state pro vybraný kraj 
    if "vybrany_kraj" not in st.session_state:
        nastav_ss_kraj()

    # Seznam krajů pro selectbox
    kraje = df["Kraj"].unique().tolist()

    # Funkce pro nastavení vybraného okresu
    def nastav_seznam_okresu():
        df_okresy = df[df["Kraj"] == st.session_state.vybrany_kraj]["Okres"]
        okresy_v_kraji = df_okresy.unique().tolist()
        return okresy_v_kraji

    def nastav_ss_okres():
        okresy_v_kraji = nastav_seznam_okresu()
        if (st.session_state.vybrany_kraj == "Ústecký kraj") and ("okres Most" in okresy_v_kraji): #primárně okres Most
            st.session_state.vybrany_okres = "okres Most"
        else:
            st.session_state.vybrany_okres = df[df["Kraj"] == st.session_state.vybrany_kraj]["Okres"].iloc[0] #jinak první v seznamu okresů

    # Inicializace session state pro vybraný okres - první řádek v df
    if "vybrany_okres" not in st.session_state:
        nastav_ss_okres()

    # Selectbox pro výběr kraje
    vybrany_kraj = st.sidebar.selectbox("Vyber kraj:", kraje, key='vybrany_kraj', index=kraje.index(st.session_state.vybrany_kraj), on_change=nastav_ss_okres)

    # Selectbox pro výběr okresu
    vybrany_okres = st.sidebar.selectbox("Vyber okres:", nastav_seznam_okresu(), key='vybrany_okres', index=nastav_seznam_okresu().index(st.session_state.vybrany_okres))

    #------------ANALÝZA - TABULKY, GRAFY------------------------------------------------------------------
    # Funkce pro zvýraznění řádku tabulky
    def zvyrazni_radek(df, kategorie, vybrana_hodnota): 
        styled_df = df.style.apply(
            lambda row: ['background-color: blue' if row[kategorie] == vybrana_hodnota else '' for _ in row],
            axis=1
        )
        return styled_df

    #funkce pro výpočet výšky tabulky(->bez scrolování)
    def vypocti_vysku(df):
        num_rows = df.shape[0]
        table_height = (num_rows+1)*35+3
        return table_height

    st.title("Analýza bytů k prodeji - Bezrealitky.cz")
    st.write(f"vybráno: {vybrany_kraj}, {vybrany_okres}")
    #ZÁLOŽKY
    tab1, tab2 =st.tabs(["Analýza v rámci ČR", "Analýza pro vybraný kraj"])
    #-------------ZÁLOŽKA 1 - ANALÝZA V RÁMCI ČR-----------------
    with tab1:
        #-----------CENA ZA M2 - ANALÝZA ČR---------
        st.subheader("Analýza v rámci ČR - ceny bytů")
        df_groupby_kraje_cena_za_m2 = df.groupby("Kraj")[["Užitná plocha", "Cena", "Cena za m2"]].mean().round(
            {"Užitná plocha":0, "Cena": -5,"Cena za m2": -2} #zaokrouhlení položek
            ).reset_index()
        sorted_df = df_groupby_kraje_cena_za_m2.sort_values(by = "Cena za m2") #seřazení dle ceny za m2
        styled_df = zvyrazni_radek(sorted_df, "Kraj", vybrany_kraj
        ).format({
            "Užitná plocha": "{:.0f}", #zobraz bez des.míst
            "Cena": "{:.0f}",
            "Cena za m2": "{:.0f}"
        }) 
        
        #tabulka - cena za m2
        st.write("Průměrné ceny bytů a užitné plochy pro jednotlivé kraje")
        st.dataframe(styled_df, height=vypocti_vysku(sorted_df), hide_index=True)

        #barchart plotly - cena za m2
        sorted_df["barva"] = sorted_df["Kraj"].apply(lambda x: "lightblue" if x == vybrany_kraj else "blue")
        
        fig = px.bar(sorted_df, y="Kraj", x="Cena za m2", color="barva",
                    color_discrete_map={"lightblue": "lightblue", "blue": "blue"},
                    category_orders={"Kraj": sorted_df["Kraj"].tolist()},
                    title="Cena bytů za m2 podle kraje")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig)

        #---------DISPOZICE ANALÝZA ČR----------------------
        st.subheader("Analýza v rámci ČR - dispozice")
        col1, col2 = st.columns(2)
        with col1:
            #dispozice -cena za m2
            df_groupby_dispozice_cena_m2 = df.groupby("Dispozice_kategorie")["Cena za m2"].mean().reset_index()
            sorted_df = df_groupby_dispozice_cena_m2.sort_values(by="Cena za m2", ascending=False)
            st.write("Dispozice bytů - cena za m2 (celá ČR)")
            styled_df = sorted_df.style.format({
                "Užitná plocha": "{:.0f}",
                "Cena": "{:.0f}",
                "Cena za m2": "{:.0f}"
            })
            st.dataframe(styled_df, height=vypocti_vysku(sorted_df))    

        with col2:
            #barchart plotly - dispozice, cena za m2            
            fig = px.bar(sorted_df, y="Dispozice_kategorie", x="Cena za m2",
                        category_orders={"Dispozice_kategorie": sorted_df["Dispozice_kategorie"].tolist()},
                        title="Cena za m2 dle dispozice bytu (celá ČR)")
            fig.update_layout(showlegend=False, height=300, width=300, bargap=0.1)
            st.plotly_chart(fig)

        col1, col2 = st.columns(2)
        with col1:
            #piechart plotly - dispozice, četnost
            df_groupby_dispozice = df.groupby("Dispozice_kategorie")["Dispozice_kategorie"].count().reset_index(name="četnost")
            # Vytvoření pie chartu - dispozice, četnost
            fig = px.pie(df_groupby_dispozice, values="četnost", names="Dispozice_kategorie", title="Dispozice bytů - zastoupení (celá ČR)")
            fig.update_traces(textinfo="percent+label")  # Přidání procentuálních hodnot k jednotlivým segmentům
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.write("Nejčetnější dispozice bytů dle krajů (celá ČR)")
            df_groupby_kraje_dispozice = df.groupby(["Kraj", "Dispozice_kategorie"]).size().reset_index(name="Počet")
            # Výpočet celkového počtu výskytů v každém kraji
            df_groupby_kraje_celkem = df.groupby("Kraj").size().reset_index(name="Celkem")
            # Sloučení tabulek pro získání procent
            df_groupby_kraje_dispozice = pd.merge(df_groupby_kraje_dispozice, df_groupby_kraje_celkem, on="Kraj")
            df_groupby_kraje_dispozice["Procento"] = (df_groupby_kraje_dispozice["Počet"] / df_groupby_kraje_dispozice["Celkem"]
                                                      ).apply(lambda x: f"{x:.0%}") # formátování procent pro zobrazení
            # Seřazení tabulky podle krajů a počtu výskytů
            sorted_df = df_groupby_kraje_dispozice.sort_values(by=["Kraj", "Počet"], ascending=[True, False])
            result_df = sorted_df.groupby("Kraj").head(1).reset_index(drop=True)
            result_df = result_df[["Kraj", "Dispozice_kategorie", "Procento"]] #nezobrazovat sloupce s počty a celk. počtem
            styled_df = zvyrazni_radek(result_df, "Kraj", vybrany_kraj)

            #výpis df - dispozice, četnost
            st.dataframe(styled_df, hide_index=True, height=vypocti_vysku(result_df))

    #-------------ZÁLOŽKA 2 - ANALÝZA PRO VYBRANÝ KRAJ-----------------
    with tab2:
        #-----------CENA ZA M2 - ANALÝZA KRAJE---------
        st.subheader("Analýza v rámci jednotlivých krajů - ceny bytů")
        df_kraj = df[df["Kraj"]==vybrany_kraj]
        df_groupby_okresy_cena_za_m2 = df_kraj.groupby("Okres")[["Užitná plocha", "Cena", "Cena za m2"]].mean().round(
            {"Užitná plocha":0, "Cena": -5,"Cena za m2": -2} #zaokrouhlení položek tablky
            ).reset_index()
        sorted_df = df_groupby_okresy_cena_za_m2.sort_values(by = "Cena za m2")
        styled_df = zvyrazni_radek(sorted_df, "Okres", vybrany_okres
        ).format({
            "Užitná plocha": "{:.0f}", #zobraz bez des.míst
            "Cena": "{:.0f}",
            "Cena za m2": "{:.0f}"
        })

        #tabulka - cena za m2
        st.write(f"Průměrné ceny bytů a užitné plochy pro jednotlivé okresy ({vybrany_kraj})")
        st.dataframe(styled_df, height=vypocti_vysku(sorted_df), hide_index=True)
        #barchart plotly - cena za m2
        sorted_df["barva"] = sorted_df["Okres"].apply(lambda x: "lightblue" if x == vybrany_okres else "blue")
        
        fig = px.bar(sorted_df, y="Okres", x="Cena za m2", color="barva",
                    color_discrete_map={"lightblue": "lightblue", "blue": "blue"},
                    category_orders={"Okres": sorted_df["Okres"].tolist()},
                    title=(f"Cena bytů za m2 podle okresu ({vybrany_kraj})"))
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig)
        
        #---------DISPOZICE ANALÝZA KRAJE----------------------
        st.subheader(f"Analýza v rámci - dispozice ({vybrany_kraj})")
        col1, col2 = st.columns(2)
        with col1:
            #dispozice -cena za m2
            df_kraj_groupby_dispozice_cena_m2 = df_kraj.groupby("Dispozice_kategorie")["Cena za m2"].mean().reset_index()
            sorted_df = df_kraj_groupby_dispozice_cena_m2.sort_values(by="Cena za m2", ascending=False)
            st.write(f"Dispozice bytů - cena za m2 ({vybrany_kraj})")
            styled_df = sorted_df.style.format({
                "Užitná plocha": "{:.0f}",
                "Cena": "{:.0f}",
                "Cena za m2": "{:.0f}"
            })
            st.dataframe(styled_df, height=vypocti_vysku(sorted_df))    

        with col2:
            #barchart plotly - dispozice, cena za m2
            fig = px.bar(sorted_df, y="Dispozice_kategorie", x="Cena za m2",
                        category_orders={"Dispozice_kategorie": sorted_df["Dispozice_kategorie"].tolist()},
                        title=(f"Cena za m2 dle dispozice bytu ({vybrany_kraj})"))
            fig.update_layout(showlegend=False, height=300, width=300, bargap=0.1)
            st.plotly_chart(fig)

        col1, col2 = st.columns(2)
        with col1:
            #piechart plotly - dispozice, četnost
            df_kraj_groupby_dispozice = df_kraj.groupby("Dispozice_kategorie")["Dispozice_kategorie"].count().reset_index(name="četnost")
            # Vytvoření pie chartu - dispozice četnost
            fig = px.pie(df_kraj_groupby_dispozice, values="četnost", names="Dispozice_kategorie", title=(f"Dispozice bytů - zastoupení ({vybrany_kraj})"))
            fig.update_traces(textinfo="percent+label")  # Přidání procentuálních hodnot k jednotlivým segmentům
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.write(f"Nejčetnější dispozice bytů dle okresů ({vybrany_kraj})")
            df_groupby_okresy_dispozice = df_kraj.groupby(["Okres", "Dispozice_kategorie"]).size().reset_index(name="Počet")
            df_groupby_okresy_celkem = df_kraj.groupby("Okres").size().reset_index(name="Celkem")
            # Sloučení tabulek pro získání procent
            df_groupby_okresy_dispozice = pd.merge(df_groupby_okresy_dispozice, df_groupby_okresy_celkem, on="Okres")
            df_groupby_okresy_dispozice["Procento"] = (df_groupby_okresy_dispozice["Počet"] / df_groupby_okresy_dispozice["Celkem"]
                                                      ).apply(lambda x: f"{x:.0%}") # formátování procent pro zobrazení
            # Seřazení tabulky podle krajů a počtu výskytů
            sorted_df = df_groupby_okresy_dispozice.sort_values(by=["Okres", "Počet"], ascending=[True, False])
            result_df = sorted_df.groupby("Okres").head(1).reset_index(drop=True)
            result_df = result_df[["Okres", "Dispozice_kategorie", "Procento"]] #nezobrazovat sloupce s počty a celk. počtem
            styled_df = zvyrazni_radek(result_df, "Okres", vybrany_okres)

            #výpis df - dispozice, četnost
            st.dataframe(styled_df, hide_index=True, height=vypocti_vysku(result_df))

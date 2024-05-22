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

df["Dispozice_kategorie"] = df["Dispozice"].apply(map_dispozice)

if "zobrazit_uvodni_obrazovku" not in st.session_state:
    st.session_state["zobrazit_uvodni_obrazovku"] = True


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
    st.sidebar.selectbox("Vyber kraj:", kraje, key='kraj', index=kraje.index(st.session_state.vybrany_kraj), on_change=set_kraj)

    # Filtrace okresů podle vybraného kraje
    okresy = df[df["Kraj"] == st.session_state.vybrany_kraj]["Okres"].unique().tolist()

    # Selectbox pro výběr okresu
    st.session_state.vybrany_okres = st.sidebar.selectbox("Vyber okres:", okresy, key='okres', index=okresy.index(st.session_state.vybrany_okres))
    vybrany_kraj = st.session_state.vybrany_kraj
    vybrany_okres = st.session_state.vybrany_okres


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

    st.write(vybrany_kraj, vybrany_okres)
    #ZALOZKY
    tab1, tab2 =st.tabs(["Analýza v rámci ČR", "Analýza pro vybraný kraj"])
    #ZALOZKA1 - ANALYZA V RAMCI CR
    with tab1:
        st.subheader("Analýza v rámci ČR - ceny bytů")
        #CENA ZA M2 - ANALÝZA ČR
        df_groupby_kraje_cena_za_m2 = df.groupby("Kraj")[["Užitná plocha", "Cena", "Cena za m2"]].mean().round({"Užitná plocha":0, "Cena": -5,"Cena za m2": -2}).reset_index().sort_values(by= "Cena za m2")
        num_rows = df_groupby_kraje_cena_za_m2.shape[0]
        # # Styling s podmíněným formátováním a formátováním hodnot
        styled_df = df_groupby_kraje_cena_za_m2.style.apply(zvyrazni_radek, axis=1, kategorie="Kraj", vybrana_hodnota=vybrany_kraj).format({
            "Užitná plocha": "{:.0f}",
            "Cena": "{:.0f}",
            "Cena za m2": "{:.0f}"
        })
     
        #výpis df - cena za m2
        st.write("Průměrné ceny bytů a užitné plochy pro jednotlivé kraje")
        st.dataframe(styled_df, height=(num_rows+1)*35+3, hide_index=True)

        #barchart plotly - cena za m2
        sorted_df = df_groupby_kraje_cena_za_m2.sort_values(by="Cena za m2")
        sorted_df["barva"] = sorted_df["Kraj"].apply(lambda x: "lightblue" if x == vybrany_kraj else "blue")
        
        fig = px.bar(sorted_df, y="Kraj", x="Cena za m2", color="barva",
                    color_discrete_map={"lightblue": "lightblue", "blue": "blue"},
                    category_orders={"Kraj": sorted_df["Kraj"].tolist()},
                    title="Cena bytů za m2 podle kraje")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig)

        #DISPOZICE ANALÝZA
        st.subheader("Analýza v rámci ČR - dispozice")
        col1, col2 = st.columns(2)
        with col1:
            df_groupby_dispozice_cena_m2 = df.groupby("Dispozice_kategorie")["Cena za m2"].mean().reset_index().sort_values(by="Cena za m2")
            #výpis df - dispozice
            st.write("Dispozice bytů - cena za m2 (celá ČR)")
            num_rows = df_groupby_dispozice_cena_m2.shape[0]
            styled_df = df_groupby_dispozice_cena_m2.style.format({
                "Užitná plocha": "{:.0f}",
                "Cena": "{:.0f}",
                "Cena za m2": "{:.0f}"
            })
            st.dataframe(styled_df, height=(num_rows+1)*35+3)    

        with col2:
            #barchart plotly - dispozice, cena za m2
            sorted_df = df_groupby_dispozice_cena_m2.sort_values(by="Cena za m2", ascending=False)
            
            fig = px.bar(sorted_df, y="Dispozice_kategorie", x="Cena za m2",
                        category_orders={"Dispozice_kategorie": sorted_df["Dispozice_kategorie"].tolist()},
                        title="Cena za m2 dle dispozice bytu (celá ČR)")
            fig.update_layout(showlegend=False, height=300, width=300, bargap=0.1)

            st.plotly_chart(fig)

        col1, col2 = st.columns(2)

        with col1:
            #dispozice - četnost
            df_groupby_dispozice = df.groupby("Dispozice_kategorie")["Dispozice_kategorie"].count().reset_index(name="četnost")
            # Výpočet procentuálního zastoupení výskytů
            df_groupby_dispozice["procenta"] = (df_groupby_dispozice["četnost"]/df_groupby_dispozice["četnost"].sum()).round(2)
            df_groupby_dispozice["procenta"] = df_groupby_dispozice["procenta"].map(lambda x: f"{x:.0%}")
            # Vytvoření pie chartu - dispozice četnost
            fig = px.pie(df_groupby_dispozice, values="četnost", names="Dispozice_kategorie", title="Dispozice bytů - zastoupení (celá ČR)")
            fig.update_traces(textinfo="percent+label")  # Přidání procentuálních hodnot k jednotlivým segmentům
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.write("Nejčetnější dispozice bytů dle krajů (celá ČR)")
            df_groupby_kraje_dispozice = df.groupby(["Kraj", "Dispozice_kategorie"]).size().reset_index(name="Počet")
            sorted_df_groupby_kraje_dispozice = df_groupby_kraje_dispozice.sort_values(by=["Kraj", "Počet"], ascending=[True, False])
            result_df = sorted_df_groupby_kraje_dispozice.groupby("Kraj").head(1).reset_index(drop=True)
            result_df = result_df[["Kraj", "Dispozice_kategorie"]]
            styled_df = result_df.style.apply(zvyrazni_radek, axis=1, kategorie="Kraj", vybrana_hodnota=vybrany_kraj)
            num_rows = result_df.shape[0]
            #výpis df - dispozice, četnost
            st.dataframe(styled_df, hide_index=True, height=(num_rows+1)*35+3)

    #ZALOZKA2 - ANALYZA PRO VYBRANY KRAJ
    with tab2:
        st.subheader("Analýza v rámci jednotlivých krajů - ceny bytů")
        df_kraj = df[df["Kraj"]==vybrany_kraj]

        #CENA ZA M2 - ANALÝZA KRAJE
        df_groupby_okresy_cena_za_m2 = df_kraj.groupby("Okres")[["Užitná plocha", "Cena", "Cena za m2"]].mean().round({"Užitná plocha":0, "Cena": -5,"Cena za m2": -2}).reset_index().sort_values(by= "Cena za m2")
        num_rows = df_groupby_okresy_cena_za_m2.shape[0]
        # # Styling s podmíněným formátováním a formátováním hodnot
        styled_df = df_groupby_okresy_cena_za_m2.style.apply(zvyrazni_radek, axis=1, kategorie="Okres", vybrana_hodnota=vybrany_okres).format({
            "Užitná plocha": "{:.0f}",
            "Cena": "{:.0f}",
            "Cena za m2": "{:.0f}"
        })
        #tabulka - cena za m2
        st.write(f"Průměrné ceny bytů a užitné plochy pro jednotlivé okresy ({vybrany_kraj})")
        st.dataframe(styled_df, height=(num_rows+1)*35+3, hide_index=True)
        #barchart plotly - cena za m2
        sorted_df = df_groupby_okresy_cena_za_m2.sort_values(by="Cena za m2")
        sorted_df["barva"] = sorted_df["Okres"].apply(lambda x: "lightblue" if x == vybrany_okres else "blue")
        
        fig = px.bar(sorted_df, y="Okres", x="Cena za m2", color="barva",
                    color_discrete_map={"lightblue": "lightblue", "blue": "blue"},
                    category_orders={"Okres": sorted_df["Okres"].tolist()},
                    title=(f"Cena bytů za m2 podle okresu ({vybrany_kraj})"))
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig)
        

        #DISPOZICE - ANALÝZA KRAJE
        st.subheader(f"Analýza v rámci - dispozice ({vybrany_kraj})")
        col1, col2 = st.columns(2)
        with col1:
            df_kraj_groupby_dispozice_cena_m2 = df_kraj.groupby("Dispozice_kategorie")["Cena za m2"].mean().reset_index().sort_values(by="Cena za m2")
            #výpis df - dispozice
            st.write(f"Dispozice bytů - cena za m2 ({vybrany_kraj})")
            num_rows = df_kraj_groupby_dispozice_cena_m2.shape[0]

            styled_df = df_kraj_groupby_dispozice_cena_m2.style.format({
                "Užitná plocha": "{:.0f}",
                "Cena": "{:.0f}",
                "Cena za m2": "{:.0f}"
            })

            st.dataframe(styled_df, height=(num_rows+1)*35+3)    

        with col2:
            #barchart plotly - dispozice, cena za m2
            sorted_df = df_kraj_groupby_dispozice_cena_m2.sort_values(by="Cena za m2", ascending=False)
            
            fig = px.bar(sorted_df, y="Dispozice_kategorie", x="Cena za m2",
                        category_orders={"Dispozice_kategorie": sorted_df["Dispozice_kategorie"].tolist()},
                        title=(f"Cena za m2 dle dispozice bytu ({vybrany_kraj})"))
            fig.update_layout(showlegend=False, height=300, width=300, bargap=0.1)

            st.plotly_chart(fig)


        col1, col2 = st.columns(2)

        with col1:
            #dispozice - četnost
            df_kraj_groupby_dispozice = df_kraj.groupby("Dispozice_kategorie")["Dispozice_kategorie"].count().reset_index(name="četnost")
            # Výpočet procentuálního zastoupení výskytů
            df_kraj_groupby_dispozice["procenta"] = (df_kraj_groupby_dispozice["četnost"]/df_kraj_groupby_dispozice["četnost"].sum()).round(2)
            df_kraj_groupby_dispozice["procenta"] = df_kraj_groupby_dispozice["procenta"].map(lambda x: f"{x:.0%}")
            # Vytvoření pie chartu - dispozice četnost
            fig = px.pie(df_kraj_groupby_dispozice, values="četnost", names="Dispozice_kategorie", title=(f"Dispozice bytů - zastoupení ({vybrany_kraj})"))
            fig.update_traces(textinfo="percent+label")  # Přidání procentuálních hodnot k jednotlivým segmentům
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.write(f"Nejčetnější dispozice bytů dle krajů ({vybrany_kraj})")
            df_groupby_okresy_dispozice = df_kraj.groupby(["Okres", "Dispozice_kategorie"]).size().reset_index(name="Počet")
            sorted_df_groupby_okresy_dispozice = df_groupby_okresy_dispozice.sort_values(by=["Okres", "Počet"], ascending=[True, False])
            result_df = sorted_df_groupby_okresy_dispozice.groupby("Okres").head(1).reset_index(drop=True)
            result_df = result_df[["Okres", "Dispozice_kategorie"]]
            styled_df = result_df.style.apply(zvyrazni_radek, axis=1, kategorie="Okres", vybrana_hodnota=vybrany_kraj)
            num_rows = result_df.shape[0]
            #výpis df - dispozice, četnost
            st.dataframe(styled_df, hide_index=True, height=(num_rows+1)*35+3)






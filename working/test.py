import json
import pandas as pd
import streamlit as st
import plotly.express as px

# Načtení dat z JSON souboru
with open("properties.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Vytvoření DataFrame
df = pd.DataFrame(data)

# Odstranění nepotřebných sloupců
df = df.drop(["Městská část", "Stav", "Číslo inzerátu", "Vlastnictví", "Rizika", "Vybaveno", 
              "Podlaží", "URL", "Popis", "Dostupné od", "PENB", "Pošta (metry)", "Pošta (minuty)", 
              "Banka (metry)", "Banka (minuty)", "Restaurace (metry)", "Restaurace (minuty)", 
              "Lékárna (metry)", "Lékárna (minuty)", "Sportoviště (metry)", "Sportoviště (minuty)", 
              "Provedení", "Stáří", "Vytápění", "Rekonstrukce", "Plocha pozemku", "Typ pozemku", 
              "Odpad", "Voda"], axis=1)

# Výpočet ceny za m²
df["Cena za m2"] = df["Cena"] / df["Užitná plocha"]

# Funkce pro mapování dispozic
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
    
# Přidání nové kategorie dispozic
df['Dispozice_kategorie'] = df['Dispozice'].apply(map_dispozice)

# Inicializace session state
if "zobrazit_uvodni_obrazovku" not in st.session_state:
    st.session_state["zobrazit_uvodni_obrazovku"] = True
if "vybrany_kraj" not in st.session_state:
    st.session_state.vybrany_kraj = "Ústecký kraj"

def show_content():
    st.session_state["zobrazit_uvodni_obrazovku"] = False
    st.experimental_rerun()

if st.session_state["zobrazit_uvodni_obrazovku"]:
    st.subheader("Projekt Python Como")
    st.title("Analýza bytů k prodeji - Bezrealitky.cz")
    if st.button("Procházet analýzu", key="btn_prochazet_analyzu"):
        st.session_state["zobrazit_uvodni_obrazovku"] = False
        st.experimental_rerun()
else:
    kraje = df['Kraj'].unique().tolist()
    
    vybrany_kraj = st.sidebar.selectbox("Vyber kraj, ke kterému se bude vztahovat analýza", kraje, key="vybrany_kraj")

    # Funkce pro formátování intervalů bez desetinných míst
    def format_interval_no_decimal(distance):
        if pd.isnull(distance):  # Kontrola, zda je hodnota NaN
            return "NaN"
        lower_bound = int((distance // 100) * 100)
        upper_bound = lower_bound + 100
        return f"{lower_bound}-{upper_bound}"




    # Vytvoření nového sloupce s formátovanými intervaly bez desetinných míst
    df["Vzdálenost od školy interval"] = df["Škola (metry)"].apply(format_interval_no_decimal)
    df = df[df["Vzdálenost od školy interval"] != "NaN"]


    # ZÁLOŽKA 1 - ANALÝZA V RÁMCI ČR
    tab1, tab2 = st.tabs(["Analýza v rámci ČR", "Analýza pro vybraný kraj"])
    
    with tab1:
        st.subheader("Analýza v rámci ČR - ceny bytů")  
        
        #filtr pro kraje:
        df_kraj = df[df["Kraj"]==vybrany_kraj]
        st.subheader(f"Analýza pro {vybrany_kraj}")

        # Vytvoření agregace včetně počtu výskytů pro každý interval
        df_groupby_dle_vzdálenosti_od = df_kraj.groupby("Vzdálenost od školy interval")["Škola (metry)"].count().reset_index(name="počet")

        # Výpočet procentuálního zastoupení výskytů
        celkovy_pocet_pozorovani = df_groupby_dle_vzdálenosti_od["počet"].sum()
        df_groupby_dle_vzdálenosti_od["procenta"] = (df_groupby_dle_vzdálenosti_od["počet"] / celkovy_pocet_pozorovani).round(2)
        df_groupby_dle_vzdálenosti_od["procenta"] = df_groupby_dle_vzdálenosti_od["procenta"].map(lambda x: f"{x:.0%}")
    
        
        # Celkový počet pozorování pro vybraný kraj
        celkovy_pocet_pozorovani = df_groupby_dle_vzdálenosti_od["počet"].sum()









        st.dataframe(df_groupby_dle_vzdálenosti_od, hide_index=True)

        

        # Vytvoření pie chartu
        fig = px.pie(df_groupby_dle_vzdálenosti_od, values='počet', names='Vzdálenost od školy interval', title='Počet bytů v jednotlivých vzdálenostních intervalech od školy')
        st.plotly_chart(fig, use_container_width=True)
        

        # Vytvoření bar chartu
        fig = px.bar(df_groupby_dle_vzdálenosti_od, x='Vzdálenost od školy interval', y='procenta', 
                    labels={'Vzdálenost od školy interval': 'Vzdálenost od školy interval'}, 
                    title='Procentuální rozložení vzdálenosti od školy')

        st.plotly_chart(fig, use_container_width=True)







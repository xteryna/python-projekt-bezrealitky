import json
import pandas as pd
import streamlit as st


with open("properties.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# new_data = []
# for value in data.values():
#     new_data.append(value)

df = pd.DataFrame(data)
df = df.drop(["výtah", "garáž", "balkon", "Dostupné od", "PENB", "Pošta (metry)", "Pošta (minuty)", "Banka (metry)", "Banka (minuty)", "Restaurace (metry)", "Restaurace (minuty)", "Lékárna (metry)", "Lékárna (minuty)", "Sportoviště (metry)", "Sportoviště (minuty)", "Provedení", "Stáří", "Vytápění", "Rekonstrukce", "Plocha pozemku", "Typ pozemku", "Odpad", "Voda"],axis=1)

st.write(df)

# hrát si s databází
#výběr soupců:
vyber1 = df[["Město", "Kraj"]]
st.write("vyber1 - mesto, kraj")
st.write(vyber1)

#filtrování:
filtr1 = df[df["Město"]=="Aš"]
st.write("filtr1 - aš")
st.write(filtr1)

filtr2 = df[(df["Město"]=="Chomutov") & (df["MHD (metry)"]<=100) ]
st.write("filtr Chomutov, MHD <= 100m")
st.write(filtr2)

#loc
mesto ="Most"
loc1 = df.loc[df["Město"] == mesto]
st.write("loc mesto ==Most")
st.write(loc1)

#přidání sloupce
st.write("přidání sloupce")
df["nový sloupec"] = "x"
st.write(df)


st.write("přidání sloupce - insert")
df.insert(0, "novy2","xx" )
st.write(df)



#konvertování hodnot ve sloupci num => str
col1, col2 = st.columns(2)

col1.write("konvertování Užitná plocha str")
df["Užitná plocha"] = df["Užitná plocha"].astype(str)
col1.write(df["Užitná plocha"])

col2.write("konvertování Užitná plocha int")
df["Užitná plocha"] = df["Užitná plocha"].astype(int)
col2.write(df["Užitná plocha"])

#grouping
# st.write("grouping")
# df["Město", "Užitná plocha"].groupby("Město").sum()



st.write("---")

prvni_mesto = df.at[0, 'Město']
st.write(f"at: Město na první pozici: {prvni_mesto}")
loc_belcice = df.loc[df["Město"]=="Bělčice"]
st.write(f'loc: Bělčice:{loc_belcice}')
loc_most = df.loc[df["Město"]=="Most"]
st.write(loc_most)
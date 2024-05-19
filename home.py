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
#filtrování:
# filtr1 = df(["Městská část"],["Město"])
# st.write(filtr1)









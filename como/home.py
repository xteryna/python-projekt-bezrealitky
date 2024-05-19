import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

url = "https://pocasi.seznam.cz/most"

response = requests.get(url)


soup = BeautifulSoup(response.text)

div_mol_weather = soup.find("div", {"data-dot": "ogm-detailed-forecast"})
div_c_et = div_mol_weather.find_all("div", {"class":"c_eT"})
st.write(div_c_et)

st.markdown("---")

with open("properties.json", "r", encoding="utf-8") as file:
    data = json.load(file)

new_data = []
for value in data.values():
    new_data.append(value)

df = pd.DataFrame(new_data)
st.write(df)
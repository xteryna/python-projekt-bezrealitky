import json

with open("properties.json", "r", encoding="utf-8") as file:
    data = json.load(file)

new_data = []
for value in data.values():
    new_data.append(value)

df = pd.DataFrame(data)
st.write(df)
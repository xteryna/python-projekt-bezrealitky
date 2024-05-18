import requests
from bs4 import BeautifulSoup

# Adresa URL stránky, kterou chcete prozkoumat
url = 'https://www.bezrealitky.cz/vypis/nabidka-prodej/byt?page=1'

# Získání obsahu stránky
response = requests.get(url)

# Kontrola, zda byl požadavek úspěšný (status kód 200)
if response.status_code == 200:
    # Získání obsahu stránky
    page_content = response.text

    # Vytvoření objektu BeautifulSoup pro analýzu HTML
    soup = BeautifulSoup(page_content, 'html.parser')

    # Vytisknutí struktury HTML stránky
    print(soup.prettify())
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")

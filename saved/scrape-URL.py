import requests
from bs4 import BeautifulSoup
import json
import time

base_url = 'https://www.bezrealitky.cz/vypis/nabidka-prodej/byt'
property_urls = []


page_number = 0

while True:
    page_number += 1
    url = f'{base_url}?page={page_number}'
    response = requests.get(url)

    if response.url != url:
        print(f"No more pages. Last page: {page_number - 1}.")
        break

    if response.status_code != 200:
        print(f"Failed to retrieve page {page_number}. Status code: {response.status_code}")
        break

    page_content = response.text
    soup = BeautifulSoup(page_content, 'html.parser')

    # Najdeme všechny prvky <a> s atributem tabindex="-1"
    apartment_links = soup.find_all('a', {'tabindex': '-1'})

    if not apartment_links:
        print(f"No apartment links found on page {page_number}. Stopping.")
        break

    for link in apartment_links:
        property_url = link['href']
        property_urls.append(property_url)

    # Zpoždění pro omezení rychlosti požadavků
    # time.sleep(1)

# Uložení URL do JSON souboru
with open('apartments.json', 'w', encoding='utf-8') as f:
    json.dump(property_urls, f, ensure_ascii=False, indent=4)

print("URL byly úspěšně uloženy do apartments.json")



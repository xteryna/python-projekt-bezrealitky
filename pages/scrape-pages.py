import json
import re
import requests
from bs4 import BeautifulSoup

def scrape_property_data(url):
    # Stáhnout HTML obsah stránky
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Stránka {url} nenalezena")
        return None
    
    # Analýza HTML pomocí BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Nalezení sekce s parametry nemovitosti
    params_section = soup.find('section', class_='box Section_section__gjwvr section mb-5 mb-lg-10')
    if not params_section:
        print(f"Sekce s parametry na stránce {url} nenalezena")
        return None
    
    # Vytáhnout jednotlivé parametry nemovitosti
    property_data = {}
    params_groups = params_section.find_all('div', class_='ParamsTable_paramsTableGroup__Flyfi')
    for group in params_groups:
        rows = group.find_all('tr')
        for row in rows:
            th = row.find('th')
            td = row.find('td')
            if th and td:
                property_data[th.text.strip()] = td.text.strip()
    
    # Nalezení ceny nemovitosti
    price_div = soup.find('div', class_='justify-content-between align-items-baseline mb-lg-9 mb-6 row')
    if price_div:
        price_span = price_div.find('strong', class_='h4 fw-bold')
        if price_span:
            # Extrahovat textovou podobu ceny a odstranit mezery, symboly a nežádoucí znaky oddělovačů tisíců
            price_text = price_span.text.strip().replace(' ', '').replace('Kč', '')
            # Odstranit nežádoucí znaky oddělovačů tisíců
            price_text = re.sub(r'[^\d]', '', price_text)
            # Převést textovou cenu na celé číslo (integer)
            property_data['Cena'] = int(price_text)
    
    # Převést hodnotu Podlaží na integer
    if 'Podlaží' in property_data:
        try:
            property_data['Podlaží'] = int(property_data['Podlaží'])
        except ValueError:
            pass
    
    # Převést hodnotu Užitná plocha na integer
    if 'Užitná plocha' in property_data:
        try:
            # Extrahovat číselnou hodnotu z textu a odstranit mezery
            area_text = re.findall(r'\d+', property_data['Užitná plocha'])
            area_int = int(area_text[0]) if area_text else None
            property_data['Užitná plocha'] = area_int
        except ValueError:
            pass
    
    # Nalezení informací o bodech zájmu v okolí
    neighborhood_div = soup.find('div', class_='Neighborhood_neighborhoodTable__Ipy5I neighborhoodTable')
    if neighborhood_div:
        poi_items = neighborhood_div.find_all('div', class_='Poi_poiItem__7JgIz poiItem')
        poi_data = {}
        for item in poi_items:
            poi_type = item.find('span', class_='Poi_poiItemContentType__XukbX poiItemContentType')
            poi_name = item.find('strong', class_='poiItemContentName')
            poi_distance = item.find('div', class_='Poi_poiItemTimes__hse64 poiItemTimes')
            if poi_type and poi_name and poi_distance:
                distance_text = poi_distance.text.strip()
                distance_match = re.match(r'🚶 (\d+) m \((\d+) min\)', distance_text)
                if distance_match:
                    meters = int(distance_match.group(1))
                    minutes = int(distance_match.group(2))
                    poi_type_text = poi_type.find('span').text.strip()  # Získat text z vnořeného elementu span
                    poi_data[poi_type_text] = {
                        'Vzdálenost': {'metry': meters, 'minuty': minutes}
                    }
        property_data['Body zájmu v okolí'] = poi_data
    
    # Extrahovat údaje o městě a městské části
    breadcrumb_div = soup.find('div', class_='Container_container--narrow__0pGYY container')
    if breadcrumb_div:
        breadcrumb_items = breadcrumb_div.find_all('li', class_='breadcrumb-item')
        if len(breadcrumb_items) >= 6:
            city = breadcrumb_items[4].text.strip()
            district = breadcrumb_items[5].text.strip()
            property_data['Kraj'] = city
            property_data['Okres'] = district
    
    # Přidat URL stránky do výsledných dat
    property_data['URL'] = url
    
    # Scrapovat text z elementu <div class="box mb-8">
    text_div = soup.find('div', class_='box mb-8')
    if text_div:
        paragraphs = text_div.find_all('p', class_='text-perex-lg') + text_div.find_all('p', class_='text-perex text-grey-dark')
        description = '\n'.join(paragraph.text.strip() for paragraph in paragraphs if paragraph.text.strip())
        property_data['Popis'] = description
    
    return property_data

# Načíst seznam URL adres z JSON souboru
with open('apartments.json', 'r', encoding='utf-8') as file:
    urls = json.load(file)

# Procházení seznamu URL adres
property_dict = {}
for i, url in enumerate(urls):
    print(f"Zpracovává se: {url}")
    data = scrape_property_data(url)
    if data:
        property_dict[i] = data

# Uložit data do jednoho JSON souboru
with open('properties.json', 'w', encoding='utf-8') as json_file:
    json.dump(property_dict, json_file, ensure_ascii=False, indent=4)

print("Data uložena do properties.json")








import json  
import requests # type: ignore  
import os
from bs4 import BeautifulSoup # type: ignore  

# URL for the List of Ships page  
url = "https://azurlane.koumakan.jp/wiki/List_of_Ships"  

def parse_html_table(page_content):  
    soup = BeautifulSoup(page_content, 'html.parser')  
    ships = []  
    ship_names = set()  # Keep track of unique ship names  
    
    # Find each row with relevant data  
    for row in soup.find_all("tr"):  
        cells = row.find_all("td")  
        if len(cells) >= 6:  
            # Extract ship details  
            ship_id_text = cells[0].get_text(strip=True)  

            # Check if ship_id is non-integer  
            if ship_id_text.isdigit():  
                ship_id = int(ship_id_text)  
            else:  
                if ship_id_text.startswith("Collab"):  
                    # Strip "Collab" and prepend "10" to the numeric part  
                    stripped_id = '10' + ship_id_text[6:]  
                    ship_id = int(stripped_id)  
                elif ship_id_text.startswith("Plan"):  
                    # Strip "Plan" and prepend "20" to the numeric part  
                    stripped_id = '20' + ship_id_text[4:]  
                    ship_id = int(stripped_id)  

            name_en = cells[1].get_text(strip=True)  

            # Check if the ship name is already in the list  
            if name_en not in ship_names:  
                rarity = cells[2].get_text(strip=True)  
                hull_type = cells[3].get_text(strip=True)  
                nationality = cells[4].get_text(strip=True)  

                ship_data = {  
                    "shipId": ship_id,  
                    "name_en": name_en,  
                    "rarity": rarity,  
                    "hullType": hull_type,  
                    "nationality": nationality,  
                    "level": 0  
                }  
                ships.append(ship_data)  
                ship_names.add(name_en)  # Add the ship name to the set  

    return ships  

response = requests.get(url)  
response.encoding = 'utf-8'  # Ensure correct encoding  
page_content = response.text  

# Parse the page content  
all_ships = parse_html_table(page_content)  

# Save all ship data to one JSON file  
output_path = os.path.join(os.path.dirname(__file__), 'list', 'all_ships.json')

# Ensure the subfolder exists
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, 'w', encoding='utf-8') as f:  
    json.dump(all_ships, f, ensure_ascii=False, indent=2)  

print(f"Data saved to list/all_ships.json")
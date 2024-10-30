import json
import requests # type: ignore
from bs4 import BeautifulSoup # type: ignore
import re
import sys
import io
import os
import time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# URL for Fleet Technology page
url = "https://azurlane.koumakan.jp/wiki/Fleet_Technology"

# Load existing ship data
input_folder = os.path.join(os.path.dirname(__file__), 'list', 'all_ships.json')

with open(input_folder, "r", encoding="utf-8") as f:
    ship_data = json.load(f)

# Fetch live HTML  
response = requests.get(url)  
response.encoding = 'utf-8'  
soup = BeautifulSoup(response.text, 'html.parser')  

stat_mapping = {
    "Health": "health",
    "Firepower": "firepower",
    "Aviation": "aviation",
    "Reload": "reload",
    "Accuracy": "accuracy",
    "Anti-Air": "antiair",
    "Torpedo": "torpedo",
    "Evasion": "evasion",
    "Anti-Submarine": "antisubmarineWarfare"
}

hull_type_mapping = {
    "Destroyer": "\"Destroyer\",\"Guided-missile Destroyer\"",
    "Light Cruiser": "\"Light Cruiser\"",
    "Heavy Cruiser": "\"Heavy Cruiser\",\"Large Cruiser\",\"Monitor\"",
    "Large Cruiser": "\"Heavy Cruiser\",\"Large Cruiser\",\"Monitor\"",
    "Monitor": "\"Heavy Cruiser\",\"Large Cruiser\",\"Monitor\"",
    "Battleship": "\"Battleship\",\"Battlecruiser\",\"Aviation Battleship\"",
    "Battlecruiser": "\"Battleship\",\"Battlecruiser\",\"Aviation Battleship\"",
    "Aviation Battleship": "\"Battleship\",\"Battlecruiser\",\"Aviation Battleship\"",
    "Aircraft Carrier": "\"Aircraft Carrier\",\"Light Aircraft Carrier\"",
    "Light Aircraft Carrier": "\"Light Aircraft Carrier\",\"Aircraft Carrier\"",
    "Repair Ship": "\"Repair Ship\"",
    "Munition Ship": "\"Munition Ship\"",
    "Submarine": "\"Submarine\",\"Submarine Carrier\"",
    "Submarine Carrier": "\"Submarine\",\"Submarine Carrier\"",
    "Sailing Frigate (Main)": "\"Sailing Frigate (Main)\",\"Sailing Frigate (Vanguard)\",\"Sailing Frigate (Submarine)\"",
    "Sailing Frigate (Vanguard)": "\"Sailing Frigate (Main)\",\"Sailing Frigate (Vanguard)\",\"Sailing Frigate (Submarine)\"",
    "Sailing Frigate (Submarine)": "\"Sailing Frigate (Main)\",\"Sailing Frigate (Vanguard)\",\"Sailing Frigate (Submarine)\""
}

def parse_bonus_data(soup, bonus_type):  
    bonus_data = {}  
    current_stat = None  
    current_bonus = None  
    current_rowspan = 0  

    tables = soup.find_all("table")  

    # Go through each of 9 tabs in each table
    if bonus_type == "collection":  
        table_range = range(9)  
    elif bonus_type == "maxLevel":  
        table_range = range(9, 18)  
    else:  
        raise ValueError("Invalid bonus_type. Must be 'collection' or 'maxLevel'.")  

    for table_index in table_range:  
        table = tables[table_index]  
        # Find each row with relevant data  
        for row in table.find_all("tr", class_=["e", "o"]):  
            cells = row.find_all("td")  

            # If the first cell has rowspan, update current stat and bonus  
            if len(cells) > 0 and "rowspan" in cells[0].attrs:  
                current_stat = cells[0].find("img")["alt"] if cells[0].find("img") else None  
                current_bonus = re.match(r"\d+", cells[0].text.strip().replace("+", "")).group() if cells[0] else None  
                current_rowspan = int(cells[0]['rowspan'])  # Get the rowspan value  

            # Since cells differ from each other check for ship names in the appropriate cell (cells[2] and cells[3])  
            ship_names = []  
            if len(cells) > 2:  
                ship_names.extend(cells[2].find_all("a"))  
            if len(cells) > 3:  
                ship_names.extend(cells[3].find_all("a"))  

            # Assign the current bonus data to all ship names found  
            for ship in ship_names:  
                name_en = ship["title"]  

                desired_stat = stat_mapping.get(current_stat, current_stat)  

                # Add ship to bonus_data with its nationality  
                if name_en not in bonus_data:  
                    bonus_data[name_en] = {  
                        f"{bonus_type}Stat": desired_stat,  
                        f"{bonus_type}Bonus": current_bonus  
                    }  

            # Decrement the current_rowspan if it's greater than zero  
            if current_rowspan > 0:  
                current_rowspan -= 1  
                # Reset current stat and bonus if we're done with the rowspan  
                if current_rowspan == 0:  
                    current_stat = None  
                    current_bonus = None  

    return bonus_data  

# Parse tables for Collection and Level stats  
collection_bonus_data = parse_bonus_data(soup, "collection")  
max_level_bonus_data = parse_bonus_data(soup, "maxLevel")  

# Merge bonus data into existing ship data
for ship in ship_data:
    name_en = ship["name_en"]
    if name_en in collection_bonus_data:
        ship.update(collection_bonus_data[name_en])
    else:
        # If not found, null
        ship["collectionStat"] = None
        ship["collectionBonus"] = None
        ship["collectionApplicable"] = None
    
    if name_en in max_level_bonus_data:
        ship.update(max_level_bonus_data[name_en])
    else:
        # If not found, null
        ship["maxLevelStat"] = None
        ship["maxLevelBonus"] = None
        ship["maxLevelApplicable"] = None

    # Clean up hullType
    hull_type = ship.get("hullType", "").replace("\n", " ").strip()
    hull_type = re.sub(r'\s+', ' ', hull_type)  # Replace multiple spaces with single space
    ship["hullType"] = hull_type

    # Clean up name_en
    name_en = ship.get("name_en", "").replace("\n", " ").strip()
    name_en = re.sub(r'\s+', ' ', name_en)  # Replace multiple spaces with single space
    ship["name_en"] = name_en

    # Apply hull type applicability based on bonus values and stats
    if (ship.get("collectionBonus") in ["1", "2"]) or (ship.get("collectionStat") or ship.get("maxLevelStat")):
        if hull_type in hull_type_mapping:
            ship["collectionApplicable"] = hull_type_mapping[hull_type]
            ship["maxLevelApplicable"] = hull_type_mapping[hull_type]
        else:
            ship["collectionApplicable"] = ""
            ship["maxLevelApplicable"] = ""

# Save the updated ship data to a new JSON file
timestamp = str(int(time.time()))
output_path = os.path.join(os.path.dirname(__file__), 'output', f"{timestamp}.json")

# Ensure the subfolder exists
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(ship_data, f, ensure_ascii=False, indent=2)

print(f"Data saved to output/{timestamp}.json")

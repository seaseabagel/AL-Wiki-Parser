import json
import requests # type: ignore
import sys
import io
import os
from dotenv import load_dotenv
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load existing ship data
input_folder = os.path.join(os.path.dirname(__file__), 'missing', 'missing_ships.json')

with open(input_folder, "r", encoding="utf-8") as f:
    data = json.load(f)

# Load environment variables from .env file
load_dotenv()
api_url = os.getenv("APP_URL")
app_id = os.getenv("APP_ID")
api_key = os.getenv("APP_REST_API_KEY")

headers = {
    'X-Parse-Application-Id': app_id,
    'X-Parse-REST-API-Key': api_key,
    'Content-Type': 'application/json'
}

# Send each object individually
for item in data:
    response = requests.post(api_url, headers=headers, json=item)
    if response.status_code in {200, 201, 202}:
        print(f"Ship added successfully: {item['shipId']}, {item['name_en']}")
    else:
        print("Failed to post object:", response.status_code, response.text)

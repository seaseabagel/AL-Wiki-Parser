import os
import json

# Get the path to the input folder
input_folder = os.path.join(os.path.dirname(__file__), 'output')

# Get only JSON files with numeric names and sort them
json_files = sorted(
    [f for f in os.listdir(input_folder) if f.endswith('.json') and f[:-5].isdigit()],
    reverse=True
)[:2]

# Proceed only if there are exactly two valid files
if len(json_files) < 2:
    raise ValueError("Not enough valid JSON files with numeric names found in the input folder.")

file1_path = os.path.join(input_folder, json_files[0])
file2_path = os.path.join(input_folder, json_files[1])

# Load the JSON files
with open(file1_path, 'r') as f1, open(file2_path, 'r') as f2:
    data1 = json.load(f1)
    data2 = json.load(f2)

# Convert to dictionaries keyed by 'shipId'
data1_dict = {item['shipId']: item for item in data1}
data2_dict = {item['shipId']: item for item in data2}

# Find items in data1 that are missing in data2
missing_in_data2 = [item for key, item in data1_dict.items() if key not in data2_dict]

# Save missing items to a new JSON file
output_path = os.path.join(os.path.dirname(__file__), 'missing', 'missing_ships.json')
# Ensure the subfolder exists
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, 'w') as f_out:
    json.dump(missing_in_data2, f_out, ensure_ascii=False, indent=2)

print(f"{len(missing_in_data2)} missing items saved to missing/missing_ships.json")

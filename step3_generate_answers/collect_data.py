import os
import json
import jsonlines

# Path to the root folder
root_folder = "outputs"

# Initialize an empty list to store concatenated data
concatenated_data = []

# Recursively traverse the directory
for root, dirs, files in os.walk(root_folder):
    for filename in files:
        if filename.endswith('.jsonl'):
            file_path = os.path.join(root, filename)

            # import pdb;pdb.set_trace()
            with open(file_path, "r") as file:
                # Read each line (JSON object) and append it to the list
                for line in file:
                    line = line.strip()  # Remove leading/trailing whitespace
                    if line:
                        try:
                            json_object = json.loads(line)
                            concatenated_data.append(json_object)
                        except json.JSONDecodeError as e:
                            print(f"Error parsing JSON in file '{file_path}': {e}")

# Save the concatenated data to a new JSONL file
with open("data_merged.jsonl", 'w') as output_file:
    json.dump(concatenated_data, output_file, indent=2)

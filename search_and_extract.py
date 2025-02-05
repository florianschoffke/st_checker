import os
import re
import json

def load_config(config_file):
    with open(config_file, 'r') as file:
        return json.load(file)

import os
import re

def search_files(root_path, regex_pattern):
    matches = set()  # Use a set to ensure uniqueness
    for dirpath, dirnames, filenames in os.walk(root_path):
        # Skip directories named "examples"
        dirnames[:] = [d for d in dirnames if d != "examples"]
        
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    found_matches = re.findall(rf'"(https://[^\"]*{regex_pattern}[^\"]*)"', content)
                    matches.update(found_matches)
            except UnicodeDecodeError:
                # Silently skip files that can't be decoded
                continue
            except Exception as e:
                # Optionally handle other exceptions
                print(f"An error occurred while processing {file_path}: {e}")
    return list(matches)  # Convert set back to list


def main():
    config_file = 'config.json'
    config = load_config(config_file)
    package_path = config['package_path']
    regex_pattern = config['st_regex']
    
    results = {}
    
    for config_name, folders in config['configs'].items():
        all_matches = set()
        for folder in folders:
            folder_path = os.path.join(package_path, folder)
            if os.path.exists(folder_path):
                matches = search_files(folder_path, regex_pattern)
                all_matches.update(matches)
            else:
                print(f"Folder {folder_path} does not exist.")
        results[config_name] = list(all_matches)  # Convert set to list

    # Ensure the output directory exists
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)

    # Output results to a JSON file in the output directory
    output_file_path = os.path.join(output_dir, 'output.json')
    with open(output_file_path, 'w', encoding='utf-8') as out_file:
        json.dump(results, out_file, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()

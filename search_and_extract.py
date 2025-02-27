import os
import re
import json

def load_config(config_file):
    with open(config_file, 'r') as file:
        return json.load(file)

def search_files(root_path, regex_pattern):
    matches = set()  # Use a set to ensure uniqueness
    for dirpath, dirnames, filenames in os.walk(root_path):
        # Exclude directories named "examples"
        dirnames[:] = [d for d in dirnames if d != "examples"]
        
        # Sort filenames to ensure deterministic order
        for filename in sorted(filenames):
            file_path = os.path.join(dirpath, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    found_matches = re.findall(rf'"(http[s]?://[^\"]*{regex_pattern}[^\"]*)"', content)
                    matches.update(found_matches)
            except UnicodeDecodeError:
                # Silently skip files that can't be decoded
                continue
            except Exception as e:
                # Optionally handle other exceptions
                print(f"An error occurred while processing {file_path}: {e}")
    return sorted(matches)  # Convert set to list and sort for deterministic output

def main():
    config_file = 'config.json'
    config = load_config(config_file)
    package_path = config['package_path']
    regex_pattern = config['st_regex']
    
    results = {}

    for config_name, folders in config['configs'].items():
        unique_matches = set()
        for folder in sorted(folders):  # Sort folders to ensure deterministic order
            folder_path = os.path.join(package_path, folder)
            if os.path.exists(folder_path):
                matches = search_files(folder_path, regex_pattern)
                unique_matches.update(matches)
            else:
                print(f"Folder {folder_path} does not exist.")
        results[config_name] = sorted(unique_matches)  # Convert set to sorted list

    # Write results to a JSON file
    output_file = 'output/output.json'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as out_file:
        json.dump(results, out_file, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()

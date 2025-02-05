import json

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def extract_unique_strings(output_file, result_file):
    # Load the JSON data
    output_data = load_json(output_file)

    # Collect unique entries from all configs and extract substring starting from "SFHIR"
    unique_strings = set()
    for entries in output_data.values():
        for entry in entries:
            # Extract the part of the string starting from "SFHIR"
            if "SFHIR" in entry:
                unique_part = entry.split("SFHIR", 1)[1]
                unique_strings.add("SFHIR" + unique_part)

    # Write unique strings to a text file
    with open(result_file, 'w', encoding='utf-8') as file:
        for string in sorted(unique_strings):
            file.write(string + "\n")

def main():
    output_file = 'output/output.json'
    result_file = 'output/unique_strings.txt'
    extract_unique_strings(output_file, result_file)

if __name__ == "__main__":
    main()

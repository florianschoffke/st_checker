import json

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def extract_unique_strings(output_file, result_file):
    # Load the JSON data
    output_data = load_json(output_file)

    # Collect unique entries from all configs
    unique_strings = set()
    for entries in output_data.values():
        unique_strings.update(entries)

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

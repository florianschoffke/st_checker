import json
from collections import defaultdict
import os

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def check_for_changes(kbv_file, output_file, comparison_file, results_file):
    # Load the JSON data
    kbv_data = load_json(kbv_file)
    output_data = load_json(output_file)
    comparison_data = load_json(comparison_file)

    # Extract names and their details from kbv-all-st-rc.json
    kbv_details = {
        file_info['name']: {
            'version': file_info.get('version', 'N/A'),
            'date': file_info.get('date', 'N/A')
        }
        for file_info in kbv_data.get('contained_files', [])
    }

    # Prepare a dictionary to store matches by config
    matches_by_config = defaultdict(list)

    # Collect unique Schlüsseltabellen names
    schluesseltabellen_to_update = set()

    # Check for matches and group them by config
    for config_name, entries in output_data.items():
        for entry in entries:
            for name, details in kbv_details.items():
                if name in entry:
                    matches_by_config[config_name].append((name, details['version'], details['date']))
                    schluesseltabellen_to_update.add(name)
                    break  # Exit inner loop after finding a match for this entry

    # Prepare results for compare-kbv-st-all.json
    concern_files = defaultdict(lambda: defaultdict(list))

    # Check comparison results against output.json
    for category in ["dropped_files", "new_files", "changed_files"]:
        for file_name in comparison_data.get(category, []):
            if category == "changed_files":
                file_name = file_name["name"]
            for config_name, entries in output_data.items():
                if any(file_name in entry for entry in entries):
                    concern_files[config_name][category].append(file_name)
                    schluesseltabellen_to_update.add(file_name)

    # Write results to a text file
    with open(results_file, 'w', encoding='utf-8') as file:
        # Block for Schlüsseltabellen to update
        if schluesseltabellen_to_update:
            header = "Schlüsseltabellen to update"
            separator = "=" * len(header)
            file.write(f"{separator}\n{header}\n{separator}\n")
            for name in sorted(schluesseltabellen_to_update):
                file.write(name + "\n")
            file.write("\n")

        # Original logic output
        if matches_by_config:
            warning_message = "WARNING: Upcoming Schlüsseltabellen Changes"
            separator = "=" * len(warning_message)
            print(f"\033[93m{separator}\n{warning_message}\n{separator}\033[0m")
            file.write(f"{separator}\n{warning_message}\n{separator}\n")
            for config_name, matches in matches_by_config.items():
                config_header = f"\nConfig: {config_name}"
                print(config_header)
                file.write(config_header + "\n")
                for name, version, date in matches:
                    match_detail = f"{name}, new Version {version}, update on {date}"
                    print(match_detail)
                    file.write(match_detail + "\n")

        # New logic output
        if any(concern_files.values()):
            comparison_warning = "WARNING: Concerns from compare-kbv-st-all.json"
            separator = "=" * len(comparison_warning)
            print(f"\033[93m\n{separator}\n{comparison_warning}\n{separator}\033[0m")
            file.write(f"\n{separator}\n{comparison_warning}\n{separator}\n")
            for config_name, categories in concern_files.items():
                config_header = f"\nConfig: {config_name}"
                print(config_header)
                file.write(config_header + "\n")
                for category, files in categories.items():
                    if files:
                        category_header = f"\n{category.capitalize()}:"
                        print(category_header)
                        file.write(category_header + "\n")
                        for file_name in files:
                            print(file_name)
                            file.write(file_name + "\n")

def main():
    kbv_file = 'output/kbv-all-st-rc.json'
    output_file = 'output/output.json'
    comparison_file = 'output/compare-kbv-st-all.json'
    results_file = 'output/kbv-all-st-rc-results.txt'
    check_for_changes(kbv_file, output_file, comparison_file, results_file)

if __name__ == "__main__":
    main()

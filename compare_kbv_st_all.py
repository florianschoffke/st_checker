import os
import requests
import tarfile
import json
import feedparser
from difflib import unified_diff

def download_and_extract(url, download_path, extract_path):
    response = requests.get(url, stream=True)
    with open(download_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=1024):
            file.write(chunk)

    with tarfile.open(download_path, 'r:gz') as tar:
        tar.extractall(path=extract_path)

def get_most_recent_packages(feed_url, prefix, count=2):
    feed = feedparser.parse(feed_url)
    entries = [item for item in feed.entries if item.title.startswith(prefix)]
    entries.sort(key=lambda x: x.published_parsed, reverse=True)
    return entries[:count]

def load_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def compare_json_contents(json1, json2):
    # Compare the JSON contents and return a diff if they differ
    diff = list(unified_diff(
        json.dumps(json1, indent=4, sort_keys=True).splitlines(),
        json.dumps(json2, indent=4, sort_keys=True).splitlines(),
        lineterm=''
    ))
    return diff if diff else None

def compare_package_contents(dir1, dir2):
    dir1 = os.path.join(dir1, "package")
    dir2 = os.path.join(dir2, "package")

    # Load JSON files into dictionaries keyed by "name" property
    files1 = {}
    files2 = {}

    for filename in sorted(os.listdir(dir1)):  # Sort filenames for deterministic order
        if filename.endswith('.json') and filename != 'package.json':
            file_path = os.path.join(dir1, filename)
            json_data = load_json_file(file_path)
            name = json_data.get("name")
            if name:
                files1[name] = json_data

    for filename in sorted(os.listdir(dir2)):  # Sort filenames for deterministic order
        if filename.endswith('.json') and filename != 'package.json':
            file_path = os.path.join(dir2, filename)
            json_data = load_json_file(file_path)
            name = json_data.get("name")
            if name:
                files2[name] = json_data

    # Compare the contents
    dropped_files = sorted(list(files2.keys() - files1.keys()))  # Sort for deterministic order
    new_files = sorted(list(files1.keys() - files2.keys()))      # Sort for deterministic order
    changed_files = []

    for name in sorted(files1.keys() & files2.keys()):  # Sort for deterministic order
        diff = compare_json_contents(files1[name], files2[name])
        if diff:
            changed_files.append({"name": name, "diff": diff})

    return {
        "dropped_files": dropped_files,
        "new_files": new_files,
        "changed_files": changed_files
    }

def main():
    rss_feed_url = "https://packages.simplifier.net/rssfeed"
    package_prefix = "kbv.all.st#"
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)

    # Get the two most recent packages
    recent_packages = get_most_recent_packages(rss_feed_url, package_prefix)

    # Download and extract packages
    package_dirs = []
    for entry in recent_packages:
        title = entry.title.replace('#', '_')
        download_path = os.path.join(temp_dir, f"{title}.tgz")
        extract_path = os.path.join(temp_dir, title)
        download_and_extract(entry.link, download_path, extract_path)
        package_dirs.append(extract_path)

    # Compare package contents
    if len(package_dirs) == 2:
        # Compare package 1 to package 0
        comparison_results = compare_package_contents(package_dirs[1], package_dirs[0])

        # Write comparison results to JSON
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        output_file_path = os.path.join(output_dir, "compare-kbv-st-all.json")
        with open(output_file_path, 'w', encoding='utf-8') as out_file:
            json.dump(comparison_results, out_file, indent=4, ensure_ascii=False)
    else:
        print("Error: Could not find two recent packages to compare.")

if __name__ == "__main__":
    main()

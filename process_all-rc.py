import os
import requests
import tarfile
import json
import feedparser

def download_and_extract(url, download_path, extract_path):
    response = requests.get(url, stream=True)
    with open(download_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=1024):
            file.write(chunk)

    with tarfile.open(download_path, 'r:gz') as tar:
        tar.extractall(path=extract_path)

def process_json_files(package_path, output_file_path):
    contained_files = []

    for filename in os.listdir(package_path):
        if filename.endswith('.json') and filename != 'package.json':
            file_path = os.path.join(package_path, filename)
            print(file_path)
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                contained_files.append({
                    "name": data.get("name"),
                    "resourceType": data.get("resourceType"),
                    "version": data.get("version"),
                    "date": data.get("date")
                })

    output_data = {
        "contained_files": contained_files
    }

    with open(output_file_path, 'w', encoding='utf-8') as out_file:
        json.dump(output_data, out_file, indent=4, ensure_ascii=False)

def main():
    rss_feed_url = "https://packages.simplifier.net/rssfeed"
    feed = feedparser.parse(rss_feed_url)

    # Find the most recent entry with title starting with "kbv.all.st-rc#"
    entry = next((item for item in feed.entries if item.title.startswith("kbv.all.st-rc#")), None)

    if entry:
        link = entry.link
        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)

        download_path = os.path.join(temp_dir, "package.tgz")
        extract_path = os.path.join(temp_dir, "package")

        # Download and extract the package
        download_and_extract(link, download_path, extract_path)

        # Rename the extracted folder
        renamed_package_path = os.path.join(temp_dir, "st-rc-package")
        os.rename(extract_path, renamed_package_path)

        # Process JSON files
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        output_file_path = os.path.join(output_dir, "kbv-all-st-rc.json")
        
        package_path = os.path.join(renamed_package_path, "package")

        process_json_files(package_path, output_file_path)
    else:
        print("No matching entry found in the RSS feed.")

if __name__ == "__main__":
    main()

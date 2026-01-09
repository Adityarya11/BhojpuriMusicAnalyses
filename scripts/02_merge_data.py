import json
import os

FOLDER_PATH = "./holi"  # Folder containing per-video JSONs
OUTPUT_JSON = "merged_songs.json"

def merge_video_jsons(folder_path, output_file):
    all_songs = []

    # Get only JSON files
    json_files = [f for f in os.listdir(folder_path) if f.endswith(".json")]

    if not json_files:
        print("❌ No JSON files found in the folder.")
        return

    print(f"Found {len(json_files)} video JSON files.")

    for file_name in json_files:
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            all_songs.append(data)

    # Save merged JSON
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(all_songs, file, indent=4, ensure_ascii=False)

    print(f"✅ Merged {len(json_files)} JSON files into '{output_file}'.")

if __name__ == "__main__":
    merge_video_jsons(FOLDER_PATH, OUTPUT_JSON)

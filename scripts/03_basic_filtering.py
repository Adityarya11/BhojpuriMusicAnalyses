import json
import re
import pandas as pd
import os

# Define input/output paths using os.path.join for cross-platform compatibility
INPUT_JSON = "merged_songs.json"
OUTPUT_CSV = os.path.join("data", "raw", "filtered_comments.csv")
MIN_WORDS = 3

def clean_text(text):
    """
    Basic cleaning: Removes special characters and extra spaces.
    Why? Punctuation doesn't usually add value to topic modeling.
    """
    text = re.sub(r"[^\w\s]", "", text)  # Remove punctuation
    text = re.sub(r"\s+", " ", text)     # Normalize whitespace
    return text.strip()

def flatten_comments(json_path):
    """
    Transforms nested JSON (video -> comments) into a flat CSV format.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = []
    for song in data:
        # Extract metadata
        base_info = {
            "video_id": song.get("video_id"),
            "url": song.get("url"),
            "title": song.get("title"),
            "views": song.get("views"),
        }

        # Process each comment
        for comment in song.get("comments", []):
            cleaned = clean_text(comment)
            word_count = len(cleaned.split())
            
            # FILTERING LOGIC: Ignore very short comments
            if word_count >= MIN_WORDS:
                records.append({
                    **base_info,
                    "comment": cleaned,
                    "word_count": word_count
                })

    return pd.DataFrame(records)

if __name__ == "__main__":
    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    
    df = flatten_comments(INPUT_JSON)
    print(f"✅ Extracted {len(df)} meaningful comments.")
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"📁 Data saved to: {OUTPUT_CSV}")
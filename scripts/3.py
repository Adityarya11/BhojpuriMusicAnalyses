import json
import re
import pandas as pd

INPUT_JSON = "merged_songs.json"
OUTPUT_CSV = "filtered_comments.csv"
MIN_WORDS = 3

def clean_text(text):
    """Remove punctuation and normalize whitespace."""
    text = re.sub(r"[^\w\s]", "", text)  # Remove punctuation
    text = re.sub(r"\s+", " ", text)  # Normalize spaces
    return text.strip()

def flatten_comments(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = []
    for song in data:
        base = {
            "video_id": song.get("video_id"),
            "url": song.get("url"),
            "title": song.get("title"),
            "channel": song.get("channel"),
            "artist": song.get("artist"),
            "year": song.get("year"),
            "theme": song.get("theme"),
            "views": song.get("views"),
            "likes": song.get("likes"),
        }

        for comment in song.get("comments", []):
            cleaned = clean_text(comment)
            word_count = len(cleaned.split())
            if word_count >= MIN_WORDS:
                records.append({
                    **base,
                    "comment": cleaned,
                    "word_count": word_count
                })

    return pd.DataFrame(records)

if __name__ == "__main__":
    df = flatten_comments(INPUT_JSON)
    print(f"✅ Loaded and filtered {len(df)} comments with >= {MIN_WORDS} words.")
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"📁 Saved to: {OUTPUT_CSV}")

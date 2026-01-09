import pandas as pd
import os

# Load dataset
INPUT_FILE = os.path.join("data", "raw", "filtered_comments.csv")
OUTPUT_FILE = "video_level_stats.csv"

if __name__ == "__main__":
    df = pd.read_csv(INPUT_FILE)

    # Group by 'url' (Corrected from 'video_url') and 'title'
    video_stats = (
        df.groupby(["url", "title"])
        .agg(
            comments_collected=("comment", "count"),
            avg_word_count=("word_count", "mean"),
            total_views=("views", "max")
        )
        .reset_index()
    )

    # Sort by engagement (comments)
    video_stats = video_stats.sort_values(by="comments_collected", ascending=False)

    video_stats.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Saved stats to {OUTPUT_FILE}")
    print(video_stats.head(5))
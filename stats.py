import pandas as pd

# Load dataset
df = pd.read_csv(r"data\raw\filtered_comments.csv")

# Aggregate statistics per video_url
video_stats = (
    df.groupby(["video_url", "title"])
    .agg(
        comments_collected=("comment", "count"),
        avg_word_count=("word_count", "mean"),
        total_views=("views", "max"),   # assuming views are the same per video
        total_likes=("likes", "max")    # same assumption for likes
    )
    .reset_index()
)

# Sort by number of comments (descending)
video_stats = video_stats.sort_values(by="comments_collected", ascending=False)

# Save results
video_stats.to_csv("video_level_stats.csv", index=False)
print("✅ Saved video-level stats to video_level_stats.csv")
print(video_stats.head(10))

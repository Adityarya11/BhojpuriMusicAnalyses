import os
import json
from urllib.parse import urlparse, parse_qs
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ===============================
# API KEYS (Rotate if quota exceeds)
# ===============================
API_KEYS = [
    "AIzaSyAU4hTIaGNUpuUobVacu_dscYozWj0uYwc",
    "AIzaSyDIdetG-mjqUJlbepdLScJv7kGevpt1KDU"
]

# ===============================
# VIDEO LINKS
# ===============================
VIDEO_LINKS2 = [
    # "https://www.youtube.com/watch?v=rEcdcD25_t8",
    # "https://www.youtube.com/watch?v=OnMDHfUHE8o",
    # "https://www.youtube.com/watch?v=VPoIawaKmyw",
    # "https://www.youtube.com/watch?v=K31XiT17K_c",
    # "https://www.youtube.com/watch?v=FFlHFAKKH50",
    # "https://www.youtube.com/watch?v=9tlP9Z-biX8",
    # "https://www.youtube.com/watch?v=kdDYzDc1JSQ",
    # "https://www.youtube.com/watch?v=qGrYYRRvW6g",
    # "https://www.youtube.com/watch?v=fQfRxUt4W-s",
    # "https://www.youtube.com/watch?v=tzaEeHDrq-o",
    # "https://www.youtube.com/watch?v=ESFAErhnKXM",
    # "https://www.youtube.com/watch?v=GC7l1ic1CrA",
    "https://www.youtube.com/watch?v=xY9_55sFFKc",
    "https://www.youtube.com/watch?v=kbJi_8Cf4oI",
    "https://www.youtube.com/watch?v=h7qFaELHvnE",
    "https://www.youtube.com/watch?v=jbhc4YgN-4U",
    "https://www.youtube.com/watch?v=I4gaPdX3MkM",
    "https://www.youtube.com/watch?v=_rjMNrG5Ris",
    "https://www.youtube.com/watch?v=jCYF-Yh6a8o",
    "https://www.youtube.com/watch?v=G9JN6crCpsI",
    "https://www.youtube.com/watch?v=mm2ttyOEBZ8",
    "https://www.youtube.com/watch?v=x1zIf1Jy6OY",
    "https://www.youtube.com/watch?v=v9z4EZDllOY",
    "https://www.youtube.com/watch?v=5xH9S6tx6aw",
    "https://www.youtube.com/watch?v=bQ9xgVVtmaU",
    "https://www.youtube.com/watch?v=fK6TVFT3m-U",
    "https://www.youtube.com/watch?v=KX9gzRdWWNE",
    "https://www.youtube.com/watch?v=Tq-X62921WY",
    "https://www.youtube.com/watch?v=8c_g9TmgYUQ",
    "https://www.youtube.com/watch?v=3tGnShk9fdg",
    "https://www.youtube.com/watch?v=lH0XF51FW_c",
    "https://www.youtube.com/watch?v=yLsl8cHSVlE",
    "https://www.youtube.com/watch?v=I3kwUdOZQPU",
    "https://www.youtube.com/watch?v=1ZMYnz03wQ8",
    "https://www.youtube.com/watch?v=KjYiyW0PYyY",
    "https://www.youtube.com/watch?v=qJv15TBT_nc",
    "https://www.youtube.com/watch?v=djCiiIqQrkw",
    "https://www.youtube.com/watch?v=2ehlaifi9IE",
    "https://www.youtube.com/watch?v=l-0HTafNGVY",
    "https://www.youtube.com/watch?v=xRw_bdRpAms",
    "https://www.youtube.com/watch?v=yi5eWNosCsc",
    "https://www.youtube.com/watch?v=gMMkJ_PA9pA"
]

# ===============================
# YouTube API Helpers
# ===============================
def get_rotating_youtube_service(api_keys, attempt):
    """Returns a YouTube service object using the API key at the given attempt index."""
    api_key = api_keys[attempt % len(api_keys)]
    return build("youtube", "v3", developerKey=api_key)

def extract_video_id(url):
    """Extracts the video ID from a YouTube URL."""
    query = urlparse(url).query
    params = parse_qs(query)
    return params["v"][0] if "v" in params else None

def get_video_metadata(youtube, video_id):
    """Fetch video metadata."""
    try:
        response = youtube.videos().list(
            part="snippet,statistics",
            id=video_id
        ).execute()

        if not response["items"]:
            return None

        video_info = response["items"][0]
        snippet = video_info["snippet"]
        stats = video_info.get("statistics", {})

        title = snippet.get("title", "Unknown Title")
        channel = snippet.get("channelTitle", "Unknown Channel")
        published_at = snippet.get("publishedAt", "")
        year = published_at.split("-")[0] if published_at else "Unknown Year"
        views = int(stats.get("viewCount", 0))
        likes = int(stats.get("likeCount", 0)) if "likeCount" in stats else None

        # Basic artist/theme extraction (can be improved with NLP)
        artist = None
        theme = None
        if "|" in title:  # Common pattern: Song Name | Artist
            parts = title.split("|")
            artist = parts[-1].strip()
        elif "-" in title:  # Another pattern: Artist - Song Name
            parts = title.split("-")
            artist = parts[0].strip()

        # Very naive theme detection
        if any(word in title.lower() for word in ["love", "romance", "valentine"]):
            theme = "Romantic"
        elif any(word in title.lower() for word in ["holi", "festival", "celebration"]):
            theme = "Festive"
        elif any(word in title.lower() for word in ["sad", "heartbreak", "cry"]):
            theme = "Sad"

        return {
            "title": title,
            "channel": channel,
            "year": year,
            "views": views,
            "likes": likes,
            "artist": artist,
            "theme": theme
        }
    except Exception as e:
        print(f"Could not fetch metadata for {video_id}: {e}")
        return None

def get_video_comments(youtube, video_id, max_results=60000):
    """Fetches comments from a YouTube video."""
    comments = []
    next_page_token = None
    while len(comments) < max_results:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=min(100, max_results - len(comments)),
            pageToken=next_page_token,
            textFormat="plainText"
        )
        response = request.execute()
        for item in response.get("items", []):
            comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comments.append(comment)
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break
    return comments, next_page_token

# ===============================
# Main Script
# ===============================
def main():
    output_dir = "holi"
    os.makedirs(output_dir, exist_ok=True)

    for i, link in enumerate(VIDEO_LINKS2):
        print(f"\nProcessing video {i+1}/{len(VIDEO_LINKS2)}: {link}")
        video_id = extract_video_id(link)
        if not video_id:
            print(f"Invalid video link: {link}")
            continue

        for attempt in range(len(API_KEYS)):
            try:
                youtube = get_rotating_youtube_service(API_KEYS, attempt)
                metadata = get_video_metadata(youtube, video_id)
                if not metadata:
                    print(f"Metadata not found for {video_id}")
                    break

                comments, _ = get_video_comments(youtube, video_id)

                print(f"Fetched {len(comments)} comments for: {metadata['title']}")

                # Save to JSON
                output_data = {
                    "video_id": video_id,
                    "url": link,
                    **metadata,  # merges title, channel, year, views, likes, artist, theme
                    "comments": comments,
                }

                with open(os.path.join(output_dir, f"{video_id}.json"), "w", encoding="utf-8") as f:
                    json.dump(output_data, f, ensure_ascii=False, indent=4)

                break  # success, exit key loop

            except RuntimeError:
                print(f"[{attempt+1}] Quota exceeded. Trying next key...")
            except HttpError as e:
                print(f"[{attempt+1}] HTTP Error for {link}: {e}")
                break
            except Exception as e:
                print(f"[{attempt+1}] Failed to process {link}: {e}")
                break

if __name__ == "__main__":
    main()

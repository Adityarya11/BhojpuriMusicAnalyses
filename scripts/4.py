"""
local_cleaning.py
Task 3 & Task 4 for Holi Analysis:
- Full text cleaning (emojis, stopwords, scripts, code-mix, duplicates)
- Random 100k comment subset for Colab
"""

import pandas as pd
import re
import emoji
import random
import os
import string
import langdetect
from nltk.corpus import stopwords
import nltk

# ---------------------------------
# Config
# ---------------------------------
RAW_FILE = r"data\raw\filtered_comments.csv"
CLEAN_FILE = r"data\clean\clean_bhojpuri.csv"
SAMPLE_FILE = r"data\clean\bhojpuri_sample.csv"
SAMPLE_SIZE = 200_000
SEED = 42

# ---------------------------------
# Setup
# ---------------------------------
nltk.download("stopwords")
stopwords_en = set(stopwords.words("english"))
stopwords_hi = {
    "है", "थे", "था", "हूं", "हो", "की", "के", "का", "में", "पर", "से", "को",
    "और", "या", "नहीं", "तो", "ही", "था", "थी", "थे", "था", "वे", "यह", "ये",
    "उस", "उन", "इस", "इन", "आप", "हम", "तुम", "तुम्हारा", "मेरा", "मेरी", "मेरे",
    "था", "थी", "थे", "थी", "था", "था"
}

os.makedirs("../data/clean", exist_ok=True)

# ---------------------------------
# Helper Functions
# ---------------------------------
def count_emojis(text):
    return sum(1 for char in text if char in emoji.EMOJI_DATA)

def remove_emojis(text):
    return emoji.replace_emoji(text, replace="")

def detect_script(text):
    devanagari_pattern = re.compile(r'[\u0900-\u097F]')
    latin_pattern = re.compile(r'[A-Za-z]')
    has_dev = bool(devanagari_pattern.search(text))
    has_lat = bool(latin_pattern.search(text))
    if has_dev and has_lat:
        return "Mixed"
    elif has_dev:
        return "Devanagari"
    elif has_lat:
        return "Latin"
    return "Other"

def code_mix_ratio(text):
    words = text.split()
    if not words:
        return 0.0
    en_count = sum(1 for w in words if re.search(r'[A-Za-z]', w))
    return round(en_count / len(words), 3)

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)  # URLs
    text = re.sub(r"@\w+", "", text)  # mentions
    text = re.sub(r"\S+@\S+\.\S+", "", text)  # emails
    text = remove_emojis(text)
    text = re.sub(rf"[{string.punctuation}]", " ", text)  # punctuation
    text = re.sub(r"\s+", " ", text).strip()  # extra spaces
    tokens = [w for w in text.split() if w not in stopwords_en and w not in stopwords_hi]
    return " ".join(tokens)

# ---------------------------------
# Main
# ---------------------------------
print("📥 Reading raw file...")
df = pd.read_csv(RAW_FILE)

print(f"Initial rows: {len(df)}")

# Drop NAs in comment
df = df.dropna(subset=["comment"]).reset_index(drop=True)

# Emoji count
df["emoji_count"] = df["comment"].apply(count_emojis)

# Script detection
df["script_flag"] = df["comment"].apply(detect_script)

# Code-mix ratio
df["code_mix_ratio"] = df["comment"].apply(code_mix_ratio)

# Clean text
df["cleaned_comment"] = df["comment"].apply(clean_text)

# Drop short comments (<3 tokens)
df = df[df["cleaned_comment"].str.split().str.len() >= 3]

# Remove duplicates
df = df.drop_duplicates(subset=["cleaned_comment"])

print(f"✅ After cleaning: {len(df)} rows")

# Save cleaned full dataset
df.to_csv(CLEAN_FILE, index=False, encoding="utf-8")
print(f"💾 Saved cleaned file to {CLEAN_FILE}")

# Random 100k sample (stratified by video_id if possible)
if "video_id" in df.columns:
    sample_df = (
        df.groupby("video_id", group_keys=False)
        .apply(lambda x: x.sample(min(len(x), SAMPLE_SIZE // df["video_id"].nunique()), random_state=SEED))
    )
else:
    sample_df = df.sample(n=min(SAMPLE_SIZE, len(df)), random_state=SEED)

sample_df.to_csv(SAMPLE_FILE, index=False, encoding="utf-8")
print(f"💾 Saved sample file ({len(sample_df)} rows) to {SAMPLE_FILE}")
print("🎯 Done!")
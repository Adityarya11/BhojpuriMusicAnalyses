"""
04_nlp_preprocessing.py
Purpose: Advanced cleaning for NLP tasks.
- Removes emojis and stopwords.
- Detects language script (Hindi vs English).
- Prepares data for the Machine Learning model.
"""

import pandas as pd
import re
import emoji
import os
import string
from nltk.corpus import stopwords
import nltk

# Download NLTK resources (Run this once)
nltk.download("stopwords")

# Paths
RAW_FILE = os.path.join("data", "raw", "filtered_comments.csv")
CLEAN_FILE = os.path.join("data", "clean", "clean_bhojpuri.csv")

# Define Stopwords (Words to remove like "is", "the", "hai", "ka")
STOPWORDS_EN = set(stopwords.words("english"))
STOPWORDS_HI = {
    "है", "थे", "था", "हूं", "हो", "की", "के", "का", "में", "पर", "से", "को",
    "और", "या", "नहीं", "तो", "ही", "वे", "यह", "ये", "उस", "उन", "इस", "इन"
}

def clean_comment_text(text):
    """
    Applies the full NLP cleaning pipeline to a single string.
    """
    text = str(text).lower()
    
    # 1. Remove URLs and Handles
    text = re.sub(r"http\S+|www\S+|https\S+", "", text) 
    text = re.sub(r"@\w+", "", text)
    
    # 2. Remove Emojis (They add noise to simple text models)
    text = emoji.replace_emoji(text, replace="")
    
    # 3. Remove Punctuation
    text = re.sub(rf"[{string.punctuation}]", " ", text)
    
    # 4. Remove Stopwords
    tokens = text.split()
    tokens = [w for w in tokens if w not in STOPWORDS_EN and w not in STOPWORDS_HI]
    
    return " ".join(tokens)

if __name__ == "__main__":
    print("Reading data...")
    df = pd.read_csv(RAW_FILE)

    # Apply Cleaning
    print("Cleaning text...")
    df["cleaned_comment"] = df["comment"].apply(clean_comment_text)

    # Filter: Remove rows that became empty after cleaning
    df = df[df["cleaned_comment"].str.len() > 2]
    
    # Remove duplicates
    df = df.drop_duplicates(subset=["cleaned_comment"])

    # Save
    os.makedirs(os.path.dirname(CLEAN_FILE), exist_ok=True)
    df.to_csv(CLEAN_FILE, index=False, encoding="utf-8")
    print(f"✅ Saved clean data to {CLEAN_FILE}")
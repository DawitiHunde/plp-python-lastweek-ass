# cord19_explorer.py
# Complete pipeline: load, clean, analyze, visualize. Well-commented.

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns    # optional, for nicer default plots
from collections import Counter
import re

# Optional imports for wordcloud and text processing
try:
    from wordcloud import WordCloud
    import nltk
    nltk.download('stopwords', quiet=True)
    from nltk.corpus import stopwords
    STOPWORDS = set(stopwords.words('english'))
    WORDCLOUD_AVAILABLE = True
except Exception:
    WORDCLOUD_AVAILABLE = False
    STOPWORDS = set()

# ---------- CONFIG ----------
DATA_PATH = "metadata.csv"           # path to the downloaded metadata.csv
SAMPLE_IF_LARGE = True               # if True and file > sample_rows_threshold, sample
sample_rows_threshold = 5_000_000    # if file has more rows than this, we'll sample
SAMPLE_SIZE = 200_000                # sample size if sampling
CHUNKSIZE = 200_000                  # used for chunked reading when needed
# ----------------------------

# ----------  Part 1: Load & Basic Exploration ----------
def load_metadata(path=DATA_PATH, use_sampling=True):
    """Load metadata.csv with safety for very large files.
    Returns a pandas DataFrame (possibly sampled).
    """
    # 1) Check file exists
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}. Put metadata.csv at this path or update DATA_PATH.")

    # 2) Get estimated number of lines (fast)
    total_lines = None
    try:
        with open(path, 'rb') as f:
            total_lines = sum(1 for _ in f)
    except Exception:
        total_lines = None

    # 3) If file seems large and sampling enabled, sample by reading in chunks
    if use_sampling and total_lines is not None and total_lines > sample_rows_threshold:
        print(f"Large file detected (~{total_lines} lines). Loading a random sample of {SAMPLE_SIZE} rows using chunks.")
        # read in chunks, randomly sample from each chunk
        rng = np.random.default_rng(42)
        sampled_parts = []
        for chunk in pd.read_csv(path, chunksize=CHUNKSIZE, dtype=str, low_memory=False):
            # sample a fraction of the chunk
            frac = SAMPLE_SIZE / total_lines
            frac = min(max(frac, 0.0001), 1.0)
            # sample rows (approx)
            chunk_sample = chunk.sample(frac=frac, random_state=rng.integers(1_000_000)) if frac < 1 else chunk
            sampled_parts.append(chunk_sample)
            # break early if we've collected enough
            if sum(len(p) for p in sampled_parts) >= SAMPLE_SIZE:
                break
        df = pd.concat(sampled_parts, ignore_index=True)
        # if too many rows, downsample to exact size
        if len(df) > SAMPLE_SIZE:
            df = df.sample(n=SAMPLE_SIZE, random_state=42).reset_index(drop=True)
    else:
        # safe full read
        df = pd.read_csv(path, dtype=str, low_memory=False)
    print(f"Loaded DataFrame with shape: {df.shape}")
    return df

# Run load
df = load_metadata(DATA_PATH, use_sampling=SAMPLE_IF_LARGE)

# Peek at data
print("\nFirst 5 rows:")
display(df.head())

print("\nDataFrame info:")
print(df.info())

print("\nColumns:")
print(df.columns.tolist())

# Basic dimension
print(f"\nRows: {df.shape[0]}, Columns: {df.shape[1]}")

# Data types & missing values (important columns)
print("\nMissing value counts (top columns):")
important_cols = ['cord_uid','title','doi','publish_time','journal','abstract','pdf_json_files','pmcid','pmid']
for c in important_cols:
    if c in df.columns:
        print(f"{c}: {df[c].isnull().sum()} / {len(df)} missing")

# numeric summary (if any numeric columns exist)
print("\nNumeric columns summary (if present):")
num_cols = df.select_dtypes(include=['int64','float64']).columns.tolist()
if num_cols:
    print(df[num_cols].describe())
else:
    print("No numeric columns detected in this csv by dtype.")

# ---------- Part 2: Cleaning & Preparation ----------
# 1) Convert publish_time to datetime if present
if 'publish_time' in df.columns:
    # create a cleaned publish_time column with robust parsing
    df['publish_time_raw'] = df['publish_time']  # keep original
    df['publish_time'] = pd.to_datetime(df['publish_time'], errors='coerce', dayfirst=False)
    print(f"Converted publish_time; nulls after parsing: {df['publish_time'].isna().sum()}")
    # extract year
    df['year'] = df['publish_time'].dt.year
else:
    print("No publish_time column found; skipping date conversion.")
    df['year'] = np.nan

# 2) Create abstract word count column (if abstract exists)
if 'abstract' in df.columns:
    def count_words(text):
        if pd.isnull(text):
            return 0
        # some abstracts are lists or JSON strings; coerce to str
        s = str(text)
        s = re.sub(r'\s+', ' ', s).strip()
        if not s:
            return 0
        return len(s.split())
    df['abstract_word_count'] = df['abstract'].apply(count_words)
    print("Added abstract_word_count.")
else:
    df['abstract_word_count'] = 0

# 3) Identify columns with many missing values (report)
missing_pct = (df.isnull().sum() / len(df)).sort_values(ascending=False)
print("\nColumns sorted by missing % (top 20):")
print(missing_pct.head(20))

# Strategy: drop columns > 90% missing (example threshold)
high_missing_cols = missing_pct[missing_pct > 0.90].index.tolist()
print("\nColumns with >90% missing (will be dropped):", high_missing_cols)
df_clean = df.drop(columns=high_missing_cols)

# Optionally drop rows with no title and no abstract and no publish_time (unhelpful rows)
rows_before = len(df_clean)
df_clean = df_clean[~(df_clean.get('title', '').fillna('').str.strip().eq('') &
                      df_clean.get('abstract', '').fillna('').str.strip().eq('') &
                      df_clean.get('publish_time').isna())]
rows_after = len(df_clean)
print(f"Dropped {rows_before - rows_after} rows with no title & no abstract & no publish_time.")

# Fill some missing fields with placeholders where useful
if 'journal' in df_clean.columns:
    df_clean['journal'] = df_clean['journal'].fillna('Unknown Journal')

# ---------- Part 3: Analysis & Visualizations ----------
# 3.1 Count papers by publication year
year_counts = df_clean['year'].value_counts(dropna=True).sort_index()
print("\nPapers by year (sample):")
print(year_counts.head(20))

# Plot publications over time
plt.figure(figsize=(10,5))
year_counts.plot(kind='bar')
plt.title('Publications by Year')
plt.xlabel('Year')
plt.ylabel('Number of publications')
plt.tight_layout()
plt.show()

# 3.2 Top journals
if 'journal' in df_clean.columns:
    top_journals = df_clean['journal'].value_counts().head(20)
    plt.figure(figsize=(10,6))
    top_journals.sort_values().plot(kind='barh')
    plt.title('Top 20 Journals by Number of Papers')
    plt.xlabel('Count')
    plt.tight_layout()
    plt.show()
else:
    top_journals = pd.Series(dtype=int)

# 3.3 Most frequent words in titles (simple tokenization)
def tokenize_title(title):
    if pd.isnull(title):
        return []
    # lowercase, remove punctuation, split
    s = re.sub(r'[^a-zA-Z0-9\s]', ' ', str(title).lower())
    words = [w for w in s.split() if len(w) > 2]  # drop very short words
    return words

all_title_words = []
if 'title' in df_clean.columns:
    for t in df_clean['title'].dropna().astype(str):
        all_title_words.extend([w for w in tokenize_title(t) if w not in STOPWORDS])
    wc = Counter(all_title_words)
    top_words = wc.most_common(30)
    print("\nTop words in titles (top 30):")
    print(top_words)
    # bar plot of top 20
    top20 = top_words[:20]
    words, counts = zip(*top20)
    plt.figure(figsize=(10,6))
    plt.barh(words[::-1], counts[::-1])
    plt.title('Top words in titles (excl. stopwords)')
    plt.tight_layout()
    plt.show()
else:
    top_words = []

# 3.4 Wordcloud (optional)
if WORDCLOUD_AVAILABLE and len(all_title_words) > 0:
    wc_text = " ".join(all_title_words)
    w = WordCloud(width=800, height=400, background_color='white', stopwords=STOPWORDS).generate(wc_text)
    plt.figure(figsize=(12,6))
    plt.imshow(w, interpolation='bilinear')
    plt.axis('off')
    plt.title('Word Cloud of Title Words')
    plt.show()
else:
    print("WordCloud not available or no title words found. To enable, install 'wordcloud' and 'nltk' packages.")

# 3.5 Distribution of paper counts by source (if 'source_x' or similar exists)
possible_source_cols = [c for c in df_clean.columns if 'source' in c.lower() or 'source_x' in c.lower()]
if possible_source_cols:
    src_col = possible_source_cols[0]
    print(f"Using {src_col} for source distribution:")
    src_counts = df_clean[src_col].value_counts().head(20)
    plt.figure(figsize=(10,6))
    src_counts.sort_values().plot(kind='barh')
    plt.title(f'Top sources ({src_col})')
    plt.tight_layout()
    plt.show()
else:
    print("No obvious 'source' column found. Skip source distribution.")

# ---------- Part 4: Save a small cleaned CSV for the Streamlit app ----------
clean_out_path = "metadata_clean_sample.csv"
df_clean.to_csv(clean_out_path, index=False)
print(f"Saved cleaned sample to {clean_out_path}. Use this file for the Streamlit app.")

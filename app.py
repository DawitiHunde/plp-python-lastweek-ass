# app.py - Streamlit app for CORD-19 Data Explorer
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="CORD-19 Data Explorer", layout='wide')

@st.cache_data
def load_data(path='metadata_clean_sample.csv'):
    return pd.read_csv(path, low_memory=False)

st.title("CORD-19 Data Explorer")
st.write("Simple exploration of COVID-19 research metadata (sample).")

# Load
with st.spinner("Loading data..."):
    df = load_data()

# Sidebar controls
st.sidebar.header("Filters")
min_year = int(pd.to_datetime(df['publish_time'], errors='coerce').dt.year.min(skipna=True) or 2019)
max_year = int(pd.to_datetime(df['publish_time'], errors='coerce').dt.year.max(skipna=True) or 2022)
year_range = st.sidebar.slider("Select year range", min_year, max_year, (min_year, max_year))

journal_options = ['All'] + sorted(df['journal'].dropna().unique().tolist())[:200]  # limit for dropdown
journal_sel = st.sidebar.selectbox("Journal (top 200 unique)", journal_options)

# Filter data
df['publish_time_dt'] = pd.to_datetime(df['publish_time'], errors='coerce')
df['year'] = df['publish_time_dt'].dt.year
yr_low, yr_high = year_range
df_filtered = df[(df['year'] >= yr_low) & (df['year'] <= yr_high)]
if journal_sel != 'All':
    df_filtered = df_filtered[df_filtered['journal'] == journal_sel]

st.sidebar.markdown(f"Rows after filter: {len(df_filtered)}")

# Main layout
col1, col2 = st.columns([2,1])
with col1:
    st.header("Publications by Year")
    year_counts = df_filtered['year'].value_counts().sort_index()
    fig1, ax1 = plt.subplots(figsize=(8,3))
    ax1.bar(year_counts.index.astype('Int64').astype(int), year_counts.values)
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Count")
    st.pyplot(fig1)

    st.header("Top Journals (filtered)")
    top_j = df_filtered['journal'].value_counts().head(15)
    fig2, ax2 = plt.subplots(figsize=(6,4))
    ax2.barh(top_j.index[::-1], top_j.values[::-1])
    st.pyplot(fig2)

with col2:
    st.header("Sample records")
    st.dataframe(df_filtered[['cord_uid','title','publish_time','journal','abstract_word_count']].head(50))

st.write("Download filtered sample:")
st.download_button("Download CSV", df_filtered.to_csv(index=False).encode('utf-8'), "cord19_filtered.csv", "text/csv")

st.markdown("---")
st.write("Notes: This is a simple Streamlit app. Add more visualizations or interactivity as needed.")

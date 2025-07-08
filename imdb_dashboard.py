import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json

# 🎬 Title
st.title("IMDb 2024 Movies Dashboard")

# 📥 Load the CSV
df = pd.read_csv("IMDb_2024_Merged.csv")

# ✅ SAFELY parse GenreMain column
import json

def parse_genre(val):
    if pd.isna(val):
        return []
    try:
        if isinstance(val, list):
            return val
        elif isinstance(val, str) and val.startswith("["):
            return json.loads(val.replace("'", '"'))  # safer than ast
        else:
            return [val]
    except Exception as e:
        return []

df['GenreMain'] = df['GenreMain'].apply(parse_genre)

# 🧼 Clean numeric columns
df['Votes'] = pd.to_numeric(df['Votes'].astype(str).str.replace(",", ""), errors='coerce')
df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')

# 🎛️ Sidebar Filters
st.sidebar.header("🎯 Filter Movies")

# 🎭 Genre filter
all_genres = sorted({g for sub in df['GenreMain'] for g in sub if isinstance(g, str)})
selected_genre = st.sidebar.selectbox("Select Genre", ["All"] + all_genres)

# 🔢 Votes filter
min_votes = int(df['Votes'].min()) if df['Votes'].notna().any() else 0
max_votes = int(df['Votes'].max()) if df['Votes'].notna().any() else 100000
vote_threshold = st.sidebar.slider("Minimum Number of Votes", min_votes, max_votes, 1000)

# 🎯 Filter dataset
filtered_df = df[df['Votes'] >= vote_threshold]
if selected_genre != "All":
    filtered_df = filtered_df[filtered_df['GenreMain'].apply(lambda genres: selected_genre in genres)]

# 📊 Display filtered results
st.markdown(f"### Showing {len(filtered_df)} movies in '{selected_genre}' genre with at least {vote_threshold} votes")
st.dataframe(filtered_df[['Title', 'GenreMain', 'Rating', 'Votes', 'Duration']])

# 📈 Rating distribution
if not filtered_df['Rating'].dropna().empty:
    fig, ax = plt.subplots()
    ax.hist(filtered_df['Rating'].dropna(), bins=20, color='skyblue', edgecolor='black')
    ax.set_title("IMDb Ratings Distribution")
    ax.set_xlabel("Rating")
    ax.set_ylabel("Number of Movies")
    st.pyplot(fig)
else:
    st.warning("No ratings available to display the distribution.")

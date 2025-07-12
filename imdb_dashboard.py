import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import re

# Streamlit page configuration
st.set_page_config(
    page_title="IMDb 2024 Movies Dashboard",
    layout="wide",
    page_icon="🎬"
)

st.title("🎬 IMDb 2024 Movies Dashboard")

df = pd.read_csv("IMDb_2024_Merged.csv")

# Clean Votes column to be numeric
df['Votes'] = df['Votes'].str.replace(r"[(),KkMm]", "", regex=True)
df['Votes'] = pd.to_numeric(df['Votes'], errors='coerce')

# Convert Duration to numeric minutes
def convert_duration(duration_str):
    if pd.isna(duration_str):
        return None
    match = re.match(r'(?:(\d+)h)?\s*(?:(\d+)m)?', duration_str.strip())
    if match:
        hours = int(match.group(1)) if match.group(1) else 0
        minutes = int(match.group(2)) if match.group(2) else 0
        return hours * 60 + minutes
    return None

df['DurationMinutes'] = df['Duration'].apply(convert_duration)

# Sidebar filters
with st.sidebar:
    st.header("Filter Options")
    genres = df['Genre'].unique().tolist()
    selected_genre = st.selectbox("Select Genre", ["All"] + genres, key='genre_filter')
    min_rating, max_rating = float(df['Rating'].min()), float(df['Rating'].max())
    selected_rating = st.slider("Minimum Rating", min_rating, max_rating, min_rating, key='rating_filter')
    min_votes, max_votes = int(df['Votes'].min()), int(df['Votes'].max())
    vote_threshold = st.slider("Minimum Votes", min_votes, max_votes, 1000, key='votes_filter')
    duration_category = st.selectbox("Duration", ["All", "< 2 hours", "2 - 3 hours", "> 3 hours"], key='duration_filter')
    show_correlation = st.checkbox("Show Correlation: Ratings vs Votes")

# Apply filters
filtered_df = df.copy()
if selected_genre != "All":
    filtered_df = filtered_df[filtered_df['Genre'] == selected_genre]
filtered_df = filtered_df[filtered_df['Rating'] >= selected_rating]
filtered_df = filtered_df[filtered_df['Votes'] >= vote_threshold]
if duration_category == "< 2 hours":
    filtered_df = filtered_df[filtered_df['DurationMinutes'] < 120]
elif duration_category == "2 - 3 hours":
    filtered_df = filtered_df[(filtered_df['DurationMinutes'] >= 120) & (filtered_df['DurationMinutes'] <= 180)]
elif duration_category == "> 3 hours":
    filtered_df = filtered_df[filtered_df['DurationMinutes'] > 180]

# Display filtered data
st.write(f"Showing {len(filtered_df)} movies with filters applied")
st.dataframe(filtered_df[['Title', 'Genre', 'Rating', 'Votes', 'Duration']])

# Rating Distribution
st.subheader("Rating Distribution")
if not filtered_df['Rating'].dropna().empty:
    fig, ax = plt.subplots()
    ax.hist(filtered_df['Rating'].dropna(), bins=10, color='orange', edgecolor='black')
    ax.set_xlabel("Rating")
    ax.set_ylabel("Number of Movies")
    ax.set_title("IMDb Ratings")
    st.pyplot(fig)
else:
    st.warning("No ratings to display.")

# Genre Distribution
st.subheader("Genre Distribution")
genre_counts = filtered_df['Genre'].value_counts()
if not genre_counts.empty:
    fig2, ax2 = plt.subplots()
    genre_counts.plot(kind='bar', color='skyblue', edgecolor='black', ax=ax2)
    ax2.set_xlabel("Genre")
    ax2.set_ylabel("Number of Movies")
    ax2.set_title("Number of Movies per Genre")
    st.pyplot(fig2)
else:
    st.warning("No genre data to display.")

# Average Duration by Genre
st.subheader("Average Duration by Genre")
avg_duration = filtered_df.groupby('Genre')['DurationMinutes'].mean().sort_values()
if not avg_duration.empty:
    fig3, ax3 = plt.subplots()
    avg_duration.plot(kind='barh', color='lightgreen', edgecolor='black', ax=ax3)
    ax3.set_xlabel("Average Duration (minutes)")
    ax3.set_ylabel("Genre")
    ax3.set_title("Average Movie Duration by Genre")
    st.pyplot(fig3)
else:
    st.warning("No duration data to display.")

# Average Votes by Genre
st.subheader("Average Votes by Genre")
avg_votes = filtered_df.groupby('Genre')['Votes'].mean().sort_values()
if not avg_votes.empty:
    fig4, ax4 = plt.subplots()
    avg_votes.plot(kind='bar', color='lightblue', edgecolor='black', ax=ax4)
    ax4.set_xlabel("Genre")
    ax4.set_ylabel("Average Votes")
    ax4.set_title("Average Number of Votes by Genre")
    plt.xticks(rotation=45)
    st.pyplot(fig4)
else:
    st.warning("No vote data available to show.")

# Top 10 Highest Rated Movies
st.subheader("Top 10 Highest Rated Movies")
top_rated = filtered_df.dropna(subset=['Rating']).sort_values(by=['Rating', 'Votes'], ascending=False).head(10)
if not top_rated.empty:
    st.dataframe(top_rated[['Title', 'Genre', 'Rating', 'Votes', 'Duration']])
else:
    st.warning("No top-rated movies to display.")

# Most Popular Genres by Total Votes
st.subheader("Most Popular Genres by Total Votes")
genre_votes = filtered_df.groupby('Genre')['Votes'].sum().sort_values(ascending=False)
if not genre_votes.empty:
    fig4, ax4 = plt.subplots()
    genre_votes.plot(kind='pie', autopct='%1.1f%%', startangle=140, ax=ax4)
    ax4.set_ylabel("")
    ax4.set_title("Total Votes by Genre")
    st.pyplot(fig4)
else:
    st.warning("No vote data available to show genre popularity.")

# Top-Rated Movie by Genre
st.subheader("Top-Rated Movie by Genre")
top_rated = filtered_df.sort_values(['Genre', 'Rating'], ascending=[True, False])
top_movies = top_rated.drop_duplicates(subset='Genre', keep='first')
if not top_movies.empty:
    st.dataframe(top_movies[['Title', 'Genre', 'Rating', 'Votes', 'Duration']].sort_values(by='Rating', ascending=False))
else:
    st.warning("No data to display top-rated movies.")

# Shortest and Longest Movies
st.sidebar.markdown("---")
show_extremes = st.sidebar.checkbox("Show Shortest and Longest Movies")
if show_extremes:
    st.subheader("Shortest and Longest Movies")
    duration_df = filtered_df.dropna(subset=['DurationMinutes'])
    if not duration_df.empty:
        shortest_movie = duration_df.loc[duration_df['DurationMinutes'].idxmin()]
        longest_movie = duration_df.loc[duration_df['DurationMinutes'].idxmax()]
        st.markdown("**Shortest Movie:**")
        st.write(shortest_movie[['Title', 'Genre', 'Duration', 'Rating', 'Votes']])
        st.markdown("**Longest Movie:**")
        st.write(longest_movie[['Title', 'Genre', 'Duration', 'Rating', 'Votes']])
    else:
        st.warning("No data available for movie duration.")

# Rating Distribution by Genre
st.sidebar.markdown("---")
show_rating_dist = st.sidebar.checkbox("Show Rating Distribution by Genre")
if show_rating_dist:
    st.subheader("Rating Distribution by Genre (All Movies)")
    boxplot_data = df.dropna(subset=['Rating', 'Genre'])
    if not boxplot_data.empty:
        fig5, ax5 = plt.subplots(figsize=(10, 6))
        boxplot_data.boxplot(column='Rating', by='Genre', ax=ax5, grid=False)
        plt.xticks(rotation=45)
        ax5.set_title("Rating Distribution by Genre")
        ax5.set_xlabel("Genre")
        ax5.set_ylabel("Rating")
        st.pyplot(fig5)
    else:
        st.warning("No rating data available for genre-wise comparison.")

# Top-Rated Movie per Genre
st.sidebar.markdown("---")
show_top_per_genre = st.sidebar.checkbox("Show Top-Rated Movie per Genre")
if show_top_per_genre:
    st.subheader("Top-Rated Movie in Each Genre (All Movies)")
    top_movies = df.dropna(subset=['Genre', 'Rating'])
    top_movies = top_movies.sort_values(['Genre', 'Rating'], ascending=[True, False])
    top_per_genre = top_movies.groupby('Genre').first().reset_index()
    st.dataframe(top_per_genre[['Genre', 'Title', 'Rating', 'Votes', 'Duration']])

# Most Popular Genres by Voting (Pie Chart)
st.sidebar.markdown("---")
show_popular_genres = st.sidebar.checkbox("Show Most Popular Genres by Voting")
if show_popular_genres:
    st.subheader("Most Popular Genres by Total Votes")
    vote_data = df.dropna(subset=['Votes', 'Genre'])
    vote_data = vote_data[vote_data['Votes'] >= 0]
    genre_votes = vote_data.groupby('Genre')['Votes'].sum().sort_values(ascending=False)
    if not genre_votes.empty:
        fig5, ax5 = plt.subplots()
        ax5.pie(genre_votes, labels=genre_votes.index, autopct='%1.1f%%', startangle=140)
        ax5.set_title("Genres by Total Votes")
        ax5.axis("equal")
        st.pyplot(fig5)
    else:
        st.warning("Not enough valid vote data to show genre popularity.")

# Correlation: Rating vs Votes
if show_correlation:
    st.subheader("Correlation between Ratings and Votes")
    correlation_df = filtered_df.dropna(subset=['Rating', 'Votes'])
    if not correlation_df.empty:
        fig6, ax6 = plt.subplots()
        ax6.scatter(correlation_df['Rating'], correlation_df['Votes'], alpha=0.5, color='purple')
        ax6.set_xlabel("Rating")
        ax6.set_ylabel("Votes")
        ax6.set_title("Ratings vs. Votes")
        st.pyplot(fig6)
    else:
        st.warning("Not enough data for correlation analysis.")

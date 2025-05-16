import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

# Database Connection
engine = create_engine("mysql+mysqlconnector://root:admin@localhost/pvnc")

st.set_page_config(page_title="🎾 Tennis Competitor Dashboard", layout="wide")
st.title("🎾 Tennis Competitor Analytics")

# Load Data
@st.cache_data

def load_data():
    query = """
        SELECT c.name, c.country, c.country_code, c.abbreviation, 
               r.rank, r.movement, r.points, r.competitions_played
        FROM Competitors c
        JOIN Competitor_Rankings r ON c.competitor_id = r.competitor_id
    """
    return pd.read_sql(query, con=engine)

# DataFrame
df = load_data()

# --- 1. Homepage Summary Dashboard ---
st.subheader("🏠 Summary Dashboard")
col1, col2, col3 = st.columns(3)
col1.metric("Total Competitors", df.shape[0])
col2.metric("Countries Represented", df['country'].nunique())
col3.metric("Highest Points", df['points'].max())

# --- 2. Search and Filter Competitors ---
st.subheader("🔍 Search & Filter Competitors")

# Filters
name_filter = st.text_input("Search by Name")
rank_range = st.slider("Rank Range", 1, 100, (1, 20))
points_threshold = st.slider("Minimum Points", 0, int(df['points'].max()), 1000)
country_filter = st.multiselect("Filter by Country", options=df['country'].unique())

# Apply filters
filtered_df = df[
    (df['rank'] >= rank_range[0]) &
    (df['rank'] <= rank_range[1]) &
    (df['points'] >= points_threshold)
]
if name_filter:
    filtered_df = filtered_df[filtered_df['name'].str.contains(name_filter, case=False)]
if country_filter:
    filtered_df = filtered_df[filtered_df['country'].isin(country_filter)]

st.dataframe(filtered_df.reset_index(drop=True))

# --- 3. Competitor Details Viewer ---
st.subheader("👤 Competitor Details Viewer")
selected_player = st.selectbox("Select Competitor", df['name'].unique())
player = df[df['name'] == selected_player].iloc[0]
st.markdown(f"**Name:** {player['name']}")
st.markdown(f"**Rank:** {player['rank']}")
st.markdown(f"**Movement:** {player['movement']}")
st.markdown(f"**Points:** {player['points']}")
st.markdown(f"**Competitions Played:** {player['competitions_played']}")
st.markdown(f"**Country:** {player['country']}")

# --- 4. Country-Wise Analysis ---
st.subheader("🌍 Country-Wise Analysis")
country_stats = df.groupby("country").agg(
    total_competitors=pd.NamedAgg(column="name", aggfunc="count"),
    avg_points=pd.NamedAgg(column="points", aggfunc="mean")
).reset_index()
st.dataframe(country_stats)

fig1 = px.bar(country_stats, x="country", y="total_competitors", title="Total Competitors per Country")
fig2 = px.scatter(country_stats, x="country", y="avg_points", size="total_competitors", title="Average Points by Country")

st.plotly_chart(fig1)
st.plotly_chart(fig2)

# --- 5. Leaderboards ---
st.subheader("🏆 Leaderboards")
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Top 10 by Rank**")
    top_rank = df.nsmallest(10, "rank")
    st.dataframe(top_rank[["name", "rank", "country"]])

with col2:
    st.markdown("**Top 10 by Points**")
    top_points = df.nlargest(10, "points")
    st.dataframe(top_points[["name", "points", "country"]])
import pandas as pd
import streamlit as st

from utils.data import load_data, load_column_config
from utils.date import get_year

st.set_page_config(page_title = "Movies Manager", page_icon=":movie_camera:", layout="wide")

# df = pd.read_csv('test.csv')
base_df = load_data()
df = base_df.copy()


# First bar
seach_bar, year_bar, watched_date_bar, status_bar = st.columns(
    [0.3, 0.2, 0.2, 0.3], vertical_alignment="center"
)

name = seach_bar.text_input('Search movie')
if name:
    df = df[df['name'].str.contains(name, case=False, na=False)]

years = base_df['year'].dropna().astype(int).unique().tolist()
years = sorted(years, reverse=True)
selected_year = year_bar.selectbox('Year', options=years, help='Filter movies by year', index=None,)
if selected_year:
    df = df[df['year'] == selected_year]

watched_years = (
    base_df['watched_date']
    .dropna()
    .apply(get_year)
    .unique()
    .tolist()
)
watched_years = sorted(watched_years, reverse=True)
selected_watched_year = watched_date_bar.selectbox(
    'Watched year', options=watched_years, 
    help='Filter movies by watched year', index=None,
)
if selected_watched_year:
    df = df[df['watched_date'].apply(
        lambda date: str(date).startswith(str(selected_watched_year))
    )]

selected_status = status_bar.segmented_control(
    'Status', ['waiting', 'completed', 'dropped'], 
    selection_mode='single',
    # selection_mode='multi'
)
if selected_status:
    df = df[df['status'] == selected_status]

# Second bar
genre_bar, type_bar, country_bar = st.columns([0.5, 0.25, 0.25], vertical_alignment="center")
genres = (
    base_df['genres']
    .dropna()
    .apply(lambda x: [g.strip() for g in x.split(',')])
    .explode()  # flatten lists into rows
    .unique()
    .tolist()
)
genres = sorted(genres)
selected_genres = genre_bar.multiselect(
    'Genres', genres,
    help='Filter by genres'
)
if selected_genres:
    df = df[df['genres'].apply(
        lambda genres: all(genre in str(genres) for genre in selected_genres)
    )]

types = sorted(base_df['type'].unique().tolist())
selected_type = type_bar.selectbox('Type', options=types, index=None,)
if selected_type:
    df = df[df['type'] == selected_type]

countries = sorted(base_df['country'].dropna().unique().tolist())
selected_country = country_bar.selectbox('Country', options=countries, index=None,)
# if not df.empty and selected_country:
if selected_country:
    df = df[df['country'] == selected_country]

# Dataframe
st.dataframe(df, column_config=load_column_config(), hide_index=True)
st.write(f'Total: {df.shape[0]}')
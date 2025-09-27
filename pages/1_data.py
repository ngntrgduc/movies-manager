import streamlit as st
import pandas as pd

from utils.data import load_data, load_column_config
from utils.date import get_year

st.set_page_config(page_title = 'Movies Manager', page_icon=':movie_camera:', layout='wide')

df = load_data()

# First bar
seach_bar, year_bar, watched_date_bar, status_bar = st.columns(
    [0.3, 0.2, 0.2, 0.3], vertical_alignment='center'
)
name = seach_bar.text_input('Search movie')
years = df['year'].dropna().astype(int).unique().tolist()
years = sorted(years, reverse=True)
selected_year = year_bar.selectbox('Year', options=years, help='Filter movies by year', index=None)
watched_years = (
    df['watched_date']
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
selected_status = status_bar.segmented_control(
    'Status', ['waiting', 'completed', 'dropped'], selection_mode='single'
)


# Second bar
genre_bar, type_bar, country_bar = st.columns([0.5, 0.25, 0.25], vertical_alignment='center')
genres = (
    df['genres']
    .dropna()
    .apply(lambda x: [g.strip() for g in x.split(',')])
    .explode()  # flatten lists into rows
    .unique()
    .tolist()
)
genres = sorted(genres)
selected_genres = genre_bar.multiselect('Genres', genres, help='Filter by genres')

types = sorted(df['type'].unique().tolist())
selected_type = type_bar.selectbox('Type', options=types, index=None)

countries = sorted(df['country'].dropna().unique().tolist())
selected_country = country_bar.selectbox('Country', options=countries, index=None)


# Filtering by mask
mask = pd.Series(True, index=df.index)
if name:
    mask &= df['name'].str.contains(name, case=False, na=False)

if selected_year:
    mask &= df['year'] == selected_year

if selected_watched_year:
    mask &= df['watched_date'].str.startswith(str(selected_watched_year))

if selected_status:
    mask &= df['status'] == selected_status

if selected_genres:
    genres_set = (
        df['genres']
        .fillna('')
        .apply(lambda x: {g.strip() for g in x.split(',') if g.strip()})
    )
    mask &= genres_set.apply(lambda g: set(selected_genres).issubset(g))

if selected_type:
    mask &= df['type'] == selected_type

if selected_country:
    mask &= df['country'] == selected_country


filtered_df = df[mask]
st.dataframe(filtered_df, column_config=load_column_config(), hide_index=True)
st.write(f'Total: **{filtered_df.shape[0]}**')
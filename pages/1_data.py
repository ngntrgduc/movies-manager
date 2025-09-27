import streamlit as st
import pandas as pd

from utils.data import load_data, load_column_config

st.set_page_config(page_title = 'Movies Manager', page_icon=':movie_camera:', layout='wide')

df, options = load_data(return_options=True)
column_config = load_column_config()

# First bar
seach_bar, year_bar, watched_year_bar, status_bar = st.columns(
    [0.3, 0.2, 0.2, 0.3], vertical_alignment='center'
)
name = seach_bar.text_input('Search movie')
selected_year = year_bar.selectbox('Year', options=options['year'], index=None)
selected_watched_year = watched_year_bar.selectbox(
    'Watched year', options=options['watched_year'], index=None
)
selected_status = status_bar.segmented_control(
    'Status', options=['waiting', 'completed', 'dropped'], selection_mode='single', 
    # width='stretch'
)

# Second bar
genre_bar, type_bar, country_bar = st.columns([0.5, 0.25, 0.25], vertical_alignment='center')
selected_genres = genre_bar.multiselect('Genres', options=options['genres'])
selected_type = type_bar.selectbox('Type', options=options['type'], index=None)
selected_country = country_bar.selectbox('Country', options=options['country'], index=None)

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
st.dataframe(filtered_df, column_config=column_config, hide_index=True)
st.write(f'Total: **{filtered_df.shape[0]}**')
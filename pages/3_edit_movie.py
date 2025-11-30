import streamlit as st
from utils.streamlit_helpers import load_data_with_cache, load_column_config
from utils.db import get_connection
from utils.movie import load_movies, add_movie, update_movie, delete_movie
from utils.constants import UNWATCHED_STATUS

st.set_page_config(page_title = 'Edit movies', page_icon=':pencil2:', layout='wide')

def get_default_values() -> dict:
    return {
        'name': '',
        'year': None,
        'status': UNWATCHED_STATUS,
        'type': 'movie',
        'country': None,
        'genres': None,
        'rating': None,
        'watched_date': None,
        'note': None,
    }

df = load_data_with_cache()
st.data_editor(
    df,
    column_config=load_column_config(),
    hide_index=False,
    num_rows='dynamic',
    key='editor',
)

left, right = st.columns([1, 1], vertical_alignment='top')
container = left.container(horizontal=True, horizontal_alignment='left')
if container.button(
    'Update', type='primary',
    help='Streamlit reruns on every widget interaction. \
    When editing data, double-click to update the database.'
):
    edited = st.session_state['editor']

    with get_connection() as con:
        cur = con.cursor()
        
        # Add
        for movie in edited['added_rows']:
            new_movie = get_default_values()
            new_movie.update(movie)
            add_movie(new_movie, cur)

        # Update
        for row_number, updated_data in edited['edited_rows'].items():
            movie_id = int(df.index[row_number])
            update_movie(movie_id, updated_data, cur)

        # Delete 
        for row_number in edited['deleted_rows']:
            movie_id = int(df.index[row_number])
            delete_movie(movie_id, cur)

        con.commit()
        
        # Update csv file
        df = load_movies(con, with_index=True)
        df.to_csv('data/data.csv', index=False)

    load_data_with_cache.clear()  # Clear cache
    st.toast('Updated database.', icon='✅')

if container.button('Refresh'):
    load_data_with_cache.clear()

# Because of streamlit data_editor behavior
right.info('After clicking `Update`, click `Refresh` to continue editing on this page.')
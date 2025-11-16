import streamlit as st
from utils.date import get_today, get_year
from utils.movie import add_movie, get_connection, load_movies, get_countries

st.set_page_config(page_title = 'Add movie', page_icon=':heavy_plus_sign:', layout='wide')

# Use session state to clear user input instead of st.form, 
# so that watch_date is auto-added when the status changes.
def reset_form() -> None:
    default_settings = {
        'name': '',
        'year': None,
        'status': 'waiting',
        'type': 'movie',
        'country': None,
        'genres': '',
        'rating': None,
        'watched_date': None,
        'note': None,
    }
    for key, val in default_settings.items():
        st.session_state[key] = val

def update_watched_date() -> None:
    st.session_state['watched_date'] = None if st.session_state['status'] == 'waiting' else get_today()

def add_to_db() -> None:
    name = st.session_state['name'].strip()
    if not name:
        st.toast('**Movie name is missing.**', icon='❌')
        return
    
    genres = st.session_state['genres']
    if not genres:
        st.toast('**Movie genres is missing.**', icon='❌')
        return
    
    movie = {
        'name': name,
        'year': st.session_state['year'],
        'status': st.session_state['status'],
        'type': st.session_state['type'],
        'country': st.session_state['country'],
        'genres': ','.join(
            genre for genre in (g.strip() for g in genres.split(',')) if genre
        ),
        'rating': st.session_state['rating'],
        'watched_date': st.session_state['watched_date'],
        'note': st.session_state['note'],
    }

    with get_connection() as con:
        cur = con.cursor()
        add_movie(movie, cur)
        con.commit()

        # Update csv file
        df = load_movies(con, with_index=True)
        df.to_csv('data/data.csv', index=False)

    st.toast(f'Added **{name}**.', icon='✅')
    reset_form()

left_container, right_container = st.columns([0.5, 0.5], gap='medium')

# Left container
left_container.text_input('Name', max_chars=150, key='name')

year_bar, type_bar, country_bar = left_container.columns([1, 1, 1], vertical_alignment='bottom')
year_bar.number_input(
    'Year', min_value=1900, max_value=get_year(get_today()), value=None, step=1, key='year'
)
type_bar.selectbox('Type', options=['movie', 'series'], key='type')

with get_connection() as con:
    cur = con.cursor()
    countries = get_countries(cur)

country_bar.selectbox(
    'Country', options=countries, placeholder='Choose or add option', 
    # 'Country', options=options['country'], placeholder='Choose or add option', 
    accept_new_options=True, index=None, key='country'
)

genres_bar, add_button = left_container.columns([2, 1], vertical_alignment='bottom')
genres_bar.text_input('Genres (separated by comma)', key='genres')
add_button.button('Add', type='primary', width='stretch', on_click=add_to_db)

# Right container
if 'status' not in st.session_state:
    st.session_state['status'] = 'waiting'

status_bar, watched_year_bar, rating_bar = right_container.columns(
    [1.2, 0.8, 0.6], vertical_alignment='center'
)
status_bar.segmented_control(
    'Status', ['waiting', 'completed' ,'dropped'], width='stretch',
    key='status', on_change=update_watched_date
)
watched_year_bar.text_input('Watched date', value=None, placeholder='YYYY-MM-DD', key='watched_date')
rating_bar.number_input(
    'Rating', min_value=1, max_value=10, value=None, step=1, placeholder='1-10', key='rating'
)

right_container.text_area('Note', value=None, height='stretch', key='note')

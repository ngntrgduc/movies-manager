import streamlit as st
import pandas as pd

from utils.data import load_data, write_data
from utils.date import get_today, get_year

st.set_page_config(page_title = "Add movies", page_icon=":heavy_plus_sign:", layout="wide")

# Use session state instead of form to auto-add watch_date when status changes
def reset_form():
    default_settings = {
        "name": "",
        "year": None,
        "status": "waiting",
        "type": "movie",
        "country": None,
        "genres": "",
        "rating": None,
        "watched_date": "",
        "note": "",
    }
    for key, val in default_settings.items():
        st.session_state[key] = val

def update_watched_date():
    st.session_state['watched_date'] = "" if st.session_state['status'] == "waiting" else get_today()

def add_movie_to_db(record: dict):
    """Append a new movie record to the database."""
    df = load_data()
    df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    write_data(df)

def add_movie():
    name = st.session_state["name"].strip()
    if not name:
        st.error("Movie name is missing.")
        return
    
    record = {
        "name": name,
        "year": int(st.session_state["year"]) if st.session_state["year"] else None,
        "status": st.session_state["status"],
        "type": st.session_state["type"],
        "country": st.session_state["country"].strip() if st.session_state["country"] else None,
        "genres": ",".join(
            genre for genre in (g.strip() for g in st.session_state["genres"].split(",")) if genre
        ),
        "rating": st.session_state["rating"],
        "watched_date": st.session_state["watched_date"],
        "note": st.session_state["note"],
    }
    add_movie_to_db(record)
    st.toast(f"Added **{name}**.", icon='✅')
    reset_form()
    # TODO clear cache of load_data()


left_container, right_container = st.columns([0.5, 0.5], gap="medium")

# Left container
left_container.text_input('Name', max_chars=150, key='name')

year_bar, type_bar, country_bar = left_container.columns([1, 1, 1], vertical_alignment='bottom')
year_bar.number_input(
    'Year', min_value=1900, max_value=get_year(get_today()), 
    value=None, step=1, key='year'
)
type_bar.selectbox('Type', options=['movie', 'series'], key='type')
country_bar.selectbox(
    'Country', ['China', 'Japan', 'Korea', 'US'], placeholder='Choose or add option', 
    accept_new_options=True, index=None, key='country'
)

genres_bar, add_button = left_container.columns([2, 1], vertical_alignment='bottom')
genres_bar.text_input('Genres (separated by comma)', key='genres')
add_button.button('Add', type="primary", width="stretch", on_click=add_movie)

# Right container
if "status" not in st.session_state:
    st.session_state["status"] = "waiting"

status_bar, watched_year_bar, rating_bar = right_container.columns(
    [1.2, 0.8, 0.6], vertical_alignment='center'
)
status_bar.segmented_control(
    'Status', ['waiting', 'completed' ,'dropped'], width='stretch',
    key='status', on_change=update_watched_date
)
watched_year_bar.text_input("Watched date", placeholder='YYYY-MM-DD', key='watched_date')
rating_bar.number_input(
    'Rating', min_value=1, max_value=10, value=None, step=1,
    placeholder='1-10', key='rating'
)

right_container.text_area('Note', height='stretch', key='note')

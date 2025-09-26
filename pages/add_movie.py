import streamlit as st
import pandas as pd

from utils.data import load_data
from utils.date import get_today, get_year

st.set_page_config(page_title = "Add movies", page_icon=":heavy_plus_sign:", layout="wide")

# Use session state instead of form to auto-add watch_date when status changes
default_settings = {
    "name": "",
    "year": None,
    "status": "waiting",
    "date": "",
    "genres": "",
    "type": "movie",
    "country": None,
    "rating": None,
    "note": "",
}
def reset_form():
    for key, val in default_settings.items():
        st.session_state[key] = val

def add_movie_to_db(record: dict):
    """Append a new movie record to the database."""
    df = load_data()
    df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    df.to_csv('test.csv', index=False)

def update_date():
    st.session_state['date'] = "" if st.session_state['status'] == "waiting" else get_today()


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

# Right container
if "status" not in st.session_state:
    st.session_state["status"] = "waiting"

status_bar, watched_year_bar, rating_bar = right_container.columns(
    [1.2, 0.8, 0.6], vertical_alignment='center'
)
status_bar.segmented_control(
    'Status', ['waiting', 'completed' ,'dropped'], width='stretch',
    # default='waiting',  # since using session state for setting value, this is unecessary
    key='status', on_change=update_date
)
watched_year_bar.text_input("Watched date", key='date')
rating_bar.number_input(
    'Rating', min_value=0.0, max_value=10.0, step=0.5, 
    value=None, format='%.1f', key='rating'
)

right_container.text_area('Note', height='stretch', key='note')

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
        "country": st.session_state["country"].strip(),
        "genres": ",".join(
            [g.strip() for g in st.session_state["genres"].split(",") if g.strip()]
        ),
        "rating": st.session_state["rating"] if st.session_state["rating"] else None,
        "watched_date": st.session_state["date"],
        "note": st.session_state["note"],
    }
    add_movie_to_db(record)
    st.toast(f"Added **{name}**.", icon='✅')
    reset_form()

add_button.button('Add', type="primary", width="stretch", on_click=add_movie)
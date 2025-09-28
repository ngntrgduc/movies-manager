import streamlit as st
import pandas as pd
from ast import literal_eval

from utils.data import load_data, load_column_config, write_data

st.set_page_config(page_title = 'Edit movies', page_icon=':pencil2:', layout='wide')

def prepare_for_save(df: pd.DataFrame) -> pd.DataFrame:
    # Convert the 'genres' column from a string representation of a list 
    # into a comma-separated string. Because the data editor stores genres as 
    # lists, while pandas does not handle lists in DataFrame columns.
    df['genres'] = df['genres'].apply(
        lambda g: ','.join(literal_eval(g)) 
        if isinstance(g, str) and (g.startswith('[') and g.endswith(']')) else g
    )
    return df


# Due to streamlit data editor behavior, don't delete a movie after adding a movie
df = load_data()
edited_df = st.data_editor(
    df,
    column_config=load_column_config(),
    hide_index=True,
    num_rows='dynamic',
)

if st.button(
    'Update', type='primary',
    help='Streamlit reruns on every widget interaction. \
    When editing data, double-click to update the database.'
):
    saved_df = prepare_for_save(edited_df.copy())
    write_data(saved_df)
    st.toast('Updated database.', icon='✅')
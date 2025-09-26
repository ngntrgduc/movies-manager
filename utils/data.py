import streamlit as st
import pandas as pd

# @st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv('test.csv')

def write_data(df: pd.DataFrame) -> None:
    df.to_csv('test.csv', index=False)

def load_column_config() -> dict:
    """Load column config for Streamlit dataframe and data editor"""
    return {
        'name': st.column_config.TextColumn(pinned=True, width='medium', required=True),
        'year': st.column_config.NumberColumn(width=8),
        'status': st.column_config.SelectboxColumn(
            width=35, options=['waiting', 'completed', 'dropped'], 
            default='waiting', required=True
        ),
        'type': st.column_config.SelectboxColumn(
            width=20, options=['movie', 'series'], required=True,
            # default='movie', 
        ),
        'country': st.column_config.TextColumn(width=10),
        'genres': st.column_config.ListColumn(
            width='medium', 
            # default=[]
        ),
        'rating': st.column_config.NumberColumn(width=5, min_value=0, max_value=10),
        'date': st.column_config.TextColumn(width=30),
        'note': st.column_config.TextColumn(width='small'),
    }


def from_csv_to_db(df):
    """Transfer data from dataframe to database"""
    for index, row in df.iterrows():
        query = f'INSERT INTO movies VALUES ()'
    raise NotImplementedError


def get_genres():
    """Get genres of a movie from database"""
    # TODO using CTE or something to represent genres as list
    f"SELECT concat_ws(',', genres) as genres FROM world"
    raise NotImplementedError
import streamlit as st
import pandas as pd

from .date import get_year

@st.cache_data
def load_data_with_cache() -> pd.DataFrame:
    # return pd.read_csv('data.csv')
    return pd.read_csv(
        'data/data.csv', 
        dtype={'note': 'string'}  # in case all movies in data don't have note
    )  

def write_data(df: pd.DataFrame) -> None:
    # df.to_csv('data.csv', index=False)
    df.to_csv('data/data.csv', index=False)

@st.cache_data
def get_options(df: pd.DataFrame) -> dict:
    return {
            'year': sorted(df['year'].dropna().astype(int).unique().tolist(), reverse=True),
            # 'status': ['waiting', 'completed' ,'dropped'],
            # 'type': ['movie', 'series'], 
            'type': sorted(df['type'].unique().tolist()),
            'country': sorted(df['country'].dropna().unique().tolist()),
            'genres': sorted(
                df['genres']
                .dropna()
                .apply(lambda x: [g.strip() for g in x.split(',')])
                .explode()  # flatten lists into rows
                .unique().tolist()
            ),
            'watched_year': sorted((
                df['watched_date']
                .dropna()
                .apply(get_year)
                .unique().tolist()
            ), reverse=True),
        }

@st.cache_data
def load_column_config() -> dict:
    """Load column config for Streamlit dataframe and data editor"""
    return {
        'name': st.column_config.TextColumn(pinned=True, width='medium', required=True),
        'year': st.column_config.NumberColumn(width=8),
        'status': st.column_config.SelectboxColumn(
            width=35, options=['waiting', 'completed', 'dropped'], default='waiting', required=True
        ),
        'type': st.column_config.SelectboxColumn(
            width=20, options=['movie', 'series'], required=True
        ),
        'country': st.column_config.TextColumn(width=10),
        'genres': st.column_config.ListColumn(width='medium'),
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
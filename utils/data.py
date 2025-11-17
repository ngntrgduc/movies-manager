import streamlit as st
import pandas as pd

@st.cache_data
def load_data_with_cache() -> pd.DataFrame:
    from utils.movie import load_movies, get_connection
    with get_connection() as con:
        return load_movies(con, with_index=True)

@st.cache_data
def get_options(df: pd.DataFrame) -> dict:
    from .date import get_year
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
        'id': st.column_config.NumberColumn(disabled=True),
        'name': st.column_config.TextColumn(pinned=True, width='medium', required=True),
        'year': st.column_config.NumberColumn(width=8, required=True),
        'status': st.column_config.SelectboxColumn(
            width=35, options=['waiting', 'completed', 'dropped'], default='waiting', required=True
        ),
        'type': st.column_config.SelectboxColumn(
            width=20, options=['movie', 'series'], required=True
        ),
        'country': st.column_config.TextColumn(width=10),
        'genres': st.column_config.ListColumn(width='medium', required=True),
        'rating': st.column_config.NumberColumn(width=5, min_value=0, max_value=10),
        'date': st.column_config.TextColumn(width=30),
        'note': st.column_config.TextColumn(width='small'),
    }

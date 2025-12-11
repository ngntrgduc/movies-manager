import pytest
import sqlite3
from io import StringIO
import pandas as pd
from csv_to_sqlite import csv_to_sqlite
from utils.db import fetch_rows_count
from utils.movie import add_movie, update_movie, delete_movie, get_movie

csv_data = """name,year,status,type,country,genres,rating,watched_date,note
Inception,2010,waiting,movie,US,"action,sci-fi,thriller,epic",,,
Interstella,2014,waiting,movie,US,"time travel,adventure,sci-fi,epic",,,
The Boy and the Beast,2015,waiting,movie,Japan,"animation,adventure,fantasy",,,
Her,2013,waiting,movie,US,"comedy,romance,sci-fi",,,
Soul,2020,waiting,movie,US,animation,,,
"""
df = pd.read_csv(StringIO(csv_data))
with open('sql/schema.sql', 'r') as f:
    schema_sql = f.read()

def get_movie_name(movie: tuple) -> str:
    return movie[1]

@pytest.fixture(scope='module')
def db():
    con = sqlite3.connect(':memory:')
    con.executescript(schema_sql)
    con.commit()
    csv_to_sqlite(df, con)
    con.commit()
    yield con
    
    # Teardown
    con.close()

def test_read_db(db):
    cur = db.cursor()
    assert get_movie_name(get_movie(1, cur)) == 'Inception'
    assert get_movie_name(get_movie(5, cur)) == 'Soul'
    assert get_movie(6, cur) == None
    assert fetch_rows_count(cur) == 5

def test_add_db(db):
    new_movie = {
        'name': 'Frieren',
        'year': 2023,
        'status': 'waiting',
        'type': 'series',
        'country': 'Japan',
        'genres': ['animation', 'adventure', 'fantasy'],
        'rating': None,
        'watched_date': '',
        'note': ''
    }    
    cur = db.cursor()
    add_movie(new_movie, cur)
    db.commit()
    assert fetch_rows_count(cur) == 6
    assert get_movie_name(get_movie(6, cur)) == new_movie['name']

def test_update_db(db):
    cur = db.cursor()
    updated_note = 'updated note :)'
    update_movie(6, {'note': updated_note}, cur)
    assert fetch_rows_count(cur) == 6
    assert get_movie(6, cur)[-1] == updated_note

def test_delete_db(db):
    cur = db.cursor()

    delete_movie(1, cur)
    assert get_movie(1, cur) == None
    assert fetch_rows_count(cur) == 5

    delete_movie(2, cur)
    assert get_movie(2, cur) == None
    assert fetch_rows_count(cur) == 4

def test_get_deleted_id(db):
    cur = db.cursor()
    assert get_movie(1, cur) == None
    assert get_movie(2, cur) == None
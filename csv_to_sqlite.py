import sqlite3
import pandas as pd
from utils.movie import add_movie
from time import perf_counter

def csv_to_sqlite(df: pd.DataFrame, con: sqlite3.Connection) -> None:
    """Export csv data to SQLite database."""
    cur = con.cursor()
    for _, movie in df.iterrows():
        add_movie(movie, cur)


tic = perf_counter()
con = sqlite3.connect("data/movies.db")
cur = con.cursor()
with open('sql/schema.sql', 'r') as f:
    schema_sql = f.read()

cur.executescript(schema_sql)
con.commit()

df = pd.read_csv('data/data.csv')
csv_to_sqlite(df, con)
con.commit()

con.close()
print(f'Moved data from CSV to SQLite database, took {(perf_counter() - tic):.4f}s')
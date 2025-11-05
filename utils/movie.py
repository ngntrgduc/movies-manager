import sqlite3
import pandas as pd

def get_genre_id(name: str, cur: sqlite3.Cursor) -> int:
    """Get genre id by name."""
    cur.execute("SELECT id FROM genre WHERE name = ?", (name,))
    return cur.fetchone()[0]

def add_genre(name: str, cur: sqlite3.Cursor) -> None:
    """Add genre to the database."""
    cur.execute("INSERT OR IGNORE INTO genre (name) VALUES (?)", (name,))

def add_movie_genre(movie_id: int, genres: list[str], cur: sqlite3.Cursor) -> None:
    """Link genres to a movie."""
    for genre_name in genres:
        add_genre(genre_name, cur)
        genre_id = get_genre_id(genre_name, cur)
        cur.execute(
            "INSERT OR IGNORE INTO movie_genre (movie_id, genre_id) VALUES (?, ?)",
            (movie_id, genre_id)
        )

def add_movie(movie: dict, cur: sqlite3.Cursor) -> None:
    """Add a movie to the database."""
    # Handle manually to avoid inserting NaN (pandas), SQLite doesn't understand NaN
    cur.execute("""
        INSERT INTO movie (name, year, status, type, country, rating, watched_date, note)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        movie['name'],
        int(movie['year']) if not pd.isna(movie['year']) else None,
        movie['status'],
        movie['type'],
        movie['country'],
        float(movie['rating']) if not pd.isna(movie['rating']) else None,
        movie['watched_date'],
        movie['note']
    ))

    movie_id = cur.lastrowid
    genres = [g.strip() for g in str(movie['genres']).split(',') if g.strip()]
    add_movie_genre(movie_id, genres, cur)

def delete_movie(movie_id: int, cur: sqlite3.Cursor) -> None:
    """Delete a movie by id."""
    cur.execute("DELETE FROM movie WHERE id = ?", (movie_id,))

def update_movie(movie_id: int, updated_data: dict, cur: sqlite3.Cursor) -> None:
    """Update an existing movie by id."""
    if not updated_data:
        return 

    # movie table doesn't has genres field
    genres = updated_data.pop('genres', None)

    if updated_data:
        placeholders = ', '.join(f'{field} = ?' for field in updated_data.keys())
        values = list(updated_data.values())
        values.append(movie_id)
        cur.execute(f"UPDATE movie SET {placeholders} WHERE id = ?", values)

    # update genres relationship
    if genres is not None:
        cur.execute("DELETE FROM movie_genre WHERE movie_id = ?", (movie_id,)) # remove old relations
        add_movie_genre(movie_id, genres, cur)

def load_movies(con: sqlite3.Connection, with_index: bool = False) -> pd.DataFrame:
    """
    Load movies data from the database, return as a pandas DataFrame.
    Parameters:
        con (sqlite3.Connection): Active SQLite database connection.
        with_index (bool, optional): 
            If True, set the 'id' column as the DataFrame index. 
            Defaults to False.
    """
    if with_index:
        return pd.read_sql_query( "SELECT * FROM movie_detail", con, index_col='id')

    return pd.read_sql_query("SELECT * FROM movie_detail", con)

# For Power BI Dashboard
# def update_csv(con: sqlite3.Connection) -> None:
#     """Update CSV file with data from database."""
#     df = load_movies(con, with_index=True)
#     df.to_csv('data/data.csv', index=False)
# def write_csv(df: pd.DataFrame) -> None:
    # """Write DataFrame data to csv file."""
    # df.to_csv('data/data.csv', index=False)
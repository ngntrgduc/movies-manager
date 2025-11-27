import sqlite3

def get_connection(file_path: str = 'data/movies.db') -> sqlite3.Connection:
    """Create and return a SQLite connection with foreign key support enabled."""
    con = sqlite3.connect(file_path)
    con.execute('PRAGMA foreign_keys = ON')  # enable foreign keys constraint and ON DELETE CASCADE
    return con

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
        int(movie['year']) if movie['year'] is not None else None,
        movie['status'],
        movie['type'],
        movie['country'],
        float(movie['rating']) if movie['rating'] is not None else None,
        movie['watched_date'],
        movie['note']
    ))

    movie_id = cur.lastrowid
    add_movie_genre(movie_id, movie['genres'], cur)

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

def load_movies(con: sqlite3.Connection, with_index: bool = False):
    """
    Load movies data from the database, return as a pandas DataFrame.
    Parameters:
        con (sqlite3.Connection): Active SQLite database connection.
        with_index (bool, optional): 
            If True, set the 'id' column as the DataFrame index. 
            Defaults to False.
    """
    import pandas as pd

    if with_index:
        return pd.read_sql_query( "SELECT * FROM movie_detail", con, index_col='id')

    return pd.read_sql_query("SELECT * FROM movie_detail", con)

def get_movie(movie_id: int, cur: sqlite3.Cursor) -> tuple | None:
    """Get movie information by id. Return a tuple or None if not found."""
    cur.execute('SELECT * FROM movie_detail WHERE id = ?', (movie_id,))
    return cur.fetchone()

def get_countries(cur: sqlite3.Cursor) -> list[str]:
    """Return a list of all countries in the database.""" 
    cur.execute('SELECT DISTINCT country FROM movie WHERE country IS NOT NULL ORDER BY country')
    return [country for (country,) in cur.fetchall()]

def get_statuses(cur: sqlite3.Cursor) -> list[str]:
    """Return a list of all statuses in the database."""
    cur.execute('SELECT DISTINCT status FROM movie ORDER BY status')
    return [status for (status,) in cur.fetchall()]

def get_types(cur: sqlite3.Cursor) -> list[str]:
    """Return a list of all movie types in the database."""
    cur.execute('SELECT DISTINCT type FROM movie')
    return [movie_type for (movie_type,) in cur.fetchall()]

def get_genres(cur: sqlite3.Cursor) -> list[str]:
    """Return a list of all genres in the database.""" 
    cur.execute('SELECT name FROM genre')
    return [genre for (genre,) in cur.fetchall()]
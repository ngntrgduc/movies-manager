import sqlite3

def get_connection(file_path: str = 'data/movies.db') -> sqlite3.Connection:
    """Create and return a SQLite connection with foreign key support enabled."""
    con = sqlite3.connect(file_path)
    con.execute('PRAGMA foreign_keys = ON')  # enable foreign keys constraint and ON DELETE CASCADE
    return con

def fetch_scalar(cur: sqlite3.Cursor, query: str) -> int | float:
    """Run a SQL query and return its single scalar value."""
    return cur.execute(query).fetchone()[0]

def fetch_rows(
    cur: sqlite3.Cursor, query: str, parameters: tuple = None
) -> tuple[list[tuple], list[str]]:
    """Run a (parameterized) SQL query and return its rows and column names."""
    if parameters:
        cur.execute(query, parameters)
    else:
        cur.execute(query)

    rows = cur.fetchall()
    column_names = [d[0] for d in cur.description]
    return rows, column_names

def fetch_rows_count(cur: sqlite3.Cursor, table: str = 'movie') -> int:
    """Return the number of rows in the specified table."""
    return fetch_scalar(cur, f'SELECT COUNT(*) FROM {table}')
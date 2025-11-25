import sqlite3

def fetch_scalar(cur: sqlite3.Cursor, query: str) -> int | float:
    """Run a SQL query and return its single scalar value."""
    return cur.execute(query).fetchone()[0]

def fetch_rows(
    cur: sqlite3.Cursor, query: str, parameter: tuple = None
) -> tuple[list[tuple], list[str]]:
    """Run a (parameterized) SQL query and return its rows and column names."""
    if parameter:
        cur.execute(query, parameter)
    else:
        cur.execute(query)

    rows = cur.fetchall()
    column_names = [d[0] for d in cur.description]
    return rows, column_names
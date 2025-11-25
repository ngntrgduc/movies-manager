from pathlib import Path

def list_sql_files() -> list[str]:
    """Return a list of all SQL files in the 'sql/' folder."""
    sql_folder = Path('sql/')
    excluded = ['schema.sql']
    return [
        f.stem for f in sql_folder.glob('*.sql')
        if f.name not in excluded
    ]

def get_fuzzy_match(value: str, choices: list[str], n: int = 1) -> str | None:
        """Return the closest fuzzy match to `value` among `choices`."""
        from difflib import get_close_matches
        matches = get_close_matches(value, choices, n=n)
        return matches[0] if matches else None

def resolve_sql_path(
    filename: str, sql_folder: Path, sql_files: list[str]
) -> tuple[Path | None, str | None]:
    """
    Resolve a SQL file path from user filename input.
    
    Exact match -> Prefix match -> Fuzzy match

    Returns (resolved_path, match_type):
        match_type: 'Exact', 'Prefix', 'Fuzzy', or None if file not found
    """

    sql_path = sql_folder / f'{filename}.sql'
    if sql_path.exists():
        return sql_path, 'Exact'

    # Prefix match
    prefix_matches = [name for name in sql_files if name.startswith(filename)]
    if prefix_matches:
        return sql_path.with_stem(prefix_matches[0]), 'Prefix'
    
    # Fuzzy match
    fuzzy_match = get_fuzzy_match(filename, sql_files)
    if fuzzy_match:
        return sql_path.with_stem(fuzzy_match), 'Fuzzy'

    return None, None

from datetime import datetime
def parse_sort_column(value):
    """
    Normalize a value into a sortable key.

    Returns a tuple `(type_priority, normalized_value)` so that
    mixed types never get compared directly during sorting.

    Priority order:
        0: numeric
        1: percentage
        2: date (YYYY / YYYY-MM / YYYY-MM-DD)
        3: string
        4: None (always last)
    """

    if value is None:
        return (4, '')  # None always last in ascending

    # Numeric values
    if isinstance(value, (int, float)):
        return (0, float(value))
    
    if isinstance(value, str):
        # Percentages ("85%" -> 85.0)
        # Checked before numeric-like to avoid raising Exception for float("85%")
        if value.endswith('%'):
            try:
                return (1, float(value.rstrip('%')))
            except ValueError:
                pass

        # Dates string
        for format in ('%Y', '%Y-%m', '%Y-%m-%d'):
            try:
                datetime.strptime(value, format)
                return (2, value)
            except ValueError:
                continue
        
    # Fallback: regular string
    return (3, value.lower())

def run_sql(cur, query: str, note: bool = False, sort: tuple[str, str] | None = None) -> None:
    """
    Run a SQL query and display the results, optionally hiding the 'note' column,
    converting 'rating' to int, and sorting by a column.

    Args:
        cur: SQLite cursor object
        query: SQL query string to execute
        note: Show the 'note' column if True; hide if False
        sort: Tuple (column_name, order) to sort results.
              order can be 'asc', 'a', '+', 'desc', 'd', '-'
    """
    from utils.cli import print_rows
    from utils.db import fetch_rows

    rows, column_names = fetch_rows(cur, query)
    rows = [list(row) for row in rows]  # convert tuple to list

    # Convert rating to int if present
    if 'rating' in column_names:
        col_idx = column_names.index('rating')
        for row in rows:
            if row[col_idx] is not None:
                row[col_idx] = int(row[col_idx])

    # Hide note column
    if not note and 'note' in column_names:
        rows = [row[:-1] for row in rows]  # assume 'note' always the last column
        column_names.remove('note')

    # Sorting
    if sort:
        sort_column, sort_order = sort
        matched_column = get_fuzzy_match(sort_column, column_names)
        if not matched_column:
            print(f'Column {sort_column!r} not found. Skipping sort.')
        else:
            descending_aliases = {'desc', 'd', '-'}
            descending = sort_order in descending_aliases

            valid_orders = descending_aliases | {'asc', 'a', '+'}
            if sort_order not in valid_orders:
                print(f'Invalid sort order {sort_order!r}. Using ascending.')

            col_idx = column_names.index(matched_column)
            rows.sort(
                key=lambda row: parse_sort_column(row[col_idx]), 
                reverse=descending
            )

    print_rows(rows, column_names)
    print(f'Total: {len(rows)}')

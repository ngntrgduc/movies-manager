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
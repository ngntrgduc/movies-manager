import click
import sqlite3
from rich import print
from pathlib import Path
from utils.movie import get_connection, load_movies

DB_FILE = Path('data/movies.db')
BACKUP_FILE = Path('data/backup.db')
CON = get_connection(DB_FILE)

def update_csv() -> None:
    """Update CSV file with data from database."""
    df = load_movies(CON, with_index=True)
    df.to_csv('data/data.csv', index=False)

# changes the default parameters to -h and --help instead of just --help
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.group(context_settings=CONTEXT_SETTINGS, no_args_is_help=True)
def cli():
    """Command-line tool to manage, filter, and analyze your movie collection."""
    pass


@cli.command(no_args_is_help=True)
@click.option('-n', '--name', help='Filter by name (case-insensitive)')
@click.option('-y', '--year', type=int, help='Filter by release year')
@click.option('-s', '--status', help="Filter by status: 'waiting', 'completed', or 'dropped'")
@click.option('-t', '--movie-type', help="Filter by type: 'movie' or 'series'")
@click.option('-c', '--country', help='Filter by country')
@click.option('-g', '--genres', help='Filter by genres (comma-separated)')
@click.option('-r', '--rating', type=click.IntRange(1, 10, clamp=True), help='Filter by rating')
@click.option('-w', '--watched-year', help='Filter by watched year')
@click.option('-nc', '--note-contains', help='Filter by substring in note (case-insensitive)')
@click.option('--sort', help='Sort result by year or rating or watched date')
@click.option('--stats', help='Show statistics for the filtered results', is_flag=True)
@click.option('--note', help='Show notes', is_flag=True)
def filter(
    name, year, status, movie_type, country, genres, rating, watched_year, sort, 
    stats, note, note_contains
):
    """Filter movies by attributes."""

    # Prevent printing all movies to the command line when using with just flags
    filters = [name, year, status, movie_type, country, genres, rating, watched_year, note_contains]
    has_filter = any(arg is not None for arg in filters)
    if not has_filter:
        print('No filters specified. Use --help to see available options.')
        return

    from utils.cli import resolve_choice, apply_filters

    df = load_movies(CON, with_index=False)
    # For table displaying purpose
    df['year'] = df['year'].astype('Int64')
    df['rating'] = df['rating'].astype('Int64')

    filtered_df = apply_filters(
        df, name, year, status, movie_type, country, genres, rating, watched_year, note_contains
    )
    
    if not note:
        filtered_df = filtered_df.drop('note', axis=1)

    sort = sort.strip() if sort else None
    if sort:
        try: 
            descending_columns = ['rating']
            excluded_columns = ['genres', 'note']
            sortable_columns = [col for col in filtered_df.columns 
                                if col not in excluded_columns]
            resolved = resolve_choice(sort, sortable_columns, strict=True)
            ascending = resolved not in descending_columns
            filtered_df = filtered_df.sort_values(by=[resolved], ascending=ascending)
        except ValueError as e:
            raise click.BadParameter(str(e))

    if filtered_df.empty:
        print('No data.')
        return

    from utils.cli import print_df
    
    def print_stats(df, excluded: list = []) -> None:
        """Print DataFrame statistics."""
        for col in ['status', 'type', 'country']:
            if col in excluded:
                continue

            print(col.capitalize())
            for value, count in df[col].value_counts().items():
                print(f' - {value}: {count}')

    print_df(filtered_df)
    print(f'Total: {filtered_df.shape[0]}')
    if stats:
        option_to_col = {'status': status, 'type': movie_type, 'country': country}
        excluded = [col for col, val in option_to_col.items() if val]
        print_stats(filtered_df, excluded)

@cli.command()
@click.argument('movie_id', type=int)
def get(movie_id: int):
    """Get information of a movie by id."""
    from utils.movie import get_movie

    CON.row_factory = sqlite3.Row  # for dictionary conversion
    cur = CON.cursor()

    movie = get_movie(movie_id, cur)
    if movie is None:
        print(f'Movie with id {movie_id} not found.')
        return

    print(dict(movie))

@cli.command()
def add():
    """Add a new movie interactively."""
    from rich.status import Status
    from utils.movie_input import prompt_add_movie

    movie = prompt_add_movie()
    print(movie)

    with Status(f'Adding...') as rich_status:
        from utils.movie import add_movie
        cur = CON.cursor()
        add_movie(movie, cur)
        CON.commit()
        update_csv()
    print(f"Added {movie['type']}: {movie['name']!r} ({movie['year']})")

@cli.command()
@click.argument('movie_id', type=int)
def update(movie_id: int):
    """Update a movie interactively by id."""
    from utils.movie import get_movie, update_movie
    from utils.movie_input import prompt_update_movie

    CON.row_factory = sqlite3.Row
    cur = CON.cursor()

    existing_movie = get_movie(movie_id, cur)
    if existing_movie is None:
        print(f'Movie with id {movie_id} not found.')
        return

    existing_movie = dict(existing_movie)
    print(existing_movie)
    existing_movie.pop('id')

    updated_data = prompt_update_movie(existing_movie)
    print(updated_data)

    update_movie(movie_id, updated_data, cur)
    CON.commit()
    update_csv()
    print('Updated successfully.')

@cli.command()
@click.argument('movie_id', type=int)
def delete(movie_id: int):
    """Delete a movie by id."""
    from utils.movie import get_movie, delete_movie

    CON.row_factory = sqlite3.Row  # for dictionary conversion
    cur = CON.cursor()

    # Sacrifice formatting for speed by using a tuple instead of a pandas DataFrame
    # Importing pandas is costly compared to sqlite
    movie = get_movie(movie_id, cur)
    if movie is None:
        print(f'Movie with id {movie_id} not found.')
        return

    movie = dict(movie)
    print(movie)

    if click.confirm(f'Do you want to delete this {movie['type']}?', default=True):
        delete_movie(movie_id, cur)
        CON.commit()
        update_csv()
        print('Deleted successfully.')
    else:
        print('Deletion cancelled.')

@cli.command()
@click.option('-v', '--verbose', help='Show extended statistics.', is_flag=True)
def stats(verbose):
    """Show statistics for the movie data."""
    from utils.cli import print_rows
    from utils.db import fetch_scalar, fetch_rows

    cur = CON.cursor()

    total = fetch_scalar(cur, 'SELECT COUNT(*) FROM movie')
    avg_rating = fetch_scalar(cur, 'SELECT ROUND(AVG(rating), 2) FROM movie')
    genres_count = fetch_scalar(cur, 'SELECT COUNT(*) FROM genre')
    print(f'Total: {total}')
    print(f'Average rating: {avg_rating}')
    print(f'Genres count: {genres_count}')

    sql_folder = Path('sql/')
    stat_files = ['status', 'type', 'country']
    extended_files = ['watchedyear', 'rating', 'genres']

    if verbose:
        stat_files.extend(extended_files)

    for stat_file in stat_files:
        sql_path = sql_folder / f'{stat_file}.sql'
        if not sql_path.exists():
            print(f'SQL file {sql_path.name!r} not found.')
            continue
        query = sql_path.read_text()
        rows, column_names = fetch_rows(cur, query)
        print_rows(rows, column_names, title=f'{stat_file.capitalize()}:')

@cli.command()
@click.option('--csv', help='Back up to data/backup.csv for safer recovery', is_flag=True)
def backup(csv):
    """Back up data."""
    try:
        with sqlite3.connect(BACKUP_FILE) as backup_con:
            CON.backup(backup_con)
        if csv:
            df = load_movies(CON, with_index=True)
            df.to_csv('data/backup.csv', index=False)
        print('Backup successful.')
    except Exception as e:
        print(f'Backup failed: {e}')

@cli.command()
def restore():
    """Restore data from backup."""
    import shutil

    if not BACKUP_FILE.exists():
        print("Backup file not found. Run 'backup' first.")
        return

    from datetime import datetime
    print(f'Backup last modified: {
        datetime.fromtimestamp(BACKUP_FILE.stat().st_mtime):%Y-%m-%d %X
    }')

    click.confirm(
        'This will replace your current movie database with the backup file. Continue?', abort=True
    )

    try:
        shutil.copyfile(BACKUP_FILE, DB_FILE)
        update_csv()
        print('Restore successful.')
    except Exception as e:
        print(f'Restore failed: {e}')

@cli.command()
@click.argument('filename', type=str, required=False)
@click.option('--note', help='Show notes', is_flag=True)
@click.option('-s', '--sort', help='Sort result by column', nargs=2)
@click.option('-v', '--verbose', help='Show SQL file contents', is_flag=True)
def sql(filename, note, sort, verbose):
    """Run a SQL file from the 'sql/' folder."""

    sql_folder = Path('sql/')
    def list_sql_files() -> list[str]:
        """Return a list of all SQL files in the 'sql/' folder."""
        excluded = ['schema.sql']
        return [
            f.stem for f in sql_folder.glob('*.sql')
            if f.name not in excluded
        ]

    def print_sql_files(sql_files: list[str]) -> None:
        """Print a list of available SQL files."""
        from rich.columns import Columns
        from rich.console import Console
        console = Console(width=60)
        console.print('[bold cyan]Available SQL files:[/bold cyan]')
        colored_files = [f'[green]{name}[/green]' for name in sql_files]
        console.print(Columns(colored_files, equal=True, expand=True))

    sql_files = list_sql_files()
    if not filename:
        print_sql_files(sql_files)
        return

    def get_fuzzy_match(value: str, choices: list[str], n: int = 1) -> str | None:
        """Return the closest fuzzy match to `value` among `choices`."""
        from difflib import get_close_matches
        matches = get_close_matches(value, choices, n=n)
        return matches[0] if matches else None
    
    # If exact file doesn't exist -> attempt prefix match + fuzzy match
    sql_path = sql_folder / f'{filename}.sql'
    if not sql_path.exists():
        print(f'SQL file {sql_path.name!r} not found.')

        # Prefix match
        prefix_matches = [name for name in sql_files if name.startswith(filename)]
        if prefix_matches:
            matched_name = prefix_matches[0]
            print(f"Closest prefix match: '{matched_name}.sql'")
        else:
            # Fuzzy match
            fuzzy_match = get_fuzzy_match(filename, sql_files)
            if fuzzy_match:
                matched_name = fuzzy_match
                print(f"Closest fuzzy match: '{matched_name}.sql'") 
            else:
                print(f"No similar SQL files found in '{sql_folder}/'")
                return

        sql_path = sql_path.with_stem(matched_name)

    query = sql_path.read_text()
    if verbose:
        print(f'\n[dim]{query}[/dim]\n')

    from utils.cli import print_rows
    from utils.db import fetch_rows

    cur = CON.cursor()
    rows, column_names = fetch_rows(cur, query)
    rows = [list(row) for row in rows]  # convert tuple to list

    # Handle numeric format
    if 'rating' in column_names:
        col_idx = column_names.index('rating')
        for row in rows:
            if row[col_idx] is not None:
                row[col_idx] = int(row[col_idx])

    if not note and 'note' in column_names:
        rows = [row[:-1] for row in rows]  # assume 'note' always the last column
        column_names.remove('note')

    if sort:
        sort_column, sort_order = sort
        matched_column = get_fuzzy_match(sort_column, column_names)
        if not matched_column:
            print(f'Column {sort_column!r} not found. Skipping sort.')
        else:
            from utils.cli import parse_sort_column

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

@cli.command()
@click.argument('number', type=int, required=False, default=10)
@click.option('--note', help='Show notes', is_flag=True)
def recent(number, note):
    """List recently watched movies."""
    sql_folder = Path('sql/')
    sql_path = sql_folder / 'command' / 'recent.sql'
    if not sql_path.exists():
        print(f"SQL file '{sql_path}' not found.")
        return

    query = sql_path.read_text()

    from utils.db import fetch_rows
    from utils.cli import print_rows

    cur = CON.cursor()
    rows, column_names = fetch_rows(cur, query, (number,))
    rows = [list(row) for row in rows]  # convert tuple to list

    # Handle numeric format
    if 'rating' in column_names:
        col_idx = column_names.index('rating')
        for row in rows:
            if row[col_idx] is not None:
                row[col_idx] = int(row[col_idx])
    
    if not note and 'note' in column_names:
        rows = [row[:-1] for row in rows]  # assume 'note' always the last column
        column_names.remove('note')

    print_rows(rows, column_names)

if __name__ == '__main__':
    try:
        cli()
    except Exception as e:
        print(f'Exception: {e}')
    finally:
        CON.close()
        # print('Closed connection.')
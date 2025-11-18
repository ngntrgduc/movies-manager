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
@click.option('--sort', help='Sort result by year or rating or watched date')
@click.option('--stats', help='Show statistics for the filtered results', is_flag=True)
@click.option('--note', help='Show notes', is_flag=True)
def filter(name, year, status, movie_type, country, genres, rating, watched_year, sort, stats, note):
    """Filter movies by attributes."""

    # Prevent printing all movies to the command line when using with just flags
    filters = [name, year, status, movie_type, country, genres, rating, watched_year]
    has_filter = any(arg is not None for arg in filters)
    if not has_filter:
        print('No filters specified. Use --help to see available options.')
        return

    from utils.cli import resolve_choice, apply_filters

    df = load_movies(CON, with_index=False)
    # For table displaying purpose
    df['year'] = df['year'].astype('Int64')
    df['rating'] = df['rating'].astype('Int64')
    if not note:
        df.drop('note', axis=1, inplace=True)

    filtered_df = apply_filters(
        df, name, year, status, movie_type, country, genres, rating, watched_year
    )

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
def stats():
    """Show statistics for the movie data."""
    cur = CON.cursor()
    total = cur.execute('SELECT COUNT(*) FROM movie').fetchone()[0]
    print(f'Total: {total}')
    for col in ['status', 'type', 'country']:
        query = f"""
            SELECT {col}, COUNT(*) as count 
            FROM movie
            GROUP BY {col}
            ORDER BY count DESC
        """
        rows = cur.execute(query).fetchall()
        print(col.capitalize())
        for value, count in rows:
            print(f' - {value}: {count}')

@cli.command()
def backup():
    """Back up data."""
    try:
        with sqlite3.connect(BACKUP_FILE) as backup_con:
            CON.backup(backup_con)
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
def sql(filename, note, sort):
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
            from difflib import get_close_matches
            fuzzy_match = get_close_matches(filename, sql_files, n=1)
            if fuzzy_match:
                matched_name = fuzzy_match[0]
                print(f"Closest fuzzy match: '{matched_name}.sql'") 
            else:
                print(f"No similar SQL files found in '{sql_folder}/'")
                return

        sql_path = sql_path.with_stem(matched_name)

    import pandas as pd
    from utils.cli import print_df

    query = sql_path.read_text()
    print(f'\n[dim]{query}[/dim]')
    print()
    df = pd.read_sql_query(query, CON)
    if df.empty:
        print('No data.')
        return 

    # Handle numeric format
    for col in ['rating', 'year']:
        if col in df.columns:
            df[col] = df[col].astype('Int64')
    
    if not note and 'note' in df.columns:
        df.drop('note', axis=1, inplace=True)

    if sort:
        from utils.cli import resolve_choice

        column, order = sort
        resolved = resolve_choice(column, list(df.columns))
        if not resolved:
            print(f"Column '{column}' not found. Skipping sort.\n")
        else:
            if order in ('asc', 'a'):
                ascending = True
            elif order in ('desc', 'd'):
                ascending = False
            else:
                ascending = True  # default if invalid
                print(f"Invalid sort order '{order}', using 'asc' by default.\n")

            df = df.sort_values(by=[resolved], ascending=ascending)

    print_df(df)
    print(f'Total: {df.shape[0]}')

if __name__ == '__main__':
    try:
        cli()
    except Exception as e:
        print(f'Exception: {e}')
    finally:
        CON.close()
        # print('Closed connection.')
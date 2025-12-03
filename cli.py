import click
import sqlite3
from rich import print
from pathlib import Path
from utils.movie import load_movies
from utils.db import get_connection
from utils.timing import timing

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
@click.option('--sort', help='Sort result by column')
@click.option('--note', help='Show notes', is_flag=True)
@click.option('--clean', help='Hide filtered column', is_flag=True)
@timing
def filter(
    name, year, status, movie_type, country, genres, rating, watched_year, note_contains,
    sort, note, clean
):
    """Filter movies by attributes."""

    # Prevent printing all movies to the command line when using with just flags
    filters = [name, year, status, movie_type, country, genres, rating, watched_year, note_contains]
    has_filter = any(arg is not None for arg in filters)
    if not has_filter:
        print('No filters specified. Use --help to see available options.')
        return
    
    from utils.cli import resolve_choice
    from utils.constants import MOVIE_STATUSES, MOVIE_TYPES, COUNTRIES, UNWATCHED_STATUS

    cur = CON.cursor()
    if status:
        status = resolve_choice(status, MOVIE_STATUSES)
    if movie_type:
        movie_type = resolve_choice(movie_type, MOVIE_TYPES)
    if country:
        country = resolve_choice(country, COUNTRIES)

    def get_filter_query(
        name, year, status, movie_type, country, genres, rating, watched_year, note_contains
    ) -> tuple[str, list]:
        """Build a parameterized SQL query for filtering movies."""

        clause = []
        parameters = []
        if name:
            clause.append('name LIKE ?')
            parameters.append(f'%{name}%')
        if year:
            clause.append('year = ?')
            parameters.append(year)
        if status:
            clause.append('status = ?')
            parameters.append(status)
        if movie_type:
            clause.append('type = ?')
            parameters.append(movie_type)
        if country:
            clause.append('country = ?')
            parameters.append(country)
        if genres:
            from utils.format import format_genres
            from utils.movie import get_genres

            all_genres = get_genres(cur)
            resolved_genres = []

            # Prefix match user input to full genre names
            # Example: "com" → "comedy" (but not "dark comedy")
            # This prevents LIKE '%com%' from matching wrong genres.
            for filter_genre in format_genres(genres):
                for genre in all_genres:
                    if genre.startswith(filter_genre):
                        resolved_genres.append(genre)
                        break
            
            # Exact genre match using comma-delimited boundaries
            for resolved_genre in resolved_genres:
                clause.append("',' || genres || ',' LIKE ?")
                parameters.append(f'%,{resolved_genre},%')
        if rating:
            clause.append('rating = ?')
            parameters.append(rating)
        if watched_year:            
            # Handle both full year and abbreviated year matching
            year_length = len(str(watched_year))
            clause.append(f'substr(watched_date, {4 - year_length + 1}, {year_length}) = ?')
            parameters.append(watched_year)
        if note_contains:
            clause.append('note LIKE ?')
            parameters.append(f'%{note_contains}%')
        
        where_clause = 'WHERE ' + ' AND '.join(clause)
        select_clause = 'SELECT * FROM movie_detail '
        query = select_clause + where_clause
        return query, parameters

    query, parameters = get_filter_query(
        name, year, status, movie_type, country, genres, rating, watched_year, note_contains
    )

    # Show note if note_contains is given
    note = True if note_contains else note

    # Handle sort order for specific column
    if sort:
        sort_orders = {
            'id': 'asc',
            'name': 'asc',
            'year': 'asc',
            'status': 'asc',
            'type': 'asc',
            'country': 'asc',
            # 'genres' - genres sorting is not intuitive
            'rating': 'desc',
            'watched_date': 'asc',
            # 'note' is conflict with 'name' abbreviation, also not intuitive
        }

        try:
            sort_order = resolve_choice(sort, list(sort_orders.keys()), strict=True)
            sort = (sort_order, sort_orders[sort_order])
        except ValueError as e:
            raise click.BadParameter(str(e))

    from utils.sql import run_sql
    from utils.cli import print_rows

    # Hide rating and watched_date column for unwatched movie
    hide_columns = ['rating', 'watched_date'] if status == UNWATCHED_STATUS else []

    # Hide filtered column
    if clean:
        if status:
            hide_columns.append('status')
        if movie_type:
            hide_columns.append('type')
        if country:
            hide_columns.append('country')

    rows, column_names = run_sql(cur, query, parameters=parameters, note=note, sort=sort)
    print_rows(rows, column_names, hide_columns=hide_columns, print_total=True)

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
@click.option('-n', '--note', help='Only update note', is_flag=True)
def update(movie_id, note):
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

    updated_data = prompt_update_movie(existing_movie, just_note=note)
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
    from utils.file import get_last_modified
    print(f'Backup last modified: {get_last_modified(BACKUP_FILE)}')
    click.confirm(
        'This will overwrite the existing backup file. Continue?', abort=True, default=True
    )

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

    from utils.file import get_last_modified
    print(f'Backup last modified: {get_last_modified(BACKUP_FILE)}')
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
@timing
def sql(filename, note, sort, verbose):
    """Run a SQL file from the 'sql/' folder."""
    from utils.sql import list_sql_files
    from utils.cli import print_sql_files

    sql_folder = Path('sql/')
    sql_files = list_sql_files(sql_folder)
    if not filename:
        print_sql_files(sql_files)
        return

    from utils.sql import resolve_sql_path
    sql_path, match_type = resolve_sql_path(filename, sql_folder, sql_files)
    if match_type is None:
        raise FileNotFoundError(f"No SQL file found matching '{filename}'")
    else:
        print(f"{match_type} match: '{sql_path.name}'")

    query = sql_path.read_text()
    if verbose:
        print(f'\n[dim]{query}[/dim]\n')

    from utils.sql import run_sql
    from utils.cli import print_rows

    cur = CON.cursor()
    rows, column_names = run_sql(cur, query, note=note, sort=sort)
    print_rows(rows, column_names, print_total=True)

@cli.command()
@click.argument('number', type=int, required=False, default=10)
@click.option('--note', help='Show notes', is_flag=True)
def recent(number, note):
    """
    Show recently watched movies.
    
    NUMBER  Number of movies to show (default: 10)
    """
    from utils.sql import run_sql
    from utils.cli import print_rows

    query = Path('sql/command/recent.sql').read_text()
    cur = CON.cursor()
    rows, column_names = run_sql(cur, query, parameters=(number,), note=note)
    print_rows(rows, column_names)

@cli.command()
@click.argument('number', type=int, required=False, default=10)
@click.option('--note', help='Show notes', is_flag=True)
def latest(number, note):
    """
    Show latest added movies.
    
    NUMBER  Number of movies to show (default: 10)
    """
    from utils.sql import run_sql
    from utils.cli import print_rows

    query = Path('sql/command/latest.sql').read_text()
    cur = CON.cursor()
    rows, column_names = run_sql(cur, query, parameters=(number,), note=note)
    print_rows(rows, column_names)

@cli.command()
@click.argument('keyword', type=str)
@click.option('--note', help='Show notes', is_flag=True)
@timing
def search(keyword, note):
    """
    Search movies by keyword.

    Default searches in 'name'. Use --note to search in 'note' and display it.
    """
    from utils.sql import run_sql
    from utils.cli import print_rows

    if note:
        query = "SELECT * FROM movie_detail WHERE note LIKE '%' || ? || '%'"
    else:
        query = "SELECT * FROM movie_detail WHERE name LIKE '%' || ? || '%'"

    cur = CON.cursor()
    rows, column_names = run_sql(cur, query, parameters=(keyword,), note=note)
    print_rows(rows, column_names)

@cli.command()
@timing
def optimize():
    """
    Optimize the SQLite database using VACUUM.
    Reclaims space, defragments pages, and rebuilds indexes.
    """
    from utils.file import get_file_size, convert_bytes

    before = get_file_size(DB_FILE)

    cur = CON.cursor()
    print('Optimizing database...')
    try:
        print('Running VACUUM...')
        cur.execute('VACUUM')
    except Exception as e:
        print(f'[red]Error during VACUUM:[/red] {e}')
        return

    after = get_file_size(DB_FILE)
    reduction = before - after
    percent = (reduction / before * 100)
    print(
        f'VACUUM completed. Size reduced from {convert_bytes(before)} to {convert_bytes(after)}'
        f' ({convert_bytes(reduction)}, {percent:.1f}% reduction).'
    )
    print('Database optimized successfully.')


if __name__ == '__main__':
    try:
        cli()
    except Exception as e:
        print(f'Exception: {e}')
    finally:
        CON.close()
        # print('Closed connection.')
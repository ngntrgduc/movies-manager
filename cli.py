import click
from rich import print

# The @st.cache_data decorator in utils.data is intended for Streamlit apps,
# but the CLI does not run inside a Streamlit runtime. 
# Therefore, we define a separate load_data function here without caching.
def load_data():
    """Return data as a pandas DataFrame."""
    import pandas as pd
    # return pd.read_csv('data.csv')
    return pd.read_csv('data/demo.csv', dtype={'note': 'string'})  

def resolve_choice(value: str, choices: list[str], strict: bool = False) -> str | None:
    """Resolve user input against choices with abbreviation and case-insensitive support."""
    lookup = {c[0].lower(): c for c in choices}     # abbreviation
    lookup.update({c.lower(): c for c in choices})  # lowercase

    value = value.strip().lower()
    if value in lookup:
        return lookup[value]
    
    if strict:
        raise ValueError(
            # Click-like error message
            f"{value!r} is not one of {', '.join(repr(c) for c in choices)} or their initials."
        )

    return None

def apply_filters(
        df, name=None, year=None, status=None, movie_type=None, 
        country=None, genres=None, rating=None, watched_year=None
):
    """Apply filters to the movie DataFrame."""
    import pandas as pd

    def filter_by_choice(series: pd.Series, value: str, choices: list[str]) -> pd.Series:
        """Return a boolean mask for rows where the series matches a resolved choice."""
        resolved = resolve_choice(value, choices)
        if resolved:
            return series == resolved
        
        return pd.Series(False, index=series.index)

    mask = pd.Series(True, index=df.index)
    if name:
        mask &= df['name'].str.contains(name, case=False, na=False)
    if year:
        mask &= df['year'] == year
    if watched_year:
        mask &= df['watched_date'].str[:4].str.endswith(watched_year)
    if status:
        mask &= filter_by_choice(df['status'], status, ['waiting', 'completed', 'dropped'])
    if movie_type:
        mask &= filter_by_choice(df['type'], movie_type, ['movie', 'series'])
    if country:
        mask &= filter_by_choice(df['country'], country, ['China', 'Japan', 'Korea', 'US'])
    if genres:
        genres = [genre.strip() for genre in genres.split(',')]
        genres_set = (
            df['genres'].fillna('') .apply(lambda x: {g.strip() for g in x.split(',') if g.strip()})
        )
        mask &= genres_set.apply(lambda g: set(genres).issubset(g))
    if rating:
        mask &= df['rating'] == rating

    return df[mask]

def print_stats(df, excluded: list = [], print_total: bool = True) -> None:
    """Print DataFrame statistics."""
    def print_value_counts(name: str, series) -> None:
        print(name)
        value_counts = series.value_counts()
        for value, count in value_counts.items():
            if count:
                print(f' - {value}: {count}')

    if print_total:
        print(f'Total: {df.shape[0]}')
    for col in ['status', 'type', 'country']:
        if col not in excluded:
            print_value_counts(col.capitalize(), df[col])

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
@click.option('--sort', help='Sort result by rating or watched date')
@click.option('--stats', help='Show statistics for the filtered results', is_flag=True)
@click.option('--note', help='Show notes', is_flag=True)
def filter(name, year, status, movie_type, country, genres, rating, watched_year, sort, stats, note):
    """Filter movies by attributes."""
    import pandas as pd

    def print_df(df: pd.DataFrame) -> None:
        """Display a DataFrame as a rich table."""
        from rich.console import Console
        from rich.table import Table

        # Remove empty columns (e.g., rating, watched_date for 'waiting' status)
        df = df.dropna(axis=1, how='all')

        table = Table(show_header=True, header_style='bold blue')
        for column in df.columns:
            table.add_column(column)

        for _, row in df.iterrows():
            table.add_row(*[str(x) if pd.notna(x) else '' for x in row])

        console = Console()
        console.print(table)

    df = load_data()
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
            resolved = resolve_choice(sort, ['rating', 'watched_date'], strict=True)
            ascending = resolved == 'watched_date'
            filtered_df = filtered_df.sort_values(by=[resolved], ascending=ascending)
        except ValueError as e:
            raise click.BadParameter(str(e))

    if not filtered_df.empty:
        print_df(filtered_df)
        print(f'Total: {filtered_df.shape[0]}')
        if stats:
            option_to_col = {
                'status': status,
                'type': movie_type,
                'country': country,
            }
            excluded = [col for col, val in option_to_col.items() if val]
            print_stats(filtered_df, excluded, print_total=False)
    else:
        print('No data.')


@cli.command()
def add():
    """Add a new movie interactively."""
    import pandas as pd
    from utils.cli import IntRangeOrNone
    from utils.date import get_current_year

    def format_genres(genres: str) -> str:
        """Normalize comma-separated genres by stripping whitespace and removing empties."""
        return ','.join(
            genre for genre in (g.strip() for g in genres.split(',')) if genre
        )

    class AbbrevChoice(click.Choice):
        """Choice type with abbreviation, case-insensitive matching."""
        def __init__(self, choices):
            super().__init__(choices)
        
        def convert(self, value, param, ctx):
            if isinstance(value, str) and value.strip() == '':
                return ''

            try:
                return resolve_choice(value, self.choices, strict=True)
            except ValueError as e:
                self.fail(str(e), param, ctx)

    skippable_settings = {'default': '', 'show_default': False}

    name = click.prompt('Name').strip()
    year = click.prompt(
        'Year', type=IntRangeOrNone(1900, get_current_year()), **skippable_settings
    )
    status = click.prompt(
        'Status', type=AbbrevChoice(['waiting', 'completed', 'dropped']), default='waiting'
    )
    movie_type = click.prompt('Type', type=AbbrevChoice(['movie', 'series']))
    country = click.prompt(
        'Country', type=AbbrevChoice(['China', 'Japan', 'Korea', 'US']), **skippable_settings
    )
    genres = click.prompt('Genres (comma-separated)', value_proc=format_genres)

    if status == 'waiting':
        rating = None
        watched_date = ''
    else:
        rating = click.prompt(
            'Rating', type=IntRangeOrNone(1, 10, clamp=True), **skippable_settings
        )
        
        def valid_date(date: str) -> str:
            from datetime import datetime
            if date.strip() == '':
                return ''

            formats = ['%Y', '%Y-%m', '%Y-%m-%d']
            for format in formats:
                try:
                    return datetime.strptime(date, format).strftime(format)
                except ValueError:
                    continue

            raise click.BadParameter(
                f"{date!r} does not match the formats 'YYYY', 'YYYY-MM', 'YYYY-MM-DD'"
            )

        watched_date = click.prompt('Watched date', value_proc=valid_date, **skippable_settings)

    note = click.prompt('Note', **skippable_settings).strip()

    new_record = {
        'name': name,
        'year': year,
        'status': status,
        'type': movie_type,
        'country': country,
        'genres': genres,
        'rating': rating,
        'watched_date': watched_date,
        'note': note
    }

    df = load_data()
    new_row = pd.DataFrame([new_record]).astype(df.dtypes.to_dict())
    new_df = pd.concat([df, new_row], ignore_index=True)
    # new_df.to_csv('data.csv', index=False)
    new_df.to_csv('data/demo.csv', index=False)
    print(f'Added {movie_type}: {name!r} ({year})')


@cli.command()
def stats():
    """Show statistics for the movie data."""
    df = load_data()
    # df.drop('note', axis=1, inplace=True)
    print_stats(df)

@cli.command()
def backup():
    """Back up data."""
    try:
        df = load_data()
        df.to_csv('backup.csv', index=False)
        print('Backup successful.')
    except Exception as e:
        print(f'Backup failed: {e}')

if __name__ == '__main__':
    cli()
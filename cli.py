import click
import pandas as pd
from rich import print

# The @st.cache_data decorator in utils.data is intended for Streamlit apps,
# but the CLI does not run inside a Streamlit runtime. 
# Therefore, we define a separate load_data function here without caching.
def load_data() -> pd.DataFrame:
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
        country=None, genres=None, watched_year=None
) -> pd.DataFrame:
    """Apply filters to the movie DataFrame."""

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

    return df[mask]

def print_stats(df: pd.DataFrame, excluded: list = [], print_total: bool = True) -> None:
    """Print DataFrame statistics."""
    def print_value_counts(name: str, series: pd.Series) -> None:
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
@click.option('-w', '--watched-year', help='Filter by watched year')
@click.option('--sort', help='Sort result by rating', is_flag=True)
@click.option('--stats', help='Show statistics for the filtered results', is_flag=True)
def filter(name, year, status, movie_type, country, genres, watched_year, sort, stats):
    """Filter movies by attributes."""
    
    def print_df(df: pd.DataFrame) -> None:
        """Display a DataFrame as a rich table."""
        from rich.console import Console
        from rich.table import Table

        console = Console()
        table = Table(show_header=True, header_style='bold blue')
        for column in df.columns:
            table.add_column(column)

        for _, row in df.iterrows():
            table.add_row(*[str(x) if pd.notna(x) else '' for x in row])

        console.print(table)

    df = load_data()
    # For table displaying purpose
    df['year'] = df['year'].astype('Int64')
    df['rating'] = df['rating'].astype('Int64')
    df.drop('note', axis=1, inplace=True)

    filtered_df = apply_filters(df, name, year, status, movie_type, country, genres, watched_year)
    if sort:
        filtered_df = filtered_df.sort_values(by='rating', ascending=False)
    
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
    """Add a new movie interactively (default status: waiting)."""
    def valid_year(year: str) -> int | None:
        """Validate year input, returning a number or None if blank."""
        from utils.date import get_current_year
        current_year = get_current_year()

        if year.strip() == '':
            return None

        try:
            year = int(year)
        except ValueError:
            raise click.BadParameter('Year must be a number')
        
        if year < 1900 or year > current_year:
            raise click.BadParameter(f'Year must be between 1900 and {current_year}')

        return year

    def format_genres(genres) -> str:
        """Normalize comma-separated genres by stripping whitespace and removing empties."""
        return ','.join(
            genre for genre in (g.strip() for g in genres.split(',')) if genre
        )

    def prompt_with_choice(text: str, choices: list[str], **kwargs) -> str:
        """Prompt user for input and resolve it against choices."""
        def value_proc(value):
            if not value.strip():   # allow skip
                return ''
            
            try:
                # raise ValueError on invalid input
                return resolve_choice(value, choices, strict=True)
            except ValueError as e:
                raise click.BadParameter(str(e))
        
        return click.prompt(f"{text} ({', '.join(choices)})", value_proc=value_proc, **kwargs)

    skippable_settings = {'default': '', 'show_default': False}

    name = click.prompt('Name')
    year = click.prompt('Year', value_proc=valid_year, **skippable_settings)
    status = prompt_with_choice(
        'Status', ['waiting', 'completed', 'dropped'], 
        **{'default': 'waiting', 'show_default': True}
    )
    movie_type = prompt_with_choice('Type', ['movie', 'series'])
    country = prompt_with_choice('Country', ['China', 'Japan', 'Korea', 'US'], **skippable_settings)
    genres = click.prompt('Genres (comma-separated)', value_proc=format_genres)

    if status != 'waiting':
        def valid_rating(rating):
            """Validate rating input, returning a number or None if blank."""
            if rating.strip() == '':
                return None
            
            try:
                rating = int(rating)
            except ValueError:
                raise click.BadParameter('Rating must be an integer')

            if rating < 1 or rating > 10:
                raise click.BadParameter(f'Rating must be between 1 and 10')

            return rating

        rating = click.prompt('Rating', value_proc=valid_rating, **skippable_settings)
        
        def valid_date(date):
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
    else:
        rating = None
        watched_date = ''

    note = click.prompt('Note', **skippable_settings)

    new_record = {
        'name': name.strip(),
        'year': year,
        'status': status,
        'type': movie_type,
        'country': country,
        'genres': genres,
        'rating': rating,
        'watched_date': watched_date,
        'note': note.strip()
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
    df.drop('note', axis=1, inplace=True)
    print_stats(df)


if __name__ == '__main__':
    cli()
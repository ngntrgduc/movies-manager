import click

class IntRangeOrNone(click.ParamType):
    """Extended click.IntRange type, allow blank by default."""
    name = 'integer'

    def __init__(self, min=None, max=None, clamp=False, allow_blank=True):
        self.min = min
        self.max = max
        self.clamp = clamp
        self.allow_blank = allow_blank

    def convert(self, value, param, ctx):
        # Handle blanks because Click does not return None when skipping input
        if isinstance(value, str) and value.strip() == '':
            if self.allow_blank:
                return None
            else:
                self.fail('This field cannot be blank', param, ctx)

        try:
            ivalue = int(value)
        except (TypeError, ValueError):
            self.fail(f'{value!r} must be an integer', param, ctx)

        if self.clamp:
            if self.min is not None and ivalue < self.min:
                return self.min
            if self.max is not None and ivalue > self.max:
                return self.max

        if self.min is not None and ivalue < self.min:
            self.fail(f'Value must be at least {self.min}', param, ctx)
        if self.max is not None and ivalue > self.max:
            self.fail(f'Value must be at most {self.max}', param, ctx)

        return ivalue

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

class AbbrevChoice(click.Choice):
    """Choice type with abbreviation and case-insensitive matching."""
    def __init__(self, choices):
        super().__init__(choices)

    def convert(self, value, param, ctx):
        if isinstance(value, str) and value.strip() == '':
            return None

        try:
            return resolve_choice(value, self.choices, strict=True)
        except ValueError as e:
            self.fail(str(e), param, ctx)

def valid_date(date: str) -> str:
    from datetime import datetime
    if date.strip() == '':
        return ''

    for format in ('%Y', '%Y-%m', '%Y-%m-%d'):
        try:
            return datetime.strptime(date, format).strftime(format)
        except ValueError:
            continue

    raise click.BadParameter(
        f"{date!r} does not match the formats 'YYYY', 'YYYY-MM', 'YYYY-MM-DD'"
    )

def print_df(df) -> None:
    """Display a DataFrame in a Rich table."""
    import pandas as pd
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

def print_rows(rows: list[tuple], headers: list[str], title: str = None) -> None:
    """Display rows in a Rich table."""
    from rich.console import Console
    from rich.table import Table
    
    table = Table(
        title=title, title_justify='left', title_style='bold',
        show_header=True, header_style='bold blue'
    )
    for header in headers:
        table.add_column(header)

    for row in rows:
        table.add_row(*[str(x) if x is not None else '' for x in row])

    console = Console()
    console.print(table)

def apply_filters(
    df, name=None, year=None, status=None, movie_type=None, 
    country=None, genres=None, rating=None, watched_year=None, note_contains=None
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
        from utils.format import format_genres
        genres = format_genres(genres)
        genres_set = df['genres'].fillna('').apply(lambda g: format_genres(g, as_set=True))
        set_mask = genres_set.apply(lambda g: set(genres).issubset(g))
        if set_mask.any():
            mask &= set_mask
        else:
            # Fallback fuzzy matching using substring search
            def fuzzy_match(row: str) -> bool:
                row_genres = format_genres(row)
                return all(
                    any(search_genre in genre for genre in row_genres)
                    for search_genre in genres
                )

            fuzzy_mask = df['genres'].fillna('').apply(fuzzy_match)
            mask &= fuzzy_mask
    if rating:
        mask &= df['rating'] == rating
    if note_contains:
        mask &= df['note'].str.contains(note_contains, case=False, na=False)

    # prevent showing all rows after filtering
    if mask.all():
        mask[:] = False

    return df[mask]

def print_sql_files(sql_files: list[str]) -> None:
    """Print a list of available SQL files."""
    from rich.columns import Columns
    from rich.console import Console
    console = Console(width=60)
    console.print('[bold cyan]Available SQL files:[/bold cyan]')
    colored_files = [f'[green]{name}[/green]' for name in sql_files]
    console.print(Columns(colored_files, equal=True, expand=True))
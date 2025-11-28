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

def print_rows(
    rows: list[tuple],
    headers: list[str],
    title: str = None,
    hide_columns: list[str] | None = None,
    print_total: bool = False,
) -> None:
    """Display rows in a Rich table with optional hidden columns."""
    
    if len(rows) == 0:
        print('No data.')
        return

    from rich.console import Console
    from rich.table import Table
    
    # Determine columns to display
    hide_columns = hide_columns or []
    filtered_headers = [h for h in headers if h not in hide_columns]
    keep_indexes = [i for i, h in enumerate(headers) if h not in hide_columns]

    table = Table(
        title=title, title_justify='left', title_style='bold',
        show_header=True, header_style='bold blue'
    )
    for header in filtered_headers:
        table.add_column(header)

    for row in rows:
        table.add_row(
            *[
                str(value) if (value := row[i]) is not None else '' 
                for i in keep_indexes
            ]
        )

    console = Console()
    console.print(table)
    console.print(f'Total: {len(rows)}')

def print_sql_files(sql_files: list[str]) -> None:
    """Print a list of available SQL files."""
    from rich.columns import Columns
    from rich.console import Console
    console = Console(width=60)
    console.print('[bold cyan]Available SQL files:[/bold cyan]')
    colored_files = [f'[green]{name}[/green]' for name in sql_files]
    console.print(Columns(colored_files, equal=True, expand=True))
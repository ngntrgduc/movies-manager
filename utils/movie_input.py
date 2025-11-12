import click
from utils.cli import IntRangeOrNone, AbbrevChoice, valid_date
from utils.date import get_current_year

def format_genres(genres: str) -> str:
    """Normalize comma-separated genres by stripping whitespace and removing empties."""
    return ','.join(
        genre for genre in (g.strip() for g in genres.split(',')) if genre
    )

def prompt_add_movie() -> dict:
    """Prompt the user interactively to add a new movie and return the data as a dictionary."""

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
        watched_date = None
    else:
        rating = click.prompt('Rating', type=IntRangeOrNone(1, 10, clamp=True), **skippable_settings)
        watched_date = click.prompt('Watched date', value_proc=valid_date, **skippable_settings)
        if not watched_date:
            watched_date = None

    note = click.prompt('Note', **skippable_settings).strip()
    if not note:
        note = None

    return {
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
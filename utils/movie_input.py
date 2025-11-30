import click
from utils.cli import IntRangeOrNone, AbbrevChoice, valid_date
from utils.date import get_current_year
from utils.format import format_genres
from utils.constants import MOVIE_STATUSES, MOVIE_TYPES, COUNTRIES, UNWATCHED_STATUS

def prompt_add_movie() -> dict:
    """Prompt the user interactively to add a new movie and return the data as a dictionary."""

    skippable_settings = {'default': '', 'show_default': False}

    name = click.prompt('Name').strip()
    year = click.prompt(
        'Year', type=IntRangeOrNone(1900, get_current_year()), **skippable_settings
    )
    status = click.prompt('Status', type=AbbrevChoice(MOVIE_STATUSES), default=UNWATCHED_STATUS)
    movie_type = click.prompt('Type', type=AbbrevChoice(MOVIE_TYPES))
    country = click.prompt('Country', type=AbbrevChoice(COUNTRIES), **skippable_settings)
    genres = click.prompt('Genres (comma-separated)', value_proc=format_genres)

    if status == UNWATCHED_STATUS:
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

def prompt_update_movie(existing_movie: dict) -> dict:
    """Prompt the user interactively for fields to update, return only changed fields."""

    def default_setting(default_value: str | int | float | None) -> dict:
        return {'default': default_value, 'show_default': False}

    # Handle None value to be compatible with click.prompt by convert it to empty string
    for field, value in existing_movie.items():
        if value is None:
            existing_movie[field] = ''

    movie = {}
    print('Press Enter to keep old value')
    movie['name'] = click.prompt('Name', **default_setting(existing_movie['name'])).strip()
    movie['year'] = click.prompt(
        'Year', type=IntRangeOrNone(1900, get_current_year()),
        **default_setting(existing_movie['year'])
    )
    movie['status'] = click.prompt(
        'Status', type=AbbrevChoice(MOVIE_STATUSES), **default_setting(existing_movie['status'])
    )
    movie['type'] = click.prompt(
        'Type', type=AbbrevChoice(MOVIE_TYPES), **default_setting(existing_movie['type'])
    )
    movie['country'] = click.prompt(
        'Country', type=AbbrevChoice(COUNTRIES), **default_setting(existing_movie['country'])
    )
    movie['genres'] = click.prompt(
        'Genres (comma-separated)', value_proc=format_genres,
          **default_setting(existing_movie['genres'])
    )

    if movie['status'] == UNWATCHED_STATUS:
        movie['rating'] = None
        movie['watched_date'] = None
    else:
        movie['rating'] = click.prompt(
            'Rating', type=IntRangeOrNone(1, 10, clamp=True),
            **default_setting(existing_movie['rating'])
        )
        watched_date = click.prompt(
            'Watched date', value_proc=valid_date, **default_setting(existing_movie['watched_date'])
        )
        movie['watched_date'] = watched_date if watched_date else None

    note = click.prompt('Note', **default_setting(existing_movie['note'])).strip()
    movie['note'] = note if note else None

    # Re-convert empty string to None for SQLite compatible and comparison with updated data
    for field, value in existing_movie.items():
        if value == '':
            existing_movie[field] = None
    
    # Ensure genres format of the new movie matches the format of the old movie,
    # prevent genres from being displayed when updating without genre updates
    existing_movie['genres'] = format_genres(existing_movie['genres'])

    # Only include fields that have changed compared to the existing movie
    updated_data = {field: value for field, value in movie.items()
                    if value != existing_movie[field]}
    return updated_data
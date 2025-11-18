def format_genres(genres: str, as_set: bool = False) -> list[str] | set[str]:
    """
    Normalize a comma-separated string of genres by stripping whitespace, \\
    removing empties and return them as a list or a set.
    
    Example:
        >>> format_genres(" action, romance , ,, comedy ")
        # ['action', 'romance', 'comedy']

        >>> format_genres(" action, romance , ,, comedy ", as_set=True)
        # {'action', 'romance', 'comedy'}
    """

    # return [genre for genre in (g.strip() for g in genres.split(',')) if genre]
    formatted = [genre for g in genres.split(',') if (genre := g.strip())]
    return set(formatted) if as_set else formatted

# if __name__ == '__main__':
#     print(format_genres(" action, romance , ,, comedy "))
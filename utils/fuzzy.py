def get_fuzzy_match(value: str, choices: list[str], n: int = 1) -> str | None:
    """Return the closest fuzzy match to `value` among `choices`."""
    from difflib import get_close_matches

    matches = get_close_matches(value, choices, n=n)
    return matches[0] if matches else None

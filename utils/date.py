"""Date utilities"""

def get_year(date: str | float) -> int:
    """Return year of a date as integer"""
    # return str(date).split('-')[0]
    return int(str(date)[:4])  # slicing is faster than spliting

def get_today() -> str:
    """Return current date as string"""
    from datetime import date
    return date.today().isoformat()

def get_current_year() -> int:
    """Return current year as integer"""
    from datetime import date
    return date.today().year
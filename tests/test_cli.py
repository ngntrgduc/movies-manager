import pytest
from utils.cli import resolve_choice, valid_date
from utils.constants import MOVIE_STATUSES, MOVIE_TYPES, COUNTRIES

def test_resolve_choice():
    assert resolve_choice('k', COUNTRIES) == 'Korea'
    assert resolve_choice('K', COUNTRIES) == 'Korea'
    assert resolve_choice('w', MOVIE_STATUSES) == 'waiting'
    assert resolve_choice('s', MOVIE_TYPES) == 'series'

def test_invalid_choice():
    assert resolve_choice('x', MOVIE_TYPES) is None
    assert resolve_choice('ab', MOVIE_TYPES) is None

def test_same_initial():
    with pytest.xfail(reason="Resolve choice can't handle same initials yet"):
        assert resolve_choice('a', ['abc', 'abcd', 'aaa']) == 'abc'

def test_valid_date():
    assert valid_date('2025') == '2025'
    assert valid_date('2025-12') == '2025-12'
    assert valid_date('2025-12-06') == '2025-12-06'

def test_valid_date_with_empty_input():
    assert valid_date('') == ''
    assert valid_date('  ') == ''

@pytest.mark.parametrize('test_input, expected', [
    pytest.param('202', '202', marks=pytest.mark.xfail(reason='Invalid date format')),
])
def test_invalid_date(test_input: str, expected: int):
    assert valid_date(test_input) == expected
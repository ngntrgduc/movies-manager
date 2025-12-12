import pytest
from utils.cli import resolve_choice
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

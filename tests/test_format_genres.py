import pytest
from utils.format import format_genres

def test_commas_and_space():
    assert format_genres(' ') == []
    assert format_genres(',') == []

def test_example():
    assert format_genres(" action, romance , ,, comedy ") == ['action', 'romance', 'comedy']
    assert format_genres(" action, romance , ,, comedy ", as_set=True) == {'action', 'romance', 'comedy'}

@pytest.mark.parametrize('test_input, expected', [
    pytest.param([], [], marks=pytest.mark.xfail(reason='Expected string, not list'))
])
def test_genres_list(test_input: str, expected: list[str]):
    assert format_genres(test_input) == expected
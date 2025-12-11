import pytest
from utils.cli import valid_date

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
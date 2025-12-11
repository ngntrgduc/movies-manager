import pytest
from utils.date import get_year

@pytest.mark.parametrize('test_input, expected', [
    ('2025', 2025),
    ('2025-12', 2025),
])
def test_get_year(test_input: str, expected: int):
    assert get_year(test_input) == expected
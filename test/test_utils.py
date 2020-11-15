import pytest

from util import normalize


@pytest.mark.parametrize("s,expected", [("Andalucía", 'Andalucia'), ("Jaén", 'Jaen'), ("Andújar", 'Andujar'),
                                         ("España", 'Espana'), ("Málaga", 'Malaga'), ("Castellón", 'Castellon'),
                                         ("C. Valenciana", 'CValenciana')])
def test_normalize(s, expected):
    assert normalize(s) == expected
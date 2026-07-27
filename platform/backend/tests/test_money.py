from decimal import Decimal

from app.core.money import Money


def test_from_euros_is_cent_accurate():
    m = Money.from_euros("199999.99")
    assert m.cents == 19999999
    assert m.euros == Decimal("199999.99")


def test_format_de_uses_german_separators():
    m = Money.from_euros("1234567.89")
    assert m.format_de() == "1.234.567,89 €"


def test_arithmetic_stays_cent_accurate():
    a = Money.from_euros("100.10")
    b = Money.from_euros("50.05")
    assert (a - b).cents == 5005
    assert (a + b).cents == 15015

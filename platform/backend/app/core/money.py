"""Money handling per Regel C.31 (cent-accurate) and Regel C.38 (German
formatting). Money is always stored and computed as integer cents so that
no floating point rounding can creep into currency arithmetic.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal


@dataclass(frozen=True, slots=True)
class Money:
    cents: int
    currency: str = "EUR"

    @classmethod
    def from_euros(cls, amount: Decimal | str | int | float, currency: str = "EUR") -> "Money":
        d = Decimal(str(amount))
        cents = int((d * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        return cls(cents=cents, currency=currency)

    @property
    def euros(self) -> Decimal:
        return (Decimal(self.cents) / Decimal(100)).quantize(Decimal("0.01"))

    def __add__(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        return Money(self.cents + other.cents, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        return Money(self.cents - other.cents, self.currency)

    def __neg__(self) -> "Money":
        return Money(-self.cents, self.currency)

    def __mul__(self, factor: Decimal | int | float) -> "Money":
        d = Decimal(str(factor))
        cents = int((Decimal(self.cents) * d).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        return Money(cents, self.currency)

    def __lt__(self, other: "Money") -> bool:
        self._assert_same_currency(other)
        return self.cents < other.cents

    def __le__(self, other: "Money") -> bool:
        self._assert_same_currency(other)
        return self.cents <= other.cents

    def _assert_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise ValueError(f"currency mismatch: {self.currency} vs {other.currency}")

    def format_de(self) -> str:
        """Regel C.38: render as German-style EUR amount, e.g. '1.234.567,89 €'."""
        euros = self.euros
        sign = "-" if euros < 0 else ""
        whole, _, frac = f"{abs(euros):.2f}".partition(".")
        grouped = f"{int(whole):,}".replace(",", ".")
        return f"{sign}{grouped},{frac} €"

    def to_json(self) -> dict:
        return {"cents": self.cents, "currency": self.currency, "formatted_de": self.format_de()}

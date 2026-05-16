from decimal import Decimal, ROUND_HALF_UP


MONEY_PLACES = Decimal("0.01")
PRICE_PLACES = Decimal("0.000001")
SHARE_PLACES = Decimal("0.000001")


def quantize_money(value: Decimal | None) -> Decimal | None:
    if value is None:
        return None

    return value.quantize(MONEY_PLACES, rounding=ROUND_HALF_UP)


def quantize_price(value: Decimal | None) -> Decimal | None:
    if value is None:
        return None

    return value.quantize(PRICE_PLACES, rounding=ROUND_HALF_UP)


def quantize_shares(value: Decimal | None) -> Decimal | None:
    if value is None:
        return None

    return value.quantize(SHARE_PLACES, rounding=ROUND_HALF_UP)

def annualization_factor(dividend_frequency: str | None) -> Decimal:
    if dividend_frequency is None:
        return Decimal("4")

    frequency = dividend_frequency.lower().strip()

    mapping = {
        "monthly": Decimal("12"),
        "quarterly": Decimal("4"),
        "semiannual": Decimal("2"),
        "semi-annual": Decimal("2"),
        "semi_annually": Decimal("2"),
        "annual": Decimal("1"),
        "annually": Decimal("1"),
    }

    return mapping.get(frequency, Decimal("4"))

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any


@dataclass
class ImportColumnMapping:
    symbol: str
    company: str
    quantity: str
    price: str


@dataclass
class ImportedHolding:
    row_number: int
    symbol: str
    company: str
    quantity: Decimal
    price: Decimal


@dataclass
class ImportValidationError:
    row_number: int
    field: str
    message: str
    raw_value: Any = None


@dataclass
class ImportDryRunResult:
    rows_detected: int = 0
    valid_rows: int = 0
    invalid_rows: int = 0

    warnings: list[str] = field(default_factory=list)

    validation_errors: list[ImportValidationError] = field(default_factory=list)

    sample_rows: list[ImportedHolding] = field(default_factory=list)

    would_create_securities: list[str] = field(default_factory=list)

    would_create_positions: list[str] = field(default_factory=list)

    would_create_transactions: int = 0

    would_create_watchlist_items: list[str] = field(default_factory=list)

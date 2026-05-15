from decimal import Decimal, InvalidOperation
from pathlib import Path

import pandas as pd

from app.services.imports.models import (
    ImportColumnMapping,
    ImportedHolding,
    ImportValidationError,
)


SUPPORTED_EXTENSIONS = {".ods", ".xlsx", ".xls", ".csv"}

def detect_file_type(file_path: str) -> str:
    suffix = Path(file_path).suffix.lower()

    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file extension: {suffix}")

    return suffix

def _detect_engine(path: Path) -> str:
    suffix = detect_file_type(str(path))

    if suffix == ".ods":
        return "odf"

    if suffix == ".xlsx":
        return "openpyxl"

    if suffix == ".xls":
        return "xlrd"

    raise ValueError(f"Unsupported file extension: {suffix}")


def load_spreadsheet(
    file_path: str,
    sheet_name: str | None = None,
) -> pd.DataFrame:
    path = Path(file_path)

    suffix = detect_file_type(file_path)

    if suffix == ".csv":
        return pd.read_csv(path)

    engine = _detect_engine(path)

    return pd.read_excel(
        path,
        sheet_name=sheet_name,
        engine=engine,
    )


def parse_holdings_dataframe(
    dataframe: pd.DataFrame,
    mapping: ImportColumnMapping,
) -> tuple[list[ImportedHolding], list[ImportValidationError]]:
    holdings: list[ImportedHolding] = []
    errors: list[ImportValidationError] = []

    for index, row in dataframe.iterrows():
        row_number = index + 2

        mapped_values = [
            row.get(mapping.symbol),
            row.get(mapping.company),
            row.get(mapping.quantity),
            row.get(mapping.price),
        ]

        if all(pd.isna(value) for value in mapped_values):
            continue

        symbol_raw = row.get(mapping.symbol)
        company_raw = row.get(mapping.company)

        symbol_text = "" if pd.isna(symbol_raw) else str(symbol_raw).strip().upper()
        company_text = "" if pd.isna(company_raw) else str(company_raw).strip().upper()

        if not symbol_text:
            continue

        if symbol_text == "CASH":
            continue

        if company_text.startswith("TTL"):
            continue

        try:
            symbol = str(row[mapping.symbol]).strip().upper()
            company = str(row[mapping.company]).strip()

            quantity_raw = row[mapping.quantity]
            price_raw = row[mapping.price]

            quantity = Decimal(str(quantity_raw))
            price = Decimal(str(price_raw))

            if not symbol:
                raise ValueError("Missing symbol")

            if quantity < 0:
                raise ValueError("Quantity cannot be negative")

            if price < 0:
                raise ValueError("Price cannot be negative")

            holdings.append(
                ImportedHolding(
                    row_number=row_number,
                    symbol=symbol,
                    company=company,
                    quantity=quantity,
                    price=price,
                )
            )

        except (InvalidOperation, ValueError, KeyError) as exc:
            errors.append(
                ImportValidationError(
                    row_number=row_number,
                    field="row",
                    message=str(exc),
                    raw_value=dict(row),
                )
            )

    return holdings, errors

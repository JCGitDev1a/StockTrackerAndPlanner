import csv
from decimal import Decimal
from pathlib import Path

from sqlalchemy.orm import Session

from app.services.market_data_import_service import (
    import_price_rows,
)


REQUIRED_COLUMNS = {
    "symbol",
    "price_date",
    "price",
}


def import_market_data_csv(
    db: Session,
    csv_path: str | Path,
    source_provider: str = "csv",
) -> dict:
    csv_path = Path(csv_path)

    if not csv_path.exists():
        raise FileNotFoundError(
            f"CSV file not found: {csv_path}"
        )

    rows: list[dict] = []

    with csv_path.open(
        newline="",
        encoding="utf-8",
    ) as csvfile:
        reader = csv.DictReader(csvfile)

        if reader.fieldnames is None:
            raise ValueError(
                "CSV file has no header row"
            )

        missing_columns = (
            REQUIRED_COLUMNS
            - set(reader.fieldnames)
        )

        if missing_columns:
            raise ValueError(
                "Missing required columns: "
                + ", ".join(
                    sorted(missing_columns)
                )
            )

        for line_number, row in enumerate(
            reader,
            start=2,
        ):
            try:
                symbol = (
                    row["symbol"]
                    .strip()
                    .upper()
                )

                price_date = row[
                    "price_date"
                ].strip()

                price = Decimal(
                    row["price"].strip()
                )

                rows.append(
                    {
                        "symbol": symbol,
                        "price_date": price_date,
                        "price": price,
                    }
                )

            except Exception as exc:
                raise ValueError(
                    f"Invalid row at line "
                    f"{line_number}: {exc}"
                ) from exc

    return import_price_rows(
        db=db,
        rows=rows,
        source_provider=source_provider,
    )

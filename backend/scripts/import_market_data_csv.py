import sys
from pathlib import Path

from app.db.session import SessionLocal

from app.services.market_data_csv_import import (
    import_market_data_csv,
)


def main() -> None:
    if len(sys.argv) != 2:
        print(
            "Usage: python "
            "scripts/import_market_data_csv.py "
            "<csv_file>"
        )
        sys.exit(1)

    csv_path = Path(sys.argv[1])

    db = SessionLocal()

    try:
        result = import_market_data_csv(
            db=db,
            csv_path=csv_path,
            source_provider="csv",
        )

        print("\nImport Results")
        print("----------------")

        print(
            f"Created: "
            f"{len(result['created'])}"
        )

        print(
            f"Updated: "
            f"{len(result['updated'])}"
        )

        print(
            f"Missing Securities: "
            f"{len(result['missing_securities'])}"
        )

        print(
            f"Invalid Rows: "
            f"{len(result['invalid_rows'])}"
        )

        if result["missing_securities"]:
            print(
                "\nMissing Securities:"
            )

            for symbol in result[
                "missing_securities"
            ]:
                print(f"  {symbol}")

        if result["invalid_rows"]:
            print("\nInvalid Rows:")

            for row in result[
                "invalid_rows"
            ]:
                print(row)

    finally:
        db.close()


if __name__ == "__main__":
    main()

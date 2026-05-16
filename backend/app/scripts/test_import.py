import argparse
from pprint import pprint

from app.services.imports.import_service import dry_run_import
from app.services.imports.models import ImportColumnMapping

from datetime import date

from app.db.session import SessionLocal
from app.services.imports.database_importer import import_holdings
from app.services.imports.parsers.spreadsheet_parser import (
    load_spreadsheet,
    parse_holdings_dataframe,
)

DEFAULT_SYMBOL_COLUMN = "Sym"
DEFAULT_COMPANY_COLUMN = "Company"
DEFAULT_QUANTITY_COLUMN = "Qty"
DEFAULT_PRICE_COLUMN = "B P"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Dry-run holdings import from ODS, XLSX, XLS, or CSV."
    )

    parser.add_argument(
        "--file",
        required=True,
        help="Path to import file, such as /app/data/Holdings-2026-02-08-clean.ods",
    )

    parser.add_argument(
        "--sheet",
        required=False,
        default=None,
        help="Sheet name for spreadsheet files. Ignored for CSV.",
    )

    parser.add_argument(
        "--symbol-column",
        default=DEFAULT_SYMBOL_COLUMN,
        help=f"Column name containing ticker symbols. Default: {DEFAULT_SYMBOL_COLUMN}",
    )

    parser.add_argument(
        "--company-column",
        default=DEFAULT_COMPANY_COLUMN,
        help=f"Column name containing company/security names. Default: {DEFAULT_COMPANY_COLUMN}",
    )

    parser.add_argument(
        "--quantity-column",
        default=DEFAULT_QUANTITY_COLUMN,
        help=f"Column name containing share quantity. Default: {DEFAULT_QUANTITY_COLUMN}",
    )

    parser.add_argument(
        "--price-column",
        default=DEFAULT_PRICE_COLUMN,
        help=f"Column name containing price or basis price. Default: {DEFAULT_PRICE_COLUMN}",
    )

    parser.add_argument(
        "--commit",
        action="store_true",
        help="Actually import holdings into the database.",
    )

    parser.add_argument(
        "--account-id",
        required=False,
        help="Account UUID for database import.",
    )

    parser.add_argument(
        "--start-date",
        required=False,
        default="2026-02-08",
        help="Opening transaction date (YYYY-MM-DD).",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    mapping = ImportColumnMapping(
        symbol=args.symbol_column,
        company=args.company_column,
        quantity=args.quantity_column,
        price=args.price_column,
    )

    result = dry_run_import(
        file_path=args.file,
        sheet_name=args.sheet,
        mapping=mapping,
    )

    print("\n=== IMPORT SUMMARY ===")
    print(f"Rows detected: {result.rows_detected}")
    print(f"Valid rows: {result.valid_rows}")
    print(f"Invalid rows: {result.invalid_rows}")
    print(f"Transactions to create: {result.would_create_transactions}")

    print("\n=== COLUMN MAPPING ===")
    print(f"Symbol:   {args.symbol_column}")
    print(f"Company:  {args.company_column}")
    print(f"Quantity: {args.quantity_column}")
    print(f"Price:    {args.price_column}")

    print("\n=== SECURITIES ===")
    pprint(result.would_create_securities)

    print("\n=== POSITIONS ===")
    pprint(result.would_create_positions)

    print("\n=== WATCHLIST ===")
    pprint(result.would_create_watchlist_items)

    print("\n=== SAMPLE ROWS ===")
    pprint(result.sample_rows[:5])

    print("\n=== VALIDATION ERRORS ===")
    pprint(result.validation_errors[:10])

    if not args.commit:
        print("\nDry-run only. No database changes made.")
        return

    if not args.account_id:
        raise ValueError("--account-id is required with --commit")

    dataframe = load_spreadsheet(
        file_path=args.file,
        sheet_name=args.sheet,
    )

    holdings, errors = parse_holdings_dataframe(
        dataframe=dataframe,
        mapping=mapping,
    )

    if errors:
        raise ValueError(
            f"Import contains validation errors: {len(errors)}"
        )

    db = SessionLocal()

    try:
        import_result = import_holdings(
            db=db,
            account_id=args.account_id,
            holdings=holdings,
            start_date=date.fromisoformat(args.start_date),
        )

        print("\n=== DATABASE IMPORT RESULT ===")
        pprint(import_result)

    finally:
        db.close()

if __name__ == "__main__":
    main()

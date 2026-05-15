from app.services.imports.models import (
    ImportColumnMapping,
    ImportDryRunResult,
)
from app.services.imports.parsers.spreadsheet_parser import (
    load_spreadsheet,
    parse_holdings_dataframe,
)


def dry_run_import(
    file_path: str,
    sheet_name: str | None,
    mapping: ImportColumnMapping,
) -> ImportDryRunResult:
    dataframe = load_spreadsheet(
        file_path=file_path,
        sheet_name=sheet_name,
    )

    holdings, errors = parse_holdings_dataframe(
        dataframe=dataframe,
        mapping=mapping,
    )

    result = ImportDryRunResult()

    result.rows_detected = len(dataframe.index)
    result.valid_rows = len(holdings)
    result.invalid_rows = len(errors)

    result.validation_errors.extend(errors)

    result.sample_rows.extend(holdings[:10])

    for holding in holdings:
        result.would_create_securities.append(holding.symbol)

        if holding.quantity == 0:
            result.would_create_watchlist_items.append(
                holding.symbol
            )
        else:
            result.would_create_positions.append(
                holding.symbol
            )
            result.would_create_transactions += 1

    result.would_create_securities = sorted(
        list(set(result.would_create_securities))
    )

    result.would_create_positions = sorted(
        list(set(result.would_create_positions))
    )

    result.would_create_watchlist_items = sorted(
        list(set(result.would_create_watchlist_items))
    )

    return result

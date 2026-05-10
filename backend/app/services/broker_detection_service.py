from typing import Iterable


def normalize_headers(headers: Iterable[str]) -> set[str]:
    return {
        str(h).strip().lower()
        for h in headers
        if h
    }


def detect_source_from_headers(headers: Iterable[str]) -> str:
    normalized = normalize_headers(headers)

    ibkr_headers = {
        "symbol",
        "buy/sell",
        "quantity",
        "tradeprice",
        "date/time",
    }

    mt5_headers = {
        "symbol",
        "type",
        "volume",
        "price",
        "time",
    }

    canonical_csv_headers = {
        "symbol",
        "side",
        "quantity",
        "price",
        "timestamp",
    }

    if ibkr_headers.issubset(normalized):
        return "ibkr"

    if mt5_headers.issubset(normalized):
        return "mt5"

    if canonical_csv_headers.issubset(normalized):
        return "csv"

    return "unknown"
from .trade_normalizer import (
    normalize_side,
    normalize_symbol,
    parse_rows_by_source,
    parse_datetime,
    process_import_rows,
    safe_float,
    build_trade_fingerprint,
    generate_trade_hash,
)


def build_import_job_payload(
    workspace_id: int,
    source_type: str,
    filename: str | None = None,
    mode: str = "manual",
):
    return {
        "workspace_id": workspace_id,
        "source_type": source_type,
        "filename": filename,
        "mode": mode,
    }


def build_stream_event_payload(
    workspace_id: int,
    source_type: str,
    trade: dict,
):
    return {
        "workspace_id": workspace_id,
        "source_type": source_type,
        "event_type": "trade",
        "trade": trade,
    }


__all__ = [
    "normalize_side",
    "normalize_symbol",
    "parse_rows_by_source",
    "parse_datetime",
    "process_import_rows",
    "safe_float",
    "build_trade_fingerprint",
    "generate_trade_hash",
    "build_import_job_payload",
    "build_stream_event_payload",
]
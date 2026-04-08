from __future__ import annotations

from typing import Any, Dict, List, Tuple, Set
from datetime import datetime
import csv
from io import StringIO


# ----------------------------------------
# LOW-LEVEL HELPERS
# ----------------------------------------

def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        if isinstance(value, str):
            value = value.replace(",", "").strip()
        return float(value)
    except Exception:
        return default


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def normalize_symbol(value: Any) -> str:
    return normalize_text(value).upper()


def normalize_timestamp(value: Any) -> str | None:
    raw = normalize_text(value)
    if not raw:
        return None

    # foundation only: preserve input when parse is uncertain
    # if parse succeeds, convert to ISO-like string
    candidates = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y.%m.%d %H:%M:%S",
        "%Y.%m.%d %H:%M",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M",
    ]

    for fmt in candidates:
        try:
            dt = datetime.strptime(raw, fmt)
            return dt.isoformat(sep=" ")
        except Exception:
            pass

    return raw


def normalize_side(value: Any) -> str:
    if not value:
        return "unknown"

    v = normalize_text(value).lower()

    if v in ["buy", "long", "b"]:
        return "buy"
    if v in ["sell", "short", "s"]:
        return "sell"

    return "unknown"


def build_trade_fingerprint(trade: Dict[str, Any]) -> str:
    return "|".join(
        [
            normalize_symbol(trade.get("symbol")),
            normalize_side(trade.get("side")),
            str(safe_float(trade.get("quantity"))),
            str(safe_float(trade.get("price"))),
            str(safe_float(trade.get("pnl"))),
            normalize_text(trade.get("timestamp")),
            normalize_text(trade.get("external_id")),
            normalize_text(trade.get("source_type")),
        ]
    )


# ----------------------------------------
# SOURCE-SPECIFIC ROW MAPPERS
# ----------------------------------------

def map_csv_row(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "symbol": row.get("symbol") or row.get("Symbol"),
        "side": row.get("side") or row.get("Side"),
        "quantity": row.get("quantity") or row.get("Qty"),
        "price": row.get("price") or row.get("Price"),
        "pnl": row.get("pnl") or row.get("PnL"),
        "timestamp": row.get("timestamp") or row.get("Time"),
        "external_id": row.get("id") or row.get("Ticket"),
        "source_type": "csv",
        "raw_row": row,
    }


def map_mt5_row(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "symbol": row.get("Symbol") or row.get("symbol"),
        "side": row.get("Type") or row.get("type") or row.get("side"),
        "quantity": row.get("Volume") or row.get("volume") or row.get("quantity"),
        "price": row.get("Price") or row.get("price"),
        "pnl": row.get("Profit") or row.get("profit") or row.get("pnl"),
        "timestamp": row.get("Time") or row.get("time") or row.get("timestamp"),
        "external_id": row.get("Ticket") or row.get("ticket") or row.get("id"),
        "source_type": "mt5",
        "raw_row": row,
    }


def map_ibkr_row(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "symbol": row.get("Symbol") or row.get("symbol"),
        "side": row.get("Buy/Sell") or row.get("buy_sell") or row.get("side"),
        "quantity": row.get("Quantity") or row.get("quantity") or row.get("Qty"),
        "price": row.get("TradePrice") or row.get("price") or row.get("Price"),
        "pnl": row.get("Realized P&L") or row.get("RealizedPnL") or row.get("pnl"),
        "timestamp": row.get("Date/Time") or row.get("datetime") or row.get("timestamp"),
        "external_id": row.get("TradeID") or row.get("trade_id") or row.get("id"),
        "source_type": "ibkr",
        "raw_row": row,
    }


# ----------------------------------------
# CANONICAL TRADE NORMALIZATION
# ----------------------------------------

def normalize_trade(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert raw trade input into canonical broker-neutral format.
    """

    normalized = {
        "symbol": normalize_symbol(raw.get("symbol")),
        "side": normalize_side(raw.get("side")),
        "quantity": safe_float(raw.get("quantity")),
        "price": safe_float(raw.get("price")),
        "pnl": safe_float(raw.get("pnl")),
        "timestamp": normalize_timestamp(raw.get("timestamp")),
        "external_id": normalize_text(raw.get("external_id")) or None,
        "source_type": normalize_text(raw.get("source_type")) or "manual",
    }

    normalized["fingerprint"] = build_trade_fingerprint(normalized)
    return normalized


# ----------------------------------------
# VALIDATION
# ----------------------------------------

def validate_trade(trade: Dict[str, Any]) -> Tuple[bool, str]:
    if not trade["symbol"]:
        return False, "Missing symbol"

    if trade["side"] == "unknown":
        return False, "Invalid side"

    if trade["quantity"] <= 0:
        return False, "Invalid quantity"

    if trade["timestamp"] is None:
        return False, "Missing timestamp"

    return True, ""


# ----------------------------------------
# INGESTION ENGINE
# ----------------------------------------

def process_import_rows(
    rows: List[Dict[str, Any]],
    *,
    source_type: str = "csv",
    existing_fingerprints: Set[str] | None = None,
) -> Dict[str, Any]:
    """
    Main ingestion processor.

    Returns:
    - normalized rows
    - rejected rows
    - duplicate rows
    - stats
    """

    normalized: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
    duplicates: List[Dict[str, Any]] = []

    seen: Set[str] = set()
    existing = existing_fingerprints or set()

    for row in rows:
        row = dict(row)
        row["source_type"] = source_type

        trade = normalize_trade(row)
        ok, reason = validate_trade(trade)

        if not ok:
            rejected.append(
                {
                    "row": row,
                    "reason": reason,
                }
            )
            continue

        fingerprint = trade["fingerprint"]

        if fingerprint in seen or fingerprint in existing:
            duplicates.append(
                {
                    "row": row,
                    "reason": "Duplicate trade fingerprint",
                    "fingerprint": fingerprint,
                }
            )
            continue

        seen.add(fingerprint)
        normalized.append(trade)

    return {
        "normalized": normalized,
        "rejected": rejected,
        "duplicates": duplicates,
        "stats": {
            "received": len(rows),
            "accepted": len(normalized),
            "rejected": len(rejected),
            "duplicates": len(duplicates),
        },
    }


# ----------------------------------------
# PARSERS
# ----------------------------------------

def parse_csv_text(text: str) -> List[Dict[str, Any]]:
    reader = csv.DictReader(StringIO(text))
    return [map_csv_row(row) for row in reader]


def parse_csv_rows(file_bytes: bytes) -> List[Dict[str, Any]]:
    text = file_bytes.decode("utf-8")
    return parse_csv_text(text)


def parse_mt5_rows(file_bytes: bytes) -> List[Dict[str, Any]]:
    """
    Foundation parser for MT5 CSV-like exports.
    """
    text = file_bytes.decode("utf-8")
    reader = csv.DictReader(StringIO(text))
    return [map_mt5_row(row) for row in reader]


def parse_ibkr_rows(file_bytes: bytes) -> List[Dict[str, Any]]:
    """
    Foundation parser for IBKR CSV-like exports.
    """
    text = file_bytes.decode("utf-8")
    reader = csv.DictReader(StringIO(text))
    return [map_ibkr_row(row) for row in reader]


# ----------------------------------------
# SOURCE ROUTER
# ----------------------------------------

def parse_rows_by_source(source_type: str, file_bytes: bytes) -> List[Dict[str, Any]]:
    source = normalize_text(source_type).lower()

    if source == "csv":
        return parse_csv_rows(file_bytes)

    if source == "mt5":
        return parse_mt5_rows(file_bytes)

    if source == "ibkr":
        return parse_ibkr_rows(file_bytes)

    raise ValueError(f"Unsupported source type: {source_type}")


# ----------------------------------------
# AUTO-IMPORT / REAL-TIME FOUNDATIONS
# ----------------------------------------

def build_import_job_payload(
    workspace_id: int,
    source_type: str,
    *,
    filename: str | None = None,
    mode: str = "manual",
) -> Dict[str, Any]:
    """
    Foundation payload for future scheduled and streaming ingestion jobs.
    """

    return {
        "workspace_id": workspace_id,
        "source_type": normalize_text(source_type).lower(),
        "filename": filename,
        "mode": normalize_text(mode).lower() or "manual",
        "requested_at": datetime.utcnow().isoformat(),
    }


def build_stream_event_payload(
    workspace_id: int,
    source_type: str,
    trade: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Foundation shape for future real-time ingestion.
    """
    normalized = normalize_trade(
        {
            **trade,
            "source_type": source_type,
        }
    )

    return {
        "workspace_id": workspace_id,
        "source_type": normalize_text(source_type).lower(),
        "event_type": "trade_ingested",
        "ingested_at": datetime.utcnow().isoformat(),
        "trade": normalized,
    }
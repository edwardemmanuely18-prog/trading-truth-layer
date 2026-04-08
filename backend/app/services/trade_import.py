# (FULL FILE — upgraded version)

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


def parse_datetime(value: Any) -> datetime | None:
    raw = normalize_text(value)
    if not raw:
        return None

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
            return datetime.strptime(raw, fmt)
        except Exception:
            pass

    return None


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
            str(safe_float(trade.get("entry_price"))),
            str(safe_float(trade.get("net_pnl"))),
            normalize_text(trade.get("opened_at")),
            normalize_text(trade.get("external_id")),
            normalize_text(trade.get("source_type")),
        ]
    )


# ----------------------------------------
# SOURCE-SPECIFIC ROW MAPPERS (UPGRADED)
# ----------------------------------------

def map_mt5_row(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "symbol": row.get("Symbol"),
        "side": row.get("Type"),
        "quantity": row.get("Volume"),
        "entry_price": row.get("Price"),
        "exit_price": row.get("Price") if row.get("Profit") else None,
        "net_pnl": row.get("Profit"),
        "opened_at": row.get("Time"),
        "closed_at": row.get("Time"),
        "external_id": row.get("Ticket"),
        "source_type": "mt5",
        "raw_row": row,
    }


def map_ibkr_row(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "symbol": row.get("Symbol"),
        "side": row.get("Buy/Sell"),
        "quantity": row.get("Quantity"),
        "entry_price": row.get("TradePrice"),
        "exit_price": row.get("TradePrice"),
        "net_pnl": row.get("Realized P&L"),
        "opened_at": row.get("Date/Time"),
        "closed_at": row.get("Date/Time"),
        "external_id": row.get("TradeID"),
        "source_type": "ibkr",
        "raw_row": row,
    }


def map_csv_row(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "symbol": row.get("symbol"),
        "side": row.get("side"),
        "quantity": row.get("quantity"),
        "entry_price": row.get("price"),
        "exit_price": None,
        "net_pnl": row.get("pnl"),
        "opened_at": row.get("timestamp"),
        "closed_at": None,
        "external_id": row.get("id"),
        "source_type": "csv",
        "raw_row": row,
    }


# ----------------------------------------
# NORMALIZATION (UPGRADED)
# ----------------------------------------

def normalize_trade(raw: Dict[str, Any]) -> Dict[str, Any]:
    opened_at = parse_datetime(raw.get("opened_at"))
    closed_at = parse_datetime(raw.get("closed_at"))

    normalized = {
        "symbol": normalize_symbol(raw.get("symbol")),
        "side": normalize_side(raw.get("side")),
        "quantity": safe_float(raw.get("quantity")),
        "entry_price": safe_float(raw.get("entry_price")),
        "exit_price": safe_float(raw.get("exit_price"), None),
        "net_pnl": safe_float(raw.get("net_pnl"), None),
        "opened_at": opened_at,
        "closed_at": closed_at,
        "external_id": normalize_text(raw.get("external_id")) or None,
        "source_type": normalize_text(raw.get("source_type")),
    }

    normalized["fingerprint"] = build_trade_fingerprint(normalized)
    return normalized


# ----------------------------------------
# VALIDATION (UPGRADED)
# ----------------------------------------

def validate_trade(trade: Dict[str, Any]) -> Tuple[bool, str]:
    if not trade["symbol"]:
        return False, "Missing symbol"

    if trade["side"] == "unknown":
        return False, "Invalid side"

    if trade["quantity"] <= 0:
        return False, "Invalid quantity"

    if trade["opened_at"] is None:
        return False, "Missing opened_at"

    return True, ""


# ----------------------------------------
# INGESTION ENGINE (UPGRADED)
# ----------------------------------------

def process_import_rows(
    rows: List[Dict[str, Any]],
    *,
    source_type: str = "csv",
    existing_fingerprints: Set[str] | None = None,
) -> Dict[str, Any]:

    normalized: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
    duplicates: List[Dict[str, Any]] = []

    seen: Set[str] = set()
    existing = existing_fingerprints or set()

    for row in rows:
        trade = normalize_trade(row)
        ok, reason = validate_trade(trade)

        if not ok:
            rejected.append({"row": row, "reason": reason})
            continue

        fingerprint = trade["fingerprint"]

        if fingerprint in seen or fingerprint in existing:
            duplicates.append({"row": row, "reason": "Duplicate", "fingerprint": fingerprint})
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

def parse_rows_by_source(source_type: str, file_bytes: bytes) -> List[Dict[str, Any]]:
    text = file_bytes.decode("utf-8")
    reader = csv.DictReader(StringIO(text))

    if source_type == "mt5":
        return [map_mt5_row(row) for row in reader]

    if source_type == "ibkr":
        return [map_ibkr_row(row) for row in reader]

    return [map_csv_row(row) for row in reader]

# ----------------------------------------
# AUTO-IMPORT JOB PAYLOAD (RESTORE)
# ----------------------------------------

def build_import_job_payload(
    workspace_id: int,
    source_type: str,
    *,
    filename: str | None = None,
    mode: str = "manual",
) -> Dict[str, Any]:
    return {
        "workspace_id": workspace_id,
        "source_type": source_type,
        "filename": filename,
        "mode": mode,
        "requested_at": datetime.utcnow().isoformat(),
    }

# ----------------------------------------
# STREAM EVENT PAYLOAD (RESTORE)
# ----------------------------------------

def build_stream_event_payload(
    workspace_id: int,
    source_type: str,
    trade: Dict[str, Any],
) -> Dict[str, Any]:
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
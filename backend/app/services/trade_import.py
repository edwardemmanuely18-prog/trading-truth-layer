from __future__ import annotations

from typing import Any, Dict, List, Tuple, Set
from datetime import datetime
import csv
from io import StringIO
from app.services.broker_detection_service import (
    detect_source_from_headers,
)
from app.services.strategy_classifier import (
    classify_symbol,
)


print("=== TRADE IMPORT FILE LOADED V2 ===", flush=True)



def build_trade_fingerprint(
    workspace_id: int,
    member_id: int,
    symbol: str,
    side: str,
    opened_at,
    entry_price: float,
    quantity: float,
) -> str:
    import hashlib

    raw = "|".join(
        [
            str(workspace_id),
            str(member_id),
            symbol.strip().upper(),
            side.strip().upper(),
            (
                opened_at.isoformat()
                if opened_at is not None
                else "missing-opened-at"
            ),
            f"{entry_price:.8f}",
            f"{quantity:.8f}",
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


# ----------------------------------------
# LOW-LEVEL HELPERS
# ----------------------------------------

def safe_float(
    value: Any,
    default: float | None = 0.0,
) -> float | None:
    try:
        if value is None:
            return default

        if isinstance(value, str):
            value = value.replace(",", "").strip()

            if value == "":
                return default

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

    raw = raw.replace(",", " ")

    while "  " in raw:
        raw = raw.replace("  ", " ")

    raw = raw.strip()

    candidates = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%dT%H:%M:%S",
        "%Y.%m.%d %H:%M:%S",
        "%Y.%m.%d %H:%M",
        "%Y%m%d %H:%M:%S",
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

    print(
        "DATETIME PARSE FAILURE:",
        raw,
        flush=True,
    )

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


# DEPRECATED
# Canonical fingerprint generation now lives in:
# app.services.ingestion_service.build_trade_fingerprint
#
# This function is intentionally disabled to avoid
# architectural divergence between normalization and persistence layers.


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
        "opened_at": (
            row.get("Open Time")
            or row.get("Time")
        ),

        "closed_at": (
            row.get("Close Time")
            or row.get("Time")
        ),
        "external_id": row.get("Ticket"),
        "source_type": "mt5",
        "raw_row": row,
    }


def map_ibkr_row(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "symbol": row.get("Symbol"),
        "side": row.get("Buy/Sell"),
        "quantity": row.get("Quantity"),
        "entry_price": (
            row.get("TradePrice")
            or row.get("Price")
        ),
        "exit_price": (
            row.get("TradePrice")
            or row.get("Price")
        ),
        "net_pnl": (
            row.get("Realized P&L")
            or row.get("Realized P/L")
        ),
        "opened_at": row.get("Date/Time"),
        "closed_at": row.get("Date/Time"),
        "external_id": row.get("TradeID"),
        "source_type": "ibkr",
        "strategy_tag": "ibkr_import",
        "raw_row": row,
    }


def map_csv_row(row: Dict[str, Any]) -> Dict[str, Any]:
    opened_at = (
        row.get("timestamp")
        or row.get("opened_at")
        or row.get("Date/Time")
        or row.get("date")
    )

    entry_price = (
        row.get("price")
        or row.get("entry_price")
        or row.get("Price")
    )

    quantity = (
        row.get("quantity")
        or row.get("qty")
        or row.get("Quantity")
    )

    side = (
        row.get("side")
        or row.get("Side")
        or row.get("Buy/Sell")
    )

    symbol = (
        row.get("symbol")
        or row.get("Symbol")
    )

    return {
        "symbol": symbol,
        "side": side,
        "quantity": quantity,
        "entry_price": entry_price,
        "exit_price": row.get("exit_price"),
        "net_pnl": (
            row.get("pnl")
            or row.get("net_pnl")
            or row.get("Realized P/L")
        ),
        "opened_at": opened_at,
        "closed_at": row.get("closed_at"),
        "external_id": (
            row.get("id")
            or row.get("TradeID")
        ),
        "source_type": "csv",
        "raw_row": row,
    }


# ----------------------------------------
# NORMALIZATION (UPGRADED)
# ----------------------------------------

def normalize_trade(raw: Dict[str, Any]) -> Dict[str, Any]:
    opened_at = parse_datetime(raw.get("opened_at"))
    closed_at = parse_datetime(raw.get("closed_at"))

    print(
        "RAW NORMALIZE INPUT:",
        raw,
        flush=True,
    )

    normalized = {
        "symbol": normalize_symbol(raw.get("symbol")),
        "side": normalize_side(raw.get("side")),
        "quantity": abs(
            safe_float(raw.get("quantity"))
        ),
        "entry_price": safe_float(raw.get("entry_price")),
        "exit_price": safe_float(raw.get("exit_price"), None),
        "net_pnl": safe_float(raw.get("net_pnl"), None),
        "opened_at": opened_at,
        "closed_at": closed_at,
        "external_id": normalize_text(raw.get("external_id")) or None,
        "source_type": normalize_text(raw.get("source_type")),
        "strategy_tag": (
            normalize_text(raw.get("strategy_tag"))
            or classify_symbol(
                normalize_symbol(raw.get("symbol"))
            )
        ),
    }

    if normalized.get("opened_at") is None:
        print(
            "WARNING: opened_at missing during normalize_trade",
            normalized,
            flush=True,
        )

    normalized["fingerprint"] = build_trade_fingerprint(
        workspace_id=normalized.get("workspace_id", 0),
        member_id=normalized.get("member_id", 0),
        symbol=normalized.get("symbol", ""),
        side=normalized.get("side", ""),
        opened_at=normalized.get("opened_at"),
        entry_price=float(
            normalized.get("entry_price") or 0
        ),
        quantity=float(
            normalized.get("quantity") or 0
        ),
    )
    if normalized.get("opened_at") is None:
        print(
            "NORMALIZATION FAILURE RAW:",
            raw,
            flush=True,
        )

        print(
            "NORMALIZATION FAILURE NORMALIZED:",
            normalized,
            flush=True,
        )

        raise ValueError(
            "Trade missing opened_at after normalization"
        )

    print(
        "NORMALIZED TRADE:",
        normalized,
        flush=True,
    )

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

        print(
            "PROCESSING ROW:",
            row,
            flush=True,
        )

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

    headers = reader.fieldnames or []

    if source_type == "auto":
        source_type = detect_source_from_headers(headers)

    print(
        "DETECTED SOURCE TYPE:",
        source_type,
        flush=True,
    )

    print(
        "CSV HEADERS:",
        headers,
        flush=True,
    )

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
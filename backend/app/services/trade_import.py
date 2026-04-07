from typing import List, Dict, Tuple


# ----------------------------------------
# CANONICAL TRADE NORMALIZATION
# ----------------------------------------

def normalize_trade(raw: Dict) -> Dict:
    """
    Convert raw trade input into canonical format.
    This is the most important layer for broker-neutral ingestion.
    """

    return {
        "symbol": raw.get("symbol"),
        "side": normalize_side(raw.get("side")),
        "quantity": safe_float(raw.get("quantity")),
        "price": safe_float(raw.get("price")),
        "pnl": safe_float(raw.get("pnl")),
        "timestamp": raw.get("timestamp"),
        "external_id": raw.get("external_id"),
    }


def normalize_side(value: str) -> str:
    if not value:
        return "unknown"

    v = value.lower()

    if v in ["buy", "long"]:
        return "buy"
    if v in ["sell", "short"]:
        return "sell"

    return "unknown"


def safe_float(value):
    try:
        return float(value)
    except Exception:
        return 0.0


# ----------------------------------------
# VALIDATION
# ----------------------------------------

def validate_trade(trade: Dict) -> Tuple[bool, str]:
    """
    Validate normalized trade before ingestion.
    """

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

def process_import_rows(rows: List[Dict]) -> Dict:
    """
    Main ingestion processor.

    Returns:
    - normalized rows
    - rejected rows
    - stats
    """

    normalized = []
    rejected = []

    for row in rows:
        trade = normalize_trade(row)
        ok, reason = validate_trade(trade)

        if ok:
            normalized.append(trade)
        else:
            rejected.append({
                "row": row,
                "reason": reason,
            })

    return {
        "normalized": normalized,
        "rejected": rejected,
        "stats": {
            "received": len(rows),
            "accepted": len(normalized),
            "rejected": len(rejected),
        },
    }


# ----------------------------------------
# CSV PARSER (FOUNDATION)
# ----------------------------------------

def parse_csv_rows(file_bytes: bytes) -> List[Dict]:
    """
    Basic CSV parser.
    This will evolve into MT5 / IBKR adapters later.
    """

    import csv
    from io import StringIO

    text = file_bytes.decode("utf-8")
    reader = csv.DictReader(StringIO(text))

    rows = []

    for row in reader:
        rows.append({
            "symbol": row.get("symbol") or row.get("Symbol"),
            "side": row.get("side") or row.get("Side"),
            "quantity": row.get("quantity") or row.get("Qty"),
            "price": row.get("price") or row.get("Price"),
            "pnl": row.get("pnl") or row.get("PnL"),
            "timestamp": row.get("timestamp") or row.get("Time"),
            "external_id": row.get("id") or row.get("Ticket"),
        })

    return rows
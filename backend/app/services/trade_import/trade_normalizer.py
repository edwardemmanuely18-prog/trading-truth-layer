from hashlib import sha256
from datetime import datetime


def normalize_symbol(value):

    if value is None:
        return ""

    return str(value).strip().upper()


def normalize_side(value):

    if value is None:
        return "unknown"

    side = str(value).strip().lower()

    if side in [
        "buy",
        "long",
        "b",
        "0",
    ]:
        return "buy"

    if side in [
        "sell",
        "short",
        "s",
        "1",
    ]:
        return "sell"

    return "unknown"


def safe_float(
    value,
    default=0.0,
):

    try:

        if value in [
            None,
            "",
        ]:
            return default

        return float(value)

    except Exception:
        return default


def parse_datetime(value):

    if value is None:
        return None

    if isinstance(
        value,
        datetime,
    ):
        return value

    try:
        return datetime.fromisoformat(
            str(value)
        )

    except Exception:
        return None


def build_trade_fingerprint(
    workspace_id,
    member_id,
    symbol,
    side,
    opened_at,
    entry_price,
    quantity,
):

    raw = (
        f"{workspace_id}|"
        f"{member_id}|"
        f"{symbol}|"
        f"{side}|"
        f"{opened_at}|"
        f"{entry_price}|"
        f"{quantity}"
    )

    return sha256(
        raw.encode()
    ).hexdigest()


def generate_trade_hash(
    broker_trade_id,
    symbol,
    opened_at,
):

    raw = (
        f"{broker_trade_id}|"
        f"{symbol}|"
        f"{opened_at}"
    )

    return sha256(
        raw.encode()
    ).hexdigest()


def parse_rows_by_source(
    rows,
    source_type,
):
    return rows


def process_import_rows(
    rows,
    source_type,
):

    return {
        "normalized": rows,
        "rejected": [],
        "duplicates": [],
        "stats": {
            "received": len(rows),
            "rejected": 0,
            "duplicates": 0,
        },
    }
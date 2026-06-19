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
    source_type,
    file_bytes,
):
    import importlib.util
    from pathlib import Path

    legacy_path = (
        Path(__file__)
        .resolve()
        .parent.parent
        / "trade_import.py"
    )

    spec = importlib.util.spec_from_file_location(
        "ttl_trade_import_legacy",
        legacy_path,
    )

    module = importlib.util.module_from_spec(
        spec)

    spec.loader.exec_module(module)

    return module.parse_rows_by_source(
        source_type=source_type,
        file_bytes=file_bytes,
    )


def process_import_rows(
    rows,
    source_type,
    existing_fingerprints=None,
):
    import importlib.util
    from pathlib import Path

    legacy_path = (
        Path(__file__)
        .resolve()
        .parent.parent
        / "trade_import.py"
    )

    spec = importlib.util.spec_from_file_location(
        "ttl_trade_import_legacy",
        legacy_path,
    )

    module = importlib.util.module_from_spec(
        spec)

    spec.loader.exec_module(module)

    return module.process_import_rows(
        rows,
        source_type=source_type,
        existing_fingerprints=(
            existing_fingerprints
            or set()
        ),
    )
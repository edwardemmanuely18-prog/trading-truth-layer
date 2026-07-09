import json
import hashlib

from datetime import datetime

from sqlalchemy.orm import Session

from app.models.trade import Trade
from app.models.claim_schema import ClaimSchema



def parse_period_start(date_str: str | None):
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str)
    except Exception:
        return None


def parse_period_end(date_str: str | None):
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str)
    except Exception:
        return None


def coerce_trade_opened_at(value):
    if value is None:
        return None

    if isinstance(value, datetime):
        return value

    text = str(value).strip()
    candidates = [
        text,
        text.replace("Z", "+00:00"),
        text.replace(" ", "T"),
    ]

    for candidate in candidates:
        try:
            return datetime.fromisoformat(candidate)
        except ValueError:
            continue

    return None


def resolve_schema_trades(
    schema: ClaimSchema,
    db: Session,
    workspace_trades: list[Trade] | None = None,
):
    included_members = json.loads(schema.included_member_ids_json or "[]")
    included_symbols = [s.upper() for s in json.loads(schema.included_symbols_json or "[]")]
    excluded_trade_ids = set(json.loads(schema.excluded_trade_ids_json or "[]"))

    period_start = parse_period_start(schema.period_start)
    period_end = parse_period_end(schema.period_end)

    if workspace_trades is None:
        workspace_trades = (
            db.query(Trade)
            .filter(
                Trade.workspace_id == schema.workspace_id
            )
            .all()
        )

    trades = workspace_trades

    filtered = []
    for trade in trades:
        trade_dt = coerce_trade_opened_at(trade.opened_at)

        if period_start is not None and (trade_dt is None or trade_dt < period_start):
            continue

        if period_end is not None and (trade_dt is None or trade_dt >= period_end):
            continue

        if included_members and trade.member_id not in included_members:
            continue

        symbol = (trade.symbol or "").upper()
        if included_symbols and symbol not in included_symbols:
            continue

        if trade.id in excluded_trade_ids:
            continue

        filtered.append(trade)

    return filtered


def compute_trade_set_hash(trades: list[Trade]) -> str:
    normalized_rows = []

    for t in sorted(trades, key=lambda x: x.id):
        normalized_rows.append(
            {
                "id": t.id,
                "workspace_id": t.workspace_id,
                "member_id": t.member_id,
                "symbol": t.symbol,
                "side": t.side,
                "opened_at": t.opened_at.isoformat() if isinstance(t.opened_at, datetime) else str(t.opened_at),
                "entry_price": t.entry_price,
                "quantity": t.quantity,
                "net_pnl": t.net_pnl,
                "currency": t.currency,
                "strategy_tag": t.strategy_tag,
                "source_system": t.source_system,
            }
        )

    raw = json.dumps(normalized_rows, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def compute_scope_hash(
    schema: ClaimSchema,
):
    payload = {
        "period_start":
            schema.period_start,

        "period_end":
            schema.period_end,

        "included_members":
            json.loads(
                schema.included_member_ids_json
                or "[]"
            ),

        "included_symbols":
            json.loads(
                schema.included_symbols_json
                or "[]"
            ),

        "excluded_trade_ids":
            json.loads(
                schema.excluded_trade_ids_json
                or "[]"
            ),
    }

    raw = json.dumps(
        payload,
        sort_keys=True,
    )

    return hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()


def compute_lifecycle_hash(
    schema: ClaimSchema,
):
    payload = {
        "status":
            schema.status,

        "verified_at":
            str(schema.verified_at),

        "published_at":
            str(schema.published_at),

        "locked_at":
            str(schema.locked_at),
    }

    raw = json.dumps(
        payload,
        sort_keys=True,
    )

    return hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()


def compute_integrity_snapshot(
    schema,
    trades,
):
    return {
        "trade_hash":
            compute_trade_set_hash(
                trades
            ),

        "trade_count":
            len(trades),

        "scope_hash":
            compute_scope_hash(
                schema
            ),

        "lifecycle_hash":
            compute_lifecycle_hash(
                schema
            ),
    }
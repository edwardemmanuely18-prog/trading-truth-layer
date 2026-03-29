from datetime import datetime, timedelta
from io import BytesIO
import hashlib
import json
import os
import re
import zipfile
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session

from app.api.deps import (
    get_current_user,
    require_workspace_member,
    require_workspace_operator_or_owner,
    require_workspace_owner,
)
from app.core.db import get_db
from app.models.audit_event import AuditEvent
from app.models.claim_schema import ClaimSchema
from app.models.trade import Trade
from app.models.user import User
from app.models.workspace import Workspace
from app.services.audit_service import log_audit_event
from app.services.claim_service import compute_claim_hash
from app.services.entitlements import enforce_claim_creation_allowed

router = APIRouter()

EXCLUSION_REASON_OUTSIDE_PERIOD = "OUTSIDE_PERIOD"
EXCLUSION_REASON_MEMBER_FILTER = "MEMBER_FILTER"
EXCLUSION_REASON_SYMBOL_FILTER = "SYMBOL_FILTER"
EXCLUSION_REASON_MANUAL_EXCLUSION = "MANUAL_EXCLUSION"

EXCLUSION_REASON_LABELS = {
    EXCLUSION_REASON_OUTSIDE_PERIOD: "Outside claim period",
    EXCLUSION_REASON_MEMBER_FILTER: "Member not included",
    EXCLUSION_REASON_SYMBOL_FILTER: "Symbol not included",
    EXCLUSION_REASON_MANUAL_EXCLUSION: "Manually excluded",
}


class ClaimSchemaCreate(BaseModel):
    workspace_id: int
    name: str
    period_start: str
    period_end: str
    included_member_ids_json: List[int] = []
    included_symbols_json: List[str] = []
    excluded_trade_ids_json: List[int] = []
    methodology_notes: str = ""
    visibility: str = "private"


class ClaimSchemaUpdate(BaseModel):
    name: str
    period_start: str
    period_end: str
    included_member_ids_json: List[int] = []
    included_symbols_json: List[str] = []
    excluded_trade_ids_json: List[int] = []
    methodology_notes: str = ""
    visibility: str = "private"


def normalize_visibility(value: str | None) -> str:
    allowed_visibility = {"private", "unlisted", "public"}
    if value in allowed_visibility:
        return value
    return "private"


def normalize_symbol_list(symbols: List[str] | None) -> list[str]:
    if not symbols:
        return []

    normalized = []
    seen = set()

    for symbol in symbols:
        cleaned = str(symbol).strip().upper()
        if not cleaned:
            continue
        if cleaned in seen:
            continue
        seen.add(cleaned)
        normalized.append(cleaned)

    return normalized


def normalize_int_list(values: List[int] | None) -> list[int]:
    if not values:
        return []

    normalized = []
    seen = set()

    for value in values:
        int_value = int(value)
        if int_value in seen:
            continue
        seen.add(int_value)
        normalized.append(int_value)

    return normalized


def get_workspace_or_404(workspace_id: int, db: Session) -> Workspace:
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace


def parse_bool_like(value: str | None) -> bool:
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def read_env_value_from_backend_dotenv(key: str) -> str | None:
    try:
        env_path = Path(__file__).resolve().parents[3] / ".env"
        if not env_path.exists():
            return None

        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            env_key, env_value = line.split("=", 1)
            if env_key.strip() != key:
                continue

            return env_value.strip().strip('"').strip("'")
    except Exception:
        return None

    return None


def workspace_limits_disabled() -> bool:
    direct_env_value = os.getenv("DISABLE_WORKSPACE_LIMITS")
    if direct_env_value is not None:
        return parse_bool_like(direct_env_value)

    dotenv_value = read_env_value_from_backend_dotenv("DISABLE_WORKSPACE_LIMITS")
    return parse_bool_like(dotenv_value)


def is_claim_publicly_accessible(schema: ClaimSchema) -> bool:
    return (
        schema.visibility in {"public", "unlisted"}
        and schema.status in {"published", "locked"}
    )


def serialize_schema(schema: ClaimSchema):
    return {
        "id": schema.id,
        "workspace_id": schema.workspace_id,
        "name": schema.name,
        "period_start": schema.period_start,
        "period_end": schema.period_end,
        "included_member_ids_json": json.loads(schema.included_member_ids_json or "[]"),
        "included_symbols_json": json.loads(schema.included_symbols_json or "[]"),
        "excluded_trade_ids_json": json.loads(schema.excluded_trade_ids_json or "[]"),
        "methodology_notes": schema.methodology_notes,
        "status": schema.status,
        "visibility": schema.visibility,
        "parent_claim_id": schema.parent_claim_id,
        "root_claim_id": schema.root_claim_id,
        "version_number": schema.version_number,
        "verified_at": schema.verified_at.isoformat() if schema.verified_at else None,
        "published_at": schema.published_at.isoformat() if schema.published_at else None,
        "locked_at": schema.locked_at.isoformat() if schema.locked_at else None,
        "locked_trade_set_hash": schema.locked_trade_set_hash,
        "claim_hash": compute_claim_hash(schema),
    }


def serialize_version_row(schema: ClaimSchema):
    return {
        "id": schema.id,
        "name": schema.name,
        "status": schema.status,
        "visibility": schema.visibility,
        "version_number": schema.version_number,
        "parent_claim_id": schema.parent_claim_id,
        "root_claim_id": schema.root_claim_id,
        "claim_hash": compute_claim_hash(schema),
    }


def serialize_audit_event(event: AuditEvent):
    return {
        "id": event.id,
        "event_type": event.event_type,
        "entity_type": event.entity_type,
        "entity_id": event.entity_id,
        "actor_id": event.actor_id,
        "workspace_id": event.workspace_id,
        "old_state": event.old_state,
        "new_state": event.new_state,
        "metadata_json": event.metadata_json,
        "created_at": event.created_at.isoformat() if event.created_at else None,
    }


def parse_period_start(date_str: str | None):
    if not date_str:
        return None
    return datetime.fromisoformat(date_str)


def parse_period_end(date_str: str | None):
    if not date_str:
        return None
    return datetime.fromisoformat(date_str) + timedelta(days=1)


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


def resolve_schema_trades(schema: ClaimSchema, db: Session):
    included_members = json.loads(schema.included_member_ids_json or "[]")
    included_symbols = [s.upper() for s in json.loads(schema.included_symbols_json or "[]")]
    excluded_trade_ids = set(json.loads(schema.excluded_trade_ids_json or "[]"))

    period_start = parse_period_start(schema.period_start)
    period_end = parse_period_end(schema.period_end)

    trades = db.query(Trade).filter(Trade.workspace_id == schema.workspace_id).all()

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


def build_exclusion_reason_detail(
    reason: str,
    trade: Trade,
    schema: ClaimSchema,
    included_members: list[int],
    included_symbols: list[str],
):
    opened_at_value = coerce_trade_opened_at(trade.opened_at)
    opened_at_text = (
        opened_at_value.isoformat()
        if isinstance(opened_at_value, datetime)
        else str(trade.opened_at)
    )

    if reason == EXCLUSION_REASON_OUTSIDE_PERIOD:
        return (
            f"Trade opened at {opened_at_text} is outside the claim period "
            f"{schema.period_start} to {schema.period_end}."
        )

    if reason == EXCLUSION_REASON_MEMBER_FILTER:
        allowed = ", ".join(str(x) for x in included_members) or "all members"
        return f"Trade member_id {trade.member_id} is not in the included member set ({allowed})."

    if reason == EXCLUSION_REASON_SYMBOL_FILTER:
        allowed = ", ".join(included_symbols) or "all symbols"
        return f"Trade symbol {(trade.symbol or '').upper()} is not in the included symbol set ({allowed})."

    if reason == EXCLUSION_REASON_MANUAL_EXCLUSION:
        return f"Trade {trade.id} was explicitly excluded in the claim schema."

    return "Trade was excluded by claim scope rules."


def classify_trade_scope(
    trade: Trade,
    schema: ClaimSchema,
    period_start,
    period_end,
    included_members: list[int],
    included_symbols: list[str],
    excluded_trade_ids: set[int],
):
    trade_dt = coerce_trade_opened_at(trade.opened_at)

    if period_start is not None and (trade_dt is None or trade_dt < period_start):
        return {
            "scope_status": "excluded",
            "reason": EXCLUSION_REASON_OUTSIDE_PERIOD,
            "reason_label": EXCLUSION_REASON_LABELS[EXCLUSION_REASON_OUTSIDE_PERIOD],
            "reason_detail": build_exclusion_reason_detail(
                EXCLUSION_REASON_OUTSIDE_PERIOD,
                trade,
                schema,
                included_members,
                included_symbols,
            ),
        }

    if period_end is not None and (trade_dt is None or trade_dt >= period_end):
        return {
            "scope_status": "excluded",
            "reason": EXCLUSION_REASON_OUTSIDE_PERIOD,
            "reason_label": EXCLUSION_REASON_LABELS[EXCLUSION_REASON_OUTSIDE_PERIOD],
            "reason_detail": build_exclusion_reason_detail(
                EXCLUSION_REASON_OUTSIDE_PERIOD,
                trade,
                schema,
                included_members,
                included_symbols,
            ),
        }

    if included_members and trade.member_id not in included_members:
        return {
            "scope_status": "excluded",
            "reason": EXCLUSION_REASON_MEMBER_FILTER,
            "reason_label": EXCLUSION_REASON_LABELS[EXCLUSION_REASON_MEMBER_FILTER],
            "reason_detail": build_exclusion_reason_detail(
                EXCLUSION_REASON_MEMBER_FILTER,
                trade,
                schema,
                included_members,
                included_symbols,
            ),
        }

    symbol = (trade.symbol or "").upper()
    if included_symbols and symbol not in included_symbols:
        return {
            "scope_status": "excluded",
            "reason": EXCLUSION_REASON_SYMBOL_FILTER,
            "reason_label": EXCLUSION_REASON_LABELS[EXCLUSION_REASON_SYMBOL_FILTER],
            "reason_detail": build_exclusion_reason_detail(
                EXCLUSION_REASON_SYMBOL_FILTER,
                trade,
                schema,
                included_members,
                included_symbols,
            ),
        }

    if trade.id in excluded_trade_ids:
        return {
            "scope_status": "excluded",
            "reason": EXCLUSION_REASON_MANUAL_EXCLUSION,
            "reason_label": EXCLUSION_REASON_LABELS[EXCLUSION_REASON_MANUAL_EXCLUSION],
            "reason_detail": build_exclusion_reason_detail(
                EXCLUSION_REASON_MANUAL_EXCLUSION,
                trade,
                schema,
                included_members,
                included_symbols,
            ),
        }

    return {
        "scope_status": "included",
        "reason": None,
        "reason_label": None,
        "reason_detail": None,
    }


def resolve_schema_trade_scope(schema: ClaimSchema, db: Session):
    included_members = json.loads(schema.included_member_ids_json or "[]")
    included_symbols = [s.upper() for s in json.loads(schema.included_symbols_json or "[]")]
    excluded_trade_ids = set(json.loads(schema.excluded_trade_ids_json or "[]"))

    period_start = parse_period_start(schema.period_start)
    period_end = parse_period_end(schema.period_end)

    trades = db.query(Trade).filter(Trade.workspace_id == schema.workspace_id).all()

    included = []
    excluded = []
    excluded_breakdown = {
        EXCLUSION_REASON_OUTSIDE_PERIOD: 0,
        EXCLUSION_REASON_MEMBER_FILTER: 0,
        EXCLUSION_REASON_SYMBOL_FILTER: 0,
        EXCLUSION_REASON_MANUAL_EXCLUSION: 0,
    }

    for trade in trades:
        result = classify_trade_scope(
            trade=trade,
            schema=schema,
            period_start=period_start,
            period_end=period_end,
            included_members=included_members,
            included_symbols=included_symbols,
            excluded_trade_ids=excluded_trade_ids,
        )

        if result["scope_status"] == "included":
            included.append(trade)
            continue

        excluded.append(
            {
                "trade": trade,
                "reason": result["reason"],
                "reason_label": result["reason_label"],
                "reason_detail": result["reason_detail"],
            }
        )
        if result["reason"] in excluded_breakdown:
            excluded_breakdown[result["reason"]] += 1

    return {
        "workspace_trade_count": len(trades),
        "included": included,
        "excluded": excluded,
        "excluded_breakdown": excluded_breakdown,
    }


def compute_trade_metrics(trades: list[Trade]):
    trade_count = len(trades)
    pnl_values = [t.net_pnl for t in trades if t.net_pnl is not None]

    if not pnl_values:
        return {
            "trade_count": trade_count,
            "net_pnl": 0.0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "best_trade": 0.0,
            "worst_trade": 0.0,
        }

    wins = [x for x in pnl_values if x > 0]
    losses = [x for x in pnl_values if x < 0]

    gross_profit = sum(wins)
    gross_loss_abs = abs(sum(losses))
    net_pnl = sum(pnl_values)
    win_rate = len(wins) / len(pnl_values) if pnl_values else 0.0

    if gross_loss_abs == 0:
        profit_factor = gross_profit if gross_profit > 0 else 0.0
    else:
        profit_factor = gross_profit / gross_loss_abs

    return {
        "trade_count": trade_count,
        "net_pnl": round(net_pnl, 4),
        "win_rate": round(win_rate, 4),
        "profit_factor": round(profit_factor, 4),
        "best_trade": round(max(pnl_values), 4),
        "worst_trade": round(min(pnl_values), 4),
    }


def build_equity_curve(trades: list[Trade]):
    ordered = sorted(
        trades,
        key=lambda t: (
            coerce_trade_opened_at(t.opened_at) or datetime.min,
            t.id,
        ),
    )

    cumulative = 0.0
    points = []

    for index, trade in enumerate(ordered, start=1):
        pnl = float(trade.net_pnl) if trade.net_pnl is not None else 0.0
        cumulative += pnl

        opened_at_value = coerce_trade_opened_at(trade.opened_at)
        opened_at_iso = (
            opened_at_value.isoformat()
            if isinstance(opened_at_value, datetime)
            else str(trade.opened_at)
        )

        points.append(
            {
                "index": index,
                "trade_id": trade.id,
                "member_id": trade.member_id,
                "symbol": trade.symbol,
                "opened_at": opened_at_iso,
                "net_pnl": round(pnl, 4),
                "cumulative_pnl": round(cumulative, 4),
            }
        )

    return {
        "point_count": len(points),
        "starting_equity": 0.0 if not points else points[0]["cumulative_pnl"],
        "ending_equity": round(cumulative, 4),
        "curve": points,
    }


def build_trade_evidence(trades: list[Trade]):
    ordered = sorted(
        trades,
        key=lambda t: (
            coerce_trade_opened_at(t.opened_at) or datetime.min,
            t.id,
        ),
    )

    cumulative = 0.0
    rows = []

    for index, trade in enumerate(ordered, start=1):
        pnl = float(trade.net_pnl) if trade.net_pnl is not None else 0.0
        cumulative += pnl

        opened_at_value = coerce_trade_opened_at(trade.opened_at)
        opened_at_iso = (
            opened_at_value.isoformat()
            if isinstance(opened_at_value, datetime)
            else str(trade.opened_at)
        )
        closed_at_iso = (
            trade.closed_at.isoformat()
            if isinstance(trade.closed_at, datetime)
            else (str(trade.closed_at) if trade.closed_at is not None else None)
        )

        rows.append(
            {
                "index": index,
                "trade_id": trade.id,
                "workspace_id": trade.workspace_id,
                "member_id": trade.member_id,
                "symbol": trade.symbol,
                "side": trade.side,
                "opened_at": opened_at_iso,
                "closed_at": closed_at_iso,
                "entry_price": trade.entry_price,
                "exit_price": trade.exit_price,
                "quantity": trade.quantity,
                "net_pnl": round(pnl, 4),
                "currency": trade.currency,
                "strategy_tag": trade.strategy_tag,
                "source_system": trade.source_system,
                "cumulative_pnl": round(cumulative, 4),
            }
        )

    return rows


def build_trade_scope_row(
    trade: Trade,
    index: int,
    cumulative_pnl: float | None = None,
    scope_status: str = "included",
    exclusion_reason: str | None = None,
    exclusion_reason_label: str | None = None,
    exclusion_reason_detail: str | None = None,
):
    pnl = float(trade.net_pnl) if trade.net_pnl is not None else 0.0

    opened_at_value = coerce_trade_opened_at(trade.opened_at)
    opened_at_iso = (
        opened_at_value.isoformat()
        if isinstance(opened_at_value, datetime)
        else str(trade.opened_at)
    )
    closed_at_iso = (
        trade.closed_at.isoformat()
        if isinstance(trade.closed_at, datetime)
        else (str(trade.closed_at) if trade.closed_at is not None else None)
    )

    return {
        "index": index,
        "trade_id": trade.id,
        "workspace_id": trade.workspace_id,
        "member_id": trade.member_id,
        "symbol": trade.symbol,
        "side": trade.side,
        "opened_at": opened_at_iso,
        "closed_at": closed_at_iso,
        "entry_price": trade.entry_price,
        "exit_price": trade.exit_price,
        "quantity": trade.quantity,
        "net_pnl": round(pnl, 4),
        "currency": trade.currency,
        "strategy_tag": trade.strategy_tag,
        "source_system": trade.source_system,
        "cumulative_pnl": round(cumulative_pnl, 4) if cumulative_pnl is not None else None,
        "scope_status": scope_status,
        "exclusion_reason": exclusion_reason,
        "exclusion_reason_label": exclusion_reason_label,
        "exclusion_reason_detail": exclusion_reason_detail,
    }


def build_included_trade_scope_rows(trades: list[Trade]):
    ordered = sorted(
        trades,
        key=lambda t: (
            coerce_trade_opened_at(t.opened_at) or datetime.min,
            t.id,
        ),
    )

    cumulative = 0.0
    rows = []

    for index, trade in enumerate(ordered, start=1):
        pnl = float(trade.net_pnl) if trade.net_pnl is not None else 0.0
        cumulative += pnl
        rows.append(
            build_trade_scope_row(
                trade=trade,
                index=index,
                cumulative_pnl=cumulative,
                scope_status="included",
            )
        )

    return rows


def build_excluded_trade_scope_rows(excluded_items: list[dict]):
    ordered = sorted(
        excluded_items,
        key=lambda item: (
            coerce_trade_opened_at(item["trade"].opened_at) or datetime.min,
            item["trade"].id,
        ),
    )

    rows = []
    for index, item in enumerate(ordered, start=1):
        trade = item["trade"]
        rows.append(
            build_trade_scope_row(
                trade=trade,
                index=index,
                cumulative_pnl=None,
                scope_status="excluded",
                exclusion_reason=item.get("reason"),
                exclusion_reason_label=item.get("reason_label"),
                exclusion_reason_detail=item.get("reason_detail"),
            )
        )

    return rows


def build_leaderboard(trades: list[Trade]):
    buckets: dict[int, list[float]] = {}

    for trade in trades:
        if trade.net_pnl is None:
            continue
        buckets.setdefault(trade.member_id, []).append(trade.net_pnl)

    leaderboard = []

    for member_id, pnl_values in buckets.items():
        wins = [x for x in pnl_values if x > 0]
        losses = [x for x in pnl_values if x < 0]
        gross_profit = sum(wins)
        gross_loss_abs = abs(sum(losses))
        win_rate = len(wins) / len(pnl_values) if pnl_values else 0.0

        if gross_loss_abs == 0:
            profit_factor = gross_profit if gross_profit > 0 else 0.0
        else:
            profit_factor = gross_profit / gross_loss_abs

        leaderboard.append(
            {
                "member_id": member_id,
                "member": f"Member {member_id}",
                "net_pnl": round(sum(pnl_values), 4),
                "win_rate": round(win_rate, 4),
                "profit_factor": round(profit_factor, 4),
            }
        )

    leaderboard.sort(key=lambda x: x["net_pnl"], reverse=True)

    for idx, row in enumerate(leaderboard, start=1):
        row["rank"] = idx

    return leaderboard


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


def build_claim_list_row(schema: ClaimSchema, db: Session):
    filtered_trades = resolve_schema_trades(schema, db)
    metrics = compute_trade_metrics(filtered_trades)

    trade_set_hash = schema.locked_trade_set_hash
    if not trade_set_hash:
        trade_set_hash = compute_trade_set_hash(filtered_trades)

    return {
        "claim_schema_id": schema.id,
        "claim_hash": compute_claim_hash(schema),
        "name": schema.name,
        "verification_status": schema.status,
        "trade_count": metrics["trade_count"],
        "net_pnl": metrics["net_pnl"],
        "profit_factor": metrics["profit_factor"],
        "win_rate": metrics["win_rate"],
        "leaderboard": build_leaderboard(filtered_trades),
        "scope": {
            "period_start": schema.period_start,
            "period_end": schema.period_end,
            "included_members": json.loads(schema.included_member_ids_json or "[]"),
            "included_symbols": json.loads(schema.included_symbols_json or "[]"),
            "methodology_notes": schema.methodology_notes,
            "visibility": schema.visibility,
        },
        "lifecycle": {
            "status": schema.status,
            "verified_at": schema.verified_at.isoformat() if schema.verified_at else None,
            "published_at": schema.published_at.isoformat() if schema.published_at else None,
            "locked_at": schema.locked_at.isoformat() if schema.locked_at else None,
            "locked_trade_set_hash": schema.locked_trade_set_hash,
        },
        "lineage": {
            "parent_claim_id": schema.parent_claim_id,
            "root_claim_id": schema.root_claim_id,
            "version_number": schema.version_number,
        },
        "trade_set_hash": trade_set_hash,
        "is_publicly_accessible": is_claim_publicly_accessible(schema),
    }


def build_public_claim_payload(schema: ClaimSchema, db: Session):
    filtered_trades = resolve_schema_trades(schema, db)
    metrics = compute_trade_metrics(filtered_trades)
    leaderboard = build_leaderboard(filtered_trades)

    trade_set_hash = schema.locked_trade_set_hash
    if not trade_set_hash:
        trade_set_hash = compute_trade_set_hash(filtered_trades)

    integrity_status = "valid"
    if schema.status == "locked" and schema.locked_trade_set_hash:
        recomputed_trade_set_hash = compute_trade_set_hash(filtered_trades)
        if recomputed_trade_set_hash != schema.locked_trade_set_hash:
            integrity_status = "compromised"

    scope = resolve_schema_trade_scope(schema, db)
    included_rows = build_included_trade_scope_rows(scope["included"])
    excluded_rows = build_excluded_trade_scope_rows(scope["excluded"])
    equity_curve = build_equity_curve(scope["included"])

    return {
        "claim_schema_id": schema.id,
        "claim_hash": compute_claim_hash(schema),
        "name": schema.name,
        "verification_status": schema.status,
        "integrity_status": integrity_status,
        "trade_count": metrics["trade_count"],
        "net_pnl": metrics["net_pnl"],
        "profit_factor": metrics["profit_factor"],
        "win_rate": metrics["win_rate"],
        "leaderboard": leaderboard,
        "scope": {
            "period_start": schema.period_start,
            "period_end": schema.period_end,
            "included_members": json.loads(schema.included_member_ids_json or "[]"),
            "included_symbols": json.loads(schema.included_symbols_json or "[]"),
            "methodology_notes": schema.methodology_notes,
            "visibility": schema.visibility,
        },
        "lifecycle": {
            "status": schema.status,
            "verified_at": schema.verified_at.isoformat() if schema.verified_at else None,
            "published_at": schema.published_at.isoformat() if schema.published_at else None,
            "locked_at": schema.locked_at.isoformat() if schema.locked_at else None,
            "locked_trade_set_hash": schema.locked_trade_set_hash,
        },
        "lineage": {
            "parent_claim_id": schema.parent_claim_id,
            "root_claim_id": schema.root_claim_id,
            "version_number": schema.version_number,
        },
        "trade_set_hash": trade_set_hash,
        "trades": included_rows,
        "included_trade_count": len(included_rows),
        "excluded_trade_count": len(excluded_rows),
        "included_trades": included_rows,
        "excluded_trades": excluded_rows,
        "summary": {
            "workspace_trade_count": scope["workspace_trade_count"],
            "included_trade_count": len(included_rows),
            "excluded_trade_count": len(excluded_rows),
            "excluded_breakdown": scope["excluded_breakdown"],
        },
        "equity_curve": equity_curve,
    }


def build_evidence_pack_payload(schema: ClaimSchema, db: Session):
    filtered_trades = resolve_schema_trades(schema, db)
    metrics = compute_trade_metrics(filtered_trades)

    trade_set_hash = schema.locked_trade_set_hash
    if not trade_set_hash:
        trade_set_hash = compute_trade_set_hash(filtered_trades)

    return {
        "claim_schema_id": schema.id,
        "claim_hash": compute_claim_hash(schema),
        "exported_at": datetime.utcnow().isoformat(),
        "export_version": "evidence_pack_v1",
        "schema_snapshot": {
            "id": schema.id,
            "workspace_id": schema.workspace_id,
            "name": schema.name,
            "period_start": schema.period_start,
            "period_end": schema.period_end,
            "included_member_ids_json": json.loads(schema.included_member_ids_json or "[]"),
            "included_symbols_json": json.loads(schema.included_symbols_json or "[]"),
            "excluded_trade_ids_json": json.loads(schema.excluded_trade_ids_json or "[]"),
            "methodology_notes": schema.methodology_notes,
            "status": schema.status,
            "visibility": schema.visibility,
            "parent_claim_id": schema.parent_claim_id,
            "root_claim_id": schema.root_claim_id,
            "version_number": schema.version_number,
            "verified_at": schema.verified_at.isoformat() if schema.verified_at else None,
            "published_at": schema.published_at.isoformat() if schema.published_at else None,
            "locked_at": schema.locked_at.isoformat() if schema.locked_at else None,
            "locked_trade_set_hash": schema.locked_trade_set_hash,
        },
        "trade_set_hash": trade_set_hash,
        "metrics_snapshot": metrics,
        "equity_curve_snapshot": build_equity_curve(filtered_trades),
        "methodology_notes": schema.methodology_notes,
        "lifecycle": {
            "status": schema.status,
            "verified_at": schema.verified_at.isoformat() if schema.verified_at else None,
            "published_at": schema.published_at.isoformat() if schema.published_at else None,
            "locked_at": schema.locked_at.isoformat() if schema.locked_at else None,
            "locked_trade_set_hash": schema.locked_trade_set_hash,
        },
    }


def build_audit_events_payload(schema: ClaimSchema, db: Session):
    events = (
        db.query(AuditEvent)
        .filter(
            AuditEvent.entity_type == "claim_schema",
            AuditEvent.entity_id == str(schema.id),
        )
        .order_by(AuditEvent.id.asc())
        .all()
    )

    return {
        "claim_schema_id": schema.id,
        "claim_hash": compute_claim_hash(schema),
        "exported_at": datetime.utcnow().isoformat(),
        "export_version": "audit_events_v1",
        "event_count": len(events),
        "events": [serialize_audit_event(event) for event in events],
    }


def build_evidence_bundle_manifest(schema: ClaimSchema):
    claim_hash = compute_claim_hash(schema)
    return {
        "export_version": "evidence_bundle_v1",
        "exported_at": datetime.utcnow().isoformat(),
        "claim_schema_id": schema.id,
        "claim_hash": claim_hash,
        "included_files": [
            "evidence_pack.json",
            "audit_events.json",
            "manifest.json",
        ],
    }


def build_evidence_bundle_payload(schema: ClaimSchema, db: Session):
    evidence_pack = build_evidence_pack_payload(schema, db)
    audit_events = build_audit_events_payload(schema, db)
    manifest = build_evidence_bundle_manifest(schema)

    return {
        "claim_schema_id": schema.id,
        "claim_hash": compute_claim_hash(schema),
        "exported_at": manifest["exported_at"],
        "export_version": manifest["export_version"],
        "included_files": manifest["included_files"],
        "manifest": manifest,
        "evidence_pack": evidence_pack,
        "audit_events": audit_events,
    }


def build_evidence_bundle_zip_bytes(schema: ClaimSchema, db: Session) -> tuple[BytesIO, str]:
    claim_hash = compute_claim_hash(schema)
    hash_prefix = claim_hash[:12]

    evidence_pack = build_evidence_pack_payload(schema, db)
    audit_events = build_audit_events_payload(schema, db)
    manifest = build_evidence_bundle_manifest(schema)

    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("evidence_pack.json", json.dumps(evidence_pack, indent=2))
        zf.writestr("audit_events.json", json.dumps(audit_events, indent=2))
        zf.writestr("manifest.json", json.dumps(manifest, indent=2))

    zip_buffer.seek(0)
    filename = f"evidence_bundle_claim_{schema.id}_{hash_prefix}.zip"
    return zip_buffer, filename


def require_public_claim_access(schema: ClaimSchema):
    if not is_claim_publicly_accessible(schema):
        raise HTTPException(status_code=403, detail="Claim is not publicly accessible")


# =========================
# PDF HELPERS
# =========================

PDF_PAGE_WIDTH, PDF_PAGE_HEIGHT = letter
PDF_MARGIN_LEFT = 42
PDF_MARGIN_RIGHT = 42
PDF_MARGIN_TOP = 40
PDF_MARGIN_BOTTOM = 42
PDF_CONTENT_WIDTH = PDF_PAGE_WIDTH - PDF_MARGIN_LEFT - PDF_MARGIN_RIGHT
PDF_HEADER_RULE_Y = PDF_PAGE_HEIGHT - 76
PDF_FOOTER_Y = 22


def format_pdf_datetime(value) -> str:
    if not value:
        return "—"

    if isinstance(value, datetime):
        dt = value
    else:
        text = str(value).strip()
        candidates = [text, text.replace("Z", "+00:00"), text.replace(" ", "T")]
        dt = None
        for candidate in candidates:
            try:
                dt = datetime.fromisoformat(candidate)
                break
            except ValueError:
                continue
        if dt is None:
            return shorten_text(text, 28)

    return dt.strftime("%Y-%m-%d %H:%M:%S")


def draw_pdf_wrapped_text(
    pdf: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    max_width: float,
    line_height: float = 14,
    font_name: str = "Helvetica",
    font_size: int = 11,
):
    words = (text or "").split()
    if not words:
        return y

    lines = simpleSplit(" ".join(words), font_name, font_size, max_width)
    for line in lines:
        pdf.drawString(x, y, line)
        y -= line_height

    return y


def split_wrapped_lines(text: str, max_width: float, font_name: str, font_size: int) -> list[str]:
    words = (text or "").split()
    if not words:
        return []
    return simpleSplit(" ".join(words), font_name, font_size, max_width)


def shorten_text(value: str | None, max_len: int = 88) -> str:
    text = str(value or "").strip()
    if not text:
        return "—"
    if len(text) <= max_len:
        return text
    return f"{text[:max_len - 3]}..."


def short_hash(value: str | None, head: int = 16, tail: int = 12) -> str:
    text = str(value or "").strip()
    if not text:
        return "—"
    if len(text) <= head + tail + 3:
        return text
    return f"{text[:head]}...{text[-tail:]}"


def pdf_draw_header(pdf: canvas.Canvas, document_title: str):
    pdf.setFillColor(colors.HexColor("#0F172A"))
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(PDF_MARGIN_LEFT, PDF_PAGE_HEIGHT - 26, "Trading Truth Layer")
    pdf.setFillColor(colors.HexColor("#64748B"))
    pdf.setFont("Helvetica", 9)
    pdf.drawRightString(PDF_PAGE_WIDTH - PDF_MARGIN_RIGHT, PDF_PAGE_HEIGHT - 26, document_title)
    pdf.setStrokeColor(colors.HexColor("#E2E8F0"))
    pdf.line(PDF_MARGIN_LEFT, PDF_HEADER_RULE_Y, PDF_PAGE_WIDTH - PDF_MARGIN_RIGHT, PDF_HEADER_RULE_Y)


def pdf_draw_footer(pdf: canvas.Canvas, page_number: int, claim_hash: str):
    pdf.setStrokeColor(colors.HexColor("#E2E8F0"))
    pdf.line(PDF_MARGIN_LEFT, PDF_FOOTER_Y + 10, PDF_PAGE_WIDTH - PDF_MARGIN_RIGHT, PDF_FOOTER_Y + 10)

    pdf.setFillColor(colors.HexColor("#64748B"))
    pdf.setFont("Helvetica", 8)
    pdf.drawString(PDF_MARGIN_LEFT, PDF_FOOTER_Y, f"Claim hash: {short_hash(claim_hash, 14, 10)}")
    pdf.drawRightString(PDF_PAGE_WIDTH - PDF_MARGIN_RIGHT, PDF_FOOTER_Y, f"Page {page_number}")


def pdf_start_page(pdf: canvas.Canvas, page_number: int, document_title: str, claim_hash: str):
    pdf_draw_header(pdf, document_title)
    pdf_draw_footer(pdf, page_number, claim_hash)
    pdf.setFillColor(colors.black)
    pdf.setStrokeColor(colors.black)
    return PDF_PAGE_HEIGHT - 92


def pdf_new_page(pdf: canvas.Canvas, page_number: int, document_title: str, claim_hash: str):
    pdf.showPage()
    return pdf_start_page(pdf, page_number, document_title, claim_hash)


def pdf_require_space(
    pdf: canvas.Canvas,
    y: float,
    required_space: float,
    page_number: int,
    document_title: str,
    claim_hash: str,
):
    if y >= PDF_MARGIN_BOTTOM + required_space:
        return y, page_number

    page_number += 1
    y = pdf_new_page(pdf, page_number, document_title, claim_hash)
    return y, page_number


def pdf_section_title(pdf: canvas.Canvas, title: str, x: float, y: float):
    pdf.setFillColor(colors.HexColor("#0F172A"))
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(x, y, title)
    pdf.setStrokeColor(colors.HexColor("#E2E8F0"))
    pdf.line(x, y - 6, PDF_PAGE_WIDTH - PDF_MARGIN_RIGHT, y - 6)
    pdf.setFillColor(colors.black)
    pdf.setStrokeColor(colors.black)
    return y - 24


def pdf_round_box(
    pdf: canvas.Canvas,
    x: float,
    y_top: float,
    width: float,
    height: float,
    fill_color,
    stroke_color,
    radius: int = 12,
):
    pdf.setFillColor(fill_color)
    pdf.setStrokeColor(stroke_color)
    pdf.roundRect(x, y_top - height, width, height, radius, fill=1, stroke=1)
    pdf.setFillColor(colors.black)
    pdf.setStrokeColor(colors.black)


def draw_metric_card(pdf: canvas.Canvas, x: float, top_y: float, w: float, h: float, label: str, value: str, hint: str | None = None):
    pdf_round_box(
        pdf,
        x,
        top_y,
        w,
        h,
        colors.HexColor("#F8FAFC"),
        colors.HexColor("#E2E8F0"),
        radius=12,
    )
    pdf.setFillColor(colors.HexColor("#64748B"))
    pdf.setFont("Helvetica", 9)
    pdf.drawString(x + 12, top_y - 18, label)

    pdf.setFillColor(colors.HexColor("#0F172A"))
    pdf.setFont("Helvetica-Bold", 17)
    pdf.drawString(x + 12, top_y - 38, shorten_text(value, 18))

    if hint:
        pdf.setFillColor(colors.HexColor("#64748B"))
        pdf.setFont("Helvetica", 8)
        pdf.drawString(x + 12, top_y - 54, shorten_text(hint, 28))

    pdf.setFillColor(colors.black)


def draw_label_value_box(
    pdf: canvas.Canvas,
    x: float,
    top_y: float,
    w: float,
    h: float,
    label: str,
    value: str,
    fill_color=colors.HexColor("#F8FAFC"),
    stroke_color=colors.HexColor("#E2E8F0"),
    value_font_size: int = 10,
):
    pdf_round_box(pdf, x, top_y, w, h, fill_color, stroke_color, radius=12)
    pdf.setFillColor(colors.HexColor("#64748B"))
    pdf.setFont("Helvetica", 10)
    pdf.drawString(x + 12, top_y - 18, label)

    pdf.setFillColor(colors.HexColor("#0F172A"))
    pdf.setFont("Helvetica", value_font_size)
    draw_pdf_wrapped_text(
        pdf,
        value or "—",
        x + 12,
        top_y - 36,
        max_width=w - 24,
        line_height=12,
        font_name="Helvetica",
        font_size=value_font_size,
    )
    pdf.setFillColor(colors.black)


def draw_kv_pair(pdf: canvas.Canvas, x: float, y: float, label: str, value: str):
    pdf.setFillColor(colors.HexColor("#64748B"))
    pdf.setFont("Helvetica", 9)
    pdf.drawString(x, y, label)
    pdf.setFillColor(colors.HexColor("#0F172A"))
    pdf.setFont("Helvetica-Bold", 10)
    lines = split_wrapped_lines(value or "—", 136, "Helvetica-Bold", 10)
    if not lines:
        lines = ["—"]
    current_y = y - 14
    for line in lines[:2]:
        pdf.drawString(x, current_y, line)
        current_y -= 11
    pdf.setFillColor(colors.black)


def draw_hash_block(pdf: canvas.Canvas, x: float, y_top: float, width: float, label: str, value: str):
    pdf.setFillColor(colors.HexColor("#64748B"))
    pdf.setFont("Helvetica", 10)
    pdf.drawString(x, y_top, label)
    pdf_round_box(
        pdf,
        x,
        y_top - 8,
        width,
        44,
        colors.HexColor("#F8FAFC"),
        colors.HexColor("#E2E8F0"),
        radius=10,
    )
    pdf.setFillColor(colors.HexColor("#334155"))
    pdf.setFont("Helvetica", 8)
    lines = split_wrapped_lines(value or "—", width - 20, "Helvetica", 8)
    current_y = y_top - 24
    for line in lines[:2]:
        pdf.drawString(x + 10, current_y, line)
        current_y -= 10
    pdf.setFillColor(colors.black)


def compute_drawdown_stats(points: list[dict]):
    if not points:
        return {
            "max_drawdown": 0.0,
            "peak_cumulative": 0.0,
            "trough_cumulative": 0.0,
            "peak_point": None,
            "trough_point": None,
        }

    running_peak = float("-inf")
    max_drawdown = 0.0
    peak_cumulative = 0.0
    trough_cumulative = 0.0
    peak_point = None
    trough_point = None
    current_peak_point = None

    for point in points:
        current = float(point.get("cumulative_pnl", 0.0))
        if current > running_peak:
            running_peak = current
            current_peak_point = point

        drawdown = running_peak - current
        if drawdown > max_drawdown:
            max_drawdown = drawdown
            peak_cumulative = running_peak
            trough_cumulative = current
            peak_point = current_peak_point
            trough_point = point

    return {
        "max_drawdown": round(max_drawdown, 4),
        "peak_cumulative": round(peak_cumulative, 4),
        "trough_cumulative": round(trough_cumulative, 4),
        "peak_point": peak_point,
        "trough_point": trough_point,
    }


def draw_equity_curve_preview(
    pdf: canvas.Canvas,
    x: float,
    top_y: float,
    width: float,
    height: float,
    points: list[dict],
):
    pdf_round_box(
        pdf,
        x,
        top_y,
        width,
        height,
        colors.white,
        colors.HexColor("#E2E8F0"),
        radius=14,
    )

    chart_x = x + 18
    chart_y_bottom = top_y - height + 20
    chart_y_top = top_y - 40
    chart_w = width - 36
    chart_h = chart_y_top - chart_y_bottom

    pdf.setFillColor(colors.HexColor("#0F172A"))
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(x + 14, top_y - 18, "Equity Curve Preview")

    if not points:
        pdf.setFont("Helvetica", 11)
        pdf.setFillColor(colors.HexColor("#64748B"))
        pdf.drawString(x + 14, top_y - 46, "No equity curve data available.")
        pdf.setFillColor(colors.black)
        return

    values = [float(p.get("cumulative_pnl", 0.0)) for p in points]
    min_value = min(min(values), 0.0)
    max_value = max(max(values), 0.0)
    range_value = max_value - min_value
    if range_value == 0:
        range_value = 1.0

    def x_for(index: int):
        if len(points) == 1:
            return chart_x + (chart_w / 2)
        return chart_x + (index / (len(points) - 1)) * chart_w

    def y_for(value: float):
        return chart_y_bottom + ((value - min_value) / range_value) * chart_h

    zero_y = y_for(0.0)
    pdf.setStrokeColor(colors.HexColor("#CBD5E1"))
    pdf.setDash(4, 4)
    pdf.line(chart_x, zero_y, chart_x + chart_w, zero_y)
    pdf.setDash()

    pdf.setStrokeColor(colors.HexColor("#E2E8F0"))
    pdf.line(chart_x, chart_y_bottom, chart_x + chart_w, chart_y_bottom)
    pdf.line(chart_x, chart_y_bottom, chart_x, chart_y_top)

    pdf.setStrokeColor(colors.HexColor("#0F172A"))
    pdf.setLineWidth(2)

    prev_x = None
    prev_y = None
    for idx, point in enumerate(points):
        px = x_for(idx)
        py = y_for(float(point.get("cumulative_pnl", 0.0)))
        if prev_x is not None and prev_y is not None:
            pdf.line(prev_x, prev_y, px, py)
        prev_x = px
        prev_y = py

    pdf.setFillColor(colors.HexColor("#0F172A"))
    for idx, point in enumerate(points):
        px = x_for(idx)
        py = y_for(float(point.get("cumulative_pnl", 0.0)))
        pdf.circle(px, py, 2.2, stroke=0, fill=1)

    pdf.setFillColor(colors.HexColor("#64748B"))
    pdf.setFont("Helvetica", 8)
    pdf.drawString(chart_x, chart_y_top + 6, f"max {round(max_value, 4)}")
    pdf.drawString(chart_x, chart_y_bottom - 12, f"min {round(min_value, 4)}")
    pdf.setFillColor(colors.black)


def draw_table_header(pdf: canvas.Canvas, x: float, y: float, headers: list[tuple[float, str]], font_size: int = 9):
    pdf.setFont("Helvetica-Bold", font_size)
    pdf.setFillColor(colors.HexColor("#64748B"))
    for offset, label in headers:
        pdf.drawString(x + offset, y, label)
    pdf.setStrokeColor(colors.HexColor("#CBD5E1"))
    pdf.line(x, y - 8, PDF_PAGE_WIDTH - PDF_MARGIN_RIGHT, y - 8)
    pdf.setFillColor(colors.black)
    pdf.setStrokeColor(colors.black)
    return y - 22


def draw_light_note_box(pdf: canvas.Canvas, x: float, y_top: float, width: float, text: str, height: float = 44):
    pdf_round_box(
        pdf,
        x,
        y_top,
        width,
        height,
        colors.HexColor("#F8FAFC"),
        colors.HexColor("#E2E8F0"),
        radius=10,
    )
    pdf.setFillColor(colors.HexColor("#475569"))
    pdf.setFont("Helvetica", 9)
    draw_pdf_wrapped_text(
        pdf,
        text,
        x + 12,
        y_top - 18,
        max_width=width - 24,
        line_height=11,
        font_name="Helvetica",
        font_size=9,
    )
    pdf.setFillColor(colors.black)


def build_claim_report_pdf_bytes(schema: ClaimSchema, db: Session) -> tuple[BytesIO, str]:
    filtered_trades = resolve_schema_trades(schema, db)
    metrics = compute_trade_metrics(filtered_trades)
    leaderboard = build_leaderboard(filtered_trades)
    equity_curve = build_equity_curve(filtered_trades)
    evidence_rows = build_trade_evidence(filtered_trades)
    drawdown_stats = compute_drawdown_stats(equity_curve["curve"])

    trade_set_hash = schema.locked_trade_set_hash
    if not trade_set_hash:
        trade_set_hash = compute_trade_set_hash(filtered_trades)

    claim_hash = compute_claim_hash(schema)
    integrity_status = "valid"

    if schema.status == "locked" and schema.locked_trade_set_hash:
        recomputed_trade_set_hash = compute_trade_set_hash(filtered_trades)
        if recomputed_trade_set_hash != schema.locked_trade_set_hash:
            integrity_status = "compromised"

    included_members = ", ".join(str(x) for x in json.loads(schema.included_member_ids_json or "[]")) or "All in scope"
    included_symbols = ", ".join(json.loads(schema.included_symbols_json or "[]")) or "All in scope"
    excluded_trade_ids = ", ".join(str(x) for x in json.loads(schema.excluded_trade_ids_json or "[]")) or "None"

    document_title = f"Claim Report · {schema.name}"
    filename = f"claim_report_{schema.id}_{claim_hash[:12]}.pdf"

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle(filename)
    pdf.setAuthor("Trading Truth Layer")
    pdf.setSubject("Verified Trading Claim Report")

    page_number = 1
    y = pdf_start_page(pdf, page_number, document_title, claim_hash)

    # =========================
    # PAGE 1 — EXECUTIVE SUMMARY
    # =========================

    pdf.setFillColor(colors.HexColor("#0F172A"))
    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawString(PDF_MARGIN_LEFT, y, "Institutional Claim Report")
    y -= 18

    pdf.setFillColor(colors.HexColor("#64748B"))
    pdf.setFont("Helvetica", 11)
    pdf.drawString(PDF_MARGIN_LEFT, y, "Verified Trading Claims OS")
    y -= 22

    pdf.setFillColor(colors.HexColor("#475569"))
    pdf.setFont("Helvetica", 11)
    y = draw_pdf_wrapped_text(
        pdf,
        "Lifecycle-governed trading claim report with evidence-backed performance summary, canonical fingerprints, lineage state, and integrity validation context.",
        PDF_MARGIN_LEFT,
        y,
        PDF_CONTENT_WIDTH,
        14,
        "Helvetica",
        11,
    )
    y -= 14

    banner_height = 134
    banner_fill = colors.HexColor("#ECFDF5") if integrity_status == "valid" else colors.HexColor("#FEF2F2")
    banner_stroke = colors.HexColor("#A7F3D0") if integrity_status == "valid" else colors.HexColor("#FECACA")
    banner_text = colors.HexColor("#166534") if integrity_status == "valid" else colors.HexColor("#991B1B")

    pdf_round_box(
        pdf,
        PDF_MARGIN_LEFT,
        y,
        PDF_CONTENT_WIDTH,
        banner_height,
        banner_fill,
        banner_stroke,
        radius=16,
    )

    pdf.setFillColor(banner_text)
    pdf.setFont("Helvetica", 11)
    pdf.drawString(PDF_MARGIN_LEFT + 16, y - 22, "Verification Signature")

    if schema.status == "locked" and integrity_status == "valid":
        signature_text = "Verified • Locked • Integrity Valid"
        sub_text = "This report summarizes finalized lifecycle state, integrity state, performance metrics, and canonical claim fingerprinting."
    elif schema.status == "published":
        signature_text = "Published Verification Surface"
        sub_text = "This report summarizes externally visible lifecycle state, current integrity posture, performance metrics, and canonical claim fingerprinting."
    elif schema.status == "locked" and integrity_status != "valid":
        signature_text = "Locked • Integrity Compromised"
        sub_text = "This record is locked, but the current in-scope trade fingerprint no longer matches the stored locked fingerprint."
    else:
        signature_text = f"{schema.status.title()} Claim"
        sub_text = "This report summarizes current lifecycle state and scoped claim evidence."

    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(PDF_MARGIN_LEFT + 16, y - 46, signature_text)

    pdf.setFont("Helvetica", 10)
    draw_pdf_wrapped_text(
        pdf,
        sub_text,
        PDF_MARGIN_LEFT + 16,
        y - 68,
        PDF_CONTENT_WIDTH - 190,
        12,
        "Helvetica",
        10,
    )

    chip_x = PDF_PAGE_WIDTH - PDF_MARGIN_RIGHT - 150
    pdf_round_box(
        pdf,
        chip_x,
        y - 10,
        150,
        52,
        colors.white,
        colors.HexColor("#D1D5DB"),
        radius=10,
    )
    pdf.setFillColor(colors.HexColor("#0F172A"))
    pdf.setFont("Helvetica", 10)
    pdf.drawString(chip_x + 12, y - 28, f"status: {schema.status}")
    pdf.drawString(chip_x + 12, y - 42, f"integrity: {integrity_status}")
    pdf.setFillColor(colors.black)

    inner_gap = 14
    hash_box_w = (PDF_CONTENT_WIDTH - 32 - inner_gap) / 2
    hash_row_top = y - 86
    draw_label_value_box(
        pdf,
        PDF_MARGIN_LEFT + 16,
        hash_row_top,
        hash_box_w,
        54,
        "Claim Hash Fingerprint",
        short_hash(claim_hash, 26, 16),
    )
    draw_label_value_box(
        pdf,
        PDF_MARGIN_LEFT + 16 + hash_box_w + inner_gap,
        hash_row_top,
        hash_box_w,
        54,
        "Trade Set Hash Fingerprint",
        short_hash(trade_set_hash, 26, 16),
    )

    y -= banner_height + 26

    y = pdf_section_title(pdf, "Claim Identity", PDF_MARGIN_LEFT, y)

    pdf.setFillColor(colors.HexColor("#0F172A"))
    pdf.setFont("Helvetica-Bold", 22)
    title_lines = split_wrapped_lines(schema.name or "Untitled Claim", PDF_CONTENT_WIDTH, "Helvetica-Bold", 22)
    for line in title_lines[:2]:
        pdf.drawString(PDF_MARGIN_LEFT, y, line)
        y -= 24

    card_gap = 12
    card_w = (PDF_CONTENT_WIDTH - (card_gap * 3)) / 4
    card_h = 66

    draw_metric_card(pdf, PDF_MARGIN_LEFT, y, card_w, card_h, "Trade Count", str(metrics["trade_count"]), "In-scope rows")
    draw_metric_card(pdf, PDF_MARGIN_LEFT + card_w + card_gap, y, card_w, card_h, "Net PnL", str(metrics["net_pnl"]), "Aggregate result")
    draw_metric_card(pdf, PDF_MARGIN_LEFT + (card_w + card_gap) * 2, y, card_w, card_h, "Profit Factor", str(metrics["profit_factor"]), "Gross profit / loss")
    draw_metric_card(pdf, PDF_MARGIN_LEFT + (card_w + card_gap) * 3, y, card_w, card_h, "Win Rate", f"{round(metrics['win_rate'] * 100, 2)}%", "Winning trades %")
    y -= card_h + 24

    panel_gap = 16
    panel_w = (PDF_CONTENT_WIDTH - panel_gap) / 2
    panel_h = 214

    pdf_round_box(pdf, PDF_MARGIN_LEFT, y, panel_w, panel_h, colors.white, colors.HexColor("#E2E8F0"), radius=14)
    pdf.setFillColor(colors.HexColor("#0F172A"))
    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(PDF_MARGIN_LEFT + 14, y - 22, "Verification Scope")
    draw_kv_pair(pdf, PDF_MARGIN_LEFT + 14, y - 48, "Period Start", schema.period_start or "—")
    draw_kv_pair(pdf, PDF_MARGIN_LEFT + 174, y - 48, "Period End", schema.period_end or "—")
    draw_kv_pair(pdf, PDF_MARGIN_LEFT + 14, y - 96, "Included Members", included_members)
    draw_kv_pair(pdf, PDF_MARGIN_LEFT + 174, y - 96, "Included Symbols", included_symbols)
    draw_kv_pair(pdf, PDF_MARGIN_LEFT + 14, y - 144, "Excluded Trade IDs", excluded_trade_ids)
    draw_kv_pair(pdf, PDF_MARGIN_LEFT + 174, y - 144, "Visibility", schema.visibility or "—")
    pdf.setFillColor(colors.HexColor("#64748B"))
    pdf.setFont("Helvetica", 9)
    pdf.drawString(PDF_MARGIN_LEFT + 14, y - 176, "Methodology Notes")
    draw_light_note_box(
        pdf,
        PDF_MARGIN_LEFT + 14,
        y - 184,
        panel_w - 28,
        schema.methodology_notes or "No methodology notes supplied.",
        height=56,
    )

    panel2_x = PDF_MARGIN_LEFT + panel_w + panel_gap
    pdf_round_box(pdf, panel2_x, y, panel_w, panel_h, colors.white, colors.HexColor("#E2E8F0"), radius=14)
    pdf.setFillColor(colors.HexColor("#0F172A"))
    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(panel2_x + 14, y - 22, "Lifecycle & Lineage")
    draw_kv_pair(pdf, panel2_x + 14, y - 48, "Status", schema.status or "—")
    draw_kv_pair(pdf, panel2_x + 174, y - 48, "Integrity", integrity_status)
    draw_kv_pair(pdf, panel2_x + 14, y - 96, "Verified At", format_pdf_datetime(schema.verified_at))
    draw_kv_pair(pdf, panel2_x + 174, y - 96, "Published At", format_pdf_datetime(schema.published_at))
    draw_kv_pair(pdf, panel2_x + 14, y - 144, "Locked At", format_pdf_datetime(schema.locked_at))
    draw_kv_pair(pdf, panel2_x + 174, y - 144, "Version Number", str(schema.version_number or "—"))
    draw_kv_pair(pdf, panel2_x + 14, y - 192, "Root Claim ID", str(schema.root_claim_id or "—"))
    draw_kv_pair(pdf, panel2_x + 174, y - 192, "Parent Claim ID", str(schema.parent_claim_id or "—"))

    # =========================
    # PAGE 2 — PERFORMANCE DIAGNOSTICS
    # hard break so the title never remains on page 1
    # =========================
    page_number += 1
    y = pdf_new_page(pdf, page_number, document_title, claim_hash)

    y = pdf_section_title(pdf, "Performance Diagnostics", PDF_MARGIN_LEFT, y)

    diag_w = (PDF_CONTENT_WIDTH - 36) / 4
    draw_metric_card(pdf, PDF_MARGIN_LEFT, y, diag_w, 66, "Best Trade", str(metrics["best_trade"]), "Highest PnL")
    draw_metric_card(pdf, PDF_MARGIN_LEFT + diag_w + 12, y, diag_w, 66, "Worst Trade", str(metrics["worst_trade"]), "Lowest PnL")
    draw_metric_card(pdf, PDF_MARGIN_LEFT + (diag_w + 12) * 2, y, diag_w, 66, "Max Drawdown", str(drawdown_stats["max_drawdown"]), "Peak-to-trough")
    draw_metric_card(pdf, PDF_MARGIN_LEFT + (diag_w + 12) * 3, y, diag_w, 66, "Ending Equity", str(equity_curve["ending_equity"]), "Final cumulative")
    y -= 82

    start_equity = equity_curve["starting_equity"]
    end_equity = equity_curve["ending_equity"]
    point_count = equity_curve["point_count"]
    curve_points = equity_curve["curve"]
    first_point = curve_points[0] if curve_points else None
    last_point = curve_points[-1] if curve_points else None
    peak_point = drawdown_stats.get("peak_point")
    trough_point = drawdown_stats.get("trough_point")

    mini_w = (PDF_CONTENT_WIDTH - 24) / 3
    draw_label_value_box(pdf, PDF_MARGIN_LEFT, y, mini_w, 54, "Start Equity", str(start_equity))
    draw_label_value_box(pdf, PDF_MARGIN_LEFT + mini_w + 12, y, mini_w, 54, "End Equity", str(end_equity))
    draw_label_value_box(pdf, PDF_MARGIN_LEFT + (mini_w + 12) * 2, y, mini_w, 54, "Curve Points", str(point_count))
    y -= 70

    draw_equity_curve_preview(pdf, PDF_MARGIN_LEFT, y, PDF_CONTENT_WIDTH, 210, curve_points[:24])
    y -= 222

    note_w = (PDF_CONTENT_WIDTH - 36) / 4
    draw_label_value_box(
        pdf,
        PDF_MARGIN_LEFT,
        y,
        note_w,
        52,
        "First Point",
        f"Trade #{first_point['trade_id']} · {first_point['symbol']} · {format_pdf_datetime(first_point['opened_at'])}" if first_point else "—",
        value_font_size=9,
    )
    draw_label_value_box(
        pdf,
        PDF_MARGIN_LEFT + note_w + 12,
        y,
        note_w,
        52,
        "Last Point",
        f"Trade #{last_point['trade_id']} · {last_point['symbol']} · {format_pdf_datetime(last_point['opened_at'])}" if last_point else "—",
        value_font_size=9,
    )
    draw_label_value_box(
        pdf,
        PDF_MARGIN_LEFT + (note_w + 12) * 2,
        y,
        note_w,
        52,
        "Drawdown Peak",
        f"Trade #{peak_point['trade_id']} · {peak_point['symbol']} · {format_pdf_datetime(peak_point['opened_at'])}" if peak_point else "—",
        value_font_size=9,
    )
    draw_label_value_box(
        pdf,
        PDF_MARGIN_LEFT + (note_w + 12) * 3,
        y,
        note_w,
        52,
        "Drawdown Trough",
        f"Trade #{trough_point['trade_id']} · {trough_point['symbol']} · {format_pdf_datetime(trough_point['opened_at'])}" if trough_point else "—",
        value_font_size=9,
    )
    y -= 66

    draw_light_note_box(
        pdf,
        PDF_MARGIN_LEFT,
        y,
        PDF_CONTENT_WIDTH,
        "The most important additional statistic on an equity curve is usually max drawdown, because it shows the deepest peak-to-trough decline experienced along the path, not just the final result. Equity high and low help frame the range, but drawdown gives the stronger credibility signal for risk-aware review.",
        height=50,
    )
    y -= 74

    # Leaderboard
    y, page_number = pdf_require_space(pdf, y, 180, page_number, document_title, claim_hash)
    y = pdf_section_title(pdf, "Leaderboard Snapshot", PDF_MARGIN_LEFT, y)
    y = draw_table_header(
        pdf,
        PDF_MARGIN_LEFT,
        y,
        [
            (0, "Rank"),
            (72, "Member"),
            (220, "Net PnL"),
            (332, "Win Rate"),
            (446, "Profit Factor"),
        ],
    )

    pdf.setFont("Helvetica", 9)
    pdf.setFillColor(colors.HexColor("#0F172A"))
    if leaderboard:
        for row in leaderboard[:10]:
            y, page_number = pdf_require_space(pdf, y, 40, page_number, document_title, claim_hash)
            pdf.drawString(PDF_MARGIN_LEFT, y, str(row["rank"]))
            pdf.drawString(PDF_MARGIN_LEFT + 72, y, shorten_text(str(row["member"]), 20))
            pdf.drawString(PDF_MARGIN_LEFT + 220, y, str(row["net_pnl"]))
            pdf.drawString(PDF_MARGIN_LEFT + 332, y, f"{round(float(row['win_rate']) * 100, 2)}%")
            pdf.drawString(PDF_MARGIN_LEFT + 446, y, str(row["profit_factor"]))
            pdf.setStrokeColor(colors.HexColor("#E2E8F0"))
            pdf.line(PDF_MARGIN_LEFT, y - 8, PDF_PAGE_WIDTH - PDF_MARGIN_RIGHT, y - 8)
            y -= 18
    else:
        pdf.drawString(PDF_MARGIN_LEFT, y, "No leaderboard data available.")
        y -= 18

    y -= 10

    # Trade evidence snapshot
    y, page_number = pdf_require_space(pdf, y, 220, page_number, document_title, claim_hash)
    y = pdf_section_title(pdf, "Trade Evidence Snapshot", PDF_MARGIN_LEFT, y)
    y = draw_table_header(
        pdf,
        PDF_MARGIN_LEFT,
        y,
        [
            (0, "#"),
            (22, "Trade ID"),
            (70, "Opened"),
            (180, "Symbol"),
            (236, "Side"),
            (278, "Member"),
            (332, "PnL"),
            (392, "Cumulative"),
        ],
    )

    pdf.setFont("Helvetica", 8)
    pdf.setFillColor(colors.HexColor("#0F172A"))
    if evidence_rows:
        for row in evidence_rows[:20]:
            y, page_number = pdf_require_space(pdf, y, 36, page_number, document_title, claim_hash)
            pdf.drawString(PDF_MARGIN_LEFT, y, str(row["index"]))
            pdf.drawString(PDF_MARGIN_LEFT + 22, y, str(row["trade_id"]))
            pdf.drawString(PDF_MARGIN_LEFT + 70, y, shorten_text(format_pdf_datetime(row["opened_at"]), 18))
            pdf.drawString(PDF_MARGIN_LEFT + 180, y, shorten_text(str(row["symbol"]), 10))
            pdf.drawString(PDF_MARGIN_LEFT + 236, y, shorten_text(str(row["side"]), 6))
            pdf.drawString(PDF_MARGIN_LEFT + 278, y, str(row["member_id"]))
            pdf.drawString(PDF_MARGIN_LEFT + 332, y, str(row["net_pnl"]))
            pdf.drawString(PDF_MARGIN_LEFT + 392, y, str(row["cumulative_pnl"]))
            pdf.setStrokeColor(colors.HexColor("#E2E8F0"))
            pdf.line(PDF_MARGIN_LEFT, y - 8, PDF_PAGE_WIDTH - PDF_MARGIN_RIGHT, y - 8)
            y -= 16
    else:
        pdf.drawString(PDF_MARGIN_LEFT, y, "No trade evidence rows available.")
        y -= 18

    y -= 10

    # Fingerprints
    y, page_number = pdf_require_space(pdf, y, 150, page_number, document_title, claim_hash)
    y = pdf_section_title(pdf, "Canonical Fingerprints", PDF_MARGIN_LEFT, y)
    draw_hash_block(pdf, PDF_MARGIN_LEFT, y, PDF_CONTENT_WIDTH, "Claim Hash", claim_hash)
    y -= 62
    draw_hash_block(pdf, PDF_MARGIN_LEFT, y, PDF_CONTENT_WIDTH, "Trade Set Hash", trade_set_hash)
    y -= 62

    draw_light_note_box(
        pdf,
        PDF_MARGIN_LEFT,
        y,
        PDF_CONTENT_WIDTH,
        "Generated from the canonical trade ledger and lifecycle-governed claim state in Trading Truth Layer.",
        height=40,
    )

    pdf.save()
    buffer.seek(0)
    return buffer, filename

def build_next_version_name(db: Session, workspace_id: int, base_name: str) -> str:
    match = re.match(r"^(.*?)(?:\s+v(\d+))?$", base_name.strip(), re.IGNORECASE)
    root_name = match.group(1).strip() if match else base_name.strip()

    existing = db.query(ClaimSchema).filter(ClaimSchema.workspace_id == workspace_id).all()

    max_version = 1
    pattern = re.compile(rf"^{re.escape(root_name)}(?:\s+v(\d+))?$", re.IGNORECASE)

    for schema in existing:
        m = pattern.match(schema.name.strip())
        if not m:
            continue
        version_str = m.group(1)
        version_num = int(version_str) if version_str else 1
        if version_num > max_version:
            max_version = version_num

    return f"{root_name} v{max_version + 1}"


@router.get("/claim-schemas/latest")
def get_latest_claim_schema(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    schema = db.query(ClaimSchema).order_by(ClaimSchema.id.desc()).first()
    if not schema:
        raise HTTPException(status_code=404, detail="No claim schemas found")

    require_workspace_member(schema.workspace_id, current_user, db)
    return serialize_schema(schema)


@router.get("/workspaces/{workspace_id}/claim-schemas")
def list_workspace_claim_schemas(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_workspace_member(workspace_id, current_user, db)

    rows = (
        db.query(ClaimSchema)
        .filter(ClaimSchema.workspace_id == workspace_id)
        .order_by(ClaimSchema.id.desc())
        .all()
    )

    return [build_claim_list_row(schema, db) for schema in rows]


@router.post("/claim-schemas")
def create_claim_schema(
    payload: ClaimSchemaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_workspace_operator_or_owner(payload.workspace_id, current_user, db)
    enforce_claim_creation_allowed(payload.workspace_id, db)

    visibility = normalize_visibility(payload.visibility)

    schema = ClaimSchema(
        workspace_id=payload.workspace_id,
        name=payload.name.strip(),
        period_start=payload.period_start.strip(),
        period_end=payload.period_end.strip(),
        included_member_ids_json=json.dumps(normalize_int_list(payload.included_member_ids_json)),
        included_symbols_json=json.dumps(normalize_symbol_list(payload.included_symbols_json)),
        excluded_trade_ids_json=json.dumps(normalize_int_list(payload.excluded_trade_ids_json)),
        methodology_notes=payload.methodology_notes or "",
        visibility=visibility,
        status="draft",
        parent_claim_id=None,
        root_claim_id=None,
        version_number=1,
    )

    db.add(schema)
    db.commit()
    db.refresh(schema)

    schema.root_claim_id = schema.id
    db.commit()
    db.refresh(schema)

    log_audit_event(
        db,
        event_type="claim_schema_created",
        entity_type="claim_schema",
        entity_id=schema.id,
        workspace_id=schema.workspace_id,
        old_state=None,
        new_state={
            "id": schema.id,
            "name": schema.name,
            "status": schema.status,
            "visibility": schema.visibility,
            "version_number": schema.version_number,
            "root_claim_id": schema.root_claim_id,
            "claim_hash": compute_claim_hash(schema),
        },
        metadata={
            "source": "claim_schemas.create_claim_schema",
            "period_start": schema.period_start,
            "period_end": schema.period_end,
            "actor_user_id": current_user.id,
        },
    )

    return serialize_schema(schema)


@router.patch("/claim-schemas/{claim_schema_id}")
def update_claim_schema(
    claim_schema_id: int,
    payload: ClaimSchemaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    schema = db.query(ClaimSchema).filter(ClaimSchema.id == claim_schema_id).first()
    if not schema:
        raise HTTPException(status_code=404, detail="Claim schema not found")

    require_workspace_operator_or_owner(schema.workspace_id, current_user, db)

    if schema.status != "draft":
        raise HTTPException(status_code=400, detail="Only draft claims can be edited")

    old_state = serialize_schema(schema)

    schema.name = payload.name.strip()
    schema.period_start = payload.period_start.strip()
    schema.period_end = payload.period_end.strip()
    schema.included_member_ids_json = json.dumps(normalize_int_list(payload.included_member_ids_json))
    schema.included_symbols_json = json.dumps(normalize_symbol_list(payload.included_symbols_json))
    schema.excluded_trade_ids_json = json.dumps(normalize_int_list(payload.excluded_trade_ids_json))
    schema.methodology_notes = payload.methodology_notes or ""
    schema.visibility = normalize_visibility(payload.visibility)

    db.commit()
    db.refresh(schema)

    log_audit_event(
        db,
        event_type="claim_schema_updated",
        entity_type="claim_schema",
        entity_id=schema.id,
        workspace_id=schema.workspace_id,
        old_state=old_state,
        new_state=serialize_schema(schema),
        metadata={
            "source": "claim_schemas.update_claim_schema",
            "actor_user_id": current_user.id,
        },
    )

    return serialize_schema(schema)


@router.post("/claim-schemas/{claim_schema_id}/clone")
def clone_claim_schema(
    claim_schema_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    source = db.query(ClaimSchema).filter(ClaimSchema.id == claim_schema_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Claim schema not found")

    require_workspace_operator_or_owner(source.workspace_id, current_user, db)
    enforce_claim_creation_allowed(source.workspace_id, db)

    root_id = source.root_claim_id or source.id
    new_name = build_next_version_name(db, source.workspace_id, source.name)

    cloned = ClaimSchema(
        workspace_id=source.workspace_id,
        name=new_name,
        period_start=source.period_start,
        period_end=source.period_end,
        included_member_ids_json=source.included_member_ids_json,
        included_symbols_json=source.included_symbols_json,
        excluded_trade_ids_json=source.excluded_trade_ids_json,
        methodology_notes=source.methodology_notes,
        visibility=source.visibility,
        status="draft",
        parent_claim_id=source.id,
        root_claim_id=root_id,
        version_number=(source.version_number or 1) + 1,
        verified_at=None,
        published_at=None,
        locked_at=None,
        locked_trade_set_hash=None,
    )

    db.add(cloned)
    db.commit()
    db.refresh(cloned)

    log_audit_event(
        db,
        event_type="claim_schema_cloned",
        entity_type="claim_schema",
        entity_id=cloned.id,
        workspace_id=cloned.workspace_id,
        old_state={
            "source_claim_id": source.id,
            "source_status": source.status,
            "source_version_number": source.version_number,
            "source_claim_hash": compute_claim_hash(source),
        },
        new_state={
            "id": cloned.id,
            "name": cloned.name,
            "status": cloned.status,
            "version_number": cloned.version_number,
            "parent_claim_id": cloned.parent_claim_id,
            "root_claim_id": cloned.root_claim_id,
            "claim_hash": compute_claim_hash(cloned),
        },
        metadata={
            "source": "claim_schemas.clone_claim_schema",
            "actor_user_id": current_user.id,
        },
    )

    return serialize_schema(cloned)


@router.get("/claim-schemas/{claim_schema_id}/versions")
def get_claim_versions(
    claim_schema_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    schema = db.query(ClaimSchema).filter(ClaimSchema.id == claim_schema_id).first()
    if not schema:
        raise HTTPException(status_code=404, detail="Claim schema not found")

    require_workspace_member(schema.workspace_id, current_user, db)

    root_id = schema.root_claim_id or schema.id

    versions = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id == schema.workspace_id,
            ((ClaimSchema.id == root_id) | (ClaimSchema.root_claim_id == root_id)),
        )
        .order_by(ClaimSchema.version_number.asc(), ClaimSchema.id.asc())
        .all()
    )

    return [serialize_version_row(v) for v in versions]


@router.get("/claim-schemas/{claim_schema_id}")
def get_claim_schema(
    claim_schema_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    schema = db.query(ClaimSchema).filter(ClaimSchema.id == claim_schema_id).first()
    if not schema:
        raise HTTPException(status_code=404, detail="Claim schema not found")

    require_workspace_member(schema.workspace_id, current_user, db)
    return serialize_schema(schema)


@router.post("/claim-schemas/{claim_schema_id}/verify")
def verify_claim_schema(
    claim_schema_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    schema = db.query(ClaimSchema).filter(ClaimSchema.id == claim_schema_id).first()
    if not schema:
        raise HTTPException(status_code=404, detail="Claim schema not found")

    require_workspace_operator_or_owner(schema.workspace_id, current_user, db)

    if schema.status != "draft":
        raise HTTPException(status_code=400, detail="Only draft claims can be verified")

    old_state = {
        "status": schema.status,
        "verified_at": schema.verified_at.isoformat() if schema.verified_at else None,
        "claim_hash": compute_claim_hash(schema),
    }

    schema.status = "verified"
    schema.verified_at = datetime.utcnow()
    db.commit()
    db.refresh(schema)

    log_audit_event(
        db,
        event_type="claim_schema_verified",
        entity_type="claim_schema",
        entity_id=schema.id,
        workspace_id=schema.workspace_id,
        old_state=old_state,
        new_state={
            "status": schema.status,
            "verified_at": schema.verified_at.isoformat() if schema.verified_at else None,
            "claim_hash": compute_claim_hash(schema),
        },
        metadata={
            "source": "claim_schemas.verify_claim_schema",
            "actor_user_id": current_user.id,
        },
    )

    return serialize_schema(schema)


@router.post("/claim-schemas/{claim_schema_id}/publish")
def publish_claim_schema(
    claim_schema_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    schema = db.query(ClaimSchema).filter(ClaimSchema.id == claim_schema_id).first()
    if not schema:
        raise HTTPException(status_code=404, detail="Claim schema not found")

    require_workspace_owner(schema.workspace_id, current_user, db)

    if schema.status != "verified":
        raise HTTPException(status_code=400, detail="Only verified claims can be published")

    old_state = {
        "status": schema.status,
        "visibility": schema.visibility,
        "published_at": schema.published_at.isoformat() if schema.published_at else None,
        "claim_hash": compute_claim_hash(schema),
    }

    original_visibility = schema.visibility
    schema.status = "published"
    schema.published_at = datetime.utcnow()

    if schema.visibility == "private":
        schema.visibility = "unlisted"

    db.commit()
    db.refresh(schema)

    log_audit_event(
        db,
        event_type="claim_schema_published",
        entity_type="claim_schema",
        entity_id=schema.id,
        workspace_id=schema.workspace_id,
        old_state=old_state,
        new_state={
            "status": schema.status,
            "visibility": schema.visibility,
            "published_at": schema.published_at.isoformat() if schema.published_at else None,
            "claim_hash": compute_claim_hash(schema),
            "is_publicly_accessible": is_claim_publicly_accessible(schema),
        },
        metadata={
            "source": "claim_schemas.publish_claim_schema",
            "actor_user_id": current_user.id,
            "visibility_changed": original_visibility != schema.visibility,
            "original_visibility": original_visibility,
            "effective_visibility": schema.visibility,
        },
    )

    return serialize_schema(schema)


@router.post("/claim-schemas/{claim_schema_id}/lock")
def lock_claim_schema(
    claim_schema_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    schema = db.query(ClaimSchema).filter(ClaimSchema.id == claim_schema_id).first()
    if not schema:
        raise HTTPException(status_code=404, detail="Claim schema not found")

    require_workspace_owner(schema.workspace_id, current_user, db)

    if schema.status == "locked":
        return serialize_schema(schema)

    if schema.status != "published":
        raise HTTPException(status_code=400, detail="Only published claims can be locked")

    filtered_trades = resolve_schema_trades(schema, db)

    old_state = {
        "status": schema.status,
        "locked_at": schema.locked_at.isoformat() if schema.locked_at else None,
        "locked_trade_set_hash": schema.locked_trade_set_hash,
        "claim_hash": compute_claim_hash(schema),
    }

    schema.locked_trade_set_hash = compute_trade_set_hash(filtered_trades)
    schema.status = "locked"
    schema.locked_at = datetime.utcnow()

    db.commit()
    db.refresh(schema)

    log_audit_event(
        db,
        event_type="claim_schema_locked",
        entity_type="claim_schema",
        entity_id=schema.id,
        workspace_id=schema.workspace_id,
        old_state=old_state,
        new_state={
            "status": schema.status,
            "locked_at": schema.locked_at.isoformat() if schema.locked_at else None,
            "locked_trade_set_hash": schema.locked_trade_set_hash,
            "claim_hash": compute_claim_hash(schema),
        },
        metadata={
            "source": "claim_schemas.lock_claim_schema",
            "trade_count": len(filtered_trades),
            "actor_user_id": current_user.id,
        },
    )

    return serialize_schema(schema)


@router.get("/claim-schemas/{claim_schema_id}/preview")
def get_claim_schema_preview(
    claim_schema_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    schema = db.query(ClaimSchema).filter(ClaimSchema.id == claim_schema_id).first()
    if not schema:
        raise HTTPException(status_code=404, detail="Claim schema not found")

    require_workspace_member(schema.workspace_id, current_user, db)

    filtered_trades = resolve_schema_trades(schema, db)
    metrics = compute_trade_metrics(filtered_trades)
    leaderboard = build_leaderboard(filtered_trades)

    return {
        "claim_schema_id": schema.id,
        "claim_hash": compute_claim_hash(schema),
        "name": schema.name,
        "verification_status": schema.status,
        "trade_count": metrics["trade_count"],
        "net_pnl": metrics["net_pnl"],
        "profit_factor": metrics["profit_factor"],
        "win_rate": metrics["win_rate"],
        "leaderboard": leaderboard,
        "scope": {
            "period_start": schema.period_start,
            "period_end": schema.period_end,
            "included_members": json.loads(schema.included_member_ids_json or "[]"),
            "included_symbols": json.loads(schema.included_symbols_json or "[]"),
            "methodology_notes": schema.methodology_notes,
            "visibility": schema.visibility,
        },
        "lifecycle": {
            "status": schema.status,
            "verified_at": schema.verified_at.isoformat() if schema.verified_at else None,
            "published_at": schema.published_at.isoformat() if schema.published_at else None,
            "locked_at": schema.locked_at.isoformat() if schema.locked_at else None,
            "locked_trade_set_hash": schema.locked_trade_set_hash,
        },
        "lineage": {
            "parent_claim_id": schema.parent_claim_id,
            "root_claim_id": schema.root_claim_id,
            "version_number": schema.version_number,
        },
    }


@router.get("/claim-schemas/{claim_schema_id}/equity-curve")
def get_claim_equity_curve(
    claim_schema_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    schema = db.query(ClaimSchema).filter(ClaimSchema.id == claim_schema_id).first()
    if not schema:
        raise HTTPException(status_code=404, detail="Claim schema not found")

    require_workspace_member(schema.workspace_id, current_user, db)

    filtered_trades = resolve_schema_trades(schema, db)
    equity_curve = build_equity_curve(filtered_trades)

    return {
        "claim_schema_id": schema.id,
        "claim_hash": compute_claim_hash(schema),
        "name": schema.name,
        "status": schema.status,
        "trade_count": len(filtered_trades),
        **equity_curve,
    }


@router.get("/claim-schemas/{claim_schema_id}/trades")
def get_claim_trades(
    claim_schema_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    schema = db.query(ClaimSchema).filter(ClaimSchema.id == claim_schema_id).first()
    if not schema:
        raise HTTPException(status_code=404, detail="Claim schema not found")

    require_workspace_member(schema.workspace_id, current_user, db)

    scope = resolve_schema_trade_scope(schema, db)
    included_rows = build_included_trade_scope_rows(scope["included"])
    excluded_rows = build_excluded_trade_scope_rows(scope["excluded"])

    return {
        "claim_schema_id": schema.id,
        "claim_hash": compute_claim_hash(schema),
        "name": schema.name,
        "status": schema.status,
        "trade_count": len(included_rows),
        "trades": included_rows,
        "included_trade_count": len(included_rows),
        "excluded_trade_count": len(excluded_rows),
        "included_trades": included_rows,
        "excluded_trades": excluded_rows,
        "summary": {
            "workspace_trade_count": scope["workspace_trade_count"],
            "included_trade_count": len(included_rows),
            "excluded_trade_count": len(excluded_rows),
            "excluded_breakdown": scope["excluded_breakdown"],
        },
    }


@router.get("/claim-schemas/{claim_schema_id}/evidence-pack")
def get_evidence_pack(
    claim_schema_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    schema = db.query(ClaimSchema).filter(ClaimSchema.id == claim_schema_id).first()
    if not schema:
        raise HTTPException(status_code=404, detail="Claim schema not found")

    require_workspace_member(schema.workspace_id, current_user, db)
    return build_evidence_pack_payload(schema, db)


@router.get("/claim-schemas/{claim_schema_id}/evidence-pack/download")
def download_evidence_pack(
    claim_schema_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    schema = db.query(ClaimSchema).filter(ClaimSchema.id == claim_schema_id).first()
    if not schema:
        raise HTTPException(status_code=404, detail="Claim schema not found")

    require_workspace_member(schema.workspace_id, current_user, db)

    payload = build_evidence_pack_payload(schema, db)
    filename = f'evidence_pack_claim_{schema.id}_{compute_claim_hash(schema)[:12]}.json'

    return JSONResponse(
        content=payload,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/claim-schemas/{claim_schema_id}/evidence-bundle")
def get_evidence_bundle(
    claim_schema_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    schema = db.query(ClaimSchema).filter(ClaimSchema.id == claim_schema_id).first()
    if not schema:
        raise HTTPException(status_code=404, detail="Claim schema not found")

    require_workspace_member(schema.workspace_id, current_user, db)
    return build_evidence_bundle_payload(schema, db)


@router.get("/claim-schemas/{claim_schema_id}/evidence-bundle/download")
def download_evidence_bundle(
    claim_schema_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    schema = db.query(ClaimSchema).filter(ClaimSchema.id == claim_schema_id).first()
    if not schema:
        raise HTTPException(status_code=404, detail="Claim schema not found")

    require_workspace_member(schema.workspace_id, current_user, db)

    zip_buffer, filename = build_evidence_bundle_zip_bytes(schema, db)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/claim-schemas/{claim_schema_id}/claim-report/download")
def download_internal_claim_report(
    claim_schema_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    schema = db.query(ClaimSchema).filter(ClaimSchema.id == claim_schema_id).first()
    if not schema:
        raise HTTPException(status_code=404, detail="Claim schema not found")

    require_workspace_member(schema.workspace_id, current_user, db)

    pdf_buffer, filename = build_claim_report_pdf_bytes(schema, db)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/public/claim-schemas/{claim_schema_id}/claim-report/download")
def download_public_claim_report(claim_schema_id: int, db: Session = Depends(get_db)):
    schema = db.query(ClaimSchema).filter(ClaimSchema.id == claim_schema_id).first()
    if not schema:
        raise HTTPException(status_code=404, detail="Claim schema not found")

    require_public_claim_access(schema)

    pdf_buffer, filename = build_claim_report_pdf_bytes(schema, db)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/public/claim-schemas/{claim_schema_id}")
def get_public_claim_schema(claim_schema_id: int, db: Session = Depends(get_db)):
    schema = db.query(ClaimSchema).filter(ClaimSchema.id == claim_schema_id).first()
    if not schema:
        raise HTTPException(status_code=404, detail="Claim schema not found")

    require_public_claim_access(schema)
    return build_public_claim_payload(schema, db)


@router.get("/public/claims")
def list_public_claims(db: Session = Depends(get_db)):
    rows = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.visibility == "public",
            ClaimSchema.status.in_(["published", "locked"]),
        )
        .order_by(ClaimSchema.id.desc())
        .all()
    )

    return [build_claim_list_row(schema, db) for schema in rows]


@router.get("/public/verify/{claim_hash}")
def verify_public_claim_by_hash(claim_hash: str, db: Session = Depends(get_db)):
    rows = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.visibility.in_(["public", "unlisted"]),
            ClaimSchema.status.in_(["published", "locked"]),
        )
        .all()
    )

    matched_schema = None
    for schema in rows:
        if compute_claim_hash(schema) == claim_hash:
            matched_schema = schema
            break

    if not matched_schema:
        raise HTTPException(status_code=404, detail="Public claim not found for supplied hash")

    payload = build_public_claim_payload(matched_schema, db)
    payload["claim_hash"] = claim_hash
    return payload


@router.get("/claim-schemas/{claim_schema_id}/verify-integrity")
def verify_claim_schema_integrity(
    claim_schema_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    schema = db.query(ClaimSchema).filter(ClaimSchema.id == claim_schema_id).first()
    if not schema:
        raise HTTPException(status_code=404, detail="Claim schema not found")

    require_workspace_member(schema.workspace_id, current_user, db)

    if schema.status != "locked":
        raise HTTPException(status_code=400, detail="Only locked claims can be integrity-verified")

    if not schema.locked_trade_set_hash:
        raise HTTPException(status_code=400, detail="Locked claim has no stored trade set hash")

    filtered_trades = resolve_schema_trades(schema, db)
    recomputed_hash = compute_trade_set_hash(filtered_trades)
    integrity_ok = recomputed_hash == schema.locked_trade_set_hash

    return {
        "claim_schema_id": schema.id,
        "claim_hash": compute_claim_hash(schema),
        "name": schema.name,
        "status": schema.status,
        "integrity_status": "valid" if integrity_ok else "compromised",
        "trade_count": len(filtered_trades),
        "stored_hash": schema.locked_trade_set_hash,
        "recomputed_hash": recomputed_hash,
        "hash_match": integrity_ok,
        "verified_at": datetime.utcnow().isoformat(),
    }
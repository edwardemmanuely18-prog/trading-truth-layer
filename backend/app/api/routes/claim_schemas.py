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
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import qr
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import (
    get_current_user,
    require_workspace_member,
    require_workspace_operator_or_owner,
    require_workspace_owner,
)
from app.core.db import get_db
from app.models.audit_event import AuditEvent
from app.models.claim_schema import ClaimSchema
from app.models.claim_dispute import ClaimDispute
from app.models.trade import Trade
from app.models.user import User
from app.models.workspace import Workspace
from app.services.workspace_usage import can_create_public_claim 
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


def normalize_plan_code(value: str | None) -> str:
    allowed = {"sandbox", "starter", "pro", "growth", "business"}
    normalized = str(value or "").strip().lower()
    return normalized if normalized in allowed else "starter"


def normalize_billing_status(value: str | None) -> str:
    allowed = {
        "inactive",
        "active",
        "trialing",
        "past_due",
        "canceled",
        "unpaid",
        "pending_manual_review",
    }
    normalized = str(value or "").strip().lower()
    return normalized if normalized in allowed else "inactive"


def is_paid_billing_status(status: str | None) -> bool:
    return normalize_billing_status(status) in {"active", "trialing"}


def resolve_effective_workspace_plan_code(workspace: Workspace) -> str:
    configured_plan = normalize_plan_code(workspace.plan_code)
    billing_status = normalize_billing_status(workspace.billing_status)

    if configured_plan in {"sandbox", "starter"}:
        return configured_plan

    if is_paid_billing_status(billing_status):
        return configured_plan

    return "starter"


def sandbox_public_visibility_allowed(visibility: str) -> bool:
    normalized_visibility = normalize_visibility(visibility)
    return normalized_visibility in {"private", "unlisted"}


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
        "claim_hash": schema.claim_hash or compute_claim_hash(schema),
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
        "claim_hash": schema.claim_hash or compute_claim_hash(schema),
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


def resolve_claim_dispute_context(schema: ClaimSchema, db: Session):
    disputes = (
        db.query(ClaimDispute)
        .filter(ClaimDispute.claim_schema_id == schema.id)
        .all()
    )

    total = len(disputes)

    active = [d for d in disputes if d.status == "open"]
    resolved = [d for d in disputes if d.status == "resolved"]

    has_active = len(active) > 0

    # penalty logic (authoritative backend rule)
    penalty_factor = 1.0
    if has_active:
        penalty_factor = 0.7  # ← your trust penalty

    return {
        "disputes_count": total,
        "active_disputes_count": len(active),
        "resolved_disputes_count": len(resolved),
        "has_active_dispute": has_active,
        "dispute_penalty_factor": penalty_factor,
    }


def compute_backend_trust_score(
    schema: ClaimSchema,
    metrics: dict,
    integrity_status: str,
    dispute_ctx: dict,
):
    score = 0.0

    if integrity_status == "valid":
        score += 40

    if schema.status == "locked":
        score += 20
    elif schema.status in {"published", "verified"}:
        score += 12

    trade_count = int(metrics.get("trade_count", 0) or 0)
    if trade_count >= 50:
        score += 20
    elif trade_count >= 20:
        score += 15
    elif trade_count >= 10:
        score += 10
    elif trade_count > 0:
        score += 5

    if schema.verified_at:
        score += 10

    if schema.visibility == "public":
        score += 10
    elif schema.visibility == "unlisted":
        score += 6

    penalty_factor = float(dispute_ctx.get("dispute_penalty_factor", 1.0) or 1.0)
    score = score * penalty_factor

    return round(min(score, 100.0), 2)


def resolve_claim_origin_type(schema: ClaimSchema):
    version_number = int(schema.version_number or 1)
    has_parent = schema.parent_claim_id is not None
    has_root = schema.root_claim_id is not None

    if version_number > 1:
        return "versioned"
    if has_parent or has_root:
        return "derived"
    return "independent"


def compute_backend_network_score(schema: ClaimSchema, trust_score: float):
    claim_origin_type = resolve_claim_origin_type(schema)
    version_number = int(schema.version_number or 1)

    if claim_origin_type == "independent":
        independence_weight = 1.0
        lineage_penalty = 1.0
        version_decay = 1.0
        version_depth = 0
        network_context_label = "Independent"
    elif claim_origin_type == "derived":
        independence_weight = 0.90
        lineage_penalty = 0.92
        version_decay = 1.0
        version_depth = 1
        network_context_label = "Derived"
    else:
        independence_weight = 0.94
        lineage_penalty = 0.96
        version_depth = max(version_number - 1, 1)
        version_decay = max(0.82, 1 - version_depth * 0.03)
        network_context_label = "Versioned"

    network_score = trust_score * independence_weight * lineage_penalty * version_decay

    return {
        "claim_origin_type": claim_origin_type,
        "root_claim_ref": f"claim#{schema.root_claim_id}" if schema.root_claim_id else None,
        "parent_claim_ref": f"claim#{schema.parent_claim_id}" if schema.parent_claim_id else None,
        "version_depth": version_depth,
        "independence_weight": round(independence_weight, 2),
        "lineage_penalty": round(lineage_penalty, 2),
        "version_decay": round(version_decay, 2),
        "network_score": round(network_score, 2),
        "network_context_label": network_context_label,
    }


def resolve_trust_band(score: float):
    if score >= 85:
        return "high"
    if score >= 60:
        return "moderate"
    return "low"


def resolve_profile_trust_band(score: float):
    if score >= 85:
        return "institutional"
    if score >= 70:
        return "strong"
    if score >= 55:
        return "developing"
    return "fragile"


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


def resolve_claim_integrity_status(schema: ClaimSchema, trades: list[Trade]) -> str:
    """
    Canonical integrity resolver used across public surfaces and verify routes.

    locked:
      - valid        => stored locked hash matches recomputed hash
      - compromised  => stored locked hash missing or mismatched

    non-locked:
      - unlocked     => claim has not reached locked finality yet
    """
    if schema.status != "locked":
        return "unlocked"

    if not schema.locked_trade_set_hash:
        return "compromised"

    recomputed_trade_set_hash = compute_trade_set_hash(trades)
    return "valid" if recomputed_trade_set_hash == schema.locked_trade_set_hash else "compromised"


def build_issuer_payload(schema: ClaimSchema, db: Session):
    workspace = get_workspace_or_404(schema.workspace_id, db)
    profile = build_public_trust_profile_for_workspace(schema.workspace_id, db)

    return {
        "id": workspace.id,
        "name": workspace.name,
        "type": "workspace",
        "network": "internal",
        "profile": profile,
    }


def build_public_trust_profile_for_workspace(workspace_id: int, db: Session):
    workspace = get_workspace_or_404(workspace_id, db)

    claims = (
        db.query(ClaimSchema)
        .filter(ClaimSchema.workspace_id == workspace_id)
        .all()
    )

    public_claims = [
        schema
        for schema in claims
        if schema.visibility in {"public", "unlisted"}
    ]
    locked_claims = [
        schema
        for schema in public_claims
        if schema.status == "locked"
    ]

    trust_scores = []
    network_scores = []
    total_net_pnl = 0.0
    contested_claims_count = 0

    for schema in locked_claims:
        filtered_trades = resolve_schema_trades(schema, db)
        metrics = compute_trade_metrics(filtered_trades)
        dispute_ctx = resolve_claim_dispute_context(schema, db)
        integrity_status = resolve_claim_integrity_status(schema, filtered_trades)
        trust_score = compute_backend_trust_score(
            schema, metrics, integrity_status, dispute_ctx
        )
        network_ctx = compute_backend_network_score(schema, trust_score)

        trust_scores.append(trust_score)
        network_scores.append(network_ctx["network_score"])
        total_net_pnl += float(metrics.get("net_pnl", 0.0) or 0.0)

        if dispute_ctx["has_active_dispute"]:
            contested_claims_count += 1

    claims_count = len(public_claims)
    locked_claims_count = len(locked_claims)

    average_trust_score = (
        round(sum(trust_scores) / len(trust_scores), 2) if trust_scores else 0.0
    )
    average_network_score = (
        round(sum(network_scores) / len(network_scores), 2) if network_scores else 0.0
    )

    return {
        "profile_id": f"workspace:{workspace.id}",
        "workspace_id": workspace.id,
        "name": workspace.name,
        "type": "workspace",
        "network": "internal",
        "claims_count": claims_count,
        "locked_claims_count": locked_claims_count,
        "contested_claims_count": contested_claims_count,
        "average_trust_score": average_trust_score,
        "average_network_score": average_network_score,
        "total_net_pnl": round(total_net_pnl, 4),
        "trust_profile_band": resolve_profile_trust_band(average_trust_score),
    }


def build_public_profile_response(workspace_id: int, db: Session):
    profile = build_public_trust_profile_for_workspace(workspace_id, db)

    claims = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id == workspace_id,
            ClaimSchema.visibility.in_(["public", "unlisted"]),
        )
        .all()
    )

    claim_rows = [
        build_claim_list_row(schema, db)
        for schema in claims
        if is_claim_publicly_accessible(schema)
    ]

    return {
        "profile": profile,
        "claims": claim_rows,
        "claims_count": len(claim_rows),
    }


def build_claim_list_row(schema: ClaimSchema, db: Session):
    filtered_trades = resolve_schema_trades(schema, db)
    metrics = compute_trade_metrics(filtered_trades)
    leaderboard = build_leaderboard(filtered_trades)
    integrity_status = resolve_claim_integrity_status(schema, filtered_trades)
    dispute_ctx = resolve_claim_dispute_context(schema, db)
    trust_score = compute_backend_trust_score(schema, metrics, integrity_status, dispute_ctx)
    network_ctx = compute_backend_network_score(schema, trust_score)
    trust_weighted_pnl = round(float(metrics["net_pnl"]) * trust_score / 100.0, 4)
    network_weighted_pnl = round(float(metrics["net_pnl"]) * network_ctx["network_score"] / 100.0, 4)

    trade_set_hash = schema.locked_trade_set_hash
    if not trade_set_hash:
        trade_set_hash = compute_trade_set_hash(filtered_trades)

    claim_hash = schema.claim_hash or compute_claim_hash(schema)

    return {
    "claim_schema_id": schema.id,
    "claim_hash": claim_hash,

    "issuer": build_issuer_payload(schema, db),

    "integrity_status": integrity_status,
    "public_view_path": f"/claim/{schema.id}/public",
    "verify_path": f"/verify/{claim_hash}",

    "name": schema.name,
    "verification_status": schema.status,

    "trade_count": metrics["trade_count"],
    "net_pnl": metrics["net_pnl"],
    "profit_factor": metrics["profit_factor"],
    "win_rate": metrics["win_rate"],

    "leaderboard": leaderboard,

    "disputes_count": dispute_ctx["disputes_count"],
    "active_disputes_count": dispute_ctx["active_disputes_count"],
    "has_active_dispute": dispute_ctx["has_active_dispute"],
    "dispute_penalty_factor": dispute_ctx["dispute_penalty_factor"],

    "trust_score": trust_score,
    "trust_band": "contested" if dispute_ctx["has_active_dispute"] else resolve_trust_band(trust_score),
    "trust_weighted_pnl": trust_weighted_pnl,

    "network_score": network_ctx["network_score"],
    "network_weighted_pnl": network_weighted_pnl,
    "network": network_ctx,

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
    },

    "lineage": {
        "parent_claim_id": schema.parent_claim_id,
        "root_claim_id": schema.root_claim_id,
        "version_number": schema.version_number,
    },

    "is_publicly_accessible": is_claim_publicly_accessible(schema),
}


def build_public_claim_payload(schema: ClaimSchema, db: Session):
    filtered_trades = resolve_schema_trades(schema, db)
    metrics = compute_trade_metrics(filtered_trades)
    dispute_ctx = resolve_claim_dispute_context(schema, db)
    leaderboard = build_leaderboard(filtered_trades)

    # apply dispute penalty to leaderboard scores
    if dispute_ctx["has_active_dispute"]:
        for row in leaderboard:
            row["net_pnl_adjusted"] = round(
                row["net_pnl"] * dispute_ctx["dispute_penalty_factor"], 4
            )
    else:
        for row in leaderboard:
            row["net_pnl_adjusted"] = row["net_pnl"]

    # re-rank based on adjusted pnl
    leaderboard.sort(key=lambda x: x["net_pnl_adjusted"], reverse=True)

    for idx, row in enumerate(leaderboard, start=1):
        row["rank"] = idx

    trade_set_hash = schema.locked_trade_set_hash
    if not trade_set_hash:
        trade_set_hash = compute_trade_set_hash(filtered_trades)

    integrity_status = resolve_claim_integrity_status(schema, filtered_trades)
    trust_score = compute_backend_trust_score(schema, metrics, integrity_status, dispute_ctx)
    network_ctx = compute_backend_network_score(schema, trust_score)
    trust_weighted_pnl = round(float(metrics["net_pnl"]) * trust_score / 100.0, 4)
    network_weighted_pnl = round(float(metrics["net_pnl"]) * network_ctx["network_score"] / 100.0, 4)

    scope = resolve_schema_trade_scope(schema, db)
    included_rows = build_included_trade_scope_rows(scope["included"])
    excluded_rows = build_excluded_trade_scope_rows(scope["excluded"])
    equity_curve = build_equity_curve(scope["included"])
    claim_hash = schema.claim_hash or compute_claim_hash(schema)
    issuer = build_issuer_payload(schema, db)

    return {
        "claim_schema_id": schema.id,
        "claim_hash": claim_hash,
        "public_view_path": f"/claim/{schema.id}/public",
        "verify_path": f"/verify/{claim_hash}",
        "name": schema.name,
        "verification_status": schema.status,
        "integrity_status": integrity_status,
        "trade_count": metrics["trade_count"],
        "net_pnl": metrics["net_pnl"],
        "profit_factor": metrics["profit_factor"],
        "win_rate": metrics["win_rate"],
        "leaderboard": leaderboard,
        "issuer": issuer,
        "profile": build_public_trust_profile_for_workspace(schema.workspace_id, db),
        "disputes": dispute_ctx,
        "trust_score": trust_score,
        "trust_band": "contested" if dispute_ctx["has_active_dispute"] else resolve_trust_band(trust_score),
        "trust_weighted_pnl": trust_weighted_pnl,
        "network_score": network_ctx["network_score"],
        "network_weighted_pnl": network_weighted_pnl,
        "network": network_ctx,
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
        "claim_hash": schema.claim_hash or compute_claim_hash(schema),
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
        "claim_hash": schema.claim_hash or compute_claim_hash(schema),
        "exported_at": datetime.utcnow().isoformat(),
        "export_version": "audit_events_v1",
        "event_count": len(events),
        "events": [serialize_audit_event(event) for event in events],
    }


def build_evidence_bundle_manifest(schema: ClaimSchema):
    claim_hash = schema.claim_hash or compute_claim_hash(schema)
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
        "claim_hash": schema.claim_hash or compute_claim_hash(schema),
        "exported_at": manifest["exported_at"],
        "export_version": manifest["export_version"],
        "included_files": manifest["included_files"],
        "manifest": manifest,
        "evidence_pack": evidence_pack,
        "audit_events": audit_events,
    }


def build_evidence_bundle_zip_bytes(schema: ClaimSchema, db: Session) -> tuple[BytesIO, str]:
    claim_hash = schema.claim_hash or compute_claim_hash(schema)
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
            return shorten_text(text, 24)

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

    line_left = x
    line_right = PDF_PAGE_WIDTH - PDF_MARGIN_RIGHT

    pdf.setStrokeColor(colors.HexColor("#D8E1EC"))
    pdf.setLineWidth(0.8)
    pdf.line(line_left, y - 9, line_right, y - 9)
    pdf.line(line_left, y - 15, line_right, y - 15)

    pdf.setFillColor(colors.black)
    pdf.setStrokeColor(colors.black)
    pdf.setLineWidth(1)
    return y - 30


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
    pdf.setFont("Helvetica-Bold", 9)

    lines = split_wrapped_lines(value or "—", 108, "Helvetica-Bold", 9)
    if not lines:
        lines = ["—"]

    current_y = y - 14
    for line in lines[:3]:
        pdf.drawString(x, current_y, line)
        current_y -= 10

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
            "drawdown_peak_point": None,
            "drawdown_trough_point": None,
            "has_drawdown": False,
            "net_change": 0.0,
            "peak_equals_trough": False,
        }

    peak_point = max(points, key=lambda p: float(p.get("cumulative_pnl", 0.0)))
    trough_point = min(points, key=lambda p: float(p.get("cumulative_pnl", 0.0)))

    running_peak = float("-inf")
    max_drawdown = 0.0
    drawdown_peak_point = None
    drawdown_trough_point = None
    current_peak_point = None

    for point in points:
        current = float(point.get("cumulative_pnl", 0.0))
        if current > running_peak:
            running_peak = current
            current_peak_point = point

        drawdown = running_peak - current
        if drawdown > max_drawdown:
            max_drawdown = drawdown
            drawdown_peak_point = current_peak_point
            drawdown_trough_point = point

    start_value = float(points[0].get("cumulative_pnl", 0.0))
    end_value = float(points[-1].get("cumulative_pnl", 0.0))

    return {
        "max_drawdown": round(max_drawdown, 4),
        "peak_cumulative": round(float(peak_point.get("cumulative_pnl", 0.0)), 4),
        "trough_cumulative": round(float(trough_point.get("cumulative_pnl", 0.0)), 4),
        "peak_point": peak_point,
        "trough_point": trough_point,
        "drawdown_peak_point": drawdown_peak_point,
        "drawdown_trough_point": drawdown_trough_point,
        "has_drawdown": max_drawdown > 0,
        "net_change": round(end_value - start_value, 4),
        "peak_equals_trough": peak_point.get("index") == trough_point.get("index"),
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

    pdf.setFillColor(colors.HexColor("#0F172A"))
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(x + 14, top_y - 18, "Equity Curve Preview")

    if not points:
        pdf.setFillColor(colors.HexColor("#64748B"))
        pdf.setFont("Helvetica", 10)
        pdf.drawString(x + 14, top_y - 46, "No equity curve data available.")
        pdf.setFillColor(colors.black)
        return

    chart_x = x + 22
    chart_y_top = top_y - 40
    chart_y_bottom = top_y - height + 26
    chart_w = width - 44
    chart_h = chart_y_top - chart_y_bottom

    values = [float(p.get("cumulative_pnl", 0.0)) for p in points]
    min_value = min(min(values), 0.0)
    max_value = max(max(values), 0.0)
    range_value = max_value - min_value
    if range_value == 0:
        range_value = 1.0

    stats = compute_drawdown_stats(points)

    def x_for(index: int):
        if len(points) <= 1:
            return chart_x + chart_w / 2
        return chart_x + (index / (len(points) - 1)) * chart_w

    def y_for(value: float):
        return chart_y_bottom + ((value - min_value) / range_value) * chart_h

    # grid
    pdf.setStrokeColor(colors.HexColor("#F1F5F9"))
    pdf.setLineWidth(1)
    for i in range(6):
        tick_value = min_value + ((max_value - min_value) / 5) * i
        y_tick = y_for(tick_value)
        pdf.line(chart_x, y_tick, chart_x + chart_w, y_tick)

        pdf.setFillColor(colors.HexColor("#64748B"))
        pdf.setFont("Helvetica", 8)
        pdf.drawRightString(chart_x - 8, y_tick - 3, f"{round(tick_value, 1)}")

    # x axis ticks
    tick_indexes = list(range(len(points))) if len(points) <= 8 else [0, (len(points) - 1) // 2, len(points) - 1]
    tick_indexes = list(dict.fromkeys(tick_indexes))

    pdf.setStrokeColor(colors.HexColor("#F8FAFC"))
    for tick_index in tick_indexes:
        tick_x = x_for(tick_index)
        pdf.line(tick_x, chart_y_bottom, tick_x, chart_y_top)

        point = points[tick_index]
        pdf.setFillColor(colors.HexColor("#64748B"))
        pdf.setFont("Helvetica", 8)
        pdf.drawCentredString(tick_x, chart_y_bottom - 12, str(point.get("index", tick_index + 1)))

        opened_text = str(point.get("opened_at", ""))[:10]
        pdf.setFillColor(colors.HexColor("#475569"))
        pdf.setFont("Helvetica", 7)
        pdf.drawCentredString(tick_x, chart_y_bottom - 24, opened_text)

    # axes
    pdf.setStrokeColor(colors.HexColor("#CBD5E1"))
    pdf.setLineWidth(1)
    pdf.line(chart_x, chart_y_bottom, chart_x, chart_y_top)
    pdf.line(chart_x, chart_y_bottom, chart_x + chart_w, chart_y_bottom)

    # area fill
    if len(points) >= 2:
        fill_path = pdf.beginPath()
        first_x = x_for(0)
        first_y = y_for(float(points[0].get("cumulative_pnl", 0.0)))
        fill_path.moveTo(first_x, chart_y_bottom)
        fill_path.lineTo(first_x, first_y)
        for idx, point in enumerate(points[1:], start=1):
            fill_path.lineTo(x_for(idx), y_for(float(point.get("cumulative_pnl", 0.0))))
        fill_path.lineTo(x_for(len(points) - 1), chart_y_bottom)
        fill_path.close()

        pdf.setFillColor(colors.HexColor("#E2E8F0"))
        pdf.setStrokeColor(colors.HexColor("#E2E8F0"))
        pdf.drawPath(fill_path, fill=1, stroke=0)

    # drawdown shade
    if stats["has_drawdown"] and stats["drawdown_peak_point"] and stats["drawdown_trough_point"]:
        peak_idx = max(0, int(stats["drawdown_peak_point"]["index"]) - 1)
        trough_idx = max(0, int(stats["drawdown_trough_point"]["index"]) - 1)

        dd_x1 = x_for(peak_idx)
        dd_x2 = x_for(trough_idx)
        dd_y_peak = y_for(float(stats["drawdown_peak_point"]["cumulative_pnl"]))
        dd_y_trough = y_for(float(stats["drawdown_trough_point"]["cumulative_pnl"]))

        left_x = min(dd_x1, dd_x2)
        right_x = max(dd_x1, dd_x2)

        pdf.setFillColor(colors.HexColor("#FDECEC"))
        pdf.setStrokeColor(colors.HexColor("#FDECEC"))
        pdf.rect(left_x, dd_y_trough, right_x - left_x, dd_y_peak - dd_y_trough, fill=1, stroke=0)

        pdf.setStrokeColor(colors.HexColor("#94A3B8"))
        pdf.setDash(4, 4)
        pdf.line(dd_x1, dd_y_peak, dd_x2, dd_y_trough)
        pdf.setDash()

    # line halo
    pdf.setStrokeColor(colors.HexColor("#CBD5E1"))
    pdf.setLineWidth(5)
    prev_x = None
    prev_y = None
    for idx, point in enumerate(points):
        px = x_for(idx)
        py = y_for(float(point.get("cumulative_pnl", 0.0)))
        if prev_x is not None:
            pdf.line(prev_x, prev_y, px, py)
        prev_x = px
        prev_y = py

    # main line
    pdf.setStrokeColor(colors.HexColor("#0F172A"))
    pdf.setLineWidth(2.4)
    prev_x = None
    prev_y = None
    for idx, point in enumerate(points):
        px = x_for(idx)
        py = y_for(float(point.get("cumulative_pnl", 0.0)))
        if prev_x is not None:
            pdf.line(prev_x, prev_y, px, py)
        prev_x = px
        prev_y = py

    # point markers
    pdf.setFillColor(colors.HexColor("#0F172A"))
    for idx, point in enumerate(points):
        px = x_for(idx)
        py = y_for(float(point.get("cumulative_pnl", 0.0)))
        pdf.circle(px, py, 2.4, stroke=0, fill=1)

    peak_point = stats["peak_point"]
    trough_point = stats["trough_point"]

    if peak_point and trough_point and stats["peak_equals_trough"]:
        idx = max(0, int(peak_point["index"]) - 1)
        px = x_for(idx)
        py = y_for(float(peak_point["cumulative_pnl"]))
        pdf.setFillColor(colors.HexColor("#16A34A"))
        pdf.circle(px, py, 4.2, stroke=0, fill=1)
        pdf.setFont("Helvetica-Bold", 8)
        pdf.drawString(px + 10, py + 8, f"Peak / Trough {round(float(peak_point['cumulative_pnl']), 2)}")
    else:
        if peak_point:
            idx = max(0, int(peak_point["index"]) - 1)
            px = x_for(idx)
            py = y_for(float(peak_point["cumulative_pnl"]))
            pdf.setFillColor(colors.HexColor("#16A34A"))
            pdf.circle(px, py, 4.2, stroke=0, fill=1)
            pdf.setFont("Helvetica-Bold", 8)
            pdf.drawString(px + 10, py + 8, f"Peak {round(float(peak_point['cumulative_pnl']), 2)}")

        if trough_point:
            idx = max(0, int(trough_point["index"]) - 1)
            px = x_for(idx)
            py = y_for(float(trough_point["cumulative_pnl"]))
            pdf.setFillColor(colors.HexColor("#DC2626"))
            pdf.circle(px, py, 4.2, stroke=0, fill=1)
            pdf.setFont("Helvetica-Bold", 8)
            pdf.drawRightString(px - 10, py + 8, f"Trough {round(float(trough_point['cumulative_pnl']), 2)}")

    # net change
    pdf.setFillColor(colors.HexColor("#64748B"))
    pdf.setFont("Helvetica", 8)
    sign = "+" if stats["net_change"] > 0 else ""
    pdf.drawRightString(chart_x + chart_w, chart_y_top + 8, f"Net change {sign}{stats['net_change']}")
    pdf.setFillColor(colors.black)


def draw_table_header(
    pdf: canvas.Canvas,
    x: float,
    y: float,
    headers: list[tuple[float, str]],
    font_size: int = 9,
    table_width: float | None = None,
):
    pdf.setFont("Helvetica-Bold", font_size)
    pdf.setFillColor(colors.HexColor("#64748B"))
    for offset, label in headers:
        pdf.drawString(x + offset, y, label)

    line_right = x + table_width if table_width is not None else PDF_PAGE_WIDTH - PDF_MARGIN_RIGHT

    pdf.setStrokeColor(colors.HexColor("#CBD5E1"))
    pdf.line(x, y - 8, line_right, y - 8)

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
    scope = resolve_schema_trade_scope(schema, db)
    filtered_trades = scope["included"]
    excluded_trades = scope["excluded"]

    metrics = compute_trade_metrics(filtered_trades)
    leaderboard = build_leaderboard(filtered_trades)
    equity_curve = build_equity_curve(filtered_trades)
    evidence_rows = build_trade_evidence(filtered_trades)
    drawdown_stats = compute_drawdown_stats(equity_curve["curve"])

    audit_events = (
        db.query(AuditEvent)
        .filter(
            AuditEvent.entity_type == "claim_schema",
            AuditEvent.entity_id == str(schema.id),
        )
        .order_by(AuditEvent.id.asc())
        .all()
    )
    exported_at = datetime.utcnow()

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

    public_view_path = f"/claim/{schema.id}/public"
    verify_link_path = f"/verify/{claim_hash}"
    verify_link_short = f"/verify/{short_hash(claim_hash, 14, 8)}"

    if schema.status == "draft":
        document_title = f"Draft Trading Claim Report · {schema.name}"
    elif schema.status == "published":
        document_title = f"Verified Trading Claim Report · {schema.name}"
    elif schema.status == "locked":
        document_title = f"Locked Verified Claim Report · {schema.name}"
    else:
        document_title = f"Trading Claim Report · {schema.name}"

    filename = f"claim_report_{schema.id}_{claim_hash[:12]}.pdf"

    def fmt_num(value, digits=2):
        try:
            return f"{float(value):,.{digits}f}"
        except Exception:
            return "—"

    def fmt_pct_ratio(value, digits=2):
        try:
            return f"{float(value) * 100:.{digits}f}%"
        except Exception:
            return "—"

    def fmt_dt(value):
        if not value:
            return "—"
        try:
            return value.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return format_pdf_datetime(value)

    def fmt_gap_days(delta_value):
        if delta_value is None:
            return "—"
        try:
            days = float(delta_value) / 86400.0
            return f"{days:.2f}"
        except Exception:
            return "—"

    # =========================
    # VISUAL SYSTEM
    # =========================
    PAGE_TOP_GAP = 12
    SECTION_GAP = 28
    BLOCK_GAP = 18
    CARD_GAP = 12
    MINI_GAP = 10
    PAGE_BOTTOM_SAFE = 76

    SECTION_TOP_SPACING = 18
    SECTION_BOTTOM_SPACING = 10
    FIELD_ROW_SPACING = 16
    COMPACT_ROW_GAP = 10
    PANEL_INNER_PADDING = 10

    COLOR_INK = colors.HexColor("#0F172A")
    COLOR_TEXT = colors.HexColor("#334155")
    COLOR_MUTED = colors.HexColor("#64748B")
    COLOR_LINE = colors.HexColor("#CBD5E1")
    COLOR_LINE_SOFT = colors.HexColor("#E2E8F0")
    COLOR_FILL_SOFT = colors.HexColor("#F8FAFC")
    COLOR_FILL_ALT = colors.HexColor("#F1F5F9")
    COLOR_GREEN_BG = colors.HexColor("#ECFDF5")
    COLOR_GREEN_LINE = colors.HexColor("#86EFAC")
    COLOR_GREEN_TEXT = colors.HexColor("#166534")
    COLOR_RED_BG = colors.HexColor("#FEF2F2")
    COLOR_RED_LINE = colors.HexColor("#FCA5A5")
    COLOR_RED_TEXT = colors.HexColor("#991B1B")
    COLOR_NAVY = colors.HexColor("#0B132B")
    COLOR_BLUE_LINE = colors.HexColor("#CBD5F5")
    COLOR_BLUE_ACCENT = colors.HexColor("#1D4ED8")
    COLOR_TABLE_HEADER = colors.HexColor("#F1F5F9")
    COLOR_TABLE_ALT = colors.HexColor("#F8FAFC")
    COLOR_TABLE_BORDER = colors.HexColor("#D7E1EC")

    TITLE_XL = 26
    TITLE_L = 19
    TITLE_M = 15
    TITLE_S = 12
    TEXT_L = 11
    TEXT_M = 10
    TEXT_S = 9
    TEXT_XS = 8

    TABLE_TOTAL_W = PDF_PAGE_WIDTH - PDF_MARGIN_LEFT - PDF_MARGIN_RIGHT

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle(filename)
    pdf.setAuthor("Trading Truth Layer")
    pdf.setSubject("Verified Trading Claim Report")

    page_number = 1
    y = pdf_start_page(pdf, page_number, document_title, claim_hash)
    y -= PAGE_TOP_GAP

    def new_page():
        nonlocal y, page_number
        page_number += 1
        y = pdf_new_page(pdf, page_number, document_title, claim_hash)
        y -= PAGE_TOP_GAP

    def ensure_space(required_height: float):
        nonlocal y
        if y - required_height < PAGE_BOTTOM_SAFE:
            new_page()

    def should_start_new_page(required_height: float, min_remaining_after_draw: float = 100):
        return (y - required_height) < (PAGE_BOTTOM_SAFE + min_remaining_after_draw)

    def start_section_if_needed(required_height: float, min_remaining_after_draw: float = 100):
        nonlocal y
        if should_start_new_page(required_height, min_remaining_after_draw):
            new_page()

    def draw_hr(y_pos, stroke=COLOR_LINE_SOFT):
        pdf.setStrokeColor(stroke)
        pdf.setLineWidth(1)
        pdf.line(PDF_MARGIN_LEFT, y_pos, PDF_PAGE_WIDTH - PDF_MARGIN_RIGHT, y_pos)

    def draw_soft_panel(x, top_y, w, h, radius=14, fill=colors.white, stroke=COLOR_LINE_SOFT):
        pdf_round_box(pdf, x, top_y, w, h, fill, stroke, radius=radius)

    def wrapped_lines(text, max_width, font_name="Helvetica", font_size=TEXT_M):
        return split_wrapped_lines(str(text or "—"), max_width, font_name, font_size) or ["—"]

    def estimate_kv_grid_cell_height(value, max_width=120, value_font="Helvetica-Bold", value_size=10, max_lines=4):
        lines = wrapped_lines(value, max_width, value_font, value_size)[:max_lines]
        return 14 + (len(lines) * 11)

    def draw_kv_grid_cell(x, y_pos, label, value, max_width=120, value_font="Helvetica-Bold", value_size=10, max_lines=4):
        pdf.setFillColor(COLOR_MUTED)
        pdf.setFont("Helvetica", TEXT_S)
        pdf.drawString(x, y_pos, label)
        lines = wrapped_lines(value, max_width, value_font, value_size)[:max_lines]
        pdf.setFillColor(COLOR_INK)
        pdf.setFont(value_font, value_size)
        v_y = y_pos - 14
        for line in lines:
            pdf.drawString(x, v_y, line)
            v_y -= 11

    def draw_metric_card_v2(x, top_y, w, h, label, value, sublabel, value_color=COLOR_INK):
        draw_soft_panel(x, top_y, w, h, radius=14, fill=COLOR_FILL_SOFT, stroke=COLOR_BLUE_LINE)
        pdf.setFillColor(COLOR_MUTED)
        pdf.setFont("Helvetica", TEXT_M)
        pdf.drawString(x + PANEL_INNER_PADDING + 4, top_y - 20, label)

        value_lines = wrapped_lines(value, w - 28, "Helvetica-Bold", 17)[:2]
        pdf.setFillColor(value_color)
        pdf.setFont("Helvetica-Bold", 18)
        value_y = top_y - 44
        for line in value_lines:
            pdf.drawString(x + PANEL_INNER_PADDING + 4, value_y, line)
            value_y -= 16

        pdf.setFillColor(COLOR_MUTED)
        pdf.setFont("Helvetica", TEXT_S)
        pdf.drawString(x + PANEL_INNER_PADDING + 4, top_y - h + 16, sublabel)

    def draw_label_value_box_v2(x, top_y, w, h, label, value, value_font="Helvetica", value_size=8):
        draw_soft_panel(x, top_y, w, h, radius=14, fill=COLOR_FILL_ALT, stroke=COLOR_LINE)
        pdf.setFillColor(COLOR_MUTED)
        pdf.setFont("Helvetica", TEXT_M)
        pdf.drawString(x + 12, top_y - 18, label)
        pdf.setFillColor(COLOR_INK)
        pdf.setFont(value_font, value_size)
        lines = wrapped_lines(value, w - 24, value_font, value_size)[:3]
        v_y = top_y - 36
        for line in lines:
            pdf.drawString(x + 12, v_y, line)
            v_y -= 10

    def draw_highlight_note(x, top_y, w, text, label=None, min_height=44):
        text_lines = wrapped_lines(text, w - 28, "Helvetica", TEXT_M)
        h = max(min_height, 18 + 14 + (len(text_lines) * 12) + 12)
        if label:
            pdf.setFillColor(COLOR_MUTED)
            pdf.setFont("Helvetica", TEXT_M)
            pdf.drawString(x, top_y - 2, label)
            top_y -= 14
        draw_soft_panel(x, top_y, w, h, radius=14, fill=COLOR_FILL_ALT, stroke=COLOR_LINE)
        pdf.setFillColor(COLOR_TEXT)
        pdf.setFont("Helvetica", TEXT_M)
        yy = top_y - 18
        for line in text_lines:
            pdf.drawString(x + 14, yy, line)
            yy -= 12
        return top_y - h

    def estimate_highlight_note_height(text, w, label=None, min_height=44):
        text_lines = wrapped_lines(text, w - 28, "Helvetica", TEXT_M)
        h = max(min_height, 18 + 14 + (len(text_lines) * 12) + 12)
        if label:
            h += 14
        return h

    def draw_hash_block_v2(x, top_y, w, label, value, emphasize=False):
        label_color = COLOR_BLUE_ACCENT if emphasize else COLOR_MUTED
        stroke = colors.HexColor("#93C5FD") if emphasize else COLOR_LINE
        fill = colors.HexColor("#EFF6FF") if emphasize else COLOR_FILL_SOFT

        pdf.setFillColor(label_color)
        pdf.setFont("Helvetica-Bold" if label in {"Claim Hash", "Trade Set Hash", "Public View Path", "Verify Link Path"} else "Helvetica", TEXT_M)
        pdf.drawString(x, top_y - 2, label)

        lines = wrapped_lines(value, w - 24, "Courier", 8.5)
        h = max(44, 20 + (len(lines[:3]) * 10) + 10)

        pdf.setLineWidth(1.5 if emphasize else 1)
        draw_soft_panel(x, top_y - 16, w, h, radius=13, fill=fill, stroke=stroke)
        pdf.setFillColor(COLOR_INK)
        pdf.setFont("Courier", 8.5)
        yy = top_y - 34
        for line in lines[:3]:
            pdf.drawString(x + 12, yy, line)
            yy -= 10
        return top_y - 16 - h

    def estimate_hash_block_height(value, w, label=None):
        lines = wrapped_lines(value, w - 24, "Courier", 8.5)
        h = max(44, 20 + (len(lines[:3]) * 10) + 10)
        if label:
            h += 16
        return h

    def draw_standard_section_title(title, y_pos):
        y_pos -= SECTION_TOP_SPACING
        pdf.setFillColor(COLOR_INK)
        pdf.setFont("Helvetica-Bold", TITLE_L)
        pdf.drawString(PDF_MARGIN_LEFT, y_pos, title)
        draw_hr(y_pos - 10)
        return y_pos - 22 - SECTION_BOTTOM_SPACING

    def draw_table_header_row(x, top_y, total_w, columns, row_h=24):
        pdf.setFillColor(COLOR_TABLE_HEADER)
        pdf.setStrokeColor(colors.HexColor("#E2E8F0"))
        pdf.roundRect(x, top_y - row_h, total_w, row_h, 6, fill=1, stroke=1)

        pdf.setFillColor(COLOR_MUTED)
        pdf.setFont("Helvetica-Bold", TEXT_S)

        for col in columns:
            label = col["label"]
            align = col.get("align", "left")
            col_left = x + col["x"]
            col_w = col["w"]
            pad = 8

            if align == "right":
                pdf.drawRightString(col_left + col_w - pad, top_y - 16, label)
            elif align == "center":
                pdf.drawCentredString(col_left + (col_w / 2), top_y - 16, label)
            else:
                pdf.drawString(col_left + pad, top_y - 16, label)

        return top_y - row_h

    def draw_table_row(x, top_y, total_w, columns, row_values, row_h=22, alt=False):
        fill = COLOR_TABLE_ALT if alt else colors.white
        pdf.setFillColor(fill)
        pdf.setStrokeColor(COLOR_TABLE_BORDER)
        pdf.rect(x, top_y - row_h, total_w, row_h, fill=1, stroke=1)

        for col in columns:
            key = col["key"]
            align = col.get("align", "left")
            text = str(row_values.get(key, "—"))
            font_name = col.get("font", "Helvetica")
            font_size = col.get("font_size", TEXT_S)

            col_left = x + col["x"]
            col_w = col["w"]
            left_pad = 8
            right_pad = 8

            pdf.setFont(font_name, font_size)
            pdf.setFillColor(COLOR_INK)

            if align == "right":
                pdf.drawRightString(col_left + col_w - right_pad, top_y - 15, text)
            elif align == "center":
                pdf.drawCentredString(col_left + (col_w / 2), top_y - 15, text)
            else:
                pdf.drawString(col_left + left_pad, top_y - 15, text)

        return top_y - row_h

    def draw_info_chip(x, top_y, w, h, rows, fill=colors.white, stroke=COLOR_LINE):
        draw_soft_panel(x, top_y, w, h, radius=12, fill=fill, stroke=stroke)
        yy = top_y - 24
        for label, value in rows:
            pdf.setFillColor(COLOR_MUTED)
            pdf.setFont("Helvetica", TEXT_M)
            pdf.drawString(x + 14, yy, f"{label}:")
            pdf.setFillColor(COLOR_INK)
            pdf.setFont("Helvetica-Bold", 11)
            pdf.drawString(x + 72, yy, value)
            yy -= 20

    def estimate_verification_banner_height(signature_text, trust_state_text, sub_text):
        chip_w = 190
        content_w = PDF_CONTENT_WIDTH - chip_w - 42
        title_lines = wrapped_lines(signature_text, content_w, "Helvetica-Bold", 24)[:2]
        trust_lines = wrapped_lines(trust_state_text, content_w, "Helvetica", TEXT_L)[:2]
        desc_lines = wrapped_lines(sub_text, content_w, "Helvetica", TEXT_M)
        content_height = (
            24
            + (len(title_lines) * 26)
            + 6
            + (len(trust_lines) * 14)
            + 8
            + (len(desc_lines) * 13)
        )
        return max(214, content_height + 84)

    def draw_equity_curve_preview_v2(x, top_y, w, h, curve_points):
        draw_soft_panel(x, top_y, w, h, radius=16, fill=colors.white, stroke=COLOR_BLUE_LINE)
        pdf.setFillColor(COLOR_INK)
        pdf.setFont("Helvetica-Bold", TITLE_L)
        pdf.drawString(x + 18, top_y - 18, "Equity Curve Preview")

        if not curve_points:
            pdf.setFillColor(COLOR_MUTED)
            pdf.setFont("Helvetica", TEXT_M)
            pdf.drawString(x + 18, top_y - 48, "No equity curve data available.")
            return

        chart_x = x + 26
        chart_y = top_y - h + 48
        chart_w = w - 50
        chart_h = h - 98

        values = [float(p.get("cumulative_pnl", 0) or 0) for p in curve_points]
        xs = list(range(1, len(values) + 1))
        min_val = min(values)
        max_val = max(values)

        if abs(max_val - min_val) < 1e-9:
            max_val += 1
            min_val -= 1

        pad = max((max_val - min_val) * 0.08, 1.0)
        axis_min = min(0.0, min_val - pad)
        axis_max = max_val + pad

        def scale_y(v):
            return chart_y + ((v - axis_min) / (axis_max - axis_min)) * chart_h

        def scale_x(i):
            if len(xs) == 1:
                return chart_x + (chart_w / 2)
            return chart_x + ((i - 1) / (len(xs) - 1)) * chart_w

        pdf.setStrokeColor(colors.HexColor("#F1F5F9"))
        pdf.setLineWidth(1)
        grid_steps = 5
        for step in range(grid_steps + 1):
            gy = chart_y + (chart_h / grid_steps) * step
            pdf.line(chart_x, gy, chart_x + chart_w, gy)

            val = axis_min + ((axis_max - axis_min) / grid_steps) * step
            pdf.setFillColor(COLOR_MUTED)
            pdf.setFont("Helvetica", 8)
            pdf.drawRightString(chart_x - 6, gy - 2, fmt_num(val, 1))

        pdf.setStrokeColor(COLOR_LINE)
        pdf.setLineWidth(1.2)
        pdf.line(chart_x, chart_y, chart_x, chart_y + chart_h)
        pdf.line(chart_x, chart_y, chart_x + chart_w, chart_y)

        marker_count = min(4, len(xs))
        if marker_count == 1:
            marker_indexes = [0]
        else:
            marker_indexes = sorted(set(round(i * (len(xs) - 1) / (marker_count - 1)) for i in range(marker_count)))

        for idx in marker_indexes:
            px = scale_x(xs[idx])
            pdf.setStrokeColor(COLOR_LINE_SOFT)
            pdf.line(px, chart_y, px, chart_y + chart_h)

            point = curve_points[idx]
            date_label = ""
            opened_at = point.get("opened_at")
            if opened_at:
                try:
                    date_label = opened_at.strftime("%Y-%m-%d")
                except Exception:
                    date_label = str(opened_at)[:10]
            pdf.setFillColor(COLOR_MUTED)
            pdf.setFont("Helvetica", 8)
            pdf.drawCentredString(px, chart_y - 12, str(xs[idx]))
            if date_label:
                pdf.drawCentredString(px, chart_y - 24, date_label)

        path = pdf.beginPath()
        path.moveTo(scale_x(xs[0]), chart_y)
        for i, v in zip(xs, values):
            path.lineTo(scale_x(i), scale_y(v))
        path.lineTo(scale_x(xs[-1]), chart_y)
        path.close()

        pdf.setFillColor(colors.HexColor("#EEF2F7"))
        pdf.setStrokeColor(colors.HexColor("#E2E8F0"))
        pdf.drawPath(path, fill=1, stroke=0)

        pdf.setStrokeColor(COLOR_NAVY)
        pdf.setLineWidth(2.4)
        for idx in range(len(xs) - 1):
            pdf.line(
                scale_x(xs[idx]), scale_y(values[idx]),
                scale_x(xs[idx + 1]), scale_y(values[idx + 1]),
            )

        if len(xs) <= 25:
            pdf.setFillColor(COLOR_NAVY)
            for i, v in zip(xs, values):
                pdf.circle(scale_x(i), scale_y(v), 2.2, fill=1, stroke=0)

        peak_idx = max(range(len(values)), key=lambda i: values[i])
        trough_idx = min(range(len(values)), key=lambda i: values[i])

        peak_x = scale_x(xs[peak_idx])
        peak_y = scale_y(values[peak_idx])
        trough_x = scale_x(xs[trough_idx])
        trough_y = scale_y(values[trough_idx])

        pdf.setFillColor(colors.HexColor("#16A34A"))
        pdf.circle(peak_x, peak_y, 4.5, fill=1, stroke=0)
        pdf.setFont("Helvetica-Bold", 8.5)
        pdf.drawString(min(peak_x + 10, chart_x + chart_w - 80), peak_y + 10, f"Peak {fmt_num(values[peak_idx], 2)}")

        pdf.setFillColor(colors.HexColor("#DC2626"))
        pdf.circle(trough_x, trough_y, 4.5, fill=1, stroke=0)
        trough_label_x = trough_x - 54 if trough_x > chart_x + 60 else trough_x + 8
        pdf.drawString(trough_label_x, trough_y + 10, f"Trough {fmt_num(values[trough_idx], 2)}")

        pdf.setFillColor(COLOR_MUTED)
        pdf.setFont("Helvetica", 8.5)
        net_change = values[-1] - values[0]
        pdf.drawRightString(chart_x + chart_w, chart_y + chart_h + 10, f"Net change {net_change:+.4f}")

    def normalize_dt(value):
        if value is None:
            return None
        if hasattr(value, "strftime"):
            return value
        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                return None
            try:
                return datetime.fromisoformat(raw.replace("Z", "+00:00"))
            except Exception:
                try:
                    return datetime.strptime(raw[:19], "%Y-%m-%d %H:%M:%S")
                except Exception:
                    return None
        return None

    def build_equity_point_rows(curve_points):
        rows = []
        prev_cumulative = None
        prev_opened_at = None

        for idx, point in enumerate(curve_points, start=1):
            cumulative_val = float(point.get("cumulative_pnl", 0) or 0)
            trade_pnl_val = float(point.get("net_pnl", 0) or 0)

            raw_opened_at = point.get("opened_at")
            opened_at_dt = normalize_dt(raw_opened_at)

            trade_id = point.get("trade_id", "—")
            symbol = point.get("symbol", "—")
            member_id = point.get("member_id", "—")

            step_change = trade_pnl_val
            if prev_cumulative is not None:
                step_change = cumulative_val - prev_cumulative

            gap_display = "start"
            if opened_at_dt and prev_opened_at:
                try:
                    gap_display = fmt_gap_days((opened_at_dt - prev_opened_at).total_seconds())
                except Exception:
                    gap_display = "start"

            rows.append(
                {
                    "sequence": idx,
                    "trade_id": trade_id,
                    "opened_at": fmt_dt(opened_at_dt or raw_opened_at),
                    "symbol": shorten_text(str(symbol), 10),
                    "member_id": str(member_id),
                    "trade_pnl": fmt_num(trade_pnl_val, 2),
                    "cumulative_pnl": fmt_num(cumulative_val, 2),
                    "step_change": fmt_num(step_change, 2),
                    "gap_from_prior": gap_display,
                }
            )

            prev_cumulative = cumulative_val
            prev_opened_at = opened_at_dt

        return rows

    def draw_section_title_block(title):
        nonlocal y
        ensure_space(54)
        y = draw_standard_section_title(title, y)

    def draw_dual_detail_panels(top_y, left_title, left_items, right_title, right_items):
        panel_gap = 16
        panel_w = (PDF_CONTENT_WIDTH - panel_gap) / 2
        panel_padding_x = 22
        panel_title_gap = 28
        col_gap = 22
        col_w = (panel_w - (panel_padding_x * 2) - col_gap) / 2

        left_x = PDF_MARGIN_LEFT
        right_x = PDF_MARGIN_LEFT + panel_w + panel_gap

        def calc_panel_height(items):
            row_y_cursor = 0
            for pair in items:
                left_h = estimate_kv_grid_cell_height(pair[0][1], max_width=col_w, max_lines=5)
                right_h = estimate_kv_grid_cell_height(pair[1][1], max_width=col_w, max_lines=5)
                row_h = max(left_h, right_h)
                row_y_cursor += row_h + FIELD_ROW_SPACING
            return max(220, 24 + panel_title_gap + row_y_cursor + 10)

        left_panel_h = calc_panel_height(left_items)
        right_panel_h = calc_panel_height(right_items)
        panel_h = max(left_panel_h, right_panel_h)

        ensure_space(panel_h + BLOCK_GAP)

        def render_panel(panel_x, panel_title, items):
            draw_soft_panel(panel_x, top_y, panel_w, panel_h, radius=16, fill=colors.white, stroke=COLOR_LINE)
            pdf.setFillColor(COLOR_INK)
            pdf.setFont("Helvetica-Bold", TITLE_M)
            pdf.drawString(panel_x + panel_padding_x, top_y - 26, panel_title)

            left_col_x = panel_x + panel_padding_x
            right_col_x = left_col_x + col_w + col_gap
            row_top_y = top_y - 58

            for pair in items:
                left_h = estimate_kv_grid_cell_height(pair[0][1], max_width=col_w, max_lines=5)
                right_h = estimate_kv_grid_cell_height(pair[1][1], max_width=col_w, max_lines=5)
                row_h = max(left_h, right_h)

                draw_kv_grid_cell(left_col_x, row_top_y, pair[0][0], pair[0][1], max_width=col_w, max_lines=5)
                draw_kv_grid_cell(right_col_x, row_top_y, pair[1][0], pair[1][1], max_width=col_w, max_lines=5)

                row_top_y -= row_h + FIELD_ROW_SPACING

        render_panel(left_x, left_title, left_items)
        render_panel(right_x, right_title, right_items)
        return top_y - panel_h - BLOCK_GAP

    def draw_paginated_table_section(
        title,
        columns,
        rows,
        empty_text,
        row_h=22,
        header_row_h=24,
        totals_renderer=None,
        start_on_new_page=False,
        top_gap_before_title=0,
        preferred_break_height=None,
    ):
        nonlocal y

        section_started = False
        row_top = y

        if top_gap_before_title:
            y -= top_gap_before_title

        def start_table_page(table_title, continued=False):
            nonlocal y, section_started, row_top
            if section_started:
                new_page()
            elif start_on_new_page:
                new_page()
            elif preferred_break_height is not None and should_start_new_page(preferred_break_height, 40):
                new_page()

            ensure_space(96)
            rendered_title = table_title if not continued else f"{table_title} (continued)"
            y = draw_standard_section_title(rendered_title, y)
            row_top = draw_table_header_row(PDF_MARGIN_LEFT, y, TABLE_TOTAL_W, columns, row_h=header_row_h)
            section_started = True

        if not rows:
            start_table_page(title)
            pdf.setFillColor(COLOR_MUTED)
            pdf.setFont("Helvetica", TEXT_M)
            pdf.drawString(PDF_MARGIN_LEFT + 4, row_top - 18, empty_text)
            y = row_top - 38
            return

        start_table_page(title)

        current_top = row_top
        for idx, row_values in enumerate(rows):
            if current_top - row_h < PAGE_BOTTOM_SAFE + 24:
                start_table_page(title, continued=True)
                current_top = row_top

            current_top = draw_table_row(
                PDF_MARGIN_LEFT,
                current_top,
                TABLE_TOTAL_W,
                columns,
                row_values,
                row_h=row_h,
                alt=(idx % 2 == 1),
            )

        y = current_top - BLOCK_GAP

        if totals_renderer:
            totals_h = 18
            ensure_space(totals_h + 10)
            totals_renderer(y)
            y -= 12

    # =========================
    # PAGE 1 — EXECUTIVE SUMMARY
    # =========================

    pdf.setFillColor(COLOR_INK)
    pdf.setFont("Helvetica-Bold", TITLE_XL)
    title_text = "Verified Trading Claim"
    if schema.status == "draft":
        title_text = "Draft Trading Claim"
    elif schema.status == "locked":
        title_text = "Locked Verified Trading Claim"
    pdf.drawString(PDF_MARGIN_LEFT, y, title_text)
    y -= 18

    pdf.setFillColor(COLOR_MUTED)
    pdf.setFont("Helvetica", TEXT_L)
    pdf.drawString(PDF_MARGIN_LEFT, y, "Trading Truth Layer")
    y -= BLOCK_GAP

    pdf.setFillColor(COLOR_MUTED)
    pdf.setFont("Helvetica", TEXT_M)
    pdf.drawString(PDF_MARGIN_LEFT, y, f"Public View Path: {public_view_path}")
    y -= 14
    pdf.drawString(PDF_MARGIN_LEFT, y, f"Verify Link Path: {verify_link_short}")
    y -= 14
    pdf.drawString(PDF_MARGIN_LEFT, y, f"Workspace ID: {schema.workspace_id}")
    y -= 14
    pdf.drawString(PDF_MARGIN_LEFT, y, f"Exported At: {exported_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    y -= BLOCK_GAP + 6

    pdf.setFillColor(COLOR_TEXT)
    pdf.setFont("Helvetica", TEXT_L)
    y = draw_pdf_wrapped_text(
        pdf,
        "Lifecycle-governed trading claim report with public-proof framing, canonical fingerprints, integrity validation context, scope explainability, and evidence-backed performance summary.",
        PDF_MARGIN_LEFT,
        y,
        PDF_CONTENT_WIDTH,
        14,
        "Helvetica",
        TEXT_L,
    )
    y -= SECTION_GAP

    banner_fill = COLOR_GREEN_BG if integrity_status == "valid" else COLOR_RED_BG
    banner_stroke = COLOR_GREEN_LINE if integrity_status == "valid" else COLOR_RED_LINE
    banner_text = COLOR_GREEN_TEXT if integrity_status == "valid" else COLOR_RED_TEXT

    if schema.status == "locked" and integrity_status == "valid":
        signature_text = "Verified • Locked • Integrity Valid"
        sub_text = (
            "This claim is lifecycle-governed and publicly verifiable. The locked trade-set fingerprint matches "
            "the canonical record, and integrity can be independently checked through the verify route."
        )
        trust_state_text = "Trust State: High-trust finalized record"
        chip_rows = [("status", "locked"), ("integrity", "valid"), ("trust", "high")]
    elif schema.status == "published":
        signature_text = "Published Verification Surface"
        sub_text = (
            "This claim is publicly exposed and verification-ready. Its canonical identity, scope, and lifecycle "
            "posture are available for external review through Trading Truth Layer."
        )
        trust_state_text = "Trust State: Public verification surface"
        chip_rows = [("status", "published"), ("integrity", integrity_status), ("trust", "elevated")]
    elif schema.status == "locked" and integrity_status != "valid":
        signature_text = "Locked • Integrity Compromised"
        sub_text = (
            "This record is locked, but the current in-scope trade-set fingerprint no longer matches the stored "
            "locked fingerprint."
        )
        trust_state_text = "Trust State: Integrity compromised"
        chip_rows = [("status", "locked"), ("integrity", "compromised"), ("trust", "alert")]
    else:
        signature_text = f"{schema.status.title()} Claim"
        sub_text = (
            "This report summarizes current lifecycle state, scoped claim evidence, and canonical record identity for review."
        )
        if schema.status == "draft":
            trust_state_text = "Trust State: Draft (not yet published or locked)"
            chip_rows = [("status", "draft"), ("integrity", integrity_status), ("trust", "pre-public")]
        elif schema.status == "locked":
            trust_state_text = "Trust State: Locked canonical record"
            chip_rows = [("status", "locked"), ("integrity", integrity_status), ("trust", "controlled")]
        else:
            trust_state_text = f"Trust State: {schema.status.title()}"
            chip_rows = [("status", schema.status), ("integrity", integrity_status), ("trust", "contextual")]

    banner_height = estimate_verification_banner_height(signature_text, trust_state_text, sub_text)
    ensure_space(banner_height + 180)

    draw_soft_panel(PDF_MARGIN_LEFT, y, PDF_CONTENT_WIDTH, banner_height, radius=18, fill=banner_fill, stroke=banner_stroke)

    pdf.setFillColor(banner_text)
    pdf.roundRect(PDF_MARGIN_LEFT + 10, y - banner_height + 10, 8, banner_height - 20, 4, fill=1, stroke=0)

    pdf.setFillColor(banner_text)
    pdf.setFont("Helvetica", TEXT_L)
    pdf.drawString(PDF_MARGIN_LEFT + 24, y - 22, "Verification Signature")

    chip_w = 190
    chip_h = 102
    chip_x = PDF_PAGE_WIDTH - PDF_MARGIN_RIGHT - chip_w
    chip_top_y = y - 6

    content_x = PDF_MARGIN_LEFT + 24
    content_w = chip_x - content_x - 26
    content_y = y - 48

    pdf.setFont("Helvetica-Bold", 24)
    pdf.setFillColor(banner_text)
    title_lines = wrapped_lines(signature_text, content_w, "Helvetica-Bold", 24)[:2]
    for line in title_lines:
        pdf.drawString(content_x, content_y, line)
        content_y -= 26

    pdf.setFont("Helvetica", TEXT_L)
    pdf.drawString(content_x, content_y, trust_state_text)
    content_y -= 22

    content_y = draw_pdf_wrapped_text(
        pdf,
        sub_text,
        content_x,
        content_y,
        content_w,
        13,
        "Helvetica",
        TEXT_M,
    )

    draw_info_chip(
        chip_x,
        chip_top_y,
        chip_w,
        chip_h,
        chip_rows,
        fill=colors.white,
        stroke=COLOR_LINE,
    )

    hash_box_w = (PDF_CONTENT_WIDTH - CARD_GAP) / 2
    hash_row_top = y - banner_height + 60
    draw_label_value_box_v2(
        PDF_MARGIN_LEFT,
        hash_row_top,
        hash_box_w,
        56,
        "Claim Hash Fingerprint",
        short_hash(claim_hash, 18, 10),
        value_font="Courier",
        value_size=8.5,
    )
    draw_label_value_box_v2(
        PDF_MARGIN_LEFT + hash_box_w + CARD_GAP,
        hash_row_top,
        hash_box_w,
        56,
        "Trade Set Hash Fingerprint",
        short_hash(trade_set_hash, 18, 10),
        value_font="Courier",
        value_size=8.5,
    )

    y -= banner_height + 18

    claim_name_lines = wrapped_lines(schema.name or "Untitled Claim", PDF_CONTENT_WIDTH, "Helvetica-Bold", 22)[:2]
    latest_event = audit_events[-1] if audit_events else None
    latest_event_text = f"{latest_event.event_type} @ {fmt_dt(latest_event.created_at)}" if latest_event else "No audit events"
    latest_event_h = estimate_highlight_note_height(latest_event_text, PDF_CONTENT_WIDTH, label="Latest Audit Event", min_height=44)

    identity_needed_h = (
        34
        + (len(claim_name_lines) * 24)
        + MINI_GAP
        + 74
        + BLOCK_GAP
        + 72
        + BLOCK_GAP
        + latest_event_h
        + 8
    )
    ensure_space(identity_needed_h)

    pdf.setFillColor(COLOR_INK)
    pdf.setFont("Helvetica-Bold", TITLE_L)
    pdf.drawString(PDF_MARGIN_LEFT, y, "Claim Identity")
    draw_hr(y - 10)
    y -= 34

    pdf.setFillColor(COLOR_INK)
    pdf.setFont("Helvetica-Bold", 22)
    for line in claim_name_lines:
        pdf.drawString(PDF_MARGIN_LEFT, y, line)
        y -= 24
    y -= MINI_GAP

    card_w = (PDF_CONTENT_WIDTH - (CARD_GAP * 3)) / 4
    card_h = 74

    draw_metric_card_v2(PDF_MARGIN_LEFT, y, card_w, card_h, "Trade Count", str(metrics["trade_count"]), "In-scope rows")
    draw_metric_card_v2(PDF_MARGIN_LEFT + card_w + CARD_GAP, y, card_w, card_h, "Net PnL", fmt_num(metrics["net_pnl"], 2), "Aggregate result")
    draw_metric_card_v2(PDF_MARGIN_LEFT + (card_w + CARD_GAP) * 2, y, card_w, card_h, "Profit Factor", fmt_num(metrics["profit_factor"], 4), "Gross profit / loss")
    draw_metric_card_v2(PDF_MARGIN_LEFT + (card_w + CARD_GAP) * 3, y, card_w, card_h, "Win Rate", fmt_pct_ratio(metrics["win_rate"], 2), "Winning trades %")
    y -= card_h + COMPACT_ROW_GAP

    draw_metric_card_v2(PDF_MARGIN_LEFT, y, card_w, 72, "Workspace Trades", str(scope["workspace_trade_count"]), "All workspace trade rows")
    draw_metric_card_v2(PDF_MARGIN_LEFT + card_w + CARD_GAP, y, card_w, 72, "Included Trades", str(len(scope["included"])), "Rows used in claim")
    draw_metric_card_v2(PDF_MARGIN_LEFT + (card_w + CARD_GAP) * 2, y, card_w, 72, "Excluded Trades", str(len(scope["excluded"])), "Out-of-scope rows")
    draw_metric_card_v2(PDF_MARGIN_LEFT + (card_w + CARD_GAP) * 3, y, card_w, 72, "Audit Events", str(len(audit_events)), "Lifecycle trail count")
    y -= 72 + BLOCK_GAP

    y = draw_highlight_note(PDF_MARGIN_LEFT, y, PDF_CONTENT_WIDTH, latest_event_text, label="Latest Audit Event", min_height=44)
    y -= SECTION_GAP

    # =========================
    # PERFORMANCE DIAGNOSTICS
    # =========================

    diag_needed_h = 72 + COMPACT_ROW_GAP + 60 + BLOCK_GAP + 50 + BLOCK_GAP + 24 + BLOCK_GAP + 244
    start_section_if_needed(diag_needed_h + 54, 90)
    draw_section_title_block("Performance Diagnostics")

    diag_w = (PDF_CONTENT_WIDTH - (CARD_GAP * 3)) / 4
    draw_metric_card_v2(PDF_MARGIN_LEFT, y, diag_w, 72, "Best Trade", fmt_num(metrics["best_trade"], 2), "Highest PnL")
    draw_metric_card_v2(PDF_MARGIN_LEFT + diag_w + CARD_GAP, y, diag_w, 72, "Worst Trade", fmt_num(metrics["worst_trade"], 2), "Lowest PnL")
    draw_metric_card_v2(PDF_MARGIN_LEFT + (diag_w + CARD_GAP) * 2, y, diag_w, 72, "Max Drawdown", fmt_num(drawdown_stats["max_drawdown"], 2), "Peak-to-trough")
    draw_metric_card_v2(PDF_MARGIN_LEFT + (diag_w + CARD_GAP) * 3, y, diag_w, 72, "Ending Equity", fmt_num(equity_curve["ending_equity"], 2), "Final cumulative")
    y -= 72 + COMPACT_ROW_GAP

    curve_points = equity_curve["curve"]
    first_point = curve_points[0] if curve_points else None
    last_point = curve_points[-1] if curve_points else None
    peak_point = drawdown_stats.get("peak_point")
    trough_point = drawdown_stats.get("trough_point")

    note_w = (PDF_CONTENT_WIDTH - (CARD_GAP * 3)) / 4
    draw_label_value_box_v2(
        PDF_MARGIN_LEFT,
        y,
        note_w,
        60,
        "First Point",
        f"Trade #{first_point['trade_id']} · {first_point['symbol']} · {fmt_dt(first_point['opened_at'])}" if first_point else "—",
        value_font="Helvetica",
        value_size=8,
    )
    draw_label_value_box_v2(
        PDF_MARGIN_LEFT + note_w + CARD_GAP,
        y,
        note_w,
        60,
        "Last Point",
        f"Trade #{last_point['trade_id']} · {last_point['symbol']} · {fmt_dt(last_point['opened_at'])}" if last_point else "—",
        value_font="Helvetica",
        value_size=8,
    )
    draw_label_value_box_v2(
        PDF_MARGIN_LEFT + (note_w + CARD_GAP) * 2,
        y,
        note_w,
        60,
        "Peak Point",
        f"Trade #{peak_point['trade_id']} · {peak_point['symbol']} · {fmt_dt(peak_point['opened_at'])}" if peak_point else "—",
        value_font="Helvetica",
        value_size=8,
    )
    draw_label_value_box_v2(
        PDF_MARGIN_LEFT + (note_w + CARD_GAP) * 3,
        y,
        note_w,
        60,
        "Trough Point",
        f"Trade #{trough_point['trade_id']} · {trough_point['symbol']} · {fmt_dt(trough_point['opened_at'])}" if trough_point else "—",
        value_font="Helvetica",
        value_size=8,
    )
    y -= 60 + BLOCK_GAP

    y = draw_highlight_note(
        PDF_MARGIN_LEFT,
        y,
        PDF_CONTENT_WIDTH,
        "This curve mirrors the public proof surface by showing cumulative path structure, consistent peak and trough annotations, and the deepest drawdown interval when one exists. Max drawdown remains the primary risk statistic, while peak and trough identify the full performance range.",
        min_height=46,
    )
    y -= BLOCK_GAP - 4

    pdf.setFont("Helvetica", TEXT_S)
    pdf.setFillColor(COLOR_MUTED)
    pdf.drawString(PDF_MARGIN_LEFT, y, "X-axis: Trade sequence (chronological)")
    y -= 12
    pdf.drawString(PDF_MARGIN_LEFT, y, "Y-axis: Cumulative PnL")
    y -= BLOCK_GAP

    ensure_space(244 + 12)
    draw_equity_curve_preview_v2(PDF_MARGIN_LEFT, y, PDF_CONTENT_WIDTH, 244, curve_points)
    y -= 244 + BLOCK_GAP

    point_table_intro = (
        "Equity Point Analytics provides a printable companion to the curve for dense trade paths. Each row captures the "
        "sequence point, trade reference, timestamp, trade PnL, cumulative PnL, step change, and gap from the prior point."
    )
    intro_h = estimate_highlight_note_height(point_table_intro, PDF_CONTENT_WIDTH, label="Equity Point Analytics", min_height=48)
    ensure_space(intro_h + 100)
    y = draw_highlight_note(
        PDF_MARGIN_LEFT,
        y,
        PDF_CONTENT_WIDTH,
        point_table_intro,
        label="Equity Point Analytics",
        min_height=48,
    )
    y -= BLOCK_GAP

    equity_point_columns = [
        {"label": "Seq", "key": "sequence", "x": 0, "w": 26, "align": "left"},
        {"label": "Trade", "key": "trade_id", "x": 26, "w": 40, "align": "left"},
        {"label": "Opened", "key": "opened_at", "x": 66, "w": 110, "align": "left"},
        {"label": "Symbol", "key": "symbol", "x": 176, "w": 48, "align": "left"},
        {"label": "Member", "key": "member_id", "x": 224, "w": 44, "align": "left"},
        {"label": "Trade PnL", "key": "trade_pnl", "x": 268, "w": 80, "align": "right", "font_size": 8},
        {"label": "Cumulative", "key": "cumulative_pnl", "x": 348, "w": 82, "align": "right", "font_size": 8},
        {"label": "Step", "key": "step_change", "x": 430, "w": 46, "align": "right", "font_size": 8},
        {"label": "Gap", "key": "gap_from_prior", "x": 476, "w": 40, "align": "right", "font_size": 8},
    ]
    equity_point_rows = build_equity_point_rows(curve_points)

    units_note = "Units — Trade PnL: account currency • Cumulative: account currency • Step: account currency • Gap: days"
    units_note_h = estimate_highlight_note_height(units_note, PDF_CONTENT_WIDTH, label="Equity Point Units", min_height=40)
    ensure_space(units_note_h + 80)
    y = draw_highlight_note(
        PDF_MARGIN_LEFT,
        y,
        PDF_CONTENT_WIDTH,
        units_note,
        label="Equity Point Units",
        min_height=40,
    )
    y -= 8


    draw_paginated_table_section(
        "Equity Point Snapshot",
        equity_point_columns,
        equity_point_rows,
        "No equity point analytics available.",
        row_h=22,
        header_row_h=24,
        top_gap_before_title=12,
        preferred_break_height=220,
    )

    y -= SECTION_GAP

    # =========================
    # VERIFICATION CONTEXT
    # =========================

    verification_context_min_h = 360
    start_section_if_needed(verification_context_min_h, 70)
    draw_section_title_block("Verification Context")

    left_items = [
        (("Period Start", schema.period_start or "—"), ("Period End", schema.period_end or "—")),
        (("Included Members", included_members), ("Included Symbols", included_symbols)),
        (("Excluded Trade IDs", excluded_trade_ids), ("Visibility", schema.visibility or "—")),
    ]

    right_items = [
        (("Status", schema.status or "—"), ("Integrity", integrity_status)),
        (("Verified At", fmt_dt(schema.verified_at)), ("Published At", fmt_dt(schema.published_at))),
        (("Locked At", fmt_dt(schema.locked_at)), ("Version Number", str(schema.version_number or "—"))),
        (("Root Claim ID", str(schema.root_claim_id or "—")), ("Parent Claim ID", str(schema.parent_claim_id or "—"))),
    ]

    y = draw_dual_detail_panels(
        y,
        "Verification Scope",
        left_items,
        "Lifecycle & Lineage",
        right_items,
    )

    versioning_text = (
        "This claim belongs to a versioned lineage. Each version represents a scoped evaluation. "
        "Root and parent identifiers ensure full traceability of claim evolution."
    )
    methodology_text = schema.methodology_notes or "No methodology notes supplied."
    limitations_text = (
        "This report verifies the scoped trade set represented by this claim schema. It does not independently attest "
        "to broker connectivity, external account ownership, or performance outside the included evidence boundary. "
        "Public trust should be interpreted together with lifecycle status, claim hash, and locked trade-set integrity where applicable."
    )

    excluded_breakdown = scope["excluded_breakdown"]
    exclusion_summary_text = (
        f"Excluded breakdown — Outside period: {excluded_breakdown.get(EXCLUSION_REASON_OUTSIDE_PERIOD, 0)}, "
        f"Member filter: {excluded_breakdown.get(EXCLUSION_REASON_MEMBER_FILTER, 0)}, "
        f"Symbol filter: {excluded_breakdown.get(EXCLUSION_REASON_SYMBOL_FILTER, 0)}, "
        f"Manual exclusion: {excluded_breakdown.get(EXCLUSION_REASON_MANUAL_EXCLUSION, 0)}."
    )

    notes = [
        ("Versioning Context", versioning_text, 44),
        ("Methodology Notes", methodology_text, 56),
        ("Interpretation & Limitations", limitations_text, 56),
        ("Scope Exclusion Summary", exclusion_summary_text, 44),
    ]

    for label, text, min_h in notes:
        note_h = estimate_highlight_note_height(text, PDF_CONTENT_WIDTH, label=label, min_height=min_h)
        ensure_space(note_h + 10)
        y = draw_highlight_note(
            PDF_MARGIN_LEFT,
            y,
            PDF_CONTENT_WIDTH,
            text,
            label=label,
            min_height=min_h,
        )
        y -= BLOCK_GAP - 4

    # =========================
    # EVIDENCE TABLES
    # =========================

    leaderboard_columns = [
        {"label": "Rank", "key": "rank", "x": 0, "w": 56, "align": "left"},
        {"label": "Member", "key": "member", "x": 56, "w": 180, "align": "left"},
        {"label": "Net PnL", "key": "net_pnl", "x": 236, "w": 96, "align": "right"},
        {"label": "Win Rate", "key": "win_rate", "x": 332, "w": 96, "align": "right"},
        {"label": "Profit Factor", "key": "profit_factor", "x": 428, "w": 88, "align": "right"},
    ]

    leaderboard_rows = []
    for row in leaderboard[:8]:
        leaderboard_rows.append(
            {
                "rank": row["rank"],
                "member": shorten_text(str(row["member"]), 22),
                "net_pnl": fmt_num(row["net_pnl"], 2),
                "win_rate": fmt_pct_ratio(float(row["win_rate"]), 2),
                "profit_factor": fmt_num(row["profit_factor"], 4),
            }
        )

    draw_paginated_table_section(
        "Leaderboard Snapshot",
        leaderboard_columns,
        leaderboard_rows,
        "No leaderboard data available.",
        row_h=24,
        header_row_h=24,
        top_gap_before_title=10,
        preferred_break_height=220,
    )

    evidence_columns = [
        {"label": "#", "key": "index", "x": 0, "w": 26, "align": "left"},
        {"label": "Trade ID", "key": "trade_id", "x": 26, "w": 58, "align": "left"},
        {"label": "Opened", "key": "opened_at", "x": 84, "w": 134, "align": "left"},
        {"label": "Symbol", "key": "symbol", "x": 218, "w": 64, "align": "left"},
        {"label": "Side", "key": "side", "x": 282, "w": 52, "align": "left"},
        {"label": "Member", "key": "member_id", "x": 334, "w": 62, "align": "left"},
        {"label": "PnL", "key": "net_pnl", "x": 396, "w": 54, "align": "right"},
        {"label": "Cumulative", "key": "cumulative_pnl", "x": 450, "w": 66, "align": "right"},
    ]

    evidence_table_rows = []
    for row in evidence_rows:
        evidence_table_rows.append(
            {
                "index": row["index"],
                "trade_id": row["trade_id"],
                "opened_at": shorten_text(fmt_dt(row["opened_at"]), 20),
                "symbol": shorten_text(str(row["symbol"]), 10),
                "side": shorten_text(str(row["side"]), 6),
                "member_id": str(row["member_id"]),
                "net_pnl": fmt_num(row["net_pnl"], 2),
                "cumulative_pnl": fmt_num(row["cumulative_pnl"], 2),
            }
        )

    def render_evidence_totals(totals_y):
        total_pnl = sum((float(r.get("net_pnl", 0) or 0) for r in evidence_rows))
        pdf.setFillColor(COLOR_INK)
        pdf.setFont("Helvetica-Bold", TEXT_M)
        pdf.drawString(PDF_MARGIN_LEFT, totals_y, f"Total Trades: {len(evidence_rows)}")
        pdf.drawRightString(PDF_PAGE_WIDTH - PDF_MARGIN_RIGHT, totals_y, f"Total Net PnL: {fmt_num(total_pnl, 2)}")

    draw_paginated_table_section(
        "Trade Evidence Snapshot",
        evidence_columns,
        evidence_table_rows,
        "No trade evidence rows available.",
        row_h=22,
        header_row_h=24,
        totals_renderer=render_evidence_totals,
        top_gap_before_title=20,
        preferred_break_height=260,
    )

    # =========================
    # FINAL PAGE — FINGERPRINTS & VALIDATION
    # =========================

    fingerprints_min_h = 360
    start_section_if_needed(fingerprints_min_h, 70)
    draw_section_title_block("Canonical Fingerprints & Verification Paths")

    pdf.setFillColor(COLOR_MUTED)
    pdf.setFont("Helvetica", TEXT_M)
    pdf.drawString(PDF_MARGIN_LEFT, y, "Canonical Verification Anchors")
    y -= MINI_GAP + 2

    block_estimate = (
        estimate_hash_block_height(claim_hash, PDF_CONTENT_WIDTH, label="Claim Hash") + MINI_GAP +
        estimate_hash_block_height(trade_set_hash, PDF_CONTENT_WIDTH, label="Trade Set Hash") + MINI_GAP +
        estimate_hash_block_height(public_view_path, PDF_CONTENT_WIDTH, label="Public View Path") + MINI_GAP +
        estimate_hash_block_height(verify_link_path, PDF_CONTENT_WIDTH, label="Verify Link Path") + BLOCK_GAP +
        max(
            estimate_highlight_note_height(
                "The claim hash and trade-set hash uniquely identify this report and its dataset. Any modification will produce a different hash, ensuring tamper-evident verification.",
                PDF_CONTENT_WIDTH - 120,
                label="Data Integrity Statement",
                min_height=60,
            ),
            100,
        ) +
        BLOCK_GAP +
        56
    )
    ensure_space(block_estimate)

    y = draw_hash_block_v2(PDF_MARGIN_LEFT, y, PDF_CONTENT_WIDTH, "Claim Hash", claim_hash, emphasize=False) - MINI_GAP
    y = draw_hash_block_v2(PDF_MARGIN_LEFT, y, PDF_CONTENT_WIDTH, "Trade Set Hash", trade_set_hash, emphasize=False) - MINI_GAP
    y = draw_hash_block_v2(PDF_MARGIN_LEFT, y, PDF_CONTENT_WIDTH, "Public View Path", public_view_path, emphasize=False) - MINI_GAP
    y = draw_hash_block_v2(PDF_MARGIN_LEFT, y, PDF_CONTENT_WIDTH, "Verify Link Path", verify_link_path, emphasize=True) - BLOCK_GAP

    note_w = PDF_CONTENT_WIDTH - 120
    note_top_y = y
    y = draw_highlight_note(
        PDF_MARGIN_LEFT,
        y,
        note_w,
        "The claim hash and trade-set hash uniquely identify this report and its dataset. Any modification will produce a different hash, ensuring tamper-evident verification.",
        label="Data Integrity Statement",
        min_height=60,
    )

    try:
        qr_code = qr.QrCodeWidget(verify_link_path)
        bounds = qr_code.getBounds()
        qr_width = bounds[2] - bounds[0]
        qr_height = bounds[3] - bounds[1]
        qr_size = 84
        d = Drawing(
            qr_size,
            qr_size,
            transform=[qr_size / qr_width, 0, 0, qr_size / qr_height, 0, 0],
        )
        d.add(qr_code)
        renderPDF.draw(d, pdf, PDF_PAGE_WIDTH - PDF_MARGIN_RIGHT - 92, note_top_y - 88)
    except Exception:
        pass

    y -= BLOCK_GAP + 4
    ensure_space(56)
    draw_soft_panel(PDF_MARGIN_LEFT, y, PDF_CONTENT_WIDTH, 56, radius=14, fill=COLOR_FILL_ALT, stroke=COLOR_LINE)
    pdf.setFillColor(COLOR_TEXT)
    pdf.setFont("Helvetica", TEXT_M)
    footer_note = (
        "Generated from Trading Truth Layer — a verification infrastructure for trading claims. "
        "This record can be independently validated via its verify link, public view path, claim hash, and trade-set hash."
    )
    footer_lines = wrapped_lines(footer_note, PDF_CONTENT_WIDTH - 28, "Helvetica", TEXT_M)[:3]
    line_y = y - 18
    for line in footer_lines:
        pdf.drawString(PDF_MARGIN_LEFT + 14, line_y, line)
        line_y -= 12

    pdf.save()
    buffer.seek(0)
    return buffer, filename



def draw_dynamic_note_box(
    pdf: canvas.Canvas,
    x: float,
    y_top: float,
    width: float,
    text: str,
    page_number: int,
    document_title: str,
    claim_hash: str,
    label: str | None = None,
):
    note_text = text or "No methodology notes supplied."

    lines = split_wrapped_lines(note_text, width - 24, "Helvetica", 9)
    line_count = max(1, len(lines))
    text_height = line_count * 11
    box_height = max(46, text_height + 24)

    required_space = box_height + (20 if label else 0)
    y_top, page_number = pdf_require_space(
        pdf,
        y_top,
        required_space,
        page_number,
        document_title,
        claim_hash,
    )

    if label:
        pdf.setFillColor(colors.HexColor("#64748B"))
        pdf.setFont("Helvetica", 9)
        pdf.drawString(x, y_top, label)
        y_top -= 8

    pdf_round_box(
        pdf,
        x,
        y_top,
        width,
        box_height,
        colors.HexColor("#F8FAFC"),
        colors.HexColor("#E2E8F0"),
        radius=10,
    )

    pdf.setFillColor(colors.HexColor("#475569"))
    pdf.setFont("Helvetica", 9)

    current_y = y_top - 18
    for line in lines:
        pdf.drawString(x + 12, current_y, line)
        current_y -= 11

    pdf.setFillColor(colors.black)

    return y_top - box_height - 14, page_number



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

    if not workspace_limits_disabled():
        enforce_claim_creation_allowed(payload.workspace_id, db)

    visibility = normalize_visibility(payload.visibility)

    workspace = get_workspace_or_404(payload.workspace_id, db)
    effective_plan_code = resolve_effective_workspace_plan_code(workspace)

    if effective_plan_code == "sandbox" and visibility == "public":
        visibility = "unlisted"

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
    if not workspace_limits_disabled():
        enforce_claim_creation_allowed(source.workspace_id, db)

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

    workspace = get_workspace_or_404(schema.workspace_id, db)
    effective_plan_code = resolve_effective_workspace_plan_code(workspace)

    next_visibility = normalize_visibility(payload.visibility)
    if effective_plan_code == "sandbox" and next_visibility == "public":
        next_visibility = "unlisted"

    schema.visibility = next_visibility

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
    if not workspace_limits_disabled():
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
    if not workspace_limits_disabled():
        enforce_claim_creation_allowed(schema.workspace_id, db)

    if schema.status != "draft":
        raise HTTPException(status_code=400, detail="Only draft claims can be verified")

    old_state = {
        "status": schema.status,
        "verified_at": schema.verified_at.isoformat() if schema.verified_at else None,
        "claim_hash": compute_claim_hash(schema),
    }

    schema.status = "verified"
    schema.verified_at = datetime.utcnow()
    schema.claim_hash = compute_claim_hash(schema)
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
    if not workspace_limits_disabled():
        enforce_claim_creation_allowed(schema.workspace_id, db)
    workspace = get_workspace_or_404(schema.workspace_id, db)
    effective_plan_code = resolve_effective_workspace_plan_code(workspace)

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
    schema.claim_hash = compute_claim_hash(schema)

    # Normalize visibility
    if schema.visibility == "private":
        schema.visibility = "unlisted"

    workspace = get_workspace_or_404(schema.workspace_id, db)
    effective_plan_code = resolve_effective_workspace_plan_code(workspace)

    # Sandbox cannot publish to fully public visibility.
    # It may still use unlisted verification surfaces for controlled evaluation.
    if effective_plan_code == "sandbox" and not sandbox_public_visibility_allowed(schema.visibility):
        schema.visibility = "unlisted"

    # Public/unlisted exposure should be governed by the effective entitlement tier,
    # not merely the configured commercial target.
    if schema.visibility in {"public", "unlisted"}:
        allowed = can_create_public_claim(schema.workspace_id, effective_plan_code, db)
        if not allowed:
            raise HTTPException(
                status_code=403,
                detail="Public claim limit reached for the current effective workspace tier."
            )

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
            "effective_plan_code": effective_plan_code,
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
    if not workspace_limits_disabled():
        enforce_claim_creation_allowed(schema.workspace_id, db)

    if schema.status == "locked":
        return serialize_schema(schema)

    if schema.status != "published":
        raise HTTPException(status_code=400, detail="Only published claims can be locked")

    filtered_trades = resolve_schema_trades(schema, db)

    # 🔒 Freeze the exact trade IDs used at lock time
    locked_trade_ids = [t.id for t in filtered_trades]

    old_state = {
        "status": schema.status,
        "locked_at": schema.locked_at.isoformat() if schema.locked_at else None,
        "locked_trade_set_hash": schema.locked_trade_set_hash,
        "claim_hash": compute_claim_hash(schema),
    }

    schema.locked_trade_set_hash = compute_trade_set_hash(filtered_trades)
    schema.locked_trade_ids_json = json.dumps(locked_trade_ids)  # ✅ NEW
    schema.status = "locked"
    schema.locked_at = datetime.utcnow()
    schema.claim_hash = compute_claim_hash(schema)

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
            "locked_trade_ids_count": len(locked_trade_ids),  # optional but useful
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
        "issuer": build_issuer_payload(schema, db),
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

    # ✅ NEW: use snapshot instead of live scope
    locked_ids = set(json.loads(schema.locked_trade_ids_json or "[]"))

    trades = (
        db.query(Trade)
        .filter(
            Trade.workspace_id == schema.workspace_id,
            Trade.id.in_(locked_ids) if locked_ids else False
        )
        .all()
    )

    recomputed_hash = compute_trade_set_hash(trades)
    integrity_ok = recomputed_hash == schema.locked_trade_set_hash

    return {
        "claim_schema_id": schema.id,
        "claim_hash": compute_claim_hash(schema),
        "name": schema.name,
        "status": schema.status,
        "integrity_status": "valid" if integrity_ok else "compromised",
        "trade_count": len(trades),
        "stored_hash": schema.locked_trade_set_hash,
        "recomputed_hash": recomputed_hash,
        "hash_match": integrity_ok,
        "verified_at": datetime.utcnow().isoformat(),
    }

@router.get("/profiles/{workspace_id}")
def get_public_profile(
    workspace_id: int,
    db: Session = Depends(get_db),
):
    workspace = get_workspace_or_404(workspace_id, db)

    return build_public_profile_response(workspace.id, db)

@router.get("/workspaces/{workspace_id}/public-claims")
def get_workspace_public_claims(workspace_id: int, db: Session = Depends(get_db)):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    rows = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id == workspace_id,
            ClaimSchema.visibility.in_(["public", "unlisted"]),
            ClaimSchema.status.in_(["published", "locked"]),
        )
        .order_by(ClaimSchema.id.desc())
        .all()
    )

    return [build_claim_list_row(schema, db) for schema in rows]    


@router.get("/workspaces/{workspace_id}/public-claims")
def get_workspace_public_claims(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workspace = get_workspace_or_404(workspace_id, db)

    membership = require_workspace_member(workspace_id, current_user, db)

    claims = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id == workspace_id,
            ClaimSchema.visibility.in_(["public", "unlisted"]),
        )
        .all()
    )

    result = [
        build_claim_list_row(schema, db)
        for schema in claims
        if is_claim_publicly_accessible(schema)
    ]

    return result    

@router.get("/workspaces/{workspace_id}/public-claims")
def get_workspace_public_claims(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return build_public_profile_response(workspace_id, db)    

@router.get("/workspaces/{workspace_id}/public-claims")
def get_workspace_public_claims(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return build_public_profile_response(workspace_id, db)    
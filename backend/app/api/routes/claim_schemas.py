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
from app.services.audit_service import log_audit_event
from app.services.claim_service import compute_claim_hash
from app.services.entitlements import enforce_claim_creation_allowed
from app.services.evidence_pack_service import build_evidence_zip
from app.services.report_service import build_claim_pdf
from app.services.claim_governance_service import (
    can_access_verify_route,
    can_embed_claim,
    can_show_in_leaderboard,
    can_show_in_profile,
    can_show_in_public_directory,
)

from app.services.integrity_service import (
    verify_claim_integrity,
)

from app.models.integrity_scan import (
    IntegrityScan,
)

from app.models.integrity_alert import (
    IntegrityAlert,
)

from app.services.integrity_monitor_service import (
    scan_locked_claims,
)

from app.services.claim_integrity_engine import (
    resolve_schema_trades,
    parse_period_start,
    parse_period_end,
    coerce_trade_opened_at,
    compute_trade_set_hash,
    compute_integrity_snapshot,
)
from app.services.integrity_score_service import (
    calculate_integrity_score,
    get_integrity_band,
)
from app.services.trade_metrics_service import (
    compute_trade_metrics,
    build_equity_curve,
    compute_drawdown_stats,
)
from app.services.evidence_analytics_service import (
    build_evidence_analytics,
)
from app.services.integrity.integrity_dashboard_service import (
    build_integrity_dashboard,
)
from app.services.verification_network_service import (
    get_verification_network,
)
from app.services.verification.verification_service import (
    get_claim_verification_certificate,
    get_claim_verification_metrics,
)
from app.services.pdf.claim_report.claim_report_pdf_service import (
    build_claim_report_pdf,
)


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
    return can_access_verify_route(schema)


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

    trade_tier = getattr(trade, "trust_tier", None)

    if not trade_tier:

        source = str(
            getattr(
                trade,
                "source_system",
                "",
            )
        ).upper()

        if source in {
            "MT5",
            "MT4",
            "IBKR",
            "DXTRADE",
            "CTRADER",
            "MATCHTRADER",
            "TRADINGVIEW",
            "BROKER_API",
            "LIVE_SYNC",
        }:

            trade_tier = "Tier 1"

        elif source in {
            "CSV",
            "IMPORT",
        }:

            trade_tier = "Tier 2"

        else:

            trade_tier = "Tier 3"

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
        "trade_tier": trade_tier,
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
        if schema.status in {"published", "locked"}
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
        trade_metrics = compute_trade_metrics(filtered_trades)
        dispute_ctx = resolve_claim_dispute_context(schema, db)
        integrity_status = resolve_claim_integrity_status(schema, filtered_trades)
        trust_score = compute_backend_trust_score(
            schema,
            trade_metrics,
            integrity_status,
            dispute_ctx,
        )
        network_ctx = compute_backend_network_score(schema, trust_score)

        trust_scores.append(trust_score)
        network_scores.append(network_ctx["network_score"])
        total_net_pnl += float(
            trade_metrics.get("net_pnl", 0.0) or 0.0
        )

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
            ClaimSchema.status.in_(["published", "locked"]),
        )
        .all()
    )

    claim_rows = [
        build_claim_list_row(schema, db)
        for schema in claims
        if can_show_in_profile(schema)
    ]

    return {
        "profile": profile,
        "claims": claim_rows,
        "claims_count": len(claim_rows),
    }


def build_claim_list_row(schema: ClaimSchema, db: Session):
    filtered_trades = resolve_schema_trades(schema, db)

    trade_metrics = compute_trade_metrics(filtered_trades)

    integrity_status = resolve_claim_integrity_status(
        schema,
        filtered_trades,
    )

    dispute_ctx = resolve_claim_dispute_context(
        schema,
        db,
    )

    leaderboard = build_leaderboard(filtered_trades)

    certificate = get_claim_verification_certificate(
        db=db,
        claim=schema,
    )

    verification = get_claim_verification_metrics(
        db=db,
        claim=schema,
    )

    components = certificate.component_scores

    provenance = certificate.provenance

    trust_score = verification.verification_score

    network_score = components.network.earned_points

    trust_weighted_pnl = round(
        float(trade_metrics["net_pnl"]) * trust_score / 100,
        4,
    )

    network_weighted_pnl = round(
        float(trade_metrics["net_pnl"]) * network_score / 100,
        4,
    )

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

    "trade_count": trade_metrics["trade_count"],
    "net_pnl": trade_metrics["net_pnl"],
    "profit_factor": trade_metrics["profit_factor"],
    "win_rate": trade_metrics["win_rate"],

    "leaderboard": leaderboard,

    "disputes_count": dispute_ctx["disputes_count"],
    "active_disputes_count": dispute_ctx["active_disputes_count"],
    "has_active_dispute": dispute_ctx["has_active_dispute"],
    "dispute_penalty_factor": dispute_ctx["dispute_penalty_factor"],

    "trust_score": verification.verification_score,

    "verification_band": verification.verification_band,

    "verification_tier": verification.verification_tier,

    "certificate_hash":
        certificate.identity.certificate_hash,

    "certificate_id":
        certificate.identity.certificate_id,

    "certificate_version":
        certificate.identity.certificate_version,

    "tvs_version":
        certificate.identity.tvs_version,

    "verification_band":
        verification.verification_band,

    "trust_weighted_pnl": trust_weighted_pnl,

    "network_score":
        components.network.earned_points,

    "network_weighted_pnl": network_weighted_pnl,

    "network": {

        "score":
            components.network.earned_points,

        "maximum":
            components.network.maximum_points,

        "percentage":
            components.network.percentage,

        "reason":
            components.network.reason,

        "status":
            components.network.status,
    },

    "verification": {
        "score": verification.verification_score,
        "band": verification.verification_band,
        "tier": verification.verification_tier,
        "status": verification.verification_status,

        "certificate_hash": certificate.identity.certificate_hash,
        "certificate_id": certificate.identity.certificate_id,
        "certificate_version": certificate.identity.certificate_version,
        "tvs_version": certificate.identity.tvs_version,
    },

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
    trade_metrics = compute_trade_metrics(filtered_trades)
    dispute_ctx = resolve_claim_dispute_context(schema, db)
    leaderboard = build_leaderboard(filtered_trades)

    if not can_access_verify_route(schema):
        raise HTTPException(
            status_code=403,
            detail="Claim is not publicly accessible",
        )

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

    integrity_status = resolve_claim_integrity_status(
        schema,
        filtered_trades,
    )

    certificate = get_claim_verification_certificate(
        db=db,
        claim=schema,
    )

    verification = get_claim_verification_metrics(
        db=db,
        claim=schema,
    )

    components = certificate.component_scores

    provenance = certificate.provenance

    trust_score = verification.verification_score

    network_score = components.network.earned_points

    trust_weighted_pnl = round(
        float(trade_metrics["net_pnl"]) * trust_score / 100,
        4,
    )

    network_weighted_pnl = round(
        float(trade_metrics["net_pnl"]) * network_score / 100,
        4,
    )

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
        "trade_count": trade_metrics["trade_count"],
        "net_pnl": trade_metrics["net_pnl"],
        "profit_factor": trade_metrics["profit_factor"],
        "win_rate": trade_metrics["win_rate"],
        "leaderboard": leaderboard,
        "issuer": issuer,
        "profile": build_public_trust_profile_for_workspace(schema.workspace_id, db),
        "disputes": dispute_ctx,
        "verification": {

            "score":
                verification.verification_score,

            "band":
                verification.verification_band,

            "tier":
                verification.verification_tier,

            "certificate_id":
                certificate.identity.certificate_id,

            "certificate_hash":
                certificate.identity.certificate_hash,

            "certificate_version":
                certificate.identity.certificate_version,

            "tvs_version":
                certificate.identity.tvs_version,

        },

        "trust_score":
            verification.verification_score,

        "verification_band":
            verification.verification_band,

        "verification_tier":
            verification.verification_tier,

        "trust_weighted_pnl":
            trust_weighted_pnl,

        "network_score":
            components.network.earned_points,

        "network_weighted_pnl":
            network_weighted_pnl,

        "network": {

            "score":
                components.network.earned_points,

            "maximum":
                components.network.maximum_points,

            "reason":
                components.network.reason,

        },
        "component_scores": {

            "evidence":
                verification.evidence,

            "integrity":
                verification.integrity,

            "governance":
                verification.governance,

            "transparency":
                verification.transparency,

            "stability":
                verification.stability,

            "network":
                verification.network,

            "reviews":
                verification.reviews,

            "disputes":
                verification.disputes,
        },
        "provenance": {

            "primary_source":
                provenance.primary_source,

            "primary_tier":
                provenance.primary_tier,

            "tier_composition":
                provenance.tier_composition,

        },
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
    trade_metrics = compute_trade_metrics(filtered_trades)

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
        "metrics_snapshot": trade_metrics,
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
    print("CREATE CLAIM PAYLOAD:", payload.dict(), flush=True)

    # ✅ imports INSIDE function (optional but valid)
    from app.services.entitlements import enforce_claim_creation_allowed

    # ✅ workspace
    workspace = get_workspace_or_404(payload.workspace_id, db)

    # ✅ permissions
    require_workspace_operator_or_owner(payload.workspace_id, current_user, db)

    if not workspace_limits_disabled():
        enforce_claim_creation_allowed(payload.workspace_id, db)

    # =========================================
    # GOVERNANCE: drafts are always private
    # =========================================

    visibility = normalize_visibility(payload.visibility)

    if visibility == "public":
        raise HTTPException(
            status_code=400,
            detail="Draft claims cannot be public."
        )

    workspace = get_workspace_or_404(payload.workspace_id, db)
    effective_plan_code = resolve_effective_workspace_plan_code(workspace)

    # drafts should never become externally visible
    visibility = "private"

    schema = ClaimSchema(
        workspace_id=payload.workspace_id,
        name=payload.name.strip(),
        period_start=(payload.period_start or "").strip(),
        period_end=(payload.period_end or "").strip(),
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
        enforce_claim_creation_allowed(schema.workspace_id, db)

    # =========================================
    # IMMUTABLE FINALITY GOVERNANCE
    # =========================================

    if schema.status == "locked":
        raise HTTPException(
            status_code=403,
            detail="Locked claims are immutable."
        )

    if schema.status != "draft":
        raise HTTPException(
            status_code=400,
            detail="Only draft claims can be edited"
        )

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

    # =========================================
    # DRAFT CLAIM GOVERNANCE
    # =========================================

    next_visibility = normalize_visibility(payload.visibility)

    if next_visibility == "public":
        raise HTTPException(
            status_code=400,
            detail="Draft claims cannot be public."
        )

    # drafts remain private until publish lifecycle
    schema.visibility = "private"

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

    # =========================================
    # CANONICAL PUBLISH GOVERNANCE
    # =========================================

    schema.status = "published"

    # published claims cannot remain private
    if schema.visibility == "private":
        schema.visibility = "unlisted"

    schema.published_at = datetime.utcnow()
    schema.claim_hash = compute_claim_hash(schema)

    workspace = get_workspace_or_404(schema.workspace_id, db)
    effective_plan_code = resolve_effective_workspace_plan_code(workspace)

    # =========================================
    # SANDBOX GOVERNANCE
    # =========================================

    # sandbox workspaces cannot expose fully public claims
    if effective_plan_code == "sandbox" and schema.visibility == "public":
        schema.visibility = "unlisted"

    # Public/unlisted exposure should be governed by the effective entitlement tier,
    # not merely the configured commercial target.
    # Only restrict TRUE public exposure (not unlisted)
    if schema.visibility == "public":
        allowed = can_create_public_claim(
            schema.workspace_id,
            effective_plan_code,
            db
        )
        if not allowed:
            raise HTTPException(
                status_code=403,
                detail="Public claim limit reached for the current effective workspace tier."
            )
        if not can_create_public_claim(
            workspace_id=schema.workspace_id,
            effective_plan_code=resolve_effective_workspace_plan_code(workspace),
            db=db,
        ):
            raise HTTPException(
                status_code=403,
                detail="Public claim limit reached for your plan"
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

    integrity_result = verify_claim_integrity(
        schema,
        db,
    )

    if not integrity_result["valid"]:

        alert = IntegrityAlert(
            workspace_id=schema.workspace_id,
            severity="critical",
            alert_type="LOCK_BLOCKED",
            entity_type="claim_schema",
            entity_id=str(schema.id),
            message=(
                integrity_result.get(
                    "message",
                    "Integrity validation failed.",
                )
            ),
        )

        db.add(alert)
        db.commit()

        raise HTTPException(
            status_code=400,
            detail=(
                "Claim cannot be locked because "
                "integrity validation failed."
            ),
        )

    # 🔒 Freeze the exact trade IDs used at lock time
    locked_trade_ids = [t.id for t in filtered_trades]

    old_state = {
        "status": schema.status,
        "locked_at": schema.locked_at.isoformat() if schema.locked_at else None,
        "locked_trade_set_hash": schema.locked_trade_set_hash,
        "claim_hash": compute_claim_hash(schema),
    }

    # =========================================
    # CANONICAL LOCK GOVERNANCE
    # =========================================

    snapshot = compute_integrity_snapshot(
        schema,
        filtered_trades,
    )

    schema.locked_trade_set_hash = (
        snapshot["trade_hash"]
    )

    schema.integrity_snapshot_json = (
        json.dumps(snapshot)
    )

    schema.locked_trade_ids_json = json.dumps(locked_trade_ids)

    schema.status = "locked"

    # locked claims are institutionally public
    schema.visibility = "public"

    schema.locked_at = datetime.utcnow()

    schema.claim_hash = compute_claim_hash(schema)

    db.commit()
    db.refresh(schema)

    from app.services.integrity_monitor_service import (
        scan_locked_claims,
    )

    scan_locked_claims(
        db,
        schema.workspace_id,
    )

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
    trade_metrics = compute_trade_metrics(filtered_trades)
    leaderboard = build_leaderboard(filtered_trades)

    return {
        "claim_schema_id": schema.id,
        "claim_hash": compute_claim_hash(schema),
        "issuer": build_issuer_payload(schema, db),
        "name": schema.name,
        "verification_status": schema.status,
        "trade_count": trade_metrics["trade_count"],
        "net_pnl": trade_metrics["net_pnl"],
        "profit_factor": trade_metrics["profit_factor"],
        "win_rate": trade_metrics["win_rate"],
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

    claim_hash = schema.claim_hash or compute_claim_hash(schema)

    verification_url = (
        f"/public/verify/{claim_hash}"
    )

    pdf_buffer, filename = build_claim_report_pdf(
        db=db,
        schema=schema,
        verification_url=verification_url,
    )

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

    verification_url = (
        f"/public/verify/{compute_claim_hash(schema)}"
    )

    pdf_buffer, filename = build_claim_report_pdf(
        db=db,
        schema=schema,
        verification_url=verification_url,
    )

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
def verify_public_claim(
    claim_hash: str,
    db: Session = Depends(get_db),
):
    schema = (
        db.query(ClaimSchema)
        .filter(ClaimSchema.claim_hash == claim_hash)
        .first()
    )

    if not schema:
        raise HTTPException(
            status_code=404,
            detail="Claim not found",
        )

    if not can_access_verify_route(schema):
        raise HTTPException(
            status_code=404,
            detail="Public claim not found for supplied hash",
        )

    return build_public_claim_payload(schema, db)


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
        )
        .order_by(ClaimSchema.id.desc())
        .all()
    )

    rows = [
        schema
        for schema in rows
        if can_show_in_public_directory(schema)
    ]

    return [build_claim_list_row(schema, db) for schema in rows]       


@router.post("/api/claims/create")
def create_claim(
    payload: ClaimSchemaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workspace = get_workspace_or_404(payload.workspace_id, db)

    require_workspace_member(payload.workspace_id, current_user, db)

    schema = ClaimSchema(
        workspace_id=payload.workspace_id,
        name=payload.name,
        period_start=payload.period_start,
        period_end=payload.period_end,
        included_member_ids_json=json.dumps(payload.included_member_ids_json),
        included_symbols_json=json.dumps(payload.included_symbols_json),
        excluded_trade_ids_json=json.dumps(payload.excluded_trade_ids_json),
        methodology_notes=payload.methodology_notes,
        visibility=normalize_visibility(payload.visibility),
        status="draft",
    )

    db.add(schema)
    db.commit()
    db.refresh(schema)

    return {
        "id": schema.id,
        "status": "created",
    }    


@router.post("/api/claims/{claim_id}/lock")
def lock_claim(
    claim_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    schema = db.query(ClaimSchema).filter(ClaimSchema.id == claim_id).first()

    if not schema:
        raise HTTPException(status_code=404, detail="Claim not found")

    require_workspace_operator_or_owner(schema.workspace_id, current_user, db)

    trades = resolve_schema_trades(schema, db)

    trade_hash = compute_trade_set_hash(trades)

    if schema.status not in ["verified", "published"]:
        raise HTTPException(
            status_code=400,
            detail="Only verified or published claims can be locked",
        )

    schema.locked_trade_set_hash = trade_hash
    schema.status = "locked"
    schema.locked_at = datetime.utcnow()

    db.commit()

    return {
        "status": "locked",
        "claim_id": claim_id,
        "hash": trade_hash,
    }


@router.post("/api/claims/{claim_id}/publish")
def publish_claim(
    claim_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    schema = db.query(ClaimSchema).filter(ClaimSchema.id == claim_id).first()

    if not schema:
        raise HTTPException(status_code=404, detail="Claim not found")

    require_workspace_operator_or_owner(
        schema.workspace_id,
        current_user,
        db,
    )

    if schema.status == "draft":
        raise HTTPException(
            status_code=400,
            detail="Claim must be verified before publication",
        )

    schema.status = "published"

    if not schema.published_at:
        schema.published_at = datetime.utcnow()

    db.commit()
    db.refresh(schema)

    return {
        "status": schema.status,
        "claim_id": schema.id,
        "visibility": schema.visibility,
        "published_at": schema.published_at,
    } 


@router.get("/claim-schemas/{claim_id}/evidence-bundle/download")
def download_evidence_zip(claim_id: int, db: Session = Depends(get_db)):
    schema = db.query(ClaimSchema).filter(ClaimSchema.id == claim_id).first()

    trades = db.query(Trade).filter(Trade.workspace_id == schema.workspace_id).all()
    audit_events = db.query(AuditEvent).filter(AuditEvent.workspace_id == schema.workspace_id).all()

    buffer = build_evidence_zip(schema, trades, audit_events)

    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=claim_{claim_id}.zip"},
    )


@router.get("/claim-schemas/{claim_id}/report/download")
def download_claim_pdf(claim_id: int, db: Session = Depends(get_db)):
    schema = db.query(ClaimSchema).filter(ClaimSchema.id == claim_id).first()

    trades = db.query(Trade).filter(Trade.workspace_id == schema.workspace_id).all()

    metrics = {
        "trade_count": len(trades),
        "net_pnl": sum([t.net_pnl or 0 for t in trades]),
    }

    buffer = build_claim_pdf(schema, metrics)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=claim_{claim_id}.pdf"},
    )            


@router.get(
    "/workspaces/{workspace_id}/verification-analytics"
)
def get_verification_analytics(
    workspace_id: int,
    db: Session = Depends(get_db),
):
    return get_verification_network(
        db=db,
        workspace_id=workspace_id,
    )


@router.get(
    "/workspaces/{workspace_id}/trust-scores"
)
def get_trust_scores(
    workspace_id: int,
    db: Session = Depends(get_db),
):
    profile = (
        build_public_trust_profile_for_workspace(
            workspace_id,
            db,
        )
    )

    return {
        "average_trust_score":
            profile["average_trust_score"],

        "average_network_score":
            profile["average_network_score"],

        "claims_count":
            profile["claims_count"],

        "locked_claims_count":
            profile["locked_claims_count"],

        "contested_claims_count":
            profile["contested_claims_count"],

        "total_net_pnl":
            profile["total_net_pnl"],

        "trust_profile_band":
            profile["trust_profile_band"],

        "workspace_id":
            profile["workspace_id"],

        "profile_id":
            profile["profile_id"],

        "type":
            profile["type"],

        "network":
            profile["network"],
    }


@router.get(
    "/workspace/{workspace_id}/leaderboard-analytics"
)
def get_leaderboard_analytics(
    workspace_id: int,
    db: Session = Depends(get_db),
):
    schemas = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id
            == workspace_id
        )
        .all()
    )

    claim_rankings = []
    member_totals = {}

    for schema in schemas:

        trades = resolve_schema_trades(
            schema,
            db,
        )

        trade_metrics = compute_trade_metrics(
            trades
        )

        claim_rankings.append(
            {
                "claim_schema_id":
                    schema.id,
                "name":
                    schema.name,
                "status":
                    schema.status,
                "trade_count":
                    trade_metrics["trade_count"],
                "net_pnl":
                    trade_metrics["net_pnl"],
                "profit_factor":
                    trade_metrics["profit_factor"],
                "win_rate":
                    trade_metrics["win_rate"],
            }
        )

        leaderboard = build_leaderboard(
            trades
        )

        for row in leaderboard:

            member = row["member"]

            if member not in member_totals:

                member_totals[member] = {
                    "member": member,
                    "net_pnl": 0,
                }

            member_totals[member][
                "net_pnl"
            ] += row["net_pnl"]

    claim_rankings.sort(
        key=lambda x: x["net_pnl"],
        reverse=True,
    )

    member_rankings = sorted(
        member_totals.values(),
        key=lambda x: x["net_pnl"],
        reverse=True,
    )

    return {
        "summary": {
            "claims":
                len(claim_rankings),
            "members":
                len(member_rankings),
        },
        "claim_rankings":
            claim_rankings,
        "member_rankings":
            member_rankings,
    }


@router.get(
    "/workspace/{workspace_id}/risk-analytics"
)
def get_risk_analytics(
    workspace_id: int,
    db: Session = Depends(get_db),
):
    schemas = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id
            == workspace_id
        )
        .all()
    )

    total_trades = 0
    total_net_pnl = 0

    total_wins = 0
    total_losses = 0

    profit_factors = []
    drawdowns = []

    recent_claims = []

    for schema in schemas:

        trades = resolve_schema_trades(
            schema,
            db,
        )

        trade_metrics = compute_trade_metrics(
            trades
        )

        equity_curve = build_equity_curve(
            trades
        )

        drawdown_stats = (
            compute_drawdown_stats(
                equity_curve["curve"]
            )
        )

        total_trades += (
            trade_metrics["trade_count"]
        )

        total_net_pnl += (
            trade_metrics["net_pnl"]
        )

        profit_factors.append(
            trade_metrics["profit_factor"]
        )

        drawdowns.append(
            drawdown_stats[
                "max_drawdown"
            ]
        )

        for trade in trades:

            pnl = (
                trade.net_pnl or 0
            )

            if pnl > 0:
                total_wins += 1

            elif pnl < 0:
                total_losses += 1

        recent_claims.append(
            {
                "claim_schema_id":
                    schema.id,

                "name":
                    schema.name,

                "status":
                    schema.status,

                "trade_count":
                    trade_metrics["trade_count"],

                "net_pnl":
                    trade_metrics["net_pnl"],

                "profit_factor":
                    trade_metrics[
                        "profit_factor"
                    ],

                "max_drawdown":
                    drawdown_stats[
                        "max_drawdown"
                    ],
            }
        )

    recent_claims.sort(
        key=lambda x:
        x["net_pnl"],
        reverse=True,
    )

    total_closed = (
        total_wins +
        total_losses
    )

    win_rate = (
        round(
            (
                total_wins /
                total_closed
            ) * 100,
            2,
        )
        if total_closed
        else 0
    )

    average_pf = (
        round(
            sum(
                profit_factors
            )
            /
            len(
                profit_factors
            ),
            2,
        )
        if profit_factors
        else 0
    )

    max_drawdown = (
        max(drawdowns)
        if drawdowns
        else 0
    )

    return {
        "overview": {
            "trades":
                total_trades,

            "net_pnl":
                round(
                    total_net_pnl,
                    2,
                ),

            "wins":
                total_wins,

            "losses":
                total_losses,

            "win_rate":
                win_rate,

            "profit_factor":
                average_pf,

            "max_drawdown":
                round(
                    max_drawdown,
                    2,
                ),
        },

        "recent_claims":
            recent_claims[:20],
    }


@router.get(
    "/workspace/{workspace_id}/due-diligence"
)
def get_due_diligence(
    workspace_id: int,
    db: Session = Depends(get_db),
):
    workspace = (
        db.query(Workspace)
        .filter(
            Workspace.id == workspace_id
        )
        .first()
    )

    if not workspace:
        raise HTTPException(
            status_code=404,
            detail="Workspace not found",
        )

    profile = (
        build_public_trust_profile_for_workspace(
            workspace_id,
            db,
        )
    )

    claims = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id
            == workspace_id
        )
        .all()
    )

    evidence_records = (
        db.query(func.count(Trade.id))
        .filter(
            Trade.workspace_id
            == workspace_id
        )
        .scalar()
        or 0
    )

    published_claims = 0
    locked_claims = 0
    verified_claims = 0


    compromised_claims = 0

    for schema in claims:

        if schema.status == "published":
            published_claims += 1

        if schema.status == "locked":
            locked_claims += 1

        if schema.status in [
            "verified",
            "published",
            "locked",
        ]:
            verified_claims += 1

        trades = resolve_schema_trades(
            schema,
            db,
        )

        trade_metrics = compute_trade_metrics(
            trades
        )

        if (
            schema.status == "locked"
            and schema.locked_trade_set_hash
        ):
            current_hash = (
                compute_trade_set_hash(
                    trades
                )
            )

            if (
                current_hash
                != schema.locked_trade_set_hash
            ):
                compromised_claims += 1

    claim_count = len(claims)

    coverage = (
        round(
            (
                verified_claims
                / claim_count
            )
            * 100,
            2,
        )
        if claim_count > 0
        else 0
    )

    total_trades = 0
    total_wins = 0
    total_losses = 0

    profit_factors = []

    gross_profit = 0.0
    gross_loss_abs = 0.0
    drawdowns = []

    for schema in claims:

        trades = resolve_schema_trades(
            schema,
            db,
        )

        trade_metrics = compute_trade_metrics(
            trades
        )

        curve = build_equity_curve(
            trades
        )

        dd_stats = (
            compute_drawdown_stats(
                curve["curve"]
            )
        )

        total_trades += (
            trade_metrics["trade_count"]
        )

        profit_factors.append(
            metrics["profit_factor"]
        )

        drawdowns.append(
            dd_stats["max_drawdown"]
        )

        for trade in trades:

            pnl = (
                trade.net_pnl or 0
            )

            if pnl > 0:

                total_wins += 1

                gross_profit += pnl

            elif pnl < 0:

                total_losses += 1

                gross_loss_abs += abs(pnl)

    total_closed = (
        total_wins
        + total_losses
    )

    risk_win_rate = (
        round(
            (
                total_wins
                / total_closed
            ) * 100,
            2,
        )
        if total_closed
        else 0
    )

    risk_profit_factor = (
        round(
            gross_profit
            / gross_loss_abs,
            2,
        )
        if gross_loss_abs > 0
        else round(
            gross_profit,
            2,
        )
    )

    risk_max_drawdown = (
        round(
            max(drawdowns),
            2,
        )
        if drawdowns
        else 0
    )

    integrity_dashboard = (
        build_integrity_dashboard(
            db,
            workspace_id,
        )
    )

    integrity_score = (
        integrity_dashboard[
            "integrity_score"
        ]
    )

    open_findings = (
        integrity_dashboard[
            "open_findings"
        ]
    )

    resolved_findings = (
        integrity_dashboard[
            "resolved_findings"
        ]
    )

    trust_score = (
        profile.get(
            "average_trust_score",
            0,
        )
    )

    if trust_score >= 85:
        grade = "A"

    elif trust_score >= 70:
        grade = "B"

    elif trust_score >= 55:
        grade = "C"

    else:
        grade = "D"

    evidence = build_evidence_analytics(
        db,
        workspace_id,
    )

    confidence = round(
        (
            trust_score
            + integrity_score
            + coverage
            + evidence["quality"]["score"]
        ) / 4,
        2,
    )

    if confidence >= 90:
        recommendation = "LOW RISK"

    elif confidence >= 75:
        recommendation = "MODERATE RISK"

    elif confidence >= 60:
        recommendation = "MEDIUM RISK"

    else:
        recommendation = "HIGH RISK"

    governance_compliance = round(
        (
            locked_claims
            / claim_count
        ) * 100,
        2,
    ) if claim_count else 0

    verification_status = recommendation

    return {

        "overview": {
            "claims": claim_count,
            "published_claims": published_claims,
            "locked_claims": locked_claims,
            "evidence_records": evidence_records,
        },

        "trust": {
            "trust_score": profile.get(
                "average_trust_score",
                0,
            ),
            "network_score": profile.get(
                "average_network_score",
                0,
            ),
            "trust_band": profile.get(
                "trust_profile_band",
                "unknown",
            ),
        },

        "verification": {
            "coverage": coverage,
            "verified_claims": verified_claims,
            "status": verification_status,
        },

        "integrity": {

            "integrity_score":
                integrity_score,

            "compromised_claims":
                compromised_claims,

            "open_findings":
                open_findings,

            "resolved_findings":
                resolved_findings,
        },

        "evidence": {
            "quality_score":
                evidence["quality"]["score"],

            "quality_band":
                evidence["quality"]["band"],

            "coverage":
                evidence["overview"]["coverage"],
        },

        "governance": {
            "compliance":
                governance_compliance,
        },

        "risk": {
            "risk_score": confidence,
            "profit_factor":
                risk_profit_factor,
            "win_rate":
                risk_win_rate,
            "max_drawdown":
                risk_max_drawdown,
        },

        "assessment": {
            "grade": grade,
            "status":
                profile.get(
                    "trust_profile_band",
                    "unknown",
                ),
            "confidence":
                confidence,
            "recommendation":
                recommendation,
        },
    }


@router.get(
    "/workspace/{workspace_id}/integrity-alerts"
)
def get_integrity_alerts(
    workspace_id: int,
    db: Session = Depends(get_db),
):
    scan_locked_claims(
        db,
        workspace_id,
    )

    alerts = (
        db.query(
            IntegrityAlert
        )
        .filter(
            IntegrityAlert.workspace_id
            == workspace_id
        )
        .order_by(
            IntegrityAlert.id.desc()
        )
        .all()
    )

    return {
        "critical":
            len(
                [
                    a for a in alerts
                    if a.severity
                    == "critical"
                ]
            ),

        "warning":
            len(
                [
                    a for a in alerts
                    if a.severity
                    == "warning"
                ]
            ),

        "alerts": [
            {
                "id": a.id,
                "severity":
                    a.severity,
                "alert_type":
                    a.alert_type,
                "message":
                    a.message,
                "status":
                    a.status,
                "created_at":
                    a.created_at,
            }
            for a in alerts
        ],
    }


@router.post(
    "/workspace/{workspace_id}/integrity-scan"
)
def run_integrity_scan(
    workspace_id: int,
    db: Session = Depends(get_db),
):
    scanned_claims = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id
            == workspace_id
        )
        .count()
    )

    scan_locked_claims(
        db,
        workspace_id,
    )

    open_alerts = (
        db.query(
            IntegrityAlert
        )
        .filter(
            IntegrityAlert.workspace_id
            == workspace_id,

            IntegrityAlert.status
            == "open",
        )
        .all()
    )

    fatal = len([
        a for a in open_alerts
        if str(a.severity).upper()
        == "FATAL"
    ])

    critical = len([
        a for a in open_alerts
        if str(a.severity).upper()
        == "CRITICAL"
    ])

    high = len([
        a for a in open_alerts
        if str(a.severity).upper()
        == "HIGH"
    ])

    warning = len([
        a for a in open_alerts
        if str(a.severity).upper()
        == "WARNING"
    ])

    score = (
        calculate_integrity_score(
            open_alerts
        )
    )

    band = (
        get_integrity_band(
            score
        )
    )

    healthy = (
        fatal == 0
        and critical == 0
        and high == 0
    )

    scan = IntegrityScan(
        workspace_id=workspace_id,

        status=band.lower(),

        claims_scanned=scanned_claims,

        alerts_found=len(
            open_alerts
        ),

        summary_json=json.dumps({
            "integrity_score": score,
            "health_band": band,
            "fatal": fatal,
            "critical": critical,
            "high": high,
            "warning": warning,
            "open_alerts": len(
                open_alerts
            ),
        }),

        completed_at=datetime.utcnow(),
    )

    db.add(scan)
    db.commit()

    return {
        "workspace_id":
            workspace_id,

        "healthy":
            healthy,

        "integrity_score":
            score,

        "health_band":
            band,

        "open_alerts":
            len(open_alerts),

        "fatal":
            fatal,

        "critical":
            critical,

        "high":
            high,

        "warning":
            warning,
    }


@router.get(
    "/workspace/{workspace_id}/integrity-scan-history"
)
def get_integrity_scan_history(
    workspace_id: int,
    db: Session = Depends(get_db),
):
    scans = (
        db.query(
            IntegrityScan
        )
        .filter(
            IntegrityScan.workspace_id
            == workspace_id
        )
        .order_by(
            IntegrityScan.id.desc()
        )
        .limit(100)
        .all()
    )

    history = []

    for scan in scans:

        try:
            summary = json.loads(
                scan.summary_json
                or "{}"
            )

        except Exception:
            summary = {}

        history.append(
            {
                "id":
                    scan.id,

                "healthy":
                    (
                        summary.get(
                            "health_band"
                        )
                        == "HEALTHY"
                    ),

                "status":
                    scan.status,

                "integrity_score":
                    summary.get(
                        "integrity_score",
                        0,
                    ),

                "health_band":
                    summary.get(
                        "health_band",
                        "UNKNOWN",
                    ),

                "open_alerts":
                    summary.get(
                        "open_alerts",
                        0,
                    ),

                "fatal":
                    summary.get(
                        "fatal",
                        0,
                    ),

                "critical":
                    summary.get(
                        "critical",
                        0,
                    ),

                "high":
                    summary.get(
                        "high",
                        0,
                    ),

                "warning":
                    summary.get(
                        "warning",
                        0,
                    ),

                "claims_scanned":
                    scan.claims_scanned,

                "started_at":
                    scan.started_at,

                "completed_at":
                    scan.completed_at,
            }
        )

    return {
        "history":
            history
    }
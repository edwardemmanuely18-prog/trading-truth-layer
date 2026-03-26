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

router = APIRouter()


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


def enforce_workspace_claim_limit(workspace_id: int, db: Session):
    if workspace_limits_disabled():
        return

    workspace = get_workspace_or_404(workspace_id, db)

    claim_limit = workspace.claim_limit or 0
    current_claim_count = (
        db.query(ClaimSchema)
        .filter(ClaimSchema.workspace_id == workspace_id)
        .count()
    )

    if claim_limit > 0 and current_claim_count >= claim_limit:
        raise HTTPException(
            status_code=403,
            detail=(
                f"Claim limit reached for workspace {workspace_id}. "
                f"Current claims: {current_claim_count}. "
                f"Plan limit: {claim_limit}. "
                f"Upgrade workspace plan to create additional claims."
            ),
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
        "is_publicly_accessible": schema.visibility in {"public", "unlisted"} and schema.status in {"published", "locked"},
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
    if schema.visibility not in {"public", "unlisted"}:
        raise HTTPException(status_code=403, detail="Claim is not publicly accessible")

    if schema.status not in {"published", "locked"}:
        raise HTTPException(status_code=403, detail="Claim is not yet publicly publishable")


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


def pdf_new_page(pdf: canvas.Canvas, title: str | None = None):
    pdf.showPage()
    pdf.setFillColor(colors.black)
    pdf.setStrokeColor(colors.black)
    if title:
        pdf.setTitle(title)
    return 750


def pdf_require_space(pdf: canvas.Canvas, y: float, required_space: float):
    if y >= required_space:
        return y
    return pdf_new_page(pdf)


def pdf_section_title(pdf: canvas.Canvas, title: str, x: float, y: float):
    pdf.setFillColor(colors.HexColor("#0F172A"))
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(x, y, title)
    pdf.setFillColor(colors.black)
    return y - 22


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


def draw_metric_card(pdf: canvas.Canvas, x: float, top_y: float, w: float, h: float, label: str, value: str):
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
    pdf.setFont("Helvetica", 10)
    pdf.drawString(x + 12, top_y - 18, label)

    pdf.setFillColor(colors.HexColor("#0F172A"))
    pdf.setFont("Helvetica-Bold", 17)
    pdf.drawString(x + 12, top_y - 40, value)
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
):
    pdf_round_box(pdf, x, top_y, w, h, fill_color, stroke_color, radius=12)
    pdf.setFillColor(colors.HexColor("#64748B"))
    pdf.setFont("Helvetica", 10)
    pdf.drawString(x + 12, top_y - 18, label)

    pdf.setFillColor(colors.HexColor("#0F172A"))
    pdf.setFont("Helvetica-Bold", 11)
    current_y = top_y - 38
    current_y = draw_pdf_wrapped_text(
        pdf,
        value or "—",
        x + 12,
        current_y,
        max_width=w - 24,
        line_height=13,
        font_name="Helvetica",
        font_size=10,
    )
    pdf.setFillColor(colors.black)
    return current_y


def draw_kv_pair(pdf: canvas.Canvas, x: float, y: float, label: str, value: str):
    pdf.setFillColor(colors.HexColor("#64748B"))
    pdf.setFont("Helvetica", 10)
    pdf.drawString(x, y, label)
    pdf.setFillColor(colors.HexColor("#0F172A"))
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(x, y - 15, shorten_text(value, 36))
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
        34,
        colors.HexColor("#F8FAFC"),
        colors.HexColor("#E2E8F0"),
        radius=10,
    )
    pdf.setFillColor(colors.HexColor("#334155"))
    pdf.setFont("Helvetica", 8)
    pdf.drawString(x + 10, y_top - 28, shorten_text(value, 84))
    pdf.setFillColor(colors.black)


def compute_drawdown_stats(points: list[dict]):
    if not points:
        return {
            "max_drawdown": 0.0,
            "peak_cumulative": 0.0,
            "trough_cumulative": 0.0,
        }

    running_peak = float("-inf")
    max_drawdown = 0.0
    peak_cumulative = 0.0
    trough_cumulative = 0.0

    for point in points:
        current = float(point.get("cumulative_pnl", 0.0))
        if current > running_peak:
            running_peak = current

        drawdown = running_peak - current
        if drawdown > max_drawdown:
            max_drawdown = drawdown
            peak_cumulative = running_peak
            trough_cumulative = current

    return {
        "max_drawdown": round(max_drawdown, 4),
        "peak_cumulative": round(peak_cumulative, 4),
        "trough_cumulative": round(trough_cumulative, 4),
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
    chart_y_top = top_y - 34
    chart_w = width - 36
    chart_h = chart_y_top - chart_y_bottom

    pdf.setFillColor(colors.HexColor("#64748B"))
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


def build_claim_report_pdf_bytes(schema: ClaimSchema, db: Session) -> tuple[BytesIO, str]:
    filtered_trades = resolve_schema_trades(schema, db)
    metrics = compute_trade_metrics(filtered_trades)
    leaderboard = build_leaderboard(filtered_trades)
    equity_curve = build_equity_curve(filtered_trades)
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

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    left = 42
    right = width - 42
    content_width = right - left
    y = height - 42

    pdf.setTitle(f"claim_report_{schema.id}_{claim_hash[:12]}")
    pdf.setAuthor("Trading Truth Layer")
    pdf.setSubject("Verified Trading Claim Report")

    pdf.setFillColor(colors.HexColor("#0F172A"))
    pdf.setFont("Helvetica-Bold", 23)
    pdf.drawString(left, y, "Trading Truth Layer")
    y -= 24

    pdf.setFont("Helvetica", 11)
    pdf.setFillColor(colors.HexColor("#64748B"))
    pdf.drawString(left, y, "Verified Trading Claims OS")
    y -= 28

    pdf.setFont("Helvetica-Bold", 27)
    pdf.setFillColor(colors.HexColor("#0F172A"))
    pdf.drawString(left, y, "Institutional Claim Report")
    y -= 20

    pdf.setFont("Helvetica", 11)
    pdf.setFillColor(colors.HexColor("#475569"))
    y = draw_pdf_wrapped_text(
        pdf,
        "Lifecycle-governed trading claim report with evidence-backed performance summary, canonical fingerprints, lineage state, and integrity validation context.",
        left,
        y,
        max_width=content_width,
        line_height=14,
        font_name="Helvetica",
        font_size=11,
    )
    y -= 10

    banner_height = 126
    pdf_round_box(
        pdf,
        left,
        y,
        content_width,
        banner_height,
        colors.HexColor("#ECFDF5") if integrity_status == "valid" else colors.HexColor("#FEF2F2"),
        colors.HexColor("#A7F3D0") if integrity_status == "valid" else colors.HexColor("#FECACA"),
        radius=16,
    )

    pdf.setFillColor(colors.HexColor("#166534") if integrity_status == "valid" else colors.HexColor("#991B1B"))
    pdf.setFont("Helvetica", 11)
    pdf.drawString(left + 16, y - 22, "Verification Signature")

    signature_text = (
        "Verified • Locked • Integrity Valid"
        if schema.status == "locked" and integrity_status == "valid"
        else (
            "Verified • Published"
            if schema.status == "published"
            else (
                "Locked • Integrity Compromised"
                if schema.status == "locked" and integrity_status != "valid"
                else f"{schema.status.title()} Claim"
            )
        )
    )

    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(left + 16, y - 46, signature_text)

    pdf.setFont("Helvetica", 10)
    pdf.drawString(
        left + 16,
        y - 66,
        "This report summarizes lifecycle state, integrity state, performance metrics, and canonical claim fingerprinting.",
    )

    chip_x = right - 148
    pdf_round_box(
        pdf,
        chip_x,
        y - 8,
        132,
        42,
        colors.white,
        colors.HexColor("#D1D5DB"),
        radius=10,
    )
    pdf.setFillColor(colors.HexColor("#0F172A"))
    pdf.setFont("Helvetica", 10)
    pdf.drawString(chip_x + 10, y - 24, f"status: {schema.status}")
    pdf.drawString(chip_x + 10, y - 38, f"integrity: {integrity_status}")
    pdf.setFillColor(colors.black)

    hash_top = y - 84
    half_gap = 12
    box_w = (content_width - half_gap) / 2
    draw_label_value_box(
        pdf,
        left + 16,
        hash_top,
        box_w - 16,
        48,
        "Claim Hash Fingerprint",
        short_hash(claim_hash, 22, 16),
    )
    draw_label_value_box(
        pdf,
        left + 16 + box_w,
        hash_top,
        box_w - 16,
        48,
        "Trade Set Hash Fingerprint",
        short_hash(trade_set_hash, 22, 16),
    )

    y -= banner_height + 26

    y = pdf_section_title(pdf, "Claim Identity", left, y)
    pdf.setFont("Helvetica-Bold", 19)
    pdf.setFillColor(colors.HexColor("#0F172A"))
    pdf.drawString(left, y, shorten_text(schema.name, 68))
    y -= 24

    card_gap = 12
    card_w = (content_width - (card_gap * 3)) / 4
    card_h = 58
    y = pdf_require_space(pdf, y, 180)

    draw_metric_card(pdf, left, y, card_w, card_h, "Trade Count", str(metrics["trade_count"]))
    draw_metric_card(pdf, left + card_w + card_gap, y, card_w, card_h, "Net PnL", str(metrics["net_pnl"]))
    draw_metric_card(pdf, left + (card_w + card_gap) * 2, y, card_w, card_h, "Profit Factor", str(metrics["profit_factor"]))
    draw_metric_card(pdf, left + (card_w + card_gap) * 3, y, card_w, card_h, "Win Rate", f"{round(metrics['win_rate'] * 100, 2)}%")
    y -= card_h + 26

    y = pdf_require_space(pdf, y, 250)
    panel_gap = 16
    panel_w = (content_width - panel_gap) / 2
    panel_h = 202

    pdf_round_box(pdf, left, y, panel_w, panel_h, colors.white, colors.HexColor("#E2E8F0"), radius=14)
    pdf.setFillColor(colors.HexColor("#0F172A"))
    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(left + 14, y - 22, "Verification Scope")

    draw_kv_pair(pdf, left + 14, y - 50, "Period Start", schema.period_start or "—")
    draw_kv_pair(pdf, left + 170, y - 50, "Period End", schema.period_end or "—")
    draw_kv_pair(pdf, left + 14, y - 88, "Included Members", included_members)
    draw_kv_pair(pdf, left + 170, y - 88, "Included Symbols", included_symbols)
    draw_kv_pair(pdf, left + 14, y - 126, "Excluded Trade IDs", excluded_trade_ids)
    draw_kv_pair(pdf, left + 170, y - 126, "Visibility", schema.visibility or "—")

    pdf.setFillColor(colors.HexColor("#64748B"))
    pdf.setFont("Helvetica", 10)
    pdf.drawString(left + 14, y - 156, "Methodology Notes")
    pdf.setFillColor(colors.HexColor("#0F172A"))
    pdf.setFont("Helvetica", 10)
    draw_pdf_wrapped_text(
        pdf,
        schema.methodology_notes or "—",
        left + 14,
        y - 174,
        max_width=panel_w - 28,
        line_height=12,
        font_name="Helvetica",
        font_size=10,
    )

    panel2_x = left + panel_w + panel_gap
    pdf_round_box(pdf, panel2_x, y, panel_w, panel_h, colors.white, colors.HexColor("#E2E8F0"), radius=14)
    pdf.setFillColor(colors.HexColor("#0F172A"))
    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(panel2_x + 14, y - 22, "Lifecycle & Lineage")

    draw_kv_pair(pdf, panel2_x + 14, y - 50, "Status", schema.status or "—")
    draw_kv_pair(pdf, panel2_x + 170, y - 50, "Integrity", integrity_status)
    draw_kv_pair(pdf, panel2_x + 14, y - 88, "Verified At", schema.verified_at.isoformat() if schema.verified_at else "—")
    draw_kv_pair(pdf, panel2_x + 170, y - 88, "Published At", schema.published_at.isoformat() if schema.published_at else "—")
    draw_kv_pair(pdf, panel2_x + 14, y - 126, "Locked At", schema.locked_at.isoformat() if schema.locked_at else "—")
    draw_kv_pair(pdf, panel2_x + 170, y - 126, "Version Number", str(schema.version_number or "—"))
    draw_kv_pair(pdf, panel2_x + 14, y - 164, "Root Claim ID", str(schema.root_claim_id or "—"))
    draw_kv_pair(pdf, panel2_x + 170, y - 164, "Parent Claim ID", str(schema.parent_claim_id or "—"))

    y -= panel_h + 26

    y = pdf_section_title(pdf, "Performance Diagnostics", left, y)
    y = pdf_require_space(pdf, y, 200)

    diag_w = (content_width - 12 * 3) / 4
    draw_metric_card(pdf, left, y, diag_w, 58, "Best Trade", str(metrics["best_trade"]))
    draw_metric_card(pdf, left + diag_w + 12, y, diag_w, 58, "Worst Trade", str(metrics["worst_trade"]))
    draw_metric_card(pdf, left + (diag_w + 12) * 2, y, diag_w, 58, "Max Drawdown", str(drawdown_stats["max_drawdown"]))
    draw_metric_card(pdf, left + (diag_w + 12) * 3, y, diag_w, 58, "Ending Equity", str(equity_curve["ending_equity"]))
    y -= 74

    y = pdf_require_space(pdf, y, 280)
    draw_equity_curve_preview(pdf, left, y, content_width, 210, equity_curve["curve"][:24])
    y -= 228

    y = pdf_section_title(pdf, "Leaderboard Snapshot", left, y)
    y = pdf_require_space(pdf, y, 160)

    pdf.setFont("Helvetica-Bold", 10)
    pdf.setFillColor(colors.HexColor("#64748B"))
    pdf.drawString(left + 4, y, "Rank")
    pdf.drawString(left + 92, y, "Member")
    pdf.drawString(left + 240, y, "Net PnL")
    pdf.drawString(left + 350, y, "Win Rate")
    pdf.drawString(left + 470, y, "Profit Factor")
    y -= 12

    pdf.setStrokeColor(colors.HexColor("#CBD5E1"))
    pdf.line(left, y, right, y)
    y -= 16

    pdf.setFont("Helvetica", 10)
    pdf.setFillColor(colors.HexColor("#0F172A"))

    if leaderboard:
        for row in leaderboard[:10]:
            y = pdf_require_space(pdf, y, 110)
            pdf.drawString(left + 4, y, str(row["rank"]))
            pdf.drawString(left + 92, y, shorten_text(str(row["member"]), 18))
            pdf.drawString(left + 240, y, str(row["net_pnl"]))
            pdf.drawString(left + 350, y, f"{round(float(row['win_rate']) * 100, 2)}%")
            pdf.drawString(left + 470, y, str(row["profit_factor"]))
            y -= 12
            pdf.setStrokeColor(colors.HexColor("#E2E8F0"))
            pdf.line(left, y, right, y)
            y -= 12
    else:
        pdf.drawString(left + 4, y, "No leaderboard data available.")
        y -= 18

    y -= 8

    y = pdf_section_title(pdf, "Trade Evidence Snapshot", left, y)
    y = pdf_require_space(pdf, y, 180)

    pdf.setFont("Helvetica-Bold", 9)
    pdf.setFillColor(colors.HexColor("#64748B"))
    pdf.drawString(left, y, "#")
    pdf.drawString(left + 24, y, "Trade ID")
    pdf.drawString(left + 82, y, "Opened")
    pdf.drawString(left + 212, y, "Symbol")
    pdf.drawString(left + 278, y, "Side")
    pdf.drawString(left + 323, y, "Member")
    pdf.drawString(left + 385, y, "PnL")
    pdf.drawString(left + 455, y, "Cumulative")
    y -= 12

    pdf.setStrokeColor(colors.HexColor("#CBD5E1"))
    pdf.line(left, y, right, y)
    y -= 15

    pdf.setFont("Helvetica", 9)
    pdf.setFillColor(colors.HexColor("#0F172A"))
    evidence_rows = build_trade_evidence(filtered_trades)

    if evidence_rows:
        for row in evidence_rows[:20]:
            y = pdf_require_space(pdf, y, 110)
            pdf.drawString(left, y, str(row["index"]))
            pdf.drawString(left + 24, y, str(row["trade_id"]))
            pdf.drawString(left + 82, y, shorten_text(str(row["opened_at"]), 19))
            pdf.drawString(left + 212, y, shorten_text(str(row["symbol"]), 10))
            pdf.drawString(left + 278, y, shorten_text(str(row["side"]), 8))
            pdf.drawString(left + 323, y, str(row["member_id"]))
            pdf.drawString(left + 385, y, str(row["net_pnl"]))
            pdf.drawString(left + 455, y, str(row["cumulative_pnl"]))
            y -= 12
            pdf.setStrokeColor(colors.HexColor("#E2E8F0"))
            pdf.line(left, y, right, y)
            y -= 10
    else:
        pdf.drawString(left, y, "No trade evidence rows available.")
        y -= 18

    y -= 8

    y = pdf_section_title(pdf, "Canonical Fingerprints", left, y)
    y = pdf_require_space(pdf, y, 180)

    draw_hash_block(pdf, left, y, content_width, "Claim Hash", claim_hash)
    y -= 58
    draw_hash_block(pdf, left, y, content_width, "Trade Set Hash", trade_set_hash)
    y -= 66

    pdf.setFont("Helvetica-Oblique", 9)
    pdf.setFillColor(colors.HexColor("#64748B"))
    pdf.drawString(
        left,
        y,
        "Generated from the canonical trade ledger and lifecycle-governed claim state in Trading Truth Layer.",
    )

    pdf.save()
    buffer.seek(0)

    filename = f"claim_report_{schema.id}_{claim_hash[:12]}.pdf"
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
    enforce_workspace_claim_limit(payload.workspace_id, db)

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
    enforce_workspace_claim_limit(source.workspace_id, db)

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
        "published_at": schema.published_at.isoformat() if schema.published_at else None,
        "claim_hash": compute_claim_hash(schema),
    }

    schema.status = "published"
    schema.published_at = datetime.utcnow()
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
            "published_at": schema.published_at.isoformat() if schema.published_at else None,
            "claim_hash": compute_claim_hash(schema),
        },
        metadata={
            "source": "claim_schemas.publish_claim_schema",
            "actor_user_id": current_user.id,
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

    filtered_trades = resolve_schema_trades(schema, db)
    evidence_rows = build_trade_evidence(filtered_trades)

    return {
        "claim_schema_id": schema.id,
        "claim_hash": compute_claim_hash(schema),
        "name": schema.name,
        "status": schema.status,
        "trade_count": len(evidence_rows),
        "trades": evidence_rows,
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

    if schema.visibility not in {"public", "unlisted"}:
        raise HTTPException(status_code=403, detail="Claim is not publicly accessible")

    if schema.status not in {"published", "locked"}:
        raise HTTPException(status_code=403, detail="Claim is not yet publicly publishable")

    filtered_trades = resolve_schema_trades(schema, db)
    metrics = compute_trade_metrics(filtered_trades)
    leaderboard = build_leaderboard(filtered_trades)

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
    }


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

    filtered_trades = resolve_schema_trades(matched_schema, db)
    metrics = compute_trade_metrics(filtered_trades)
    leaderboard = build_leaderboard(filtered_trades)

    trade_set_hash = matched_schema.locked_trade_set_hash
    if not trade_set_hash:
        trade_set_hash = compute_trade_set_hash(filtered_trades)

    integrity_status = "valid"
    if matched_schema.status == "locked" and matched_schema.locked_trade_set_hash:
        recomputed_trade_set_hash = compute_trade_set_hash(filtered_trades)
        if recomputed_trade_set_hash != matched_schema.locked_trade_set_hash:
            integrity_status = "compromised"

    return {
        "claim_schema_id": matched_schema.id,
        "claim_hash": claim_hash,
        "name": matched_schema.name,
        "verification_status": matched_schema.status,
        "integrity_status": integrity_status,
        "trade_count": metrics["trade_count"],
        "net_pnl": metrics["net_pnl"],
        "profit_factor": metrics["profit_factor"],
        "win_rate": metrics["win_rate"],
        "leaderboard": leaderboard,
        "scope": {
            "period_start": matched_schema.period_start,
            "period_end": matched_schema.period_end,
            "included_members": json.loads(matched_schema.included_member_ids_json or "[]"),
            "included_symbols": json.loads(matched_schema.included_symbols_json or "[]"),
            "methodology_notes": matched_schema.methodology_notes,
            "visibility": matched_schema.visibility,
        },
        "lifecycle": {
            "status": matched_schema.status,
            "verified_at": matched_schema.verified_at.isoformat() if matched_schema.verified_at else None,
            "published_at": matched_schema.published_at.isoformat() if matched_schema.published_at else None,
            "locked_at": matched_schema.locked_at.isoformat() if matched_schema.locked_at else None,
        },
        "lineage": {
            "parent_claim_id": matched_schema.parent_claim_id,
            "root_claim_id": matched_schema.root_claim_id,
            "version_number": matched_schema.version_number,
        },
        "trade_set_hash": trade_set_hash,
    }


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
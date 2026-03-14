from datetime import datetime, timedelta
from io import BytesIO
import hashlib
import json
import re
import zipfile
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models.audit_event import AuditEvent
from app.models.claim_schema import ClaimSchema
from app.models.trade import Trade
from app.models.user import User
from app.models.workspace_membership import WorkspaceMembership
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
):
    words = (text or "").split()
    if not words:
        return y

    line = ""
    for word in words:
        candidate = word if not line else f"{line} {word}"
        if pdf.stringWidth(candidate, "Helvetica", 11) <= max_width:
            line = candidate
        else:
            pdf.drawString(x, y, line)
            y -= line_height
            line = word

    if line:
        pdf.drawString(x, y, line)
        y -= line_height

    return y


def ensure_pdf_space(pdf: canvas.Canvas, y: float, required_space: float):
    if y >= required_space:
        return y

    pdf.showPage()
    pdf.setFont("Helvetica", 11)
    return 750


def build_claim_report_pdf_bytes(schema: ClaimSchema, db: Session) -> tuple[BytesIO, str]:
    filtered_trades = resolve_schema_trades(schema, db)
    metrics = compute_trade_metrics(filtered_trades)
    leaderboard = build_leaderboard(filtered_trades)

    trade_set_hash = schema.locked_trade_set_hash
    if not trade_set_hash:
        trade_set_hash = compute_trade_set_hash(filtered_trades)

    claim_hash = compute_claim_hash(schema)
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    left = 50
    right = width - 50
    y = height - 50

    def section_title(title: str, current_y: float):
        current_y = ensure_pdf_space(pdf, current_y, 120)
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(left, current_y, title)
        return current_y - 22

    pdf.setTitle(f"claim_report_{schema.id}_{claim_hash[:12]}")
    pdf.setAuthor("Trading Truth Layer")
    pdf.setSubject("Verified Trading Claim Report")

    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawString(left, y, "Trading Truth Layer")
    y -= 28

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(left, y, "Verified Claim Report")
    y -= 26

    pdf.setFont("Helvetica", 11)
    pdf.drawString(left, y, f"Generated At: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    y -= 26

    y = section_title("Claim Identity", y)
    pdf.setFont("Helvetica", 11)
    pdf.drawString(left, y, f"Claim Name: {schema.name}")
    y -= 16
    pdf.drawString(left, y, f"Claim ID: {schema.id}")
    y -= 16
    pdf.drawString(left, y, f"Workspace ID: {schema.workspace_id}")
    y -= 16
    pdf.drawString(left, y, f"Status: {schema.status}")
    y -= 16
    pdf.drawString(left, y, f"Visibility: {schema.visibility}")
    y -= 16
    pdf.drawString(left, y, f"Version Number: {schema.version_number}")
    y -= 26

    y = section_title("Verification Window", y)
    pdf.setFont("Helvetica", 11)
    pdf.drawString(left, y, f"Period Start: {schema.period_start}")
    y -= 16
    pdf.drawString(left, y, f"Period End: {schema.period_end}")
    y -= 26

    y = section_title("Performance Summary", y)
    pdf.setFont("Helvetica", 11)
    pdf.drawString(left, y, f"Trade Count: {metrics['trade_count']}")
    y -= 16
    pdf.drawString(left, y, f"Net PnL: {metrics['net_pnl']}")
    y -= 16
    pdf.drawString(left, y, f"Profit Factor: {metrics['profit_factor']}")
    y -= 16
    pdf.drawString(left, y, f"Win Rate: {metrics['win_rate']}")
    y -= 16
    pdf.drawString(left, y, f"Best Trade: {metrics['best_trade']}")
    y -= 16
    pdf.drawString(left, y, f"Worst Trade: {metrics['worst_trade']}")
    y -= 26

    y = section_title("Integrity", y)
    pdf.setFont("Helvetica", 11)
    pdf.drawString(left, y, f"Claim Hash: {claim_hash}")
    y -= 16
    pdf.drawString(left, y, f"Trade Set Hash: {trade_set_hash}")
    y -= 16
    pdf.drawString(left, y, f"Verified At: {schema.verified_at.isoformat() if schema.verified_at else '-'}")
    y -= 16
    pdf.drawString(left, y, f"Published At: {schema.published_at.isoformat() if schema.published_at else '-'}")
    y -= 16
    pdf.drawString(left, y, f"Locked At: {schema.locked_at.isoformat() if schema.locked_at else '-'}")
    y -= 26

    y = section_title("Scope", y)
    pdf.setFont("Helvetica", 11)
    included_members = ", ".join(str(x) for x in json.loads(schema.included_member_ids_json or "[]")) or "All in scope"
    included_symbols = ", ".join(json.loads(schema.included_symbols_json or "[]")) or "All in scope"
    excluded_trade_ids = ", ".join(str(x) for x in json.loads(schema.excluded_trade_ids_json or "[]")) or "None"

    pdf.drawString(left, y, f"Included Members: {included_members}")
    y -= 16
    pdf.drawString(left, y, f"Included Symbols: {included_symbols}")
    y -= 16
    pdf.drawString(left, y, f"Excluded Trade IDs: {excluded_trade_ids}")
    y -= 24

    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(left, y, "Methodology Notes:")
    y -= 16
    pdf.setFont("Helvetica", 11)
    y = draw_pdf_wrapped_text(
        pdf,
        schema.methodology_notes or "-",
        left,
        y,
        max_width=right - left,
        line_height=14,
    )
    y -= 12

    y = section_title("Leaderboard", y)
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(left, y, "Rank")
    pdf.drawString(left + 50, y, "Member")
    pdf.drawString(left + 220, y, "Net PnL")
    pdf.drawString(left + 320, y, "Win Rate")
    pdf.drawString(left + 420, y, "Profit Factor")
    y -= 14

    pdf.setFont("Helvetica", 10)
    for row in leaderboard[:10]:
        y = ensure_pdf_space(pdf, y, 100)
        pdf.drawString(left, y, str(row["rank"]))
        pdf.drawString(left + 50, y, str(row["member"]))
        pdf.drawString(left + 220, y, str(row["net_pnl"]))
        pdf.drawString(left + 320, y, str(row["win_rate"]))
        pdf.drawString(left + 420, y, str(row["profit_factor"]))
        y -= 14

    y -= 16
    y = section_title("Trade Evidence Snapshot", y)

    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(left, y, "#")
    pdf.drawString(left + 25, y, "Trade ID")
    pdf.drawString(left + 90, y, "Opened")
    pdf.drawString(left + 230, y, "Symbol")
    pdf.drawString(left + 300, y, "PnL")
    pdf.drawString(left + 380, y, "Cumulative")
    y -= 14

    pdf.setFont("Helvetica", 10)
    evidence_rows = build_trade_evidence(filtered_trades)
    for row in evidence_rows[:20]:
        y = ensure_pdf_space(pdf, y, 100)
        pdf.drawString(left, y, str(row["index"]))
        pdf.drawString(left + 25, y, str(row["trade_id"]))
        pdf.drawString(left + 90, y, str(row["opened_at"])[:19])
        pdf.drawString(left + 230, y, str(row["symbol"]))
        pdf.drawString(left + 300, y, str(row["net_pnl"]))
        pdf.drawString(left + 380, y, str(row["cumulative_pnl"]))
        y -= 14

    y -= 20
    pdf.setFont("Helvetica-Oblique", 9)
    pdf.drawString(
        left,
        y,
        "This report was generated by Trading Truth Layer from the canonical trade ledger and lifecycle-governed claim state.",
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


def require_workspace_operator_or_owner(workspace_id: int, current_user: User, db: Session):
    membership = (
        db.query(WorkspaceMembership)
        .filter(
            WorkspaceMembership.workspace_id == workspace_id,
            WorkspaceMembership.user_id == current_user.id,
        )
        .first()
    )

    if not membership:
        raise HTTPException(status_code=403, detail="User is not a member of this workspace")

    if membership.role not in {"owner", "operator"}:
        raise HTTPException(status_code=403, detail="Operator or owner role required for this workspace")

    return membership


def require_workspace_member(workspace_id: int, current_user: User, db: Session):
    membership = (
        db.query(WorkspaceMembership)
        .filter(
            WorkspaceMembership.workspace_id == workspace_id,
            WorkspaceMembership.user_id == current_user.id,
        )
        .first()
    )

    if not membership:
        raise HTTPException(status_code=403, detail="User is not a member of this workspace")

    return membership


@router.get("/claim-schemas/latest")
def get_latest_claim_schema(db: Session = Depends(get_db)):
    schema = db.query(ClaimSchema).order_by(ClaimSchema.id.desc()).first()
    if not schema:
        raise HTTPException(status_code=404, detail="No claim schemas found")
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
def get_claim_versions(claim_schema_id: int, db: Session = Depends(get_db)):
    schema = db.query(ClaimSchema).filter(ClaimSchema.id == claim_schema_id).first()
    if not schema:
        raise HTTPException(status_code=404, detail="Claim schema not found")

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
def get_claim_schema(claim_schema_id: int, db: Session = Depends(get_db)):
    schema = db.query(ClaimSchema).filter(ClaimSchema.id == claim_schema_id).first()
    if not schema:
        raise HTTPException(status_code=404, detail="Claim schema not found")
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

    require_workspace_operator_or_owner(schema.workspace_id, current_user, db)

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

    require_workspace_operator_or_owner(schema.workspace_id, current_user, db)

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
def get_claim_schema_preview(claim_schema_id: int, db: Session = Depends(get_db)):
    schema = db.query(ClaimSchema).filter(ClaimSchema.id == claim_schema_id).first()
    if not schema:
        raise HTTPException(status_code=404, detail="Claim schema not found")

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
def get_claim_equity_curve(claim_schema_id: int, db: Session = Depends(get_db)):
    schema = db.query(ClaimSchema).filter(ClaimSchema.id == claim_schema_id).first()
    if not schema:
        raise HTTPException(status_code=404, detail="Claim schema not found")

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
):
    schema = db.query(ClaimSchema).filter(ClaimSchema.id == claim_schema_id).first()
    if not schema:
        raise HTTPException(status_code=404, detail="Claim schema not found")

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
def get_evidence_pack(claim_schema_id: int, db: Session = Depends(get_db)):
    schema = db.query(ClaimSchema).filter(ClaimSchema.id == claim_schema_id).first()
    if not schema:
        raise HTTPException(status_code=404, detail="Claim schema not found")

    return build_evidence_pack_payload(schema, db)


@router.get("/claim-schemas/{claim_schema_id}/evidence-pack/download")
def download_evidence_pack(claim_schema_id: int, db: Session = Depends(get_db)):
    schema = db.query(ClaimSchema).filter(ClaimSchema.id == claim_schema_id).first()
    if not schema:
        raise HTTPException(status_code=404, detail="Claim schema not found")

    payload = build_evidence_pack_payload(schema, db)
    filename = f"evidence_pack_claim_{schema.id}_{compute_claim_hash(schema)[:12]}.json"

    return JSONResponse(
        content=payload,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/claim-schemas/{claim_schema_id}/evidence-bundle")
def get_evidence_bundle(claim_schema_id: int, db: Session = Depends(get_db)):
    schema = db.query(ClaimSchema).filter(ClaimSchema.id == claim_schema_id).first()
    if not schema:
        raise HTTPException(status_code=404, detail="Claim schema not found")

    return build_evidence_bundle_payload(schema, db)


@router.get("/claim-schemas/{claim_schema_id}/evidence-bundle/download")
def download_evidence_bundle(claim_schema_id: int, db: Session = Depends(get_db)):
    schema = db.query(ClaimSchema).filter(ClaimSchema.id == claim_schema_id).first()
    if not schema:
        raise HTTPException(status_code=404, detail="Claim schema not found")

    zip_buffer, filename = build_evidence_bundle_zip_bytes(schema, db)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
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
def verify_claim_schema_integrity(claim_schema_id: int, db: Session = Depends(get_db)):
    schema = db.query(ClaimSchema).filter(ClaimSchema.id == claim_schema_id).first()
    if not schema:
        raise HTTPException(status_code=404, detail="Claim schema not found")

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

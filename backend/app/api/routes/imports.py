from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_workspace_member
from app.models.user import User

from app.core.db import get_db
from app.models.import_batch import ImportBatch
from app.models.workspace import Workspace
from app.services.trade_import import (
    build_import_job_payload,
    build_stream_event_payload,
    parse_rows_by_source,
    process_import_rows,
)

from app.services.import_preview_service import (
    build_import_preview,
    create_import_preview_session,
    get_import_preview_session,
    mark_preview_session_confirmed,
    mark_preview_session_rejected,
)
from app.services.ingestion_service import (
    import_broker_trades,
    import_csv_trades,
    persist_runtime_trade_rows,
)

router = APIRouter()

WEBHOOK_ALLOWED_SOURCES = {"csv", "mt5", "ibkr", "custom", "webhook"}


def _normalize_webhook_source(source_type: str | None) -> str:
    normalized = str(source_type or "webhook").strip().lower()
    if normalized == "custom":
        return "webhook"
    return normalized


def _adapt_webhook_trade(raw_trade: dict, source_type: str) -> dict:
    return {
        "symbol": raw_trade.get("symbol") or raw_trade.get("ticker") or raw_trade.get("instrument"),
        "side": raw_trade.get("side") or raw_trade.get("action") or raw_trade.get("type"),
        "quantity": raw_trade.get("quantity") or raw_trade.get("qty") or raw_trade.get("size"),
        "entry_price": raw_trade.get("entry_price") or raw_trade.get("price") or raw_trade.get("fill_price"),
        "exit_price": raw_trade.get("exit_price"),
        "net_pnl": raw_trade.get("net_pnl") or raw_trade.get("pnl") or raw_trade.get("profit"),
        "opened_at": raw_trade.get("opened_at") or raw_trade.get("timestamp") or raw_trade.get("time"),
        "closed_at": raw_trade.get("closed_at"),
        "member_id": raw_trade.get("member_id"),
        "currency": raw_trade.get("currency"),
        "strategy_tag": raw_trade.get("strategy_tag"),
        "source_system": raw_trade.get("source_system") or source_type.upper(),
        "external_id": raw_trade.get("external_id") or raw_trade.get("id") or raw_trade.get("trade_id"),
    }


def normalize_broker_row(row: dict, source_type: str) -> dict:

    normalized_row = {
        normalize_key(str(k).strip()): (
            str(v).strip()
            if v is not None
            else None
        )
        for k, v in row.items()
    }

    def get(*keys):
        for k in keys:
            for actual_key in normalized_row.keys():
                if actual_key == normalize_key(k):
                    val = normalized_row[actual_key]
                    if val not in (None, ""):
                        return val
        return None

    # SYMBOL
    symbol = get("symbol", "item", "instrument")

    # SIDE
    side = get("side", "type", "action")

    if isinstance(side, str):
        side = side.upper()
        if side == "BUY":
            side = "BUY"
        elif side == "SELL":
            side = "SELL"

    # IBKR fallback (no side)
    if side is None:
        qty = get("quantity", "Quantity", "Size", "qty", "Qty")
        try:
            qty = float(qty)
            side = "BUY" if qty > 0 else "SELL"
        except:
            side = None

    # QUANTITY
    quantity = get(
        "quantity",
        "qty",
        "size",
        "volume",
        "shares",
    )
    try:
        quantity = float(quantity) if quantity is not None else None
    except:
        quantity = None

    # TIME PARSING FIX (CRITICAL)
    opened_at = get(

        # canonical
        "opened_at",

        # mt5
        "time",
        "open_time",
        "open_time_msc",
        "time_msc",

        # ibkr
        "date_time",

        # generic
        "datetime",
        "timestamp",
        "date",
    )

    closed_at = get(
        "close_time",
        "closed_at",
        "closetime",
        "close_time_msc",

        # MT5
        "close time",

        # GENERIC
        "closed",
        "exit_time",
    )

    # Normalize MT5 datetime format
    def parse_dt(val):

        if not val:
            return None

        try:
            val = str(val).strip()

            # MT5
            # 2026.05.01 14:30:00
            if "." in val and ":" in val:
                val = val.replace(".", "-")

            # IBKR
            # 2026-05-01T14:30:00
            val = val.replace("T", " ")

            # normalize slash dates
            val = val.replace("/", "-")

            return val

        except Exception:
            return None

    return {
        "symbol": symbol,
        "side": side,
        "quantity": quantity,
        "entry_price": get(
            "entry_price",
            "open_price",
            "price",
            "tradeprice",
            "fill_price",
        ),
        "exit_price": get("exit_price", "close_price", "ClosePrice"),
        "net_pnl": get(
            "net_pnl",
            "profit",
            "realizedpnl",
            "realized_p&l",
            "pnl",
        ),
        "opened_at": parse_dt(opened_at),
        "closed_at": parse_dt(closed_at),
    }


def normalize_key(value):

    value = str(value).strip().lower()

    return (
        value
        .replace(" ", "_")
        .replace("-", "_")
        .replace("/", "_")
        .replace(".", "_")
        .replace("(", "")
        .replace(")", "")
    )


def _extract_webhook_trade_rows(payload: dict) -> list[dict]:
    trades = payload.get("trades")

    if isinstance(trades, list):
        return trades

    trade = payload.get("trade")
    if isinstance(trade, dict):
        return [trade]

    return []


# -----------------------------
# HELPERS
# -----------------------------
def serialize_import_batch(row: ImportBatch) -> Dict[str, Any]:
    return {
        "id": row.id,
        "workspace_id": row.workspace_id,
        "filename": row.filename,
        "source_type": row.source_type,
        "status": getattr(row, "status", "completed"),
        "rows_received": row.rows_received,
        "rows_imported": row.rows_imported,
        "rows_rejected": row.rows_rejected,
        "rows_skipped_duplicates": row.rows_skipped_duplicates,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


def create_batch_record(
    *,
    db: Session,
    workspace_id: int,
    filename: str,
    source_type: str,
    rows_received: int,
    rows_imported: int,
    rows_rejected: int,
    rows_skipped_duplicates: int,
    status: str,
) -> ImportBatch:
    batch = ImportBatch(
        workspace_id=workspace_id,
        filename=filename,
        source_type=source_type,
        rows_received=rows_received,
        rows_imported=rows_imported,
        rows_rejected=rows_rejected,
        rows_skipped_duplicates=rows_skipped_duplicates,
        created_at=datetime.utcnow(),
    )

    if hasattr(batch, "status"):
        batch.status = status

    db.add(batch)
    db.commit()
    db.refresh(batch)
    return batch


# -----------------------------
# LIST IMPORT BATCHES
# -----------------------------
@router.get("/workspaces/{workspace_id}/imports")
def list_import_batches(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_workspace_member(workspace_id, current_user, db)
    rows = (
        db.query(ImportBatch)
        .filter(ImportBatch.workspace_id == workspace_id)
        .order_by(ImportBatch.id.desc())
        .all()
    )

    return [serialize_import_batch(row) for row in rows]


# -----------------------------
# CREATE IMPORT BATCH (ENTRY POINT)
# -----------------------------
@router.post("/workspaces/{workspace_id}/imports")
def create_import_batch(
    workspace_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_workspace_member(workspace_id, current_user, db)
    """
    Canonical ingestion entry point.
    All source types should eventually route through this import control layer.
    """

    filename = payload.get("filename", "manual_import")
    source_type = payload.get("source_type", "manual")

    batch = create_batch_record(
        db=db,
        workspace_id=workspace_id,
        filename=filename,
        source_type=source_type,
        rows_received=payload.get("rows_received", 0),
        rows_imported=0,
        rows_rejected=0,
        rows_skipped_duplicates=0,
        status="processing",
    )

    return {
        "id": batch.id,
        "status": getattr(batch, "status", "processing"),
        "message": "Import batch created",
    }


# -----------------------------
# WEBHOOK INGESTION
# -----------------------------
@router.post("/webhooks/trades")
def ingest_webhook_trades(
    payload: dict,
    db: Session = Depends(get_db),
):
    workspace_id_raw = payload.get("workspace_id")
    try:
        workspace_id = int(workspace_id_raw)
    except Exception:
        raise HTTPException(status_code=400, detail="Missing or invalid workspace_id")

    source_type = _normalize_webhook_source(payload.get("source_type"))

    if source_type not in WEBHOOK_ALLOWED_SOURCES:
        raise HTTPException(status_code=400, detail=f"Unsupported source type: {source_type}")

    raw_trades = _extract_webhook_trade_rows(payload)
    if not raw_trades:
        raise HTTPException(status_code=400, detail="Missing trade payload")

    adapted_rows = [
        _adapt_webhook_trade(raw_trade, source_type)
        for raw_trade in raw_trades
        if isinstance(raw_trade, dict)
    ]

    if not adapted_rows:
        raise HTTPException(status_code=400, detail="No valid trade objects supplied")

    filename = str(payload.get("filename") or f"{source_type}_webhook")

    # 🔒 TRADE LIMIT ENFORCEMENT (WEBHOOK)
    from app.models.workspace import Workspace

    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    from app.services.usage_service import get_workspace_usage

    from app.services.entitlements import enforce_trade_import_allowed

    incoming_trade_count = len(adapted_rows)

    enforce_trade_import_allowed(
        workspace_id=workspace_id,
        db=db,
        incoming_count=incoming_trade_count,
    )

    result = persist_runtime_trade_rows(
        db=db,
        workspace_id=workspace_id,
        filename=filename,
        source_type=source_type,
        normalized_rows=adapted_rows,
        actor_user_id=None,
        audit_source="imports.ingest_webhook_trades",
    )

    # IMMUTABLE GOVERNANCE CONSUMPTION
    rows_imported = int(
        result.get("rows_imported", 0)
    )

    workspace.trades_consumed_count = (
        (workspace.trades_consumed_count or 0)
        + rows_imported
    )

    db.add(workspace)
    db.commit()
    db.refresh(workspace)

    return {
        **result,
        "message": "Webhook trades ingested",
    }

# -----------------------------
# GENERIC FILE INGESTION
# -----------------------------
@router.post("/workspaces/{workspace_id}/imports/upload")
async def upload_import_file(
    workspace_id: int,
    file: UploadFile = File(...),
    source_type: str = Form("csv"),
    mode: str = Form("manual"),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    allowed_sources = {"csv", "mt5", "ibkr"}
    normalized_source = str(source_type or "").strip().lower()

    if normalized_source not in allowed_sources:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported source type: {source_type}",
        )

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV-like file uploads are supported at this stage",
        )

    file_bytes = await file.read()

    from app.services.trade_import import parse_rows_by_source

    rows = parse_rows_by_source(normalized_source, file_bytes)

    print("DEBUG RAW ROW:", rows[0])

    # ✅ Normalize BEFORE ingestion
    normalized_rows = [
        normalize_broker_row(r, normalized_source)
        for r in rows
        if isinstance(r, dict)
    ]

    if not normalized_rows:
        raise HTTPException(
            status_code=400,
            detail="No valid trade rows detected in uploaded file",
        )

    print("DEBUG NORMALIZED ROW:", normalized_rows[0])

    # 🔒 TRADE LIMIT ENFORCEMENT (FILE IMPORT)
    from app.models.workspace import Workspace

    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    from app.services.usage_service import get_workspace_usage

    incoming_trade_count = len(normalized_rows)

    from app.services.entitlements import enforce_trade_import_allowed

    enforce_trade_import_allowed(
        workspace_id=workspace_id,
        db=db,
        incoming_count=incoming_trade_count,
    )

    # Persist accepted rows into Trade via existing ingestion service
    try:
        result = persist_runtime_trade_rows(
            db=db,
            workspace_id=workspace_id,
            filename=file.filename,
            source_type=normalized_source,
            normalized_rows=normalized_rows,
            actor_user_id=None,
            audit_source="imports.upload_import_file",
        )

        # IMMUTABLE GOVERNANCE CONSUMPTION
        rows_imported = int(
            result.get("rows_imported", 0)
        )

        workspace.trades_consumed_count = (
            (workspace.trades_consumed_count or 0)
            + rows_imported
        )

        db.add(workspace)
        db.commit()
        db.refresh(workspace)

    except Exception as e:
        print("IMPORT FAILURE:", str(e))

        raise HTTPException(
            status_code=500,
            detail=f"Import processing failed: {str(e)}"
        )

    return {
        **result,
        "mode": mode,
        "job_payload": build_import_job_payload(
            workspace_id=workspace_id,
            source_type=normalized_source,
            filename=file.filename,
            mode=mode,
        ),
        "message": f"{normalized_source.upper()} import processed",
    }


# -----------------------------
# IMPORT PREVIEW WORKFLOW
# -----------------------------
@router.post(
    "/workspaces/{workspace_id}/imports/preview"
)
async def preview_import_file(
    workspace_id: int,
    file: UploadFile = File(...),
    source_type: str = Form("csv"),
    db: Session = Depends(get_db),
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Missing filename",
        )

    allowed_sources = {
        "csv",
        "mt5",
        "ibkr",
    }

    normalized_source = (
        str(source_type or "")
        .strip()
        .lower()
    )

    if normalized_source not in allowed_sources:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported source type: "
                f"{source_type}"
            ),
        )

    file_bytes = await file.read()

    preview = build_import_preview(
        workspace_id=workspace_id,
        source_type=normalized_source,
        file_bytes=file_bytes,
    )

    preview["filename"] = file.filename

    session = (
        create_import_preview_session(
            db=db,
            workspace_id=workspace_id,
            source_type=normalized_source,
            filename=file.filename,
            preview_payload=preview,
        )
    )

    return {
        "preview_session_id": session.id,
        "status": session.status,
        "preview": preview,
        "message": (
            "Import preview generated"
        ),
    }


@router.post(
    "/workspaces/{workspace_id}/imports/preview/{preview_session_id}/confirm"
)
def confirm_import_preview(
    workspace_id: int,
    preview_session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    require_workspace_member(
        workspace_id,
        current_user,
        db,
    )

    preview_session = (
        get_import_preview_session(
            db,
            preview_session_id,
        )
    )

    if not preview_session:
        raise HTTPException(
            status_code=404,
            detail="Preview session not found",
        )

    if (
        preview_session.workspace_id
        != workspace_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Preview session does not belong to workspace",
        )

    if preview_session.status != "pending_confirmation":
        raise HTTPException(
            status_code=400,
            detail="Preview session already finalized",
        )

    import json

    payload = json.loads(
        preview_session.preview_payload_json
    )

    normalized_rows = payload.get(
        "normalized_preview",
        [],
    )

    if not normalized_rows:
        raise HTTPException(
            status_code=400,
            detail="No normalized trades available for persistence",
        )

    result = persist_runtime_trade_rows(
        db=db,
        workspace_id=workspace_id,
        filename=preview_session.filename,
        source_type=preview_session.source_type,
        normalized_rows=normalized_rows,
        actor_user_id=current_user.id,
        audit_source="imports.confirm_preview",
    )

    mark_preview_session_confirmed(
        db=db,
        preview_session=preview_session,
    )

    return {
        "preview_session_id": (
            preview_session.id
        ),
        "status": "confirmed",
        "rows_imported": result.get(
            "rows_imported",
            0,
        ),
        "rows_rejected": result.get(
            "rows_rejected",
            0,
        ),
        "rows_duplicates": result.get(
            "rows_skipped_duplicates",
            0,
        ),
        "message": (
            "Import preview confirmed and persisted"
        ),
    }


# -----------------------------
# CSV INGESTION (BACKWARD COMPAT)
# -----------------------------
@router.post("/workspaces/{workspace_id}/imports/csv")
async def upload_csv_import(
    workspace_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    file_bytes = await file.read()
    rows = parse_rows_by_source("csv", file_bytes)
    result = process_import_rows(rows, source_type="csv")

    batch = create_batch_record(
        db=db,
        workspace_id=workspace_id,
        filename=file.filename,
        source_type="csv",
        rows_received=result["stats"]["received"],
        rows_imported=result["stats"]["accepted"],
        rows_rejected=result["stats"]["rejected"],
        rows_skipped_duplicates=result["stats"]["duplicates"],
        status="completed",
    )

    return {
        **serialize_import_batch(batch),
        "normalized_preview": result["normalized"][:20],
        "rejected_preview": result["rejected"][:20],
        "duplicate_preview": result["duplicates"][:20],
        "job_payload": build_import_job_payload(
            workspace_id=workspace_id,
            source_type="csv",
            filename=file.filename,
            mode="manual",
        ),
        "message": "CSV import processed",
    }


# -----------------------------
# AUTO-IMPORT FOUNDATION
# -----------------------------
@router.post("/workspaces/{workspace_id}/imports/auto-enable")
def enable_auto_import(
    workspace_id: int,
    payload: dict | None = None,
):
    cadence = "daily"

    if payload and payload.get("cadence"):
        cadence = payload["cadence"]

    return {
        "workspace_id": workspace_id,
        "enabled": True,
        "cadence": cadence,
        "mode": "auto",
        "message": "Auto-import enabled",
    }


@router.post("/workspaces/{workspace_id}/imports/auto")
def configure_auto_import(
    workspace_id: int,
    payload: dict,
):
    source_type = str(payload.get("source_type", "csv")).strip().lower()
    enabled = bool(payload.get("enabled", True))
    cadence = str(payload.get("cadence", "hourly")).strip().lower()

    if source_type not in {"csv", "mt5", "ibkr"}:
        raise HTTPException(status_code=400, detail=f"Unsupported source type: {source_type}")

    return {
        "workspace_id": workspace_id,
        "source_type": source_type,
        "enabled": enabled,
        "cadence": cadence,
        "job_payload": build_import_job_payload(
            workspace_id=workspace_id,
            source_type=source_type,
            filename=payload.get("filename"),
            mode="auto",
        ),
        "message": "Auto-import configuration captured (foundation only)",
    }


# -----------------------------
# REAL-TIME INGESTION FOUNDATION
# -----------------------------
@router.post("/workspaces/{workspace_id}/imports/stream-enable")
def enable_stream_import(
    workspace_id: int,
    payload: dict | None = None,
):
    return {
        "workspace_id": workspace_id,
        "enabled": True,
        "mode": "realtime",
        "message": "Real-time ingestion enabled",
    }


@router.post("/workspaces/{workspace_id}/imports/stream-event")
def ingest_stream_event(
    workspace_id: int,
    payload: dict,
    db: Session = Depends(get_db),
):
    source_type = _normalize_webhook_source(payload.get("source_type", "ibkr"))
    trade = payload.get("trade")

    if source_type not in WEBHOOK_ALLOWED_SOURCES:
        raise HTTPException(status_code=400, detail=f"Unsupported source type: {source_type}")

    if not isinstance(trade, dict):
        raise HTTPException(status_code=400, detail="Missing trade payload")

    adapted_trade = _adapt_webhook_trade(trade, source_type)
    event_payload = build_stream_event_payload(
        workspace_id=workspace_id,
        source_type=source_type,
        trade=adapted_trade,
    )

    from app.services.usage_service import get_workspace_usage
    from app.services.entitlements import enforce_trade_import_allowed
    from app.models.workspace import Workspace

    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    incoming_trade_count = 1  # single event

    enforce_trade_import_allowed(
        workspace_id=workspace_id,
        db=db,
        incoming_count=incoming_trade_count,
    )

    result = persist_runtime_trade_rows(
        db=db,
        workspace_id=workspace_id,
        filename=f"{source_type}_stream_event",
        source_type=source_type,
        normalized_rows=[adapted_trade],
        actor_user_id=None,
        audit_source="imports.ingest_stream_event",
    )

    # IMMUTABLE GOVERNANCE CONSUMPTION
    rows_imported = int(
        result.get("rows_imported", 0)
    )

    workspace.trades_consumed_count = (
        (workspace.trades_consumed_count or 0)
        + rows_imported
    )

    db.add(workspace)
    db.commit()
    db.refresh(workspace)

    return {
        **result,
        "workspace_id": workspace_id,
        "source_type": source_type,
        "event": event_payload,
        "message": "Real-time ingestion event processed",
    }


# -----------------------------
# GET SINGLE IMPORT BATCH
# -----------------------------
@router.get("/imports/{import_id}")
def get_import_batch(import_id: int, db: Session = Depends(get_db)):
    batch = db.query(ImportBatch).filter(ImportBatch.id == import_id).first()

    if not batch:
        raise HTTPException(status_code=404, detail="Import batch not found")

    return serialize_import_batch(batch)


@router.post(
    "/workspaces/{workspace_id}/imports/confirm/{preview_session_id}"
)
def confirm_import_preview(
    workspace_id: int,
    preview_session_id: int,
    db: Session = Depends(get_db),
):

    import json

    preview_session = (
        get_import_preview_session(
            db,
            preview_session_id,
        )
    )

    if not preview_session:
        raise HTTPException(
            status_code=404,
            detail="Preview session not found",
        )

    if (
        preview_session.status
        == "confirmed"
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Preview already confirmed"
            ),
        )

    payload = json.loads(
        preview_session.preview_payload_json
    )

    normalized_rows = payload.get(
        "normalized_preview",
        [],
    )

    result = persist_runtime_trade_rows(
        db=db,
        workspace_id=workspace_id,
        filename=preview_session.filename,
        source_type=preview_session.source_type,
        normalized_rows=normalized_rows,
        actor_user_id=None,
        audit_source="preview_confirmation",
    )

    mark_preview_session_confirmed(
        db=db,
        preview_session=preview_session,
    )

    return {
        **result,
        "preview_session_id": (
            preview_session.id
        ),
        "message": (
            "Import confirmed and persisted"
        ),
    }


@router.post(
    "/workspaces/{workspace_id}/imports/reject/{preview_session_id}"
)
def reject_import_preview(
    workspace_id: int,
    preview_session_id: int,
    db: Session = Depends(get_db),
):

    preview_session = (
        get_import_preview_session(
            db,
            preview_session_id,
        )
    )

    if not preview_session:
        raise HTTPException(
            status_code=404,
            detail="Preview session not found",
        )

    mark_preview_session_rejected(
        db=db,
        preview_session=preview_session,
    )

    return {
        "preview_session_id": (
            preview_session.id
        ),
        "status": "rejected",
        "message": (
            "Import preview rejected"
        ),
    }
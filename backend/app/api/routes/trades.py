from datetime import datetime
import csv
import hashlib
import io
import json

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_workspace_member
from app.core.db import get_db
from app.models.claim_schema import ClaimSchema
from app.models.trade import Trade
from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_membership import WorkspaceMembership
from app.services.entitlements import enforce_trade_import_allowed
from app.services.ingestion_service import import_csv_trades
from app.services.entitlements import enforce_claim_creation_allowed

router = APIRouter()


class TradeCreate(BaseModel):
    member_id: int
    source_type: str = "manual"
    symbol: str
    side: str
    opened_at: datetime
    closed_at: datetime | None = None
    entry_price: float
    exit_price: float | None = None
    quantity: float
    fees: float = 0
    swap: float = 0
    currency: str = "USD"
    net_pnl: float | None = None
    strategy_tag: str | None = None
    source_system: str | None = None


class TradeUpdate(BaseModel):
    member_id: int
    symbol: str
    side: str
    opened_at: datetime
    closed_at: datetime | None = None
    entry_price: float
    exit_price: float | None = None
    quantity: float
    currency: str = "USD"
    net_pnl: float | None = None
    strategy_tag: str | None = None
    source_system: str | None = None


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
        raise HTTPException(
            status_code=403,
            detail="Operator or owner role required for this workspace",
        )

    return membership


def get_workspace_or_404(workspace_id: int, db: Session) -> Workspace:
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace


def increment_workspace_trades_consumed(
    workspace: Workspace,
    db: Session,
    additional_trades: int,
) -> None:
    increment = max(int(additional_trades), 0)
    if increment <= 0:
        return

    current_value = getattr(workspace, "trades_consumed_count", 0) or 0
    workspace.trades_consumed_count = int(current_value) + increment
    db.add(workspace)


def estimate_csv_row_count(content: bytes) -> int:
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    reader = csv.reader(io.StringIO(text))
    rows = list(reader)

    if not rows or len(rows) == 1:
        return 0

    return max(len(rows) - 1, 0)


def normalize_optional_text(value: str | None) -> str | None:
    cleaned = (value or "").strip()
    return cleaned or None


def build_trade_fingerprint(
    workspace_id: int,
    member_id: int,
    symbol: str,
    side: str,
    opened_at: datetime,
    entry_price: float,
    quantity: float,
) -> str:
    raw = "|".join(
        [
            str(workspace_id),
            str(member_id),
            symbol.strip().upper(),
            side.strip().upper(),
            opened_at.isoformat(),
            f"{entry_price:.8f}",
            f"{quantity:.8f}",
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def build_trade_fingerprint_from_trade(trade: Trade) -> str:
    if trade.trade_fingerprint:
        return trade.trade_fingerprint

    return build_trade_fingerprint(
        workspace_id=trade.workspace_id,
        member_id=trade.member_id,
        symbol=trade.symbol,
        side=trade.side,
        opened_at=trade.opened_at,
        entry_price=trade.entry_price,
        quantity=trade.quantity,
    )


def get_locked_claims(db: Session, workspace_id: int) -> list[ClaimSchema]:
    return (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id == workspace_id,
            ClaimSchema.status == "locked",
        )
        .all()
    )


def build_locked_trade_protection_maps(
    db: Session,
    workspace_id: int,
) -> tuple[dict[str, ClaimSchema], dict[int, ClaimSchema]]:
    locked_claims = get_locked_claims(db, workspace_id)
    locked_trade_ids: set[int] = set()

    for claim in locked_claims:
        for raw_trade_id in json.loads(claim.locked_trade_ids_json or "[]"):
            try:
                locked_trade_ids.add(int(raw_trade_id))
            except Exception:
                continue

    if not locked_trade_ids:
        return {}, {}

    locked_trades = (
        db.query(Trade)
        .filter(
            Trade.workspace_id == workspace_id,
            Trade.id.in_(locked_trade_ids),
        )
        .all()
    )

    trade_by_id = {trade.id: trade for trade in locked_trades}
    fingerprint_to_claim: dict[str, ClaimSchema] = {}
    trade_id_to_claim: dict[int, ClaimSchema] = {}

    for claim in locked_claims:
        claim_trade_ids = json.loads(claim.locked_trade_ids_json or "[]")

        for raw_trade_id in claim_trade_ids:
            try:
                trade_id = int(raw_trade_id)
            except Exception:
                continue

            trade = trade_by_id.get(trade_id)
            if not trade:
                continue

            trade_id_to_claim[trade_id] = claim

            fingerprint = build_trade_fingerprint_from_trade(trade)
            if fingerprint not in fingerprint_to_claim:
                fingerprint_to_claim[fingerprint] = claim

    return fingerprint_to_claim, trade_id_to_claim


def find_locked_claim_conflict_for_fingerprint(
    fingerprint_to_claim: dict[str, ClaimSchema],
    fingerprint: str,
) -> ClaimSchema | None:
    return fingerprint_to_claim.get(fingerprint)


def find_locked_claim_protecting_trade_id(
    trade_id_to_claim: dict[int, ClaimSchema],
    trade_id: int,
) -> ClaimSchema | None:
    return trade_id_to_claim.get(trade_id)


def compute_trade_net_pnl(
    side: str,
    entry_price: float,
    exit_price: float | None,
    quantity: float,
    fallback_net_pnl: float | None = None,
) -> float | None:
    if exit_price is None:
        return fallback_net_pnl

    normalized_side = side.strip().upper()

    if normalized_side == "BUY":
        return (exit_price - entry_price) * quantity

    if normalized_side == "SELL":
        return (entry_price - exit_price) * quantity

    return fallback_net_pnl


def serialize_trade(trade: Trade):
    return {
        "id": trade.id,
        "workspace_id": trade.workspace_id,
        "member_id": trade.member_id,
        "symbol": trade.symbol,
        "side": trade.side,
        "opened_at": trade.opened_at.isoformat(),
        "closed_at": trade.closed_at.isoformat() if trade.closed_at else None,
        "entry_price": trade.entry_price,
        "exit_price": trade.exit_price,
        "quantity": trade.quantity,
        "net_pnl": trade.net_pnl,
        "currency": trade.currency,
        "strategy_tag": trade.strategy_tag,
        "source_system": trade.source_system,
    }


@router.get("/workspaces/{workspace_id}/trades")
def list_trades(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_workspace_member(workspace_id, current_user, db)

    trades = (
        db.query(Trade)
        .filter(Trade.workspace_id == workspace_id)
        .order_by(Trade.id.asc())
        .all()
    )
    return [serialize_trade(t) for t in trades]


@router.post("/workspaces/{workspace_id}/trades")
def create_trade(
    workspace_id: int,
    payload: TradeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    require_workspace_operator_or_owner(workspace_id, current_user, db)
    workspace = get_workspace_or_404(workspace_id, db)
    
    enforce_trade_import_allowed(workspace_id, db, additional_trades=1)

    normalized_symbol = payload.symbol.strip().upper()
    normalized_side = payload.side.strip().upper()
    normalized_currency = payload.currency.strip().upper()
    normalized_strategy_tag = normalize_optional_text(payload.strategy_tag)
    normalized_source_system = normalize_optional_text(payload.source_system) or "MANUAL"

    fingerprint = build_trade_fingerprint(
        workspace_id=workspace_id,
        member_id=payload.member_id,
        symbol=normalized_symbol,
        side=normalized_side,
        opened_at=payload.opened_at,
        entry_price=payload.entry_price,
        quantity=payload.quantity,
    )

    computed_net_pnl = compute_trade_net_pnl(
        side=normalized_side,
        entry_price=payload.entry_price,
        exit_price=payload.exit_price,
        quantity=payload.quantity,
        fallback_net_pnl=payload.net_pnl,
    )

    fingerprint_to_claim, _ = build_locked_trade_protection_maps(db, workspace_id)
    conflict = find_locked_claim_conflict_for_fingerprint(
        fingerprint_to_claim=fingerprint_to_claim,
        fingerprint=fingerprint,
    )

    if conflict:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Trade conflicts with locked claim {conflict.id}. "
                "This exact trade evidence is already protected by a locked claim."
            ),
        )

    existing = (
        db.query(Trade)
        .filter(Trade.workspace_id == workspace_id, Trade.trade_fingerprint == fingerprint)
        .first()
    )

    if existing:
        result = serialize_trade(existing)
        result["duplicate_skipped"] = True
        return result

    trade = Trade(
        workspace_id=workspace_id,
        member_id=payload.member_id,
        symbol=normalized_symbol,
        side=normalized_side,
        opened_at=payload.opened_at,
        closed_at=payload.closed_at,
        entry_price=payload.entry_price,
        exit_price=payload.exit_price,
        quantity=payload.quantity,
        net_pnl=computed_net_pnl,
        currency=normalized_currency,
        strategy_tag=normalized_strategy_tag,
        source_system=normalized_source_system,
        trade_fingerprint=fingerprint,
    )

    db.add(trade)
    increment_workspace_trades_consumed(workspace, db, 1)
    db.commit()
    db.refresh(trade)
    db.refresh(workspace)

    result = serialize_trade(trade)
    result["duplicate_skipped"] = False
    result["trades_consumed_count"] = workspace.trades_consumed_count
    return result


@router.patch("/workspaces/{workspace_id}/trades/{trade_id}")
def update_trade(
    workspace_id: int,
    trade_id: int,
    payload: TradeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_workspace_operator_or_owner(workspace_id, current_user, db)

    trade = (
        db.query(Trade)
        .filter(Trade.workspace_id == workspace_id, Trade.id == trade_id)
        .first()
    )
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")

    fingerprint_to_claim, trade_id_to_claim = build_locked_trade_protection_maps(db, workspace_id)

    protected_claim = find_locked_claim_protecting_trade_id(trade_id_to_claim, trade.id)
    if protected_claim:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Trade {trade.id} is protected by locked claim {protected_claim.id} "
                "and cannot be edited."
            ),
        )

    normalized_symbol = payload.symbol.strip().upper()
    normalized_side = payload.side.strip().upper()
    normalized_currency = payload.currency.strip().upper()
    normalized_strategy_tag = normalize_optional_text(payload.strategy_tag)
    normalized_source_system = normalize_optional_text(payload.source_system) or "MANUAL"

    new_fingerprint = build_trade_fingerprint(
        workspace_id=workspace_id,
        member_id=payload.member_id,
        symbol=normalized_symbol,
        side=normalized_side,
        opened_at=payload.opened_at,
        entry_price=payload.entry_price,
        quantity=payload.quantity,
    )

    new_conflict = find_locked_claim_conflict_for_fingerprint(
        fingerprint_to_claim=fingerprint_to_claim,
        fingerprint=new_fingerprint,
    )
    if new_conflict:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Updated trade would conflict with locked claim {new_conflict.id} "
                "and cannot be saved."
            ),
        )

    existing = (
        db.query(Trade)
        .filter(
            Trade.workspace_id == workspace_id,
            Trade.trade_fingerprint == new_fingerprint,
            Trade.id != trade.id,
        )
        .first()
    )
    if existing:
        result = serialize_trade(existing)
        result["duplicate_skipped"] = True
        return result

    computed_net_pnl = compute_trade_net_pnl(
        side=normalized_side,
        entry_price=payload.entry_price,
        exit_price=payload.exit_price,
        quantity=payload.quantity,
        fallback_net_pnl=payload.net_pnl,
    )

    trade.member_id = payload.member_id
    trade.symbol = normalized_symbol
    trade.side = normalized_side
    trade.opened_at = payload.opened_at
    trade.closed_at = payload.closed_at
    trade.entry_price = payload.entry_price
    trade.exit_price = payload.exit_price
    trade.quantity = payload.quantity
    trade.currency = normalized_currency
    trade.net_pnl = computed_net_pnl
    trade.strategy_tag = normalized_strategy_tag
    trade.source_system = normalized_source_system
    trade.trade_fingerprint = new_fingerprint

    db.commit()
    db.refresh(trade)

    result = serialize_trade(trade)
    result["duplicate_skipped"] = False
    return result


@router.delete("/workspaces/{workspace_id}/trades/{trade_id}")
def delete_trade(
    workspace_id: int,
    trade_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_workspace_operator_or_owner(workspace_id, current_user, db)

    trade = (
        db.query(Trade)
        .filter(Trade.workspace_id == workspace_id, Trade.id == trade_id)
        .first()
    )
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")

    _, trade_id_to_claim = build_locked_trade_protection_maps(db, workspace_id)
    protected_claim = find_locked_claim_protecting_trade_id(trade_id_to_claim, trade.id)
    if protected_claim:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Trade {trade.id} is protected by locked claim {protected_claim.id} "
                "and cannot be deleted."
            ),
        )

    db.delete(trade)
    db.commit()
    return {"status": "deleted", "trade_id": trade_id}


@router.post("/workspaces/{workspace_id}/trades/import-csv")
async def import_trades_csv(
    workspace_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_workspace_operator_or_owner(workspace_id, current_user, db)

    if not file.filename or not file.filename.lower().endswith(".csv"):
        return {
            "workspace_id": workspace_id,
            "filename": file.filename or "",
            "rows_received": 0,
            "rows_imported": 0,
            "rows_rejected": 1,
            "rows_skipped_duplicates": 0,
            "errors": ["Only CSV files are supported"],
        }

    content = await file.read()
    estimated_rows = estimate_csv_row_count(content)

    if estimated_rows <= 0:
        return {
            "workspace_id": workspace_id,
            "filename": file.filename or "",
            "rows_received": 0,
            "rows_imported": 0,
            "rows_rejected": 1,
            "rows_skipped_duplicates": 0,
            "errors": ["CSV file appears empty or has no data rows"],
        }

    enforce_trade_import_allowed(workspace_id, db, additional_trades=estimated_rows)

    try:
        result = import_csv_trades(
            db=db,
            workspace_id=workspace_id,
            filename=file.filename,
            content=content,
            actor_user_id=current_user.id,
        )

        rows_imported = int(result.get("rows_imported", 0) or 0)
        if rows_imported > 0:
            workspace = get_workspace_or_404(workspace_id, db)
            increment_workspace_trades_consumed(workspace, db, rows_imported)
            db.commit()
            db.refresh(workspace)
            result["trades_consumed_count"] = workspace.trades_consumed_count

        return result
    except ValueError as e:
        return {
            "workspace_id": workspace_id,
            "filename": file.filename or "",
            "rows_received": 0,
            "rows_imported": 0,
            "rows_rejected": 1,
            "rows_skipped_duplicates": 0,
            "errors": [str(e)],
        }

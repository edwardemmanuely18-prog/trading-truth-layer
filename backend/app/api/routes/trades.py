from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import hashlib
import json

from app.core.db import get_db
from app.models.trade import Trade
from app.models.claim_schema import ClaimSchema
from app.models.user import User
from app.models.workspace_membership import WorkspaceMembership
from app.api.deps import get_current_user
from app.services.ingestion_service import import_csv_trades

router = APIRouter()


class TradeCreate(BaseModel):
    member_id: int
    source_type: str = "manual"
    symbol: str
    side: str
    opened_at: datetime
    entry_price: float
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
    entry_price: float
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


def parse_period_start(date_str: str | None):
    if not date_str:
        return None
    return datetime.fromisoformat(date_str)


def parse_period_end(date_str: str | None):
    if not date_str:
        return None
    return datetime.fromisoformat(date_str) + timedelta(days=1)


def trade_matches_locked_claim(
    claim: ClaimSchema,
    member_id: int,
    symbol: str,
    opened_at: datetime,
) -> bool:
    included_members = json.loads(claim.included_member_ids_json or "[]")
    included_symbols = [s.upper() for s in json.loads(claim.included_symbols_json or "[]")]

    period_start = parse_period_start(claim.period_start)
    period_end = parse_period_end(claim.period_end)

    if period_start is not None and opened_at < period_start:
        return False

    if period_end is not None and opened_at >= period_end:
        return False

    if included_members and member_id not in included_members:
        return False

    if included_symbols and symbol.upper() not in included_symbols:
        return False

    return True


def find_locked_claim_conflict(
    db: Session,
    workspace_id: int,
    member_id: int,
    symbol: str,
    opened_at: datetime,
):
    locked_claims = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id == workspace_id,
            ClaimSchema.status == "locked",
        )
        .all()
    )

    for claim in locked_claims:
        if trade_matches_locked_claim(
            claim=claim,
            member_id=member_id,
            symbol=symbol,
            opened_at=opened_at,
        ):
            return claim

    return None


def trade_is_protected_by_locked_claim(db: Session, trade: Trade):
    return find_locked_claim_conflict(
        db=db,
        workspace_id=trade.workspace_id,
        member_id=trade.member_id,
        symbol=trade.symbol,
        opened_at=trade.opened_at,
    )


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
def list_trades(workspace_id: int, db: Session = Depends(get_db)):
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

    conflict = find_locked_claim_conflict(
        db=db,
        workspace_id=workspace_id,
        member_id=payload.member_id,
        symbol=payload.symbol.strip().upper(),
        opened_at=payload.opened_at,
    )

    if conflict:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Trade conflicts with locked claim {conflict.id}. "
                "Create a new claim version or use a trade outside the locked claim scope."
            ),
        )

    fingerprint = build_trade_fingerprint(
        workspace_id=workspace_id,
        member_id=payload.member_id,
        symbol=payload.symbol,
        side=payload.side,
        opened_at=payload.opened_at,
        entry_price=payload.entry_price,
        quantity=payload.quantity,
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
        symbol=payload.symbol.strip().upper(),
        side=payload.side.strip().upper(),
        opened_at=payload.opened_at,
        closed_at=None,
        entry_price=payload.entry_price,
        exit_price=None,
        quantity=payload.quantity,
        net_pnl=payload.net_pnl,
        currency=payload.currency.strip().upper(),
        strategy_tag=payload.strategy_tag,
        source_system=payload.source_system,
        trade_fingerprint=fingerprint,
    )

    db.add(trade)
    db.commit()
    db.refresh(trade)

    result = serialize_trade(trade)
    result["duplicate_skipped"] = False
    return result


@router.put("/workspaces/{workspace_id}/trades/{trade_id}")
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

    protected_claim = trade_is_protected_by_locked_claim(db, trade)
    if protected_claim:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Trade {trade.id} is protected by locked claim {protected_claim.id} "
                "and cannot be edited."
            ),
        )

    new_conflict = find_locked_claim_conflict(
        db=db,
        workspace_id=workspace_id,
        member_id=payload.member_id,
        symbol=payload.symbol.strip().upper(),
        opened_at=payload.opened_at,
    )
    if new_conflict:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Updated trade would conflict with locked claim {new_conflict.id} "
                "and cannot be saved."
            ),
        )

    trade.member_id = payload.member_id
    trade.symbol = payload.symbol.strip().upper()
    trade.side = payload.side.strip().upper()
    trade.opened_at = payload.opened_at
    trade.entry_price = payload.entry_price
    trade.quantity = payload.quantity
    trade.currency = payload.currency.strip().upper()
    trade.net_pnl = payload.net_pnl
    trade.strategy_tag = payload.strategy_tag
    trade.source_system = payload.source_system
    trade.trade_fingerprint = build_trade_fingerprint(
        workspace_id=workspace_id,
        member_id=payload.member_id,
        symbol=payload.symbol,
        side=payload.side,
        opened_at=payload.opened_at,
        entry_price=payload.entry_price,
        quantity=payload.quantity,
    )

    db.commit()
    db.refresh(trade)
    return serialize_trade(trade)


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

    protected_claim = trade_is_protected_by_locked_claim(db, trade)
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

    try:
        return import_csv_trades(
            db=db,
            workspace_id=workspace_id,
            filename=file.filename,
            content=content,
            actor_user_id=current_user.id,
        )
    except ValueError as e:
        return {
            "workspace_id": workspace_id,
            "filename": file.filename,
            "rows_received": 0,
            "rows_imported": 0,
            "rows_rejected": 1,
            "rows_skipped_duplicates": 0,
            "errors": [str(e)],
        }
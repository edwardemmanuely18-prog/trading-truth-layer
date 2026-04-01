from datetime import datetime
import csv
import hashlib
import io
import json
import os
from pathlib import Path

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


def get_workspace_or_404(workspace_id: int, db: Session) -> Workspace:
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace


def get_workspace_trade_count(workspace_id: int, db: Session) -> int:
    return db.query(Trade).filter(Trade.workspace_id == workspace_id).count()


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


def enforce_workspace_trade_limit(workspace_id: int, db: Session, additional_needed: int = 1):
    if workspace_limits_disabled():
        return

    workspace = get_workspace_or_404(workspace_id, db)
    trade_limit = workspace.trade_limit or 0
    current_trade_count = get_workspace_trade_count(workspace_id, db)

    if trade_limit > 0 and (current_trade_count + additional_needed) > trade_limit:
        raise HTTPException(
            status_code=403,
            detail=(
                f"Trade limit reached for workspace {workspace_id}. "
                f"Current trades: {current_trade_count}. "
                f"Requested additional trades: {additional_needed}. "
                f"Plan limit: {trade_limit}. "
                f"Upgrade workspace plan to add more trades."
            ),
        )


def estimate_csv_row_count(content: bytes) -> int:
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    reader = csv.reader(io.StringIO(text))
    rows = list(reader)

    if not rows:
        return 0

    if len(rows) == 1:
        return 0

    return max(len(rows) - 1, 0)


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
    enforce_trade_import_allowed(workspace_id, db, additional_trades=1)

    fingerprint = build_trade_fingerprint(
        workspace_id=workspace_id,
        member_id=payload.member_id,
        symbol=payload.symbol,
        side=payload.side,
        opened_at=payload.opened_at,
        entry_price=payload.entry_price,
        quantity=payload.quantity,
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

    new_fingerprint = build_trade_fingerprint(
        workspace_id=workspace_id,
        member_id=payload.member_id,
        symbol=payload.symbol,
        side=payload.side,
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
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import (
    get_current_user,
    require_workspace_member,
    require_workspace_operator_or_owner,
)
from app.core.db import get_db
from app.models.claim_dispute import ClaimDispute
from app.models.claim_schema import ClaimSchema
from app.models.user import User
from app.services.audit_service import log_audit_event

router = APIRouter()


class ClaimDisputeCreate(BaseModel):
    summary: str
    challenge_type: str = "general_review"
    reason_code: str = "other"
    evidence_note: str = ""


class ClaimDisputeStatusUpdate(BaseModel):
    status: str
    resolution_note: str | None = None


def serialize_claim_dispute(row: ClaimDispute):
    return {
        "id": row.id,
        "claim_schema_id": row.claim_schema_id,
        "workspace_id": row.workspace_id,
        "status": row.status,
        "challenge_type": row.challenge_type,
        "reason_code": row.reason_code,
        "summary": row.summary,
        "evidence_note": row.evidence_note,
        "reporter_user_id": row.reporter_user_id,
        "reviewer_user_id": row.reviewer_user_id,
        "resolution_note": row.resolution_note,
        "opened_at": row.opened_at.isoformat() if row.opened_at else None,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
        "resolved_at": row.resolved_at.isoformat() if row.resolved_at else None,
    }


def get_claim_or_404(claim_schema_id: int, db: Session) -> ClaimSchema:
    row = db.query(ClaimSchema).filter(ClaimSchema.id == claim_schema_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Claim schema not found")
    return row


def validate_dispute_status(value: str) -> str:
    allowed = {"open", "under_review", "resolved", "rejected"}
    normalized = str(value or "").strip().lower()
    if normalized not in allowed:
      raise HTTPException(status_code=400, detail="Invalid dispute status")
    return normalized


@router.get("/claim-schemas/{claim_schema_id}/disputes")
def list_claim_disputes(
    claim_schema_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    claim = get_claim_or_404(claim_schema_id, db)
    require_workspace_member(claim.workspace_id, current_user, db)

    rows = (
        db.query(ClaimDispute)
        .filter(ClaimDispute.claim_schema_id == claim_schema_id)
        .order_by(ClaimDispute.id.desc())
        .all()
    )

    return [serialize_claim_dispute(row) for row in rows]


@router.post("/claim-schemas/{claim_schema_id}/disputes")
def create_claim_dispute(
    claim_schema_id: int,
    payload: ClaimDisputeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    claim = get_claim_or_404(claim_schema_id, db)
    require_workspace_member(claim.workspace_id, current_user, db)

    summary = (payload.summary or "").strip()
    if not summary:
        raise HTTPException(status_code=400, detail="Dispute summary is required")

    dispute = ClaimDispute(
        claim_schema_id=claim.id,
        workspace_id=claim.workspace_id,
        status="open",
        challenge_type=(payload.challenge_type or "general_review").strip(),
        reason_code=(payload.reason_code or "other").strip(),
        summary=summary,
        evidence_note=payload.evidence_note or "",
        reporter_user_id=current_user.id,
        reviewer_user_id=None,
        resolution_note=None,
        opened_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        resolved_at=None,
    )

    db.add(dispute)
    db.commit()
    db.refresh(dispute)

    log_audit_event(
        db,
        event_type="claim_dispute_created",
        entity_type="claim_dispute",
        entity_id=dispute.id,
        workspace_id=claim.workspace_id,
        old_state=None,
        new_state=serialize_claim_dispute(dispute),
        metadata={
            "source": "claim_disputes.create_claim_dispute",
            "claim_schema_id": claim.id,
            "actor_user_id": current_user.id,
        },
    )

    return serialize_claim_dispute(dispute)


@router.patch("/claim-disputes/{claim_dispute_id}")
def update_claim_dispute_status(
    claim_dispute_id: int,
    payload: ClaimDisputeStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dispute = db.query(ClaimDispute).filter(ClaimDispute.id == claim_dispute_id).first()
    if not dispute:
        raise HTTPException(status_code=404, detail="Claim dispute not found")

    require_workspace_operator_or_owner(dispute.workspace_id, current_user, db)

    old_state = serialize_claim_dispute(dispute)
    next_status = validate_dispute_status(payload.status)

    dispute.status = next_status
    dispute.reviewer_user_id = current_user.id
    dispute.resolution_note = payload.resolution_note

    if next_status in {"resolved", "rejected"}:
        dispute.resolved_at = datetime.utcnow()
    else:
        dispute.resolved_at = None

    dispute.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(dispute)

    log_audit_event(
        db,
        event_type="claim_dispute_updated",
        entity_type="claim_dispute",
        entity_id=dispute.id,
        workspace_id=dispute.workspace_id,
        old_state=old_state,
        new_state=serialize_claim_dispute(dispute),
        metadata={
            "source": "claim_disputes.update_claim_dispute_status",
            "actor_user_id": current_user.id,
        },
    )

    return serialize_claim_dispute(dispute)
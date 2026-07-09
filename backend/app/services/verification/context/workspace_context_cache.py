from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.trade import Trade
from app.models.claim_schema import ClaimSchema
from app.models.workspace import Workspace
from app.models.evidence_record import EvidenceRecord
from app.models.integrity_scan import IntegrityScan
from app.models.integrity_alert import IntegrityAlert
from app.models.audit_event import AuditEvent
from app.models.broker_connection import BrokerConnection
from app.models.review_statement import ReviewStatement
from app.models.claim_dispute import ClaimDispute


@dataclass(slots=True)
class WorkspaceContextCache:

    workspace: Workspace

    trades: list[Trade]

    evidence_records: list

    integrity_scan: IntegrityScan | None

    integrity_alerts: list

    audit_events: list

    audit_events_by_claim: dict[int, list[AuditEvent]]

    broker_connections: list

    review_statements: list[ReviewStatement]

    claim_disputes: list[ClaimDispute]

    claim_disputes_by_claim: dict[int, list[ClaimDispute]]


_CACHE: dict[int, WorkspaceContextCache] = {}


def get_workspace_context_cache(
    db: Session,
    workspace_id: int,
) -> WorkspaceContextCache:

    cached = _CACHE.get(workspace_id)

    if cached is not None:
        return cached

    workspace = (
        db.query(Workspace)
        .filter(
            Workspace.id == workspace_id
        )
        .first()
    )

    trades = (
        db.query(Trade)
        .filter(
            Trade.workspace_id == workspace_id
        )
        .all()
    )

    evidence_records = (
        db.query(EvidenceRecord)
        .filter(
            EvidenceRecord.workspace_id == workspace_id
        )
        .all()
    )

    integrity_scan = (
        db.query(IntegrityScan)
        .filter(
            IntegrityScan.workspace_id == workspace_id
        )
        .order_by(
            IntegrityScan.id.desc()
        )
        .first()
    )

    integrity_alerts = (
        db.query(IntegrityAlert)
        .filter(
            IntegrityAlert.workspace_id == workspace_id
        )
        .all()
    )

    audit_events = (
        db.query(AuditEvent)
        .filter(
            AuditEvent.workspace_id == str(workspace_id)
        )
        .all()
    )

    audit_events_by_claim = {}

    for event in audit_events:

        if event.entity_type != "claim_schema":
            continue

        try:
            claim_id = int(event.entity_id)
        except Exception:
            continue

        audit_events_by_claim.setdefault(
            claim_id,
            [],
        ).append(event)

    broker_connections = (
        db.query(BrokerConnection)
        .filter(
            BrokerConnection.workspace_id == workspace_id
        )
        .all()
    )

    review_statements = (
        db.query(ReviewStatement)
        .join(
            ClaimSchema,
            ClaimSchema.id == ReviewStatement.claim_schema_id,
        )
        .filter(
            ClaimSchema.workspace_id == workspace_id
        )
        .all()
    )

    claim_disputes = (
        db.query(ClaimDispute)
        .join(
            ClaimSchema,
            ClaimSchema.id == ClaimDispute.claim_schema_id,
        )
        .filter(
            ClaimSchema.workspace_id == workspace_id
        )
        .all()
    )

    claim_disputes_by_claim = {}

    for dispute in claim_disputes:

        claim_disputes_by_claim.setdefault(
            dispute.claim_schema_id,
            [],
        ).append(dispute)

    cached = WorkspaceContextCache(
        workspace=workspace,
        trades=trades,
        evidence_records=evidence_records,
        integrity_scan=integrity_scan,
        integrity_alerts=integrity_alerts,
        audit_events=audit_events,
        audit_events_by_claim=audit_events_by_claim,
        broker_connections=broker_connections,
        review_statements=review_statements,
        claim_disputes=claim_disputes,
        claim_disputes_by_claim=
            claim_disputes_by_claim,
    )

    _CACHE[workspace_id] = cached

    return cached


def clear_workspace_context_cache():

    _CACHE.clear()
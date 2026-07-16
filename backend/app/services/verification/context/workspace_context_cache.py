from __future__ import annotations

import time

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

    cache_start = time.perf_counter()

    print()
    print("=" * 80)
    print("WORKSPACE CACHE PROFILE")
    print("=" * 80)

    cached = _CACHE.get(workspace_id)

    if cached is not None:
        return cached

    workspace_start = time.perf_counter()

    workspace = (
        db.query(Workspace)
        .filter(
            Workspace.id == workspace_id
        )
        .first()
    )

    print(
        f"workspace query = "
        f"{time.perf_counter()-workspace_start:.4f}s"
    )

    trades_start = time.perf_counter()

    trades = (
        db.query(Trade)
        .filter(
            Trade.workspace_id == workspace_id
        )
        .all()
    )

    print(
        f"trades query = "
        f"{time.perf_counter()-trades_start:.4f}s"
    )

    evidence_start = time.perf_counter()

    evidence_records = (
        db.query(EvidenceRecord)
        .filter(
            EvidenceRecord.workspace_id == workspace_id
        )
        .all()
    )

    print(
        f"evidence records query = "
        f"{time.perf_counter()-evidence_start:.4f}s"
    )

    integrity_scan_start = time.perf_counter()

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

    print(
        f"integrity scan query = "
        f"{time.perf_counter()-integrity_scan_start:.4f}s"
    )

    integrity_alerts_start = time.perf_counter()

    integrity_alerts = (
        db.query(IntegrityAlert)
        .filter(
            IntegrityAlert.workspace_id == workspace_id
        )
        .all()
    )

    print(
        f"integrity alerts query = "
        f"{time.perf_counter()-integrity_alerts_start:.4f}s"
    )

    audit_events_start = time.perf_counter()

    audit_events = (
        db.query(AuditEvent)
        .filter(
            AuditEvent.workspace_id == str(workspace_id)
        )
        .all()
    )

    print(
        f"audit events query = "
        f"{time.perf_counter()-audit_events_start:.4f}s"
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

    broker_connections_start = time.perf_counter()

    broker_connections = (
        db.query(BrokerConnection)
        .filter(
            BrokerConnection.workspace_id == workspace_id
        )
        .all()
    )

    print(
        f"broker connections query = "
        f"{time.perf_counter()-broker_connections_start:.4f}s"
    )

    review_statements_start = time.perf_counter()

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

    print(
        f"review statements query = "
        f"{time.perf_counter()-review_statements_start:.4f}s"
    )

    claim_disputes_start = time.perf_counter()

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

    print(
        f"claim disputes query = "
        f"{time.perf_counter()-claim_disputes_start:.4f}s"
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

    print(
        f"WORKSPACE CACHE TOTAL = "
        f"{time.perf_counter()-cache_start:.4f}s"
    )

    print("=" * 80)
    print()

    return cached


def clear_workspace_context_cache():

    _CACHE.clear()
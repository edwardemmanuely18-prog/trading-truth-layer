from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.workspace import Workspace
from app.models.trade import Trade
from app.models.claim_schema import ClaimSchema
from app.models.evidence_record import EvidenceRecord
from app.models.broker_connection import BrokerConnection
from app.models.integrity_alert import IntegrityAlert

from app.services.trade_metrics_service import (
    compute_trade_metrics,
)

from app.services.metrics_service import (
    get_workspace_trade_metrics,
)

from app.services.evidence_analytics_service import (
    build_evidence_analytics,
)

from app.services.integrity.integrity_dashboard_service import (
    build_integrity_dashboard,
)

from app.services.verification.workspace_verification_context import (
    WorkspaceVerificationContext,
)

from app.services.verification.workspace_verification_engine import (
    compute_workspace_verification_certificate,
)


def compute_workspace_certificate(
    db: Session,
    workspace_id: int,
):
    """
    Canonical public entry point for workspace verification.

    Every workspace-level verification consumer inside
    Trading Truth Layer must call ONLY this function.

    Examples
    --------
    - Allocator Report
    - Dashboard
    - Workspace Profile
    - Public Workspace
    - Leaderboards
    - Analytics
    """

    workspace = (
        db.query(Workspace)
        .filter(
            Workspace.id == workspace_id
        )
        .first()
    )

    if workspace is None:
        raise ValueError(
            f"Workspace {workspace_id} does not exist."
        )

    trades = (
        db.query(Trade)
        .filter(
            Trade.workspace_id == workspace_id
        )
        .all()
    )

    claims = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id == workspace_id
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

    broker_connections = (
        db.query(BrokerConnection)
        .filter(
            BrokerConnection.workspace_id == workspace_id
        )
        .all()
    )

    integrity_alerts = (
        db.query(IntegrityAlert)
        .filter(
            IntegrityAlert.workspace_id == workspace_id
        )
        .all()
    )

    trade_metrics = compute_trade_metrics(
        trades
    )

    performance_metrics = (
        get_workspace_trade_metrics(
            db,
            workspace_id,
        )
    )

    evidence_metrics = (
        build_evidence_analytics(
            db,
            workspace_id,
        )
    )

    integrity_metrics = (
        build_integrity_dashboard(
            db,
            workspace_id,
        )
    )

    context = WorkspaceVerificationContext(

        workspace=workspace,

        claims=claims,

        published_claims=[
            c
            for c in claims
            if c.status == "published"
        ],

        locked_claims=[
            c
            for c in claims
            if c.status == "locked"
        ],

        trades=trades,

        trade_metrics=trade_metrics,

        performance_metrics=performance_metrics,

        evidence_records=evidence_records,

        broker_connections=broker_connections,

        integrity_alerts=integrity_alerts,

        integrity_dashboard=integrity_metrics,

        analytics_result=evidence_metrics,

    )

    return compute_workspace_verification_certificate(
        context
    )
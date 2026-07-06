from __future__ import annotations

from dataclasses import dataclass

import json

from datetime import datetime

from sqlalchemy.orm import Session

from app.models.workspace import Workspace
from app.models.trade import Trade
from app.models.evidence_record import EvidenceRecord
from app.models.integrity_scan import IntegrityScan
from app.models.integrity_alert import IntegrityAlert
from app.models.review_statement import ReviewStatement
from app.models.claim_dispute import ClaimDispute
from app.models.audit_event import AuditEvent
from app.models.broker_connection import BrokerConnection


@dataclass(slots=True)
class VerificationContextData:

    workspace: Workspace

    trades: list[Trade]

    claim_trade_count: int

    evidence_records: list[EvidenceRecord]

    integrity_scan: IntegrityScan | None

    integrity_alerts: list[IntegrityAlert]

    review_statements: list[ReviewStatement]

    disputes: list[ClaimDispute]

    audit_events: list[AuditEvent]

    broker_connections: list[BrokerConnection]


def load_context_data(
    *,
    db: Session,
    claim_schema,
) -> VerificationContextData:
    """
    Loads every object required by the
    Trading Verification Engine.

    This function performs NO scoring.
    """

    workspace = (

        db.query(Workspace)

        .filter(
            Workspace.id == claim_schema.workspace_id
        )

        .first()

    )

    #
    # ----------------------------------------------------------
    # Claim Scope
    # ----------------------------------------------------------
    #

    included_members = set(
        json.loads(
            claim_schema.included_member_ids_json or "[]"
        )
    )

    included_symbols = set(
        json.loads(
            claim_schema.included_symbols_json or "[]"
        )
    )

    excluded_trade_ids = set(
        json.loads(
            claim_schema.excluded_trade_ids_json or "[]"
        )
    )

    locked_trade_ids = set(
        json.loads(
            claim_schema.locked_trade_ids_json or "[]"
        )
    )

    query = (

        db.query(Trade)

        .filter(
            Trade.workspace_id
            == claim_schema.workspace_id
        )

    )

    #
    # Date Range
    #

    if claim_schema.period_start:

        query = query.filter(
            Trade.opened_at >= claim_schema.period_start
        )

    if claim_schema.period_end:

        query = query.filter(
            Trade.opened_at <= claim_schema.period_end
        )

    #
    # Included Members
    #

    if included_members:

        query = query.filter(
            Trade.member_id.in_(included_members)
        )

    #
    # Included Symbols
    #

    if included_symbols:

        query = query.filter(
            Trade.symbol.in_(included_symbols)
        )

    trades = query.all()

    #
    # Python-side filters
    #

    if excluded_trade_ids:

        trades = [

            trade

            for trade in trades

            if trade.id not in excluded_trade_ids

        ]

    if locked_trade_ids:

        trades = [

            trade

            for trade in trades

            if trade.id in locked_trade_ids

        ]

    evidence_records = (

        db.query(EvidenceRecord)

        .filter(

            EvidenceRecord.workspace_id
            == claim_schema.workspace_id

        )

        .all()

    )

    integrity_scan = (

        db.query(IntegrityScan)

        .filter(

            IntegrityScan.workspace_id
            == claim_schema.workspace_id

        )

        .order_by(
            IntegrityScan.id.desc()
        )

        .first()

    )

    integrity_alerts = (

        db.query(IntegrityAlert)

        .filter(

            IntegrityAlert.workspace_id
            == claim_schema.workspace_id

        )

        .all()

    )

    review_statements = (

        db.query(ReviewStatement)

        .filter(

            ReviewStatement.claim_schema_id
            == claim_schema.id

        )

        .all()

    )

    disputes = (

        db.query(ClaimDispute)

        .filter(

            ClaimDispute.claim_schema_id
            == claim_schema.id

        )

        .all()

    )

    audit_events = (

        db.query(AuditEvent)

        .filter(

            AuditEvent.workspace_id
            == str(claim_schema.workspace_id)

        )

        .all()

    )

    broker_connections = (

        db.query(BrokerConnection)

        .filter(

            BrokerConnection.workspace_id
            == claim_schema.workspace_id

        )

        .all()

    )

    return VerificationContextData(

        workspace=workspace,

        trades=trades,

        claim_trade_count=len(trades),

        evidence_records=evidence_records,

        integrity_scan=integrity_scan,

        integrity_alerts=integrity_alerts,

        review_statements=review_statements,

        disputes=disputes,

        audit_events=audit_events,

        broker_connections=broker_connections,

    )
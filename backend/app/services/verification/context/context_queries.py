from __future__ import annotations

from dataclasses import dataclass

import json

import time
from pprint import pformat

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

from .workspace_context_cache import (
    get_workspace_context_cache,
)

from app.services.claim_integrity_engine import (
    parse_period_start,
    parse_period_end,
    coerce_trade_opened_at,
)


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

    workspace_cache = get_workspace_context_cache(
        db,
        claim_schema.workspace_id,
    )

    workspace = workspace_cache.workspace

    profile = {}

    total_start = time.perf_counter()

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

    period_start = parse_period_start(
        claim_schema.period_start
    )

    period_end = parse_period_end(
        claim_schema.period_end
    )

    t = time.perf_counter()

    trades = workspace_cache.trades

    if period_start:

        trades = [
            trade
            for trade in trades
            if (
                coerce_trade_opened_at(trade.opened_at)
                is not None
                and
                coerce_trade_opened_at(trade.opened_at)
                >= period_start
            )
        ]

    if period_end:

        trades = [
            trade
            for trade in trades
            if (
                coerce_trade_opened_at(trade.opened_at)
                is not None
                and
                coerce_trade_opened_at(trade.opened_at)
                <= period_end
            )
        ]

    if included_members:

        trades = [
            trade
            for trade in trades
            if trade.member_id in included_members
        ]

    if included_symbols:

        trades = [
            trade
            for trade in trades
            if (trade.symbol or "").upper() in included_symbols
        ]

    profile["trade_filter"] = (
        time.perf_counter() - t
    )

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

    evidence_records = workspace_cache.evidence_records

    integrity_scan = workspace_cache.integrity_scan

    integrity_alerts = workspace_cache.integrity_alerts

    profile["workspace_cache"] = (
        time.perf_counter() - total_start
    )

    t = time.perf_counter()

    review_statements = [
        statement
        for statement in workspace_cache.review_statements
        if statement.claim_schema_id == claim_schema.id
    ]

    profile["review_statements"] = (
        time.perf_counter() - t
    )

    t = time.perf_counter()

    disputes = [
        dispute
        for dispute in workspace_cache.claim_disputes
        if dispute.claim_schema_id == claim_schema.id
    ]

    profile["claim_disputes"] = (
        time.perf_counter() - t
    )

    audit_events = workspace_cache.audit_events

    broker_connections = workspace_cache.broker_connections

    profile["TOTAL"] = (
        time.perf_counter() - total_start
    )

    print("\n" + "=" * 80)
    print(f"TVS CONTEXT PROFILE - CLAIM {claim_schema.id}")
    print("=" * 80)
    print(pformat(profile))
    print("=" * 80 + "\n")

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
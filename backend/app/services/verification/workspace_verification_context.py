from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class WorkspaceVerificationContext:
    """
    Canonical immutable input to the Workspace
    Trading Verification Engine.

    Every workspace-level verification computation
    consumes ONLY this context.
    """

    # =====================================================
    # Workspace
    # =====================================================

    workspace: Any

    # =====================================================
    # Claims
    # =====================================================

    claims: list[Any] = field(
        default_factory=list
    )

    published_claims: list[Any] = field(
        default_factory=list
    )

    locked_claims: list[Any] = field(
        default_factory=list
    )

    # =====================================================
    # Trades
    # =====================================================

    trades: list[Any] = field(
        default_factory=list
    )

    trade_metrics: dict[str, Any] = field(
        default_factory=dict
    )

    audit_events: list[Any] = field(
        default_factory=list
    )

    review_statements: list[Any] = field(
        default_factory=list
    )

    disputes: list[Any] = field(
        default_factory=list
    )

    claim_versions: list[Any] = field(
        default_factory=list
    )

    # =====================================================
    # Evidence
    # =====================================================

    evidence_records: list[Any] = field(
        default_factory=list
    )

    broker_connections: list[Any] = field(
        default_factory=list
    )

    broker_accounts: list[Any] = field(
        default_factory=list
    )

    evidence_metadata: dict[str, Any] = field(
        default_factory=dict
    )

    # =====================================================
    # Integrity
    # =====================================================

    integrity_alerts: list[Any] = field(
        default_factory=list
    )

    integrity_dashboard: dict[str, Any] = field(
        default_factory=dict
    )

    # =====================================================
    # Governance
    # =====================================================

    audit_events: list[Any] = field(
        default_factory=list
    )

    review_statements: list[Any] = field(
        default_factory=list
    )

    disputes: list[Any] = field(
        default_factory=list
    )

    claim_versions: list[Any] = field(
        default_factory=list
    )

    # =====================================================
    # Intelligence
    # =====================================================

    analytics_result: dict[str, Any] = field(
        default_factory=dict
    )

    network_result: dict[str, Any] = field(
        default_factory=dict
    )

    # =====================================================
    # Metadata
    # =====================================================

    metadata: dict[str, Any] = field(
        default_factory=dict
    )
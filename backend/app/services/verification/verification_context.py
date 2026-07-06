from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class VerificationContext:
    """
    Canonical input to the Trading Verification Engine.

    Every verification computation inside Trading Truth Layer
    consumes this immutable context.
    """

    # ======================================================
    # Core Claim
    # ======================================================

    claim_schema: Any

    workspace: Any

    #
    # Canonical claim trade universe
    #

    trades: list[Any]

    claim_trade_count: int = 0

    trade_metrics: dict[str, Any] = field(
        default_factory=dict
    )

    performance_metrics: dict[str, Any] = field(
        default_factory=dict
    )

    # ======================================================
    # Evidence Layer
    # ======================================================

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

    #
    # Institutional Evidence Profile
    #

    evidence_profile: dict[str, Any] = field(
        default_factory=dict
    )

    # ======================================================
    # Integrity Layer
    # ======================================================

    integrity_scan: Any | None = None

    integrity_alerts: list[Any] = field(
        default_factory=list
    )

    # ======================================================
    # Governance Layer
    # ======================================================

    audit_events: list[Any] = field(
        default_factory=list
    )

    disputes: list[Any] = field(
        default_factory=list
    )

    review_statements: list[Any] = field(
        default_factory=list
    )

    claim_versions: list[Any] = field(
        default_factory=list
    )

    # ======================================================
    # Analytics
    # ======================================================

    analytics_result: dict[str, Any] = field(
        default_factory=dict
    )

    network_result: dict[str, Any] = field(
        default_factory=dict
    )

    # ======================================================
    # Derived Outputs
    # ======================================================

    verification_metrics: Any | None = None

    verification_certificate: Any | None = None

    #
    # Identity & Presentation Metadata
    #

    identity: dict[str, Any] = field(
        default_factory=dict
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    qr_payload: dict[str, Any] = field(
        default_factory=dict
    )
from __future__ import annotations

"""
Trading Truth Layer

Trade Evidence System (TES)

Canonical Evidence Contracts

These models represent institutional evidence
analytics throughout Trading Truth Layer.

NO calculations occur here.

Every evidence consumer should consume these
contracts instead of raw dictionaries.
"""

from dataclasses import dataclass, field
from typing import Any


# ============================================================
# EVIDENCE COMPONENT
# ============================================================

@dataclass(slots=True)
class EvidenceComponent:

    name: str

    value: float

    maximum: float

    percentage: float

    status: str

    reason: str

    details: dict[str, Any] = field(
        default_factory=dict,
    )


# ============================================================
# CLAIM EVIDENCE METRICS
# ============================================================

@dataclass(slots=True)
class ClaimEvidenceMetrics:

    #
    # Identity
    #

    claim_schema_id: int

    workspace_id: int

    trade_count: int

    #
    # Verification
    #

    broker_verified: int

    verified: int

    self_reported: int

    coverage: float

    #
    # Provenance
    #

    tier1: int

    tier2: int

    tier3: int

    reliability: float

    #
    # Protection
    #

    fingerprinted: int

    hash_protected: int

    unprotected: int

    protection: float

    #
    # Quality
    #

    quality_score: float

    quality_band: str

    verification_quality: float

    protection_quality: float

    completeness_quality: float

    import_quality: float

    #
    # Components
    #

    evidence: EvidenceComponent

    provenance: EvidenceComponent

    protection_component: EvidenceComponent

    quality: EvidenceComponent

    #
    # Extension
    #

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )


# ============================================================
# WORKSPACE EVIDENCE METRICS
# ============================================================

@dataclass(slots=True)
class WorkspaceEvidenceMetrics:

    #
    # Identity
    #

    workspace_id: int

    trade_count: int

    #
    # Verification
    #

    broker_verified: int

    verified: int

    self_reported: int

    coverage: float

    #
    # Provenance
    #

    tier1: int

    tier2: int

    tier3: int

    reliability: float

    #
    # Protection
    #

    fingerprinted: int

    hash_protected: int

    unprotected: int

    protection: float

    #
    # Quality
    #

    quality_score: float

    quality_band: str

    verification_quality: float

    protection_quality: float

    completeness_quality: float

    import_quality: float

    #
    # Institutional Components
    #

    evidence: EvidenceComponent

    provenance: EvidenceComponent

    protection_component: EvidenceComponent

    quality: EvidenceComponent

    #
    # Monitoring
    #

    monitoring_feed: list[
        dict[str, Any]
    ] = field(
        default_factory=list,
    )

    exception_registry: list[
        dict[str, Any]
    ] = field(
        default_factory=list,
    )

    #
    # Extension
    #

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


# ============================================================
# Investigation Lifecycle
# ============================================================

class InvestigationStatus(str, Enum):

    NEW = "NEW"

    RUNNING = "RUNNING"

    ANALYZING = "ANALYZING"

    COMPLETE = "COMPLETE"

    APPROVED = "APPROVED"

    ARCHIVED = "ARCHIVED"


# ============================================================
# Investigation Scope
# ============================================================

class InvestigationScope(str, Enum):

    WORKSPACE = "WORKSPACE"

    CLAIM = "CLAIM"

    MEMBER = "MEMBER"

    ACCOUNT = "ACCOUNT"

    BROKER = "BROKER"

    SYNC_JOB = "SYNC_JOB"

    STRATEGY = "STRATEGY"


# ============================================================
# Finding Severity
# ============================================================

class InvestigationSeverity(str, Enum):

    INFORMATION = "INFORMATION"

    LOW = "LOW"

    MEDIUM = "MEDIUM"

    HIGH = "HIGH"

    CRITICAL = "CRITICAL"


# ============================================================
# Graph Relationship Types
# ============================================================

class RelationshipType(str, Enum):

    TRADE = "TRADE"

    CLAIM = "CLAIM"

    MEMBER = "MEMBER"

    ACCOUNT = "ACCOUNT"

    BROKER = "BROKER"

    SYMBOL = "SYMBOL"

    STRATEGY = "STRATEGY"

    SESSION = "SESSION"

    REVIEW = "REVIEW"

    AUDIT = "AUDIT"

    VERIFICATION = "VERIFICATION"

    EVIDENCE = "EVIDENCE"

    GOVERNANCE = "GOVERNANCE"

    WORKSPACE = "WORKSPACE"

    SYNC_JOB = "SYNC_JOB"


# ============================================================
# Investigation Node
# ============================================================

@dataclass(slots=True)
class InvestigationNode:

    id: str

    label: str

    node_type: str

    score: float = 0.0

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# Investigation Relationship
# ============================================================

@dataclass(slots=True)
class InvestigationRelationship:

    source: str

    target: str

    relationship: RelationshipType

    weight: float = 1.0

    confidence: float = 100.0

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# Timeline
# ============================================================

@dataclass(slots=True)
class InvestigationTimelineEvent:

    timestamp: datetime

    category: str

    title: str

    description: str

    severity: InvestigationSeverity

    evidence_reference: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# Investigation Finding
# ============================================================

@dataclass(slots=True)
class InvestigationFinding:

    id: str

    title: str

    description: str

    severity: InvestigationSeverity

    confidence: float

    affected_claims: list[int] = field(
        default_factory=list
    )

    affected_trades: list[int] = field(
        default_factory=list
    )

    affected_members: list[int] = field(
        default_factory=list
    )

    affected_accounts: list[int] = field(
        default_factory=list
    )

    affected_sync_jobs: list[int] = field(
        default_factory=list
    )

    evidence: list[str] = field(
        default_factory=list
    )

    recommendation: str = ""

    # ========================================================
    # Canonical Investigation Impact
    #
    # Summary counts describing the institutional scope
    # affected by this finding.
    # ========================================================

    impact: dict[str, int] = field(

        default_factory=lambda: {

            "claims": 0,

            "trades": 0,

            "members": 0,

            "accounts": 0,

            "sync_jobs": 0,

        }

    )


# ============================================================
# Recommendation
# ============================================================

@dataclass(slots=True)
class InvestigationRecommendation:

    priority: int

    title: str

    rationale: str

    action: str

    automated: bool = False


# ============================================================
# Executive Summary
# ============================================================

@dataclass(slots=True)
class InvestigationSummary:

    investigation_confidence: float

    total_findings: int

    critical_findings: int

    high_findings: int

    medium_findings: int

    low_findings: int

    informational_findings: int

    evidence_nodes: int

    relationships: int

    timeline_events: int

    affected_claims: int

    affected_members: int

    affected_accounts: int

    affected_sync_jobs: int

    overall_risk: InvestigationSeverity

    executive_summary: str


@dataclass(slots=True)
class InvestigationDomain:

    name: str

    confidence: float

    findings: list[InvestigationFinding] = field(
        default_factory=list,
    )

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )


@dataclass(slots=True)
class InvestigationDecision:

    decision: str

    confidence: float

    rationale: str

    residual_risk: InvestigationSeverity

    required_actions: list[str] = field(
        default_factory=list,
    )

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )


# ============================================================
# Investigation Report
# ============================================================

@dataclass(slots=True)
class InvestigationReport:

    # ========================================================
    # Investigation Identity
    # ========================================================

    workspace_id: int

    scope: InvestigationScope

    scope_id: int

    status: InvestigationStatus

    generated_at: datetime

    # ========================================================
    # Canonical Investigation Outputs (Existing)
    # ========================================================

    summary: InvestigationSummary

    graph: Any

    # ========================================================
    # Canonical Investigation Outputs
    # ========================================================

    nodes: list[InvestigationNode]

    relationships: list[InvestigationRelationship]

    timeline: list[InvestigationTimelineEvent]

    findings: list[InvestigationFinding]

    critical_path: Any

    recommendations: list[InvestigationRecommendation]

    # ========================================================
    # Institutional Investigation Domains (NEW)
    #
    # These remain optional until their corresponding engines
    # are implemented.
    # ========================================================

    execution: InvestigationDomain | None = None

    evidence: InvestigationDomain | None = None

    verification: InvestigationDomain | None = None

    governance: InvestigationDomain | None = None

    broker: InvestigationDomain | None = None

    synchronization: InvestigationDomain | None = None

    review: InvestigationDomain | None = None

    behavior: InvestigationDomain | None = None

    allocator: InvestigationDecision | None = None

    # ========================================================
    # Metadata
    # ========================================================

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )
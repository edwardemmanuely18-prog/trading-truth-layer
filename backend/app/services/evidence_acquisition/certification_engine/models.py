"""
Canonical models for the Evidence Acquisition Certification Engine (ICE).

The Certification Engine provides a provider-independent mechanism for
certifying that every acquisition engine correctly implements the TTL
Synchronization Contract.

This subsystem is engine-agnostic and is shared by:

    • Desktop Trading Engine
    • Financial Engine
    • Gateway Engine

The models defined here represent certification state only.
They never perform synchronization or provider communication.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


# ============================================================
# Certification Status
# ============================================================


class CertificationStatus(str, Enum):
    """
    Overall certification result.
    """

    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    CANCELLED = "cancelled"


# ============================================================
# Certification Level
# ============================================================


class CertificationLevel(str, Enum):
    """
    Certification maturity level.
    """

    CONTRACT = "contract"
    SIMULATION = "simulation"
    SANDBOX = "sandbox"
    PRODUCTION = "production"


# ============================================================
# Simulation Mode
# ============================================================


class SimulationMode(str, Enum):
    """
    Source of synchronization.
    """

    SIMULATION = "simulation"
    SANDBOX = "sandbox"
    LIVE = "live"


# ============================================================
# Validation Stage
# ============================================================


class ValidationStage(str, Enum):
    """
    Canonical synchronization validation stages.
    """

    AUTHENTICATION = "authentication"
    CONNECTION = "connection"
    SYNCHRONIZATION = "synchronization"
    CANONICALIZATION = "canonicalization"
    REGISTRY = "registry"
    INTEGRITY = "integrity"
    RECOVERY = "recovery"
    DISCONNECTION = "disconnection"


# ============================================================
# Validation Result
# ============================================================


@dataclass(slots=True)
class ValidationResult:
    """
    Result of a single validation stage.
    """

    stage: ValidationStage

    status: CertificationStatus

    success: bool

    message: str = ""

    duration_ms: float = 0.0

    timestamp: datetime = field(default_factory=datetime.utcnow)


# ============================================================
# Certification Summary
# ============================================================


@dataclass(slots=True)
class CertificationSummary:
    """
    Aggregated validation statistics.
    """

    total_checks: int = 0

    passed_checks: int = 0

    failed_checks: int = 0

    warning_checks: int = 0

    total_duration_ms: float = 0.0


# ============================================================
# Certification Result
# ============================================================


@dataclass(slots=True)
class CertificationResult:
    """
    Complete certification outcome for a provider.
    """

    provider: str

    engine: str

    level: CertificationLevel

    mode: SimulationMode

    status: CertificationStatus

    started_at: datetime

    completed_at: Optional[datetime] = None

    summary: CertificationSummary = field(
        default_factory=CertificationSummary
    )

    validations: List[ValidationResult] = field(
        default_factory=list
    )

    metadata: Dict[str, str] = field(
        default_factory=dict
    )


# ============================================================
# Certification Report
# ============================================================


@dataclass(slots=True)
class CertificationReport:
    """
    Institutional certification report.
    """

    generated_at: datetime

    generated_by: str

    results: List[CertificationResult] = field(
        default_factory=list
    )


# ============================================================
# Certification Statistics
# ============================================================


@dataclass(slots=True)
class CertificationStatistics:
    """
    Global certification statistics.
    """

    providers: int = 0

    passed: int = 0

    failed: int = 0

    warnings: int = 0

    pending: int = 0

    running: int = 0


# ============================================================
# Public Exports
# ============================================================

__all__ = [
    "CertificationLevel",
    "CertificationReport",
    "CertificationResult",
    "CertificationStatistics",
    "CertificationStatus",
    "CertificationSummary",
    "SimulationMode",
    "ValidationResult",
    "ValidationStage",
]
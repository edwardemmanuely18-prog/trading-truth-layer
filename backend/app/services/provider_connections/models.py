"""
Trading Truth Layer (TTL)

Provider Connections

Canonical Models

Institutional models representing authenticated
provider connections managed by Trading Truth Layer.

These models intentionally do not perform any
connection logic.

They represent the persistent definition of an
external provider connection.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime

from enum import Enum

from typing import Any

from pydantic import BaseModel

from app.services.evidence_acquisition.desktop_trading_engine.provider import (
    DesktopEvidenceProvider,
)


# ============================================================
# Connection Status
# ============================================================


class ConnectionStatus(str, Enum):

    CREATED = "created"

    CONNECTING = "connecting"

    CONNECTED = "connected"

    SYNCHRONIZING = "synchronizing"

    DISCONNECTED = "disconnected"

    FAILED = "failed"

# ============================================================
# Environment
# ============================================================


class ConnectionEnvironment(str, Enum):

    DEMO = "demo"

    LIVE = "live"

    SANDBOX = "sandbox"

    PAPER = "paper"

# ============================================================
# Health
# ============================================================


class ConnectionHealth(str, Enum):

    HEALTHY = "healthy"

    WARNING = "warning"

    ERROR = "error"

    UNKNOWN = "unknown"

# ============================================================
# Statistics
# ============================================================


@dataclass(slots=True)
class ConnectionStatistics:

    synchronization_count: int = 0

    successful_synchronizations: int = 0

    failed_synchronizations: int = 0

    evidence_packages: int = 0

    last_synchronization: datetime | None = None

# ============================================================
# Provider Connection
# ============================================================


@dataclass(slots=True)
class ProviderConnection:
    """
    Canonical provider connection.

    Represents a configured connection to an external
    evidence provider.

    This model is engine-agnostic.
    """

    id: str

    workspace_id: int

    connection_name: str

    provider: str

    engine: str

    environment: ConnectionEnvironment

    configuration: dict[str, Any] = field(default_factory=dict)

    status: ConnectionStatus = ConnectionStatus.CREATED

    health: ConnectionHealth = ConnectionHealth.UNKNOWN

    verified: bool = False

    connected: bool = False

    created_at: datetime = field(default_factory=datetime.utcnow)

    updated_at: datetime = field(default_factory=datetime.utcnow)

    statistics: ConnectionStatistics = field(
        default_factory=ConnectionStatistics,
    )


@dataclass(slots=True)
class RuntimeConnection:
    """
    Live runtime representation of a configured provider connection.

    Owns both the persisted connection configuration and the
    active DesktopEvidenceProvider.
    """

    connection: ProviderConnection

    provider: DesktopEvidenceProvider

    @property
    def id(self) -> str:
        return self.connection.id


# ============================================================
# API Response Models
# ============================================================


class DesktopConnectionCreateResponse(BaseModel):
    id: str
    provider: str
    connection_name: str
    status: str
    synchronization_profile: str
    created_at: datetime

class ProviderConnectionStatisticsResponse(BaseModel):
    synchronization_count: int
    successful_synchronizations: int
    failed_synchronizations: int
    evidence_packages: int
    last_synchronization: datetime | None


class ProviderConnectionDetailResponse(BaseModel):
    id: str
    workspace_id: int
    connection_name: str
    provider: str
    engine: str
    environment: str
    status: str
    health: str
    verified: bool
    connected: bool
    created_at: datetime
    updated_at: datetime
    statistics: ProviderConnectionStatisticsResponse


class DesktopConnectionTestResponse(BaseModel):
    success: bool
    message: str


class DesktopConnectionVerificationResponse(BaseModel):
    """
    Canonical Desktop Provider Connection verification response.
    """

    provider: str
    verified: bool
    checks: list[dict[str, Any]]
    error: str | None = None
    snapshot: dict[str, Any] | None = None
    

# ============================================================
# Public Exports
# ============================================================


__all__ = [
    "ConnectionStatus",
    "ConnectionEnvironment",
    "ConnectionHealth",
    "ConnectionStatistics",
    "ProviderConnection",
    "RuntimeConnection",
    "DesktopConnectionCreateResponse",
    "DesktopConnectionTestResponse",
    "ProviderConnectionStatisticsResponse",
    "ProviderConnectionDetailResponse",
]
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


# ============================================================
# Execution Status
# ============================================================

class ExecutionStatus(str, Enum):

    OPEN = "OPEN"

    CLOSED = "CLOSED"

    PARTIAL = "PARTIAL"

    CANCELLED = "CANCELLED"

    UNKNOWN = "UNKNOWN"


# ============================================================
# Integrity Result
# ============================================================

class IntegrityLevel(str, Enum):

    VERIFIED = "VERIFIED"

    WARNING = "WARNING"

    FAILED = "FAILED"


# ============================================================
# Canonical Execution
# ============================================================

@dataclass(slots=True)
class ExecutionState:

    workspace_id: int

    trade_id: int | None

    broker_connection_id: int | None

    account_id: str | None

    symbol: str

    side: str

    ticket: str | None

    status: ExecutionStatus

    opened_at: datetime | None

    closed_at: datetime | None

    entry_price: float

    exit_price: float | None

    quantity: float

    realized_pnl: float

    floating_pnl: float

    commission: float

    swap: float

    fingerprint: str | None

    metadata: dict[str, Any]


# ============================================================
# Sequence
# ============================================================

@dataclass(slots=True)
class ExecutionSequence:

    executions: list[ExecutionState]

    duplicate_tickets: list[str]

    missing_open_times: list[str]

    missing_close_times: list[str]

    orphan_positions: list[str]

    out_of_order: list[str]


# ============================================================
# Integrity Report
# ============================================================

@dataclass(slots=True)
class ExecutionIntegrity:

    level: IntegrityLevel

    score: float

    duplicate_count: int

    orphan_count: int

    missing_timestamp_count: int

    findings: list[str]


# ============================================================
# Replay Snapshot
# ============================================================

@dataclass(slots=True)
class ExecutionReplayPoint:

    timestamp: datetime

    equity: float

    exposure: float

    floating_pnl: float

    margin: float

    open_positions: int


# ============================================================
# Replay
# ============================================================

@dataclass(slots=True)
class ExecutionReplay:

    timeline: list[ExecutionReplayPoint]


# ============================================================
# Metrics
# ============================================================

@dataclass(slots=True)
class ExecutionMetrics:

    total_trades: int

    open_positions: int

    closed_positions: int

    duplicate_tickets: int

    orphan_positions: int

    execution_integrity_score: float

    average_open_positions: float

    peak_exposure: float

    average_exposure: float

    peak_margin: float

    average_margin: float

    peak_equity: float

    average_equity: float

    peak_floating_pnl: float

    average_floating_pnl: float

    replay_duration_seconds: int

    replay_completeness: float
from __future__ import annotations

"""
Trading Truth Layer
Performance Models

Canonical trading performance contracts.

These models represent the institutional
performance analytics consumed throughout
Trading Truth Layer.

No calculations occur here.

Every consumer should depend on these
contracts instead of raw dictionaries.

Consumers include:

• Claim Report PDF
• Allocator Report PDF
• Dashboard
• Public Claim
• Leaderboard
• Workspace APIs
• Claim APIs
"""

from dataclasses import dataclass, field
from typing import Any


# ============================================================
# CLAIM PERFORMANCE METRICS
# ============================================================

@dataclass(slots=True)
class ClaimPerformanceMetrics:
    """
    Canonical performance metrics for a
    single verified claim.

    These metrics describe historical
    trading behaviour only.

    Verification metrics belong to TVS.
    """

    # --------------------------------------------------------
    # Identity
    # --------------------------------------------------------

    claim_schema_id: int

    workspace_id: int

    trade_count: int

    # --------------------------------------------------------
    # Profitability
    # --------------------------------------------------------

    net_profit: float

    gross_profit: float

    gross_loss: float

    profit_factor: float

    expectancy: float

    average_win: float

    average_loss: float

    payoff_ratio: float

    # --------------------------------------------------------
    # Win / Loss
    # --------------------------------------------------------

    winning_trades: int

    losing_trades: int

    win_rate: float

    loss_rate: float

    # --------------------------------------------------------
    # Risk
    # --------------------------------------------------------

    max_drawdown: float

    recovery_factor: float

    # --------------------------------------------------------
    # Classification
    # --------------------------------------------------------

    performance_band: str

    # --------------------------------------------------------
    # Extension Point
    # --------------------------------------------------------

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )


# ============================================================
# WORKSPACE PERFORMANCE METRICS
# ============================================================

@dataclass(slots=True)
class WorkspacePerformanceMetrics:
    """
    Canonical workspace performance metrics.

    Aggregated from all verified claims
    belonging to a workspace.
    """

    workspace_id: int

    claim_count: int

    trade_count: int

    net_profit: float

    gross_profit: float

    gross_loss: float

    profit_factor: float

    expectancy: float

    average_win: float

    average_loss: float

    payoff_ratio: float

    win_rate: float

    loss_rate: float

    # --------------------------------------------------------
    # Trade Distribution
    # --------------------------------------------------------

    winning_trades: int

    losing_trades: int

    max_drawdown: float

    recovery_factor: float

    performance_band: str

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )
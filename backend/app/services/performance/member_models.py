from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ============================================================
# MEMBER PERFORMANCE METRICS
# ============================================================

@dataclass(slots=True)
class MemberPerformanceMetrics:
    """
    Canonical TPS contract representing the
    aggregated performance of a workspace member.

    Every member-level performance consumer
    should consume this model instead of
    recalculating metrics from trades.
    """

    # --------------------------------------------------------
    # Identity
    # --------------------------------------------------------

    member_id: str

    member_name: str

    workspace_id: int

    # --------------------------------------------------------
    # Activity
    # --------------------------------------------------------

    claim_count: int

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
    # Extension
    # --------------------------------------------------------

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )
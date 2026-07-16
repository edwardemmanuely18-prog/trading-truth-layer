from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.models.claim_schema import ClaimSchema
from app.models.trade import Trade


@dataclass
class WorkspaceClaimAnalytics:

    claim: ClaimSchema

    metrics: Any

    trades: list[Trade]


@dataclass
class WorkspaceMemberAnalytics:

    metrics: Any


@dataclass
class WorkspaceMetricsAnalytics:

    metrics: Any


@dataclass
class WorkspaceAnalyticsContext:

    workspace_id: int

    reporting_currency: str

    workspace_claims: list[ClaimSchema]

    workspace_trades: list[Trade]

    normalized_workspace_trades: list[Trade]

    claim_metrics: list[WorkspaceClaimAnalytics]

    member_metrics: list[WorkspaceMemberAnalytics]

    workspace_metrics: WorkspaceMetricsAnalytics

    claim_trade_map: dict[int, list[Trade]]
from __future__ import annotations

"""
Trade Evidence System (TES)

Monitoring Feed Builder

Canonical institutional evidence feed.

Pure projection.

No SQL.

No database access.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class MonitoringFeed:

    rows: list[dict[str, Any]] = field(
        default_factory=list,
    )


def build_monitoring_feed(
    rows: list[dict[str, Any]],
) -> MonitoringFeed:
    """
    Canonical monitoring feed.

    This builder performs no calculations.

    It simply standardizes the monitoring
    records produced by TES.
    """

    return MonitoringFeed(
        rows=list(rows),
    )
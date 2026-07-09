from __future__ import annotations

"""
Trade Evidence System (TES)

Exception Registry Builder

Canonical evidence exception registry.

Pure projection.

No SQL.

No database access.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ExceptionRegistry:

    rows: list[dict[str, Any]] = field(
        default_factory=list,
    )


def build_exception_registry(
    rows: list[dict[str, Any]],
) -> ExceptionRegistry:
    """
    Canonical evidence exception registry.

    Performs no calculations.

    Standardizes the exception records
    produced by TES.
    """

    return ExceptionRegistry(
        rows=list(rows),
    )
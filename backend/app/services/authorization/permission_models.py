from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PermissionResult:

    allowed: bool

    reason: str | None = None
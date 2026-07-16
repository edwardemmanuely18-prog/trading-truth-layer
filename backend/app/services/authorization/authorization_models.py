from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class AuthorizationSnapshot:

    role: str

    commercial_plan: str

    billing_active: bool

    pages: Dict[str, bool]

    features: Dict[str, bool]

    limits: Dict[str, int | None]
from __future__ import annotations

from dataclasses import dataclass

from app.services.authorization.identity.workspace_identity import (
    WorkspaceIdentity,
)


@dataclass(frozen=True)
class AccessContext:
    """
    Immutable authorization context consumed by the IAM engine.
    """

    identity: WorkspaceIdentity

    commercial_plan: str

    billing_active: bool

    enabled_features: frozenset[str]

    enabled_pages: frozenset[str]
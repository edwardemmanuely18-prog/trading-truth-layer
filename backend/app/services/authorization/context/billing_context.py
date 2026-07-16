from __future__ import annotations

from dataclasses import dataclass

from .workspace_context import WorkspaceContext


@dataclass(frozen=True)
class BillingContext:

    workspace: WorkspaceContext
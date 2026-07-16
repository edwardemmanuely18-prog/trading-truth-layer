from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from app.models.workspace import Workspace

from .provider_registry import (
    collect_provider_payloads,
)


# ============================================================
# Canonical Investigation Context
# ============================================================

@dataclass(slots=True)
class InvestigationContext:
    """
    Canonical immutable investigation snapshot.

    Engines must NEVER query the database.

    Engines consume only this context.
    """

    workspace: Workspace

    provider_payloads: dict[
        str,
        Any,
    ]

    metadata: dict[
        str,
        Any,
    ]


# ============================================================
# Builder
# ============================================================

class InvestigationContextBuilder:

    @staticmethod
    def build(
        *,
        db: Session,
        workspace_id: int,
    ) -> InvestigationContext:

        workspace = (
            db.query(Workspace)
            .filter(
                Workspace.id == workspace_id,
            )
            .first()
        )

        from .providers import (
            bootstrap_providers,
        )

        if workspace is None:

            raise ValueError(
                f"Workspace {workspace_id} not found."
            )

        bootstrap_providers()

        provider_payloads = (
            collect_provider_payloads(
                db=db,
                workspace_id=workspace_id,
            )
        )

        return InvestigationContext(

            workspace=workspace,

            provider_payloads=provider_payloads,

            metadata={

                # --------------------------------------------------
                # Investigation Identity
                # --------------------------------------------------

                "workspace_id": workspace_id,

                "workspace_name": getattr(
                    workspace,
                    "name",
                    None,
                ),

                # --------------------------------------------------
                # Workspace Configuration
                # --------------------------------------------------

                "plan": getattr(
                    workspace,
                    "plan",
                    None,
                ),

                "billing_status": getattr(
                    workspace,
                    "billing_status",
                    None,
                ),

                # --------------------------------------------------
                # Investigation Metadata
                # --------------------------------------------------

                "provider_count": len(
                    provider_payloads,
                ),

                "provider_names": sorted(
                    provider_payloads.keys(),
                ),

                "investigation_version": "IIS v1",

            },

        )
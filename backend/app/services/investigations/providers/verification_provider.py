from __future__ import annotations

from sqlalchemy.orm import Session

from app.services.verification.verification_service import (
    get_workspace_verification_metrics,
)

from ..base_provider import (
    InvestigationProvider,
)


class VerificationProvider(
    InvestigationProvider,
):

    name = "verification"

    priority = 100

    def collect(
        self,
        *,
        db: Session,
        workspace_id: int,
    ):

        return get_workspace_verification_metrics(
            db=db,
            workspace_id=workspace_id,
        )
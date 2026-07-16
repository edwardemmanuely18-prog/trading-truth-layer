from __future__ import annotations

from sqlalchemy.orm import Session

from ..base_provider import (
    InvestigationProvider,
)

from app.services.verification.verification_service import (
    get_workspace_verification_metrics,
)


class TVSProvider(
    InvestigationProvider,
):

    name = "tvs"

    version = "1.0"

    priority = 100

    def collect(
        self,
        *,
        db: Session,
        workspace_id: int,
    ):

        """
        Canonical TVS snapshot.

        This MUST call the canonical TVS entrypoint.

        Replace this call with the TVS workspace snapshot
        service once TVS V2 becomes the single source of
        truth.
        """

        return get_workspace_verification_metrics(

            db=db,

            workspace_id=workspace_id,

        )
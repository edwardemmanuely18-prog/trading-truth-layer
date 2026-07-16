from __future__ import annotations

from sqlalchemy.orm import Session

from ..base_provider import (
    InvestigationProvider,
)

from app.models.audit_event import (
    AuditEvent,
)


class AuditProvider(
    InvestigationProvider,
):

    name = "audit"

    version = "1.0"

    priority = 400

    def collect(
        self,
        *,
        db: Session,
        workspace_id: int,
    ):

        return (

            db.query(
                AuditEvent
            )

            .filter(
                AuditEvent.workspace_id
                == str(workspace_id)
            )

            .order_by(
                AuditEvent.created_at.asc()
            )

            .all()

        )
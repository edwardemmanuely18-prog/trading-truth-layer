from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.workspace_membership import WorkspaceMembership

from .workspace_identity import WorkspaceIdentity


class WorkspaceIdentityBuilder:

    @staticmethod
    def build(
        db: Session,
        workspace_id: int,
        user_id: int,
    ) -> WorkspaceIdentity:

        membership = (
            db.query(WorkspaceMembership)
            .filter(
                WorkspaceMembership.workspace_id == workspace_id,
                WorkspaceMembership.user_id == user_id,
            )
            .first()
        )

        if membership is None:
            raise ValueError(
                "User is not a member of this workspace."
            )

        return WorkspaceIdentity(

            workspace_id=membership.workspace_id,

            user_id=membership.user_id,

            membership_id=membership.id,

            role=membership.role,

            status=getattr(membership, "status", "active"),

            invited_by=getattr(membership, "invited_by", None),

            joined_at=getattr(membership, "joined_at", None),

            created_at=getattr(membership, "created_at", None),

            updated_at=getattr(membership, "updated_at", None),

        )
from sqlalchemy.orm import Session

from app.models.workspace_membership import WorkspaceMembership


def resolve_workspace_role(
    db: Session,
    workspace_id: int,
    user_id: int,
):

    membership = (

        db.query(

            WorkspaceMembership

        )

        .filter(

            WorkspaceMembership.workspace_id == workspace_id,

            WorkspaceMembership.user_id == user_id,

        )

        .first()

    )

    if membership is None:

        return None

    return membership.role.lower()
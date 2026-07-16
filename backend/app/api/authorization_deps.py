from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db

from app.api.deps import get_current_user

from app.models.user import User


from app.services.authorization.engine.authorization_service import (
    AuthorizationService,
)

from app.services.authorization.engine.authorization_exceptions import (
    AuthorizationError,
)


def require_page(
    page: str,
) -> Callable:

    def dependency(

        workspace_id: int,

        db: Session = Depends(get_db),

        current_user: User = Depends(get_current_user),

    ):

        context = AccessContextBuilder.build(

            db=db,

            workspace_id=workspace_id,

            current_user=current_user,

        )

        try:

            AuthorizationService.require_page(

                context.access,

                page,

            )

        except AuthorizationError as exc:

            raise HTTPException(

                status_code=403,

                detail=str(exc),

            )

        return context

    return dependency


def require_capability(
    capability: str,
) -> Callable:

    def dependency(

        workspace_id: int,

        db: Session = Depends(get_db),

        current_user: User = Depends(get_current_user),

    ):

        context = AccessContextBuilder.build(

            db=db,

            workspace_id=workspace_id,

            current_user=current_user,

        )

        try:

            AuthorizationService.require_capability(

                context.access,

                capability,

            )

        except AuthorizationError as exc:

            raise HTTPException(

                status_code=403,

                detail=str(exc),

            )

        return context

    return dependency

from app.services.authorization.context.workspace_context_builder import (
    WorkspaceContextBuilder,
)


from app.services.authorization.context.workspace_context_builder import (
    WorkspaceContextBuilder,
)


def require_workspace_context(
    page: str,
):

    def dependency(

        workspace_id: int,

        db: Session = Depends(get_db),

        current_user: User = Depends(get_current_user),

    ):

        context = WorkspaceContextBuilder.build(
            db=db,
            workspace_id=workspace_id,
            current_user=current_user,
        )

        #
        # Build the authenticated workspace context.
        #
        # Commercial plan gating is enforced
        # by enforce_workspace_page_access()
        # inside each endpoint.
        #

        return context

    return dependency
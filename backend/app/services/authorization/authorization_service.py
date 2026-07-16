from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.user import User

from app.services.authorization.role_resolver import (
    resolve_workspace_role,
)

from app.services.authorization.permission_matrix import (
    PERMISSION_MATRIX,
)

from fastapi import HTTPException


class AuthorizationService:

    @staticmethod
    def get_workspace_role(
        db: Session,
        workspace_id: int,
        current_user: User,
    ):

        return resolve_workspace_role(
            db=db,
            workspace_id=workspace_id,
            user_id=current_user.id,
        )

    @staticmethod
    def get_capabilities(
        db: Session,
        workspace_id: int,
        current_user: User,
    ):

        role = AuthorizationService.get_workspace_role(
            db,
            workspace_id,
            current_user,
        )

        if role is None:
            return set()

        return IAMRegistry.capabilities_for_role(role)

    @staticmethod
    def has_capability(
        db: Session,
        workspace_id: int,
        current_user: User,
        capability: str,
    ):

        capabilities = AuthorizationService.get_capabilities(
            db,
            workspace_id,
            current_user,
        )

        return capability in capabilities

    @staticmethod
    def can_access_page(
        db: Session,
        workspace_id: int,
        current_user: User,
        required_capabilities: set[str],
    ):

        capabilities = AuthorizationService.get_capabilities(
            db,
            workspace_id,
            current_user,
        )

        return required_capabilities.issubset(capabilities)

    @staticmethod
    def require_capability(
        db,
        workspace_id,
        current_user,
        capability,
    ):

        if not AuthorizationService.has_capability(
            db,
            workspace_id,
            current_user,
            capability,
        ):
            raise HTTPException(
                status_code=403,
                detail=f"Missing capability: {capability}",
            )

    @staticmethod
    def require_page(
        db,
        workspace_id,
        current_user,
        required_capabilities,
    ):

        if not AuthorizationService.can_access_page(
            db,
            workspace_id,
            current_user,
            required_capabilities,
        ):
            raise HTTPException(
                status_code=403,
                detail="Access denied",
            )
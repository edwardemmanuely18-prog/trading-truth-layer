from __future__ import annotations

from app.services.authorization.context.access_context import (
    AccessContext,
)

from app.services.authorization.registry.permission_matrix import (
    ROLE_CAPABILITIES,
)

from app.services.authorization.registry.iam_registry import (
    PAGE_CAPABILITIES,
)

from .authorization_exceptions import (
    CapabilityDeniedError,
    PageAccessDeniedError,
)


class AuthorizationService:

    @staticmethod
    def capabilities(
        context: AccessContext,
    ) -> set[str]:

        return set(
            ROLE_CAPABILITIES.get(
                context.identity.role,
                set(),
            )
        )

    @staticmethod
    def role(
        context: AccessContext,
    ) -> str:

        return context.identity.role

    @staticmethod
    def has_capability(
        context: AccessContext,
        capability: str,
    ) -> bool:

        return (
            capability
            in AuthorizationService.capabilities(context)
        )

    @staticmethod
    def missing_capabilities(
        context: AccessContext,
        required: set[str],
    ) -> set[str]:

        return required.difference(
            AuthorizationService.capabilities(
                context,
            )
        )

    @staticmethod
    def require_capability(
        context: AccessContext,
        capability: str,
    ) -> None:

        if not AuthorizationService.has_capability(
            context,
            capability,
        ):
            raise CapabilityDeniedError(
                f"Missing capability: {capability}"
            )

    @staticmethod
    def can_access_page(
        context: AccessContext,
        page: str,
    ) -> bool:

        if page not in context.enabled_pages:
            return False

        required = PAGE_CAPABILITIES.get(
            page,
            set(),
        )

        capabilities = AuthorizationService.capabilities(
            context,
        )

        return required.issubset(
            capabilities,
        )

    @staticmethod
    def require_page(
        context: AccessContext,
        page: str,
    ) -> None:

        if not AuthorizationService.can_access_page(
            context,
            page,
        ):
            raise PageAccessDeniedError(
                f"Access denied: {page}"
            )
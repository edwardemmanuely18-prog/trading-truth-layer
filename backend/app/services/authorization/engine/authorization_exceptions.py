from __future__ import annotations


class AuthorizationError(PermissionError):
    """
    Base authorization exception.
    """


class CapabilityDeniedError(AuthorizationError):
    """
    Raised when a capability is missing.
    """


class PageAccessDeniedError(AuthorizationError):
    """
    Raised when a page cannot be accessed.
    """

class WorkspaceAccessDeniedError(
    AuthorizationError,
):
    """
    Raised when the authenticated user
    is not a member of the workspace.
    """
from __future__ import annotations

from app.services.governance.context.membership_context import (
    MembershipContext,
)


# ==========================================================
# AUTHORITY LEVELS
# ==========================================================

CRITICAL = "Critical"

HIGH = "High"

MEDIUM = "Medium"

STANDARD = "Standard"


# ==========================================================
# PUBLIC API
# ==========================================================

def build_authority(
    context: MembershipContext,
) -> str:
    """
    Resolve the effective authority level for a workspace identity.

    This builder is the canonical authority classifier.
    It intentionally evaluates authority independently from
    the permission engine so that delegated authority,
    temporary elevation and policy overrides can be introduced
    later without changing callers.
    """

    role = context.membership.role.lower()

    if role == "owner":
        return CRITICAL

    if role == "operator":
        return HIGH

    if role == "auditor":
        return MEDIUM

    return STANDARD
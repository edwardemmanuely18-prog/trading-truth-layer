from __future__ import annotations

from dataclasses import dataclass

from app.services.governance.context.membership_context import (
    MembershipContext,
)


# ==========================================================
# MODELS
# ==========================================================

@dataclass(slots=True)
class OperationalResponsibility:

    name: str

    category: str

    critical: bool = False


# ==========================================================
# RESPONSIBILITY MAP
# ==========================================================

_OWNER = [

    OperationalResponsibility(
        "Workspace Governance",
        "Governance",
        True,
    ),

    OperationalResponsibility(
        "Identity Management",
        "Governance",
        True,
    ),

    OperationalResponsibility(
        "Commercial Operations",
        "Business",
        False,
    ),

    OperationalResponsibility(
        "Billing",
        "Business",
        False,
    ),

    OperationalResponsibility(
        "Compliance",
        "Governance",
        True,
    ),

]

_OPERATOR = [

    OperationalResponsibility(
        "Claims",
        "Operations",
        True,
    ),

    OperationalResponsibility(
        "Evidence",
        "Operations",
        True,
    ),

    OperationalResponsibility(
        "Verification",
        "Operations",
        True,
    ),

    OperationalResponsibility(
        "Reports",
        "Operations",
        False,
    ),

]

_AUDITOR = [

    OperationalResponsibility(
        "Audit",
        "Compliance",
        True,
    ),

    OperationalResponsibility(
        "Evidence Review",
        "Compliance",
        True,
    ),

    OperationalResponsibility(
        "Independent Verification",
        "Compliance",
        True,
    ),

]

_MEMBER = [

    OperationalResponsibility(
        "Own Claims",
        "Participation",
        False,
    ),

    OperationalResponsibility(
        "Evidence Upload",
        "Participation",
        False,
    ),

]


# ==========================================================
# PUBLIC API
# ==========================================================

def build_operational_responsibilities(
    context: MembershipContext,
) -> list[OperationalResponsibility]:
    """
    Resolve the canonical operational responsibilities
    for a workspace identity.

    Future versions may augment these responsibilities
    using delegated authority, policy packs, or
    commercial entitlements.
    """

    role = context.membership.role.lower()

    if role == "owner":
        return _OWNER

    if role == "operator":
        return _OPERATOR

    if role == "auditor":
        return _AUDITOR

    return _MEMBER
from __future__ import annotations

from app.services.governance.context.membership_context import (
    MembershipContext,
)

from app.services.governance.identity_models import (
    IdentityGovernanceProfile,
)


# ==========================================================
# AUTHORITY
# ==========================================================

_AUTHORITY = {

    "owner": "Critical",

    "operator": "Operational",

    "auditor": "Independent",

    "member": "Standard",

}


# ==========================================================
# RESPONSIBILITY
# ==========================================================

_SCOPE = {

    "owner": [

        "Workspace Governance",

        "Commercial",

        "Billing",

        "Identity",

        "Compliance",

    ],

    "operator": [

        "Claims",

        "Evidence",

        "Verification",

        "Reports",

    ],

    "auditor": [

        "Audit",

        "Compliance",

        "Evidence",

        "Independent Review",

    ],

    "member": [

        "Own Claims",

        "Evidence Upload",

        "Participation",

    ],

}


# ==========================================================
# GOVERNANCE STATUS
# ==========================================================

_STATUS = {

    "owner": "Critical",

    "operator": "Operational",

    "auditor": "Independent",

    "member": "Standard",

}


# ==========================================================
# PUBLIC API
# ==========================================================

def evaluate_identity(

    context: MembershipContext,

) -> IdentityGovernanceProfile:

    role = context.membership.role.lower()

    return IdentityGovernanceProfile(

        user_id=context.user.id,

        workspace_role=role,

        authority=_AUTHORITY.get(

            role,

            "Standard",

        ),

        operational_scope=_SCOPE.get(

            role,

            _SCOPE["member"],

        ),

        governance_status=_STATUS.get(

            role,

            "Standard",

        ),

        permissions=context.permissions,

    )
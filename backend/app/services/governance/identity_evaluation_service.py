from __future__ import annotations

from app.models.user import User

from .identity_models import (
    IdentityGovernanceProfile,
)

from .permission_resolution_service import (
    resolve_permission_matrix,
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
# RESPONSIBILITIES
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

        "Independent Review",

        "Evidence Validation",

    ],

    "member": [

        "Participation",

        "Evidence Submission",

        "Own Claims",

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

def build_identity_profile(

    member,

) -> IdentityGovernanceProfile:

    from .governance_roles import GovernanceRole

    role = GovernanceRole.normalize(
        member.role,
    )

    return IdentityGovernanceProfile(

        user_id=member.user_id,

        workspace_role=role.value,

        authority=_AUTHORITY.get(role.value, "Standard"),

        operational_scope=_SCOPE.get(

            role.value,

            _SCOPE["member"],

        ),

        governance_status=_STATUS.get(

            role.value,

            "Standard",

        ),

        permissions=resolve_permission_matrix(

            role.value,

        ),

    )
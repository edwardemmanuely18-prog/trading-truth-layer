from __future__ import annotations

from .capabilities import Capability
from .identity_models import PermissionMatrix


_OWNER = PermissionMatrix(
    capabilities={
        Capability.INVITE_MEMBER,
        Capability.REMOVE_MEMBER,
        Capability.MANAGE_ROLES,
        Capability.TRANSFER_OWNERSHIP,

        Capability.CLAIM_CREATE,
        Capability.CLAIM_EDIT,
        Capability.CLAIM_VERIFY,
        Capability.CLAIM_PUBLISH,
        Capability.CLAIM_LOCK,
        Capability.CLAIM_DELETE,

        Capability.EVIDENCE_UPLOAD,
        Capability.EVIDENCE_REVIEW,

        Capability.REPORT_GENERATE,

        Capability.WORKSPACE_SETTINGS,
        Capability.BRANDING,
        Capability.BILLING,

        Capability.TVS,
        Capability.TPS,
        Capability.TES,
        Capability.IGS,
    }
)

_OPERATOR = PermissionMatrix(
    capabilities={
        Capability.CLAIM_CREATE,
        Capability.CLAIM_EDIT,
        Capability.CLAIM_VERIFY,

        Capability.EVIDENCE_UPLOAD,
        Capability.EVIDENCE_REVIEW,

        Capability.REPORT_GENERATE,

        Capability.TVS,
        Capability.TPS,
        Capability.TES,
    }
)

_AUDITOR = PermissionMatrix(
    capabilities={
        Capability.EVIDENCE_REVIEW,
        Capability.REPORT_GENERATE,

        Capability.TVS,
        Capability.TPS,
        Capability.TES,
        Capability.IGS,
    }
)

_MEMBER = PermissionMatrix(
    capabilities={
        Capability.CLAIM_CREATE,
        Capability.EVIDENCE_UPLOAD,
    }
)


def resolve_permission_matrix(
    workspace_role: str | None,
) -> PermissionMatrix:

    role = (workspace_role or "member").strip().lower()

    match role:
        case "owner":
            return _OWNER
        case "operator":
            return _OPERATOR
        case "auditor":
            return _AUDITOR
        case _:
            return _MEMBER
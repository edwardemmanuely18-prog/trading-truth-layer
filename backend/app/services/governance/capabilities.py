from __future__ import annotations

from enum import StrEnum


class Capability(StrEnum):

    # =====================================================
    # Identity Governance
    # =====================================================

    INVITE_MEMBER = "identity.invite"

    REMOVE_MEMBER = "identity.remove"

    MANAGE_ROLES = "identity.roles.manage"

    TRANSFER_OWNERSHIP = "identity.owner.transfer"

    # =====================================================
    # Claims
    # =====================================================

    CLAIM_CREATE = "claim.create"

    CLAIM_EDIT = "claim.edit"

    CLAIM_VERIFY = "claim.verify"

    CLAIM_PUBLISH = "claim.publish"

    CLAIM_LOCK = "claim.lock"

    CLAIM_DELETE = "claim.delete"

    # =====================================================
    # Evidence
    # =====================================================

    EVIDENCE_UPLOAD = "evidence.upload"

    EVIDENCE_REVIEW = "evidence.review"

    # =====================================================
    # Reports
    # =====================================================

    REPORT_GENERATE = "report.generate"

    # =====================================================
    # Workspace
    # =====================================================

    WORKSPACE_SETTINGS = "workspace.settings"

    BRANDING = "workspace.branding"

    BILLING = "workspace.billing"

    # =====================================================
    # Canonical Systems
    # =====================================================

    TVS = "system.tvs"

    TPS = "system.tps"

    TES = "system.tes"

    IGS = "system.igs"
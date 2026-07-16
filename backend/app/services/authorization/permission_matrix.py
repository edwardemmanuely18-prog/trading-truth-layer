from __future__ import annotations

from .capability_catalog import *


# ============================================================
# OWNER
# ============================================================

_OWNER = {

    # Dashboard
    DASHBOARD_READ,

    # Members
    MEMBER_READ,
    MEMBER_INVITE,
    MEMBER_UPDATE,
    MEMBER_REMOVE,

    # Claims
    CLAIM_READ,
    CLAIM_CREATE,
    CLAIM_UPDATE,
    CLAIM_DELETE,
    CLAIM_VERIFY,

    # Evidence
    EVIDENCE_READ,
    EVIDENCE_IMPORT,
    EVIDENCE_VERIFY,

    # Reports
    REPORT_READ,
    REPORT_GENERATE,

    # Verification
    VERIFICATION_READ,
    VERIFICATION_EXECUTE,

    # Institutional Investigations
    INVESTIGATION_READ,
    INVESTIGATION_EXECUTE,

    # Governance
    GOVERNANCE_READ,
    GOVERNANCE_UPDATE,

    # Billing
    BILLING_READ,
    BILLING_UPDATE,

    # Workspace Settings
    SETTINGS_READ,
    SETTINGS_UPDATE,
}


# ============================================================
# OPERATOR
# ============================================================

_OPERATOR = {

    DASHBOARD_READ,

    MEMBER_READ,

    CLAIM_READ,
    CLAIM_CREATE,
    CLAIM_UPDATE,

    EVIDENCE_READ,
    EVIDENCE_IMPORT,

    REPORT_READ,
    INVESTIGATION_READ,
    REPORT_GENERATE,
}


# ============================================================
# AUDITOR
# ============================================================

_AUDITOR = {

    DASHBOARD_READ,

    MEMBER_READ,

    CLAIM_READ,

    EVIDENCE_READ,

    REPORT_READ,

    VERIFICATION_READ,

    INVESTIGATION_READ,

    GOVERNANCE_READ,
}


# ============================================================
# MEMBER
# ============================================================

_MEMBER = {

    DASHBOARD_READ,

    CLAIM_READ,

}


# ============================================================
# CANONICAL ROLE CAPABILITIES
# ============================================================

ROLE_CAPABILITIES = {

    "owner": _OWNER,

    "operator": _OPERATOR,

    "auditor": _AUDITOR,

    "member": _MEMBER,

}
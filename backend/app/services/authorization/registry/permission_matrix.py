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

    # Broker Connections
    BROKER_CONNECTION_READ,
    BROKER_CONNECTION_WRITE,

    # Reports
    REPORT_READ,
    REPORT_GENERATE,

    # Verification
    VERIFICATION_READ,
    VERIFICATION_EXECUTE,

    # Investigation
    INVESTIGATION_READ,
    INVESTIGATION_EXECUTE,
    INVESTIGATION_ASSIGN,
    INVESTIGATION_APPROVE,

    # Governance
    GOVERNANCE_READ,
    GOVERNANCE_UPDATE,

    # Billing
    BILLING_READ,
    BILLING_UPDATE,

    # Settings
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

    BROKER_CONNECTION_READ,
    BROKER_CONNECTION_WRITE,

    INVESTIGATION_READ,
    INVESTIGATION_EXECUTE,

    REPORT_READ,
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

    BROKER_CONNECTION_READ,

    REPORT_READ,

    VERIFICATION_READ,

    GOVERNANCE_READ,

    INVESTIGATION_READ,
    
    INVESTIGATION_APPROVE,
}


# ============================================================
# MEMBER
# ============================================================

_MEMBER = {

    DASHBOARD_READ,

    CLAIM_READ,

    BROKER_CONNECTION_READ,
}


# ============================================================
# ROLE → CAPABILITIES
# ============================================================

ROLE_CAPABILITIES = {

    "owner": _OWNER,

    "operator": _OPERATOR,

    "auditor": _AUDITOR,

    "member": _MEMBER,

}
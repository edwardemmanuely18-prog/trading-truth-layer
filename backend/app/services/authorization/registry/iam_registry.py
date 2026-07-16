from __future__ import annotations

from .capability_catalog import *


PAGE_CAPABILITIES = {

    #
    # Dashboard
    #
    "dashboard": {
        DASHBOARD_READ,
    },

    #
    # Members
    #
    "members": {
        MEMBER_READ,
    },

    #
    # Roles
    #
    "roles": {
        MEMBER_READ,
        GOVERNANCE_READ,
    },

    #
    # Billing
    #
    "billing": {
        BILLING_READ,
    },

    #
    # Settings
    #
    "settings": {
        SETTINGS_READ,
    },

    #
    # Claims
    #
    "claims": {
        CLAIM_READ,
    },

    #
    # Evidence
    #
    "evidence": {
        EVIDENCE_READ,
    },

    #
    # Verification
    #
    "verification": {
        VERIFICATION_READ,
    },

    #
    # Reports
    #
    "reports": {
        REPORT_READ,
    },
}
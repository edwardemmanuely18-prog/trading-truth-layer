from __future__ import annotations

# ============================================================
# Dashboard
# ============================================================

DASHBOARD_READ = "dashboard.read"

# ============================================================
# Members
# ============================================================

MEMBER_READ = "member.read"

MEMBER_INVITE = "member.invite"

MEMBER_UPDATE = "member.update"

MEMBER_REMOVE = "member.remove"

# ============================================================
# Claims
# ============================================================

CLAIM_READ = "claim.read"

CLAIM_CREATE = "claim.create"

CLAIM_UPDATE = "claim.update"

CLAIM_DELETE = "claim.delete"

CLAIM_VERIFY = "claim.verify"

# ============================================================
# Evidence
# ============================================================

EVIDENCE_READ = "evidence.read"

EVIDENCE_IMPORT = "evidence.import"

EVIDENCE_VERIFY = "evidence.verify"

# ============================================================
# Broker Connections
# ============================================================

BROKER_CONNECTION_READ = "broker_connection.read"

BROKER_CONNECTION_WRITE = "broker_connection.write"

# ============================================================
# Investigation
# ============================================================

INVESTIGATION_READ = "investigation.read"

INVESTIGATION_EXECUTE = "investigation.execute"

INVESTIGATION_ASSIGN = "investigation.assign"

INVESTIGATION_APPROVE = "investigation.approve"

# ============================================================
# Reports
# ============================================================

REPORT_READ = "report.read"

REPORT_GENERATE = "report.generate"

# ============================================================
# Verification
# ============================================================

VERIFICATION_READ = "verification.read"

VERIFICATION_EXECUTE = "verification.execute"

# ============================================================
# Governance
# ============================================================

GOVERNANCE_READ = "governance.read"

GOVERNANCE_UPDATE = "governance.update"

# ============================================================
# Billing
# ============================================================

BILLING_READ = "billing.read"

BILLING_UPDATE = "billing.update"

# ============================================================
# Settings
# ============================================================

SETTINGS_READ = "settings.read"

SETTINGS_UPDATE = "settings.update"

# ============================================================
# Workspace Roles
# ============================================================

WORKSPACE_ASSIGNABLE_ROLES = frozenset(
    {
        "member",
        "operator",
        "auditor",
    }
)
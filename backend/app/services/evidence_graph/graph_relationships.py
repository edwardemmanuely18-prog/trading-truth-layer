"""
Trading Truth Layer (TTL)
Institutional Evidence Graph Engine

Canonical Graph Relationship Registry

This module defines every supported relationship type used by the
Evidence Graph.

These constants represent the semantic meaning of graph edges and must
be used throughout the platform instead of hardcoded strings.

Subsystems using this registry:

- Evidence Graph
- Verification Network
- Trust Intelligence
- Evidence Analytics
- Integrity Scanner
- Public Verification
- Future AI Investigator

Never hardcode relationship names elsewhere.
"""

#
# ---------------------------------------------------------------------
# CLAIM RELATIONSHIPS
# ---------------------------------------------------------------------
#

CLAIM_HAS_SCHEMA = "CLAIM_HAS_SCHEMA"

CLAIM_CONTAINS_TRADE = "CLAIM_CONTAINS_TRADE"

CLAIM_HAS_REVIEW = "CLAIM_HAS_REVIEW"

CLAIM_HAS_DISPUTE = "CLAIM_HAS_DISPUTE"

CLAIM_HAS_AUDIT_EVENT = "CLAIM_HAS_AUDIT_EVENT"

CLAIM_HAS_INTEGRITY_ALERT = "CLAIM_HAS_INTEGRITY_ALERT"

CLAIM_HAS_INTEGRITY_SCAN = "CLAIM_HAS_INTEGRITY_SCAN"

CLAIM_HAS_PUBLIC_RECORD = "CLAIM_HAS_PUBLIC_RECORD"

CLAIM_HAS_VERIFICATION = "CLAIM_HAS_VERIFICATION"


#
# ---------------------------------------------------------------------
# TRADE RELATIONSHIPS
# ---------------------------------------------------------------------
#

TRADE_EXECUTED_ON_ACCOUNT = "TRADE_EXECUTED_ON_ACCOUNT"

TRADE_SYNCED_FROM_CONNECTION = "TRADE_SYNCED_FROM_CONNECTION"

TRADE_IMPORTED_FROM_BATCH = "TRADE_IMPORTED_FROM_BATCH"

TRADE_GENERATED_BY_ADAPTER = "TRADE_GENERATED_BY_ADAPTER"

TRADE_HAS_HASH = "TRADE_HAS_HASH"

TRADE_HAS_FINGERPRINT = "TRADE_HAS_FINGERPRINT"

TRADE_HAS_PROVENANCE = "TRADE_HAS_PROVENANCE"

TRADE_HAS_INTEGRITY = "TRADE_HAS_INTEGRITY"

TRADE_HAS_RISK = "TRADE_HAS_RISK"

TRADE_RECORDED_IN_LEDGER = "TRADE_RECORDED_IN_LEDGER"


#
# ---------------------------------------------------------------------
# IMPORT RELATIONSHIPS
# ---------------------------------------------------------------------
#

IMPORT_BATCH_IMPORTED_BY = "IMPORT_BATCH_IMPORTED_BY"

IMPORT_BATCH_GENERATED_TRADES = "IMPORT_BATCH_GENERATED_TRADES"

IMPORT_BATCH_LINKED_TO_WORKSPACE = "IMPORT_BATCH_LINKED_TO_WORKSPACE"


#
# ---------------------------------------------------------------------
# BROKER RELATIONSHIPS
# ---------------------------------------------------------------------
#

BROKER_CONNECTION_HAS_ACCOUNT = "BROKER_CONNECTION_HAS_ACCOUNT"

BROKER_CONNECTION_HAS_SNAPSHOT = "BROKER_CONNECTION_HAS_SNAPSHOT"

BROKER_CONNECTION_SYNCED_TRADE = "BROKER_CONNECTION_SYNCED_TRADE"

BROKER_ACCOUNT_HAS_SNAPSHOT = "BROKER_ACCOUNT_HAS_SNAPSHOT"


#
# ---------------------------------------------------------------------
# GOVERNANCE RELATIONSHIPS
# ---------------------------------------------------------------------
#

CLAIM_VERIFIED_BY = "CLAIM_VERIFIED_BY"

CLAIM_LOCKED_BY = "CLAIM_LOCKED_BY"

CLAIM_PUBLISHED_BY = "CLAIM_PUBLISHED_BY"

CLAIM_CREATED_BY = "CLAIM_CREATED_BY"

CLAIM_UPDATED_BY = "CLAIM_UPDATED_BY"

CLAIM_REVIEWED_BY = "CLAIM_REVIEWED_BY"

CLAIM_AUDITED_BY = "CLAIM_AUDITED_BY"


#
# ---------------------------------------------------------------------
# INTEGRITY RELATIONSHIPS
# ---------------------------------------------------------------------
#

INTEGRITY_SCANNED_BY = "INTEGRITY_SCANNED_BY"

INTEGRITY_FLAGGED_BY = "INTEGRITY_FLAGGED_BY"

INTEGRITY_HAS_EXCEPTION = "INTEGRITY_HAS_EXCEPTION"

INTEGRITY_DUPLICATE_OF = "INTEGRITY_DUPLICATE_OF"

INTEGRITY_HASH_MATCH = "INTEGRITY_HASH_MATCH"

INTEGRITY_HASH_MISMATCH = "INTEGRITY_HASH_MISMATCH"

INTEGRITY_FINGERPRINT_MATCH = "INTEGRITY_FINGERPRINT_MATCH"

INTEGRITY_FINGERPRINT_MISMATCH = "INTEGRITY_FINGERPRINT_MISMATCH"


#
# ---------------------------------------------------------------------
# RISK RELATIONSHIPS
# ---------------------------------------------------------------------
#

RISK_GENERATED_FROM = "RISK_GENERATED_FROM"

RISK_FLAGS_TRADE = "RISK_FLAGS_TRADE"

RISK_FLAGS_CLAIM = "RISK_FLAGS_CLAIM"

RISK_CAUSED_BY = "RISK_CAUSED_BY"


#
# ---------------------------------------------------------------------
# PROVENANCE RELATIONSHIPS
# ---------------------------------------------------------------------
#

PROVENANCE_ORIGINATED_FROM = "PROVENANCE_ORIGINATED_FROM"

PROVENANCE_IMPORTED_FROM = "PROVENANCE_IMPORTED_FROM"

PROVENANCE_SYNCED_FROM = "PROVENANCE_SYNCED_FROM"

PROVENANCE_CREATED_MANUALLY = "PROVENANCE_CREATED_MANUALLY"


#
# ---------------------------------------------------------------------
# WORKSPACE RELATIONSHIPS
# ---------------------------------------------------------------------
#

WORKSPACE_HAS_CLAIM = "WORKSPACE_HAS_CLAIM"

WORKSPACE_HAS_TRADE = "WORKSPACE_HAS_TRADE"

WORKSPACE_HAS_IMPORT = "WORKSPACE_HAS_IMPORT"

WORKSPACE_HAS_BROKER_CONNECTION = "WORKSPACE_HAS_BROKER_CONNECTION"

WORKSPACE_HAS_AUDIT = "WORKSPACE_HAS_AUDIT"

WORKSPACE_HAS_ALERT = "WORKSPACE_HAS_ALERT"

WORKSPACE_HAS_SCAN = "WORKSPACE_HAS_SCAN"


#
# ---------------------------------------------------------------------
# GENERIC RELATIONSHIPS
# ---------------------------------------------------------------------
#

BELONGS_TO = "BELONGS_TO"

GENERATED_FROM = "GENERATED_FROM"

LINKED_TO = "LINKED_TO"

USES = "USES"

PRODUCED = "PRODUCED"

CONNECTED_TO = "CONNECTED_TO"

DEPENDS_ON = "DEPENDS_ON"

REFERENCES = "REFERENCES"

ASSOCIATED_WITH = "ASSOCIATED_WITH"


#
# ---------------------------------------------------------------------
# RELATIONSHIP CONFIDENCE
# ---------------------------------------------------------------------
#

CONFIDENCE_VERIFIED = "verified"

CONFIDENCE_STRONG = "strong"

CONFIDENCE_INFERRED = "inferred"

CONFIDENCE_WEAK = "weak"


#
# ---------------------------------------------------------------------
# VALID RELATIONSHIP SET
# ---------------------------------------------------------------------
#

ALL_RELATIONSHIPS = {
    value
    for key, value in globals().items()
    if key.isupper()
    and isinstance(value, str)
}
from app.services.integrity.ledger_scanner import (
    scan_ledger_integrity,
)

from app.services.integrity.lifecycle_scanner import (
    scan_lifecycle_integrity,
)

from app.services.integrity.evidence_scanner import (
    scan_evidence_integrity,
)

from app.services.integrity.audit_scanner import (
    scan_audit_integrity,
)

from app.services.integrity.governance_scanner import (
    scan_governance_integrity,
)

from app.services.integrity.verification_scanner import (
    scan_verification_integrity,
)

from app.services.integrity.metrics_scanner import (
    scan_metrics_integrity,
)

from app.services.integrity.public_scanner import (
    scan_public_integrity,
)

from app.services.integrity.evidence_authenticity_scanner import (
    scan_evidence_authenticity_integrity,
)



def run_full_integrity_scan(
    db,
    workspace_id,
):
    scan_ledger_integrity(
        db,
        workspace_id,
    )

    scan_lifecycle_integrity(
        db,
        workspace_id,
    )

    scan_evidence_integrity(
        db,
        workspace_id,
    )

    scan_audit_integrity(
        db,
        workspace_id,
    )

    scan_governance_integrity(
        db,
        workspace_id,
    )

    scan_verification_integrity(
        db,
        workspace_id,
    )

    scan_metrics_integrity(
        db,
        workspace_id,
    )

    scan_public_integrity(
        db,
        workspace_id,
    )

    scan_evidence_authenticity_integrity(
        db,
        workspace_id,
    )

    db.commit()
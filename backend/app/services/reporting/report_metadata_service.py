from datetime import datetime

from app.services.reporting.report_hash_service import (
    generate_report_hash,
)


def build_report_metadata(
    report_type: str,
    workspace_id: int,
    claim_schema_id: int | None = None,
):
    report_hash = generate_report_hash(
        report_type=report_type,
        workspace_id=workspace_id,
        claim_schema_id=claim_schema_id,
    )

    return {
        "report_hash": report_hash,
        "report_type": report_type,
        "workspace_id": workspace_id,
        "claim_schema_id": claim_schema_id,
        "generated_at": (
            datetime.utcnow()
            .isoformat()
        ),
        "verification_url": (
            f"/report-verification/"
            f"{report_hash}"
        ),
    }
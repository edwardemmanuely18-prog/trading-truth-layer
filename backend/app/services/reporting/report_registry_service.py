from app.models.report_record import (
    ReportRecord,
)


def register_report(
    db,
    workspace_id: int,
    report_type: str,
    report_hash: str,
    claim_schema_id: int | None = None,
):

    record = ReportRecord(
        workspace_id=workspace_id,
        claim_schema_id=claim_schema_id,
        report_type=report_type,
        report_hash=report_hash,
    )

    db.add(record)

    db.commit()

    db.refresh(record)

    return record
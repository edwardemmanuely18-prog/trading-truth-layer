import json

from datetime import datetime

from app.models.integrity_scan import (
    IntegrityScan,
)


def create_scan_record(
    db,
    workspace_id,
    claims_scanned,
    alerts_found,
    summary,
):
    scan = IntegrityScan(
        workspace_id=workspace_id,
        status="completed",
        claims_scanned=claims_scanned,
        alerts_found=alerts_found,
        summary_json=json.dumps(summary),
        completed_at=datetime.utcnow(),
    )

    db.add(scan)
    db.commit()

    return scan
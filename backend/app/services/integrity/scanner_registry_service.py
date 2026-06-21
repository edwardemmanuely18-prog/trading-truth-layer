from app.models.integrity_alert import (
    IntegrityAlert,
)


SCANNERS = [
    "ledger",
    "lifecycle",
    "evidence",
    "governance",
    "verification",
    "metrics",
    "public",
    "authenticity",
]


def build_scanner_status(
    db,
    workspace_id,
):
    scanners = {
        scanner: {
            "status": "healthy",
            "findings": 0,
        }
        for scanner in SCANNERS
    }

    alerts = (
        db.query(IntegrityAlert)
        .filter(
            IntegrityAlert.workspace_id
            == workspace_id
        )
        .all()
    )

    for alert in alerts:

        alert_type = (
            str(
                alert.alert_type
                or ""
            )
            .upper()
        )

        if (
            "HASH"
            in alert_type
        ):
            scanner = "lifecycle"

        elif (
            "LEDGER"
            in alert_type
        ):
            scanner = "ledger"

        elif (
            "EVIDENCE"
            in alert_type
        ):
            scanner = "evidence"

        elif (
            "PUBLIC"
            in alert_type
        ):
            scanner = "public"

        elif (
            "VERIFICATION"
            in alert_type
        ):
            scanner = "verification"

        else:
            scanner = "authenticity"

        scanners[
            scanner
        ]["status"] = "warning"

        scanners[
            scanner
        ]["findings"] += 1

    return scanners
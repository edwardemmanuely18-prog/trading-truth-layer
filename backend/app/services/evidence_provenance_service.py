import hashlib
import json


def build_evidence_snapshot(trades):
    rows = []

    for trade in trades:
        rows.append(
            {
                "id": trade.id,
                "raw_trade_hash": trade.raw_trade_hash,
                "source_system": trade.source_system,
                "broker_connection_id":
                    trade.broker_connection_id,
                "import_job_id":
                    trade.import_job_id,
            }
        )

    payload = json.dumps(
        rows,
        sort_keys=True,
    )

    return hashlib.sha256(
        payload.encode("utf-8")
    ).hexdigest()
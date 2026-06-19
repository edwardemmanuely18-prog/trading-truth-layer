from sqlalchemy.orm import Session

from app.models.trade import Trade

from app.services.evidence_classification_service import (
    classify_trade,
)


def get_evidence_records(
    db: Session,
    workspace_id: int,
):
    trades = (
        db.query(Trade)
        .filter(
            Trade.workspace_id == workspace_id
        )
        .order_by(
            Trade.id.desc()
        )
        .all()
    )

    records = []

    for trade in trades:

        classification = (
            classify_trade(trade)
        )

        records.append({
            "trade_id": trade.id,

            "symbol": trade.symbol,

            "side": trade.side,

            "source_system":
                trade.source_system,

            "verification_state":
                classification[
                    "verification_state"
                ],

            "evidence_trust_tier":
                classification[
                    "evidence_trust_tier"
                ],

            "integrity_type":
                classification[
                    "integrity_type"
                ],

            "import_source":
                trade.import_source,

            "import_job_id":
                trade.import_job_id,

            "broker_connection_id":
                trade.broker_connection_id,

            "broker_account_id":
                trade.broker_account_id,

            "broker_trade_id":
                trade.broker_trade_id,

            "raw_trade_hash":
                trade.raw_trade_hash,

            "trade_fingerprint":
                trade.trade_fingerprint,

            "ingestion_timestamp":
                trade.ingestion_timestamp,
        })

    return records
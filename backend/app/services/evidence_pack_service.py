import json
import zipfile
from io import BytesIO
from datetime import datetime


def build_evidence_zip(schema, trades, audit_events):
    buffer = BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
        # 📦 claim metadata
        z.writestr(
            "claim.json",
            json.dumps({
                "id": schema.id,
                "name": schema.name,
                "status": schema.status,
                "created_at": str(datetime.utcnow())
            }, indent=2),
        )

        # 📊 trades
        z.writestr(
            "trades.json",
            json.dumps([
                {
                    "id": t.id,
                    "symbol": t.symbol,
                    "pnl": t.net_pnl,
                } for t in trades
            ], indent=2),
        )

        # 🧾 audit log
        z.writestr(
            "audit.json",
            json.dumps([
                {
                    "event": e.event_type,
                    "entity": e.entity_id,
                } for e in audit_events
            ], indent=2),
        )

    buffer.seek(0)
    return buffer
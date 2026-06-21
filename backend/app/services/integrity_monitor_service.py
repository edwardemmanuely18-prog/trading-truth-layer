from datetime import datetime

import json

from app.models.claim_schema import ClaimSchema
from app.models.integrity_alert import IntegrityAlert

from app.services.claim_integrity_engine import (
    compute_trade_set_hash,
    resolve_schema_trades,
    compute_integrity_snapshot,
)

from app.services.claim_service import (
    compute_claim_hash,
)

from app.services.integrity.integrity_engine import (
    run_full_integrity_scan,
)

from app.services.integrity.common import (
    create_alert,
    SEVERITY_INFO,
    SEVERITY_WARNING,
    SEVERITY_HIGH,
    SEVERITY_CRITICAL,
    SEVERITY_FATAL,
)


def scan_locked_claims(
    db,
    workspace_id,
):
    run_full_integrity_scan(
        db,
        workspace_id,
    )



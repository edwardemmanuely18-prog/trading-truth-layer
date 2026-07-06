from datetime import datetime
import hashlib
import uuid


def generate_report_hash(
    report_type: str,
    workspace_id: int,
    claim_schema_id: int | None = None,
) -> str:

    seed = (
        f"{report_type}|"
        f"{workspace_id}|"
        f"{claim_schema_id}|"
        f"{datetime.utcnow().isoformat()}|"
        f"{uuid.uuid4()}"
    )

    return hashlib.sha256(
        seed.encode()
    ).hexdigest()
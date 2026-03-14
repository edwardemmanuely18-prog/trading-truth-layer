import hashlib
import json
from typing import Any

from app.models.claim_schema import ClaimSchema


def _normalized_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def build_claim_hash_payload(schema: ClaimSchema) -> dict:
    return {
        "claim_schema_id": schema.id,
        "workspace_id": schema.workspace_id,
        "name": schema.name,
        "period_start": schema.period_start,
        "period_end": schema.period_end,
        "included_member_ids_json": json.loads(schema.included_member_ids_json or "[]"),
        "included_symbols_json": json.loads(schema.included_symbols_json or "[]"),
        "excluded_trade_ids_json": json.loads(schema.excluded_trade_ids_json or "[]"),
        "methodology_notes": schema.methodology_notes,
        "visibility": schema.visibility,
        "status": schema.status,
        "parent_claim_id": schema.parent_claim_id,
        "root_claim_id": schema.root_claim_id,
        "version_number": schema.version_number,
        "verified_at": schema.verified_at.isoformat() if schema.verified_at else None,
        "published_at": schema.published_at.isoformat() if schema.published_at else None,
        "locked_at": schema.locked_at.isoformat() if schema.locked_at else None,
        "locked_trade_set_hash": schema.locked_trade_set_hash,
    }


def compute_claim_hash(schema: ClaimSchema) -> str:
    payload = build_claim_hash_payload(schema)
    raw = _normalized_json(payload)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
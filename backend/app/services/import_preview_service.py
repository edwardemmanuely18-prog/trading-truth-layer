from typing import Any

from app.services.trade_import import (
    process_import_rows,
    parse_rows_by_source,
)


def build_import_preview(
    *,
    workspace_id: int,
    source_type: str,
    file_bytes: bytes,
    existing_fingerprints: set[str] | None = None,
) -> dict[str, Any]:

    rows = parse_rows_by_source(
        source_type=source_type,
        file_bytes=file_bytes,
    )

    result = process_import_rows(
        rows,
        source_type=source_type,
        existing_fingerprints=existing_fingerprints or set(),
    )

    return {
        "workspace_id": workspace_id,
        "source_type": source_type,
        "rows_received": result["stats"]["received"],
        "rows_accepted": result["stats"]["accepted"],
        "rows_rejected": result["stats"]["rejected"],
        "rows_duplicates": result["stats"]["duplicates"],
        "normalized_preview": result["normalized"][:25],
        "rejected_preview": result["rejected"][:25],
        "duplicate_preview": result["duplicates"][:25],
    }
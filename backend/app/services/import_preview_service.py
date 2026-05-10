from typing import Any
import json

from sqlalchemy.orm import Session

from app.models.import_preview_session import (
    ImportPreviewSession,
)

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
        existing_fingerprints=(
            existing_fingerprints or set()
        ),
    )

    return {
        "workspace_id": workspace_id,
        "source_type": source_type,
        "rows_received": result["stats"]["received"],
        "rows_accepted": result["stats"]["accepted"],
        "rows_rejected": result["stats"]["rejected"],
        "rows_duplicates": result["stats"]["duplicates"],
        "normalized_preview": (
            result["normalized"][:25]
        ),
        "rejected_preview": (
            result["rejected"][:25]
        ),
        "duplicate_preview": (
            result["duplicates"][:25]
        ),
    }


def create_import_preview_session(
    *,
    db: Session,
    workspace_id: int,
    source_type: str,
    filename: str,
    preview_payload: dict,
):

    session = ImportPreviewSession(
        workspace_id=workspace_id,
        source_type=source_type,
        filename=filename,
        preview_payload_json=json.dumps(
            preview_payload
        ),
        status="pending_confirmation",
    )

    db.add(session)

    db.commit()

    db.refresh(session)

    return session


def get_import_preview_session(
    db: Session,
    preview_session_id: int,
):

    return (
        db.query(ImportPreviewSession)
        .filter(
            ImportPreviewSession.id
            == preview_session_id
        )
        .first()
    )


def mark_preview_session_confirmed(
    *,
    db: Session,
    preview_session: ImportPreviewSession,
):

    preview_session.status = "confirmed"

    db.add(preview_session)

    db.commit()

    db.refresh(preview_session)

    return preview_session


def mark_preview_session_rejected(
    *,
    db: Session,
    preview_session: ImportPreviewSession,
):

    preview_session.status = "rejected"

    db.add(preview_session)

    db.commit()

    db.refresh(preview_session)

    return preview_session
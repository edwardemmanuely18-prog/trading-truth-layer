"""
Trading Truth Layer (TTL)

V2 Evidence Registry API

Read-only API for the institutional V2 Evidence Registry.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from app.api.deps import (
    get_current_user,
    require_workspace_member,
)
from app.core.db import get_db
from app.models.user import User
from app.services.evidence_registry_v2_service import (
    get_v2_evidence_record,
    get_v2_evidence_registry_page,
    get_v2_evidence_packages_page,
    get_v2_evidence_registry_summary,
    search_v2_evidence_registry,
)

from sqlalchemy.orm import Session


router = APIRouter(
    prefix="/workspaces/{workspace_id}/evidence-registry/v2",
    tags=["V2 Evidence Registry"],
)


def _authorize_workspace(
    workspace_id: int,
    db: Session,
    current_user: User,
) -> None:
    require_workspace_member(
        workspace_id,
        current_user,
        db,
    )


# ------------------------------------------------------------------
# Registry
# ------------------------------------------------------------------

@router.get(
    "",
    summary="V2 Evidence Registry",
)
def evidence_registry_v2(
    workspace_id: int,
    page: int = 1,
    page_size: int = 50,
    evidence_type: str | None = None,
    evidence_types: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _authorize_workspace(
        workspace_id,
        db,
        current_user,
    )

    parsed_evidence_types = (
        [
            value.strip().upper()
            for value in evidence_types.split(",")
            if value.strip()
        ]
        if evidence_types
        else None
    )

    return get_v2_evidence_registry_page(
        workspace_id,
        page=page,
        page_size=page_size,
        evidence_type=evidence_type,
        evidence_types=parsed_evidence_types,
    )


@router.get(
    "/packages",
    summary="V2 Evidence Package Registry",
)
def evidence_packages_v2(
    workspace_id: int,
    page: int = 1,
    page_size: int = 25,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _authorize_workspace(
        workspace_id,
        db,
        current_user,
    )

    return get_v2_evidence_packages_page(
        workspace_id,
        page=page,
        page_size=page_size,
    )


# ------------------------------------------------------------------
# Summary
# ------------------------------------------------------------------

@router.get(
    "/summary",
    summary="V2 Evidence Registry Summary",
)
def evidence_registry_v2_summary(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _authorize_workspace(
        workspace_id,
        db,
        current_user,
    )

    return get_v2_evidence_registry_summary(
        workspace_id,
    )


# ------------------------------------------------------------------
# Search
# ------------------------------------------------------------------

@router.get(
    "/search",
    summary="Search V2 Evidence Registry",
)
def evidence_registry_v2_search(
    workspace_id: int,
    query: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _authorize_workspace(
        workspace_id,
        db,
        current_user,
    )

    return {
        "workspace_id": workspace_id,
        "query": query,
        "results": search_v2_evidence_registry(
            workspace_id,
            query,
        ),
    }


# ------------------------------------------------------------------
# Single record
# ------------------------------------------------------------------

@router.get(
    "/{canonical_evidence_id}",
    summary="Get V2 Evidence Registry Record",
)
def evidence_registry_v2_record(
    workspace_id: int,
    canonical_evidence_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _authorize_workspace(
        workspace_id,
        db,
        current_user,
    )

    record = get_v2_evidence_record(
        workspace_id,
        canonical_evidence_id,
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="V2 evidence record not found.",
        )

    return record
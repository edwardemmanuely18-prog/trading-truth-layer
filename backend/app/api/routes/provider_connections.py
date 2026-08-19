"""
Trading Truth Layer (TTL)

Provider Connections API

Canonical API for the institutional
Provider Connections domain.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from pydantic import BaseModel
from typing import Any

from app.services.provider_connections.service import (
    ProviderConnectionsService,
    provider_connections_service,
)

from app.services.provider_connections.models import (
    DesktopConnectionCreateResponse,
    ProviderConnectionDetailResponse,
    DesktopConnectionVerificationResponse,
)

# ============================================================================
# Router
# ============================================================================

router = APIRouter(

    prefix="/workspaces/{workspace_id}/provider-connections",

    tags=["Provider Connections"],

)


# ============================================================================
# Dependencies
# ============================================================================

# ============================================================================
# Request Models
# ============================================================================


class DesktopConnectionRequest(BaseModel):

    provider: str

    connection_name: str

    environment: str

    synchronization_profile: str

    evidence_categories: list[str]

    credentials: dict[str, Any]


def get_provider_connections_service(
) -> ProviderConnectionsService:
    """
    Canonical Provider Connections Service.
    """

    return provider_connections_service


# ============================================================================
# Overview
# ============================================================================


@router.get(

    "/overview",

    summary="Provider Connections Overview",

)
def overview(

    workspace_id: int,

    service: ProviderConnectionsService = Depends(

        get_provider_connections_service,

    ),

):

    return service.overview(
        workspace_id,
    )


# ============================================================================
# Engines
# ============================================================================


@router.get(

    "/engines",

    summary="Provider Connection Engines",

)
def engines(

    workspace_id: int,

    service: ProviderConnectionsService = Depends(

        get_provider_connections_service,

    ),

):

    return service.engines()


# ============================================================================
# Connections
# ============================================================================


@router.get(

    "/connections",

    summary="Provider Connections",

)
def connections(

    workspace_id: int,

    service: ProviderConnectionsService = Depends(

        get_provider_connections_service,

    ),

):

    return service.connections(
        workspace_id,
    )


# ============================================================================
# Activity
# ============================================================================


@router.get(

    "/activity",

    summary="Provider Connection Activity",

)
def activity(

    workspace_id: int,

    service: ProviderConnectionsService = Depends(

        get_provider_connections_service,

    ),

):

    return service.activity()


# ============================================================================
# Connection Detail
# ============================================================================

@router.get(
    "/{connection_id}",
    response_model=ProviderConnectionDetailResponse,
    summary="Provider Connection Detail",
)
def get_connection(
    workspace_id: int,
    connection_id: str,
    service: ProviderConnectionsService = Depends(
        get_provider_connections_service,
    ),
):
    try:
        return service.get_connection(
            workspace_id=workspace_id,
            connection_id=connection_id,
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail="Provider connection not found",
        ) from exc


# ============================================================================
# Desktop Trading Engine
# ============================================================================


@router.post(
    "/desktop/test",
    summary="Test Desktop Provider Connection",
)
def test_desktop_connection(

    workspace_id: int,

    request: DesktopConnectionRequest,

    service: ProviderConnectionsService = Depends(
        get_provider_connections_service,
    ),

):

    return service.test_desktop_connection(

        workspace_id=workspace_id,

        provider=request.provider,

        connection_name=request.connection_name,

        environment=request.environment,

        synchronization_profile=request.synchronization_profile,

        evidence_categories=request.evidence_categories,

        credentials=request.credentials,

    )


@router.post(
    "/desktop/create",
    response_model=DesktopConnectionCreateResponse,
)
def create_desktop_connection(

    workspace_id: int,

    request: DesktopConnectionRequest,

    service: ProviderConnectionsService = Depends(
        get_provider_connections_service,
    ),

):

    print("=" * 80)
    print("API REQUEST CREDENTIALS")
    print("=" * 80)
    print(request.credentials)
    print("=" * 80)

    return service.create_desktop_connection(

        workspace_id=workspace_id,

        provider=request.provider,

        connection_name=request.connection_name,

        environment=request.environment,

        synchronization_profile=request.synchronization_profile,

        evidence_categories=request.evidence_categories,

        credentials=request.credentials,

    )


# ============================================================================
# Synchronization
# ============================================================================


@router.post(
    "/{connection_id}/synchronize",
    summary="Synchronize Provider Connection",
)
def synchronize_connection(

    workspace_id: int,

    connection_id: str,

    service: ProviderConnectionsService = Depends(
        get_provider_connections_service,
    ),

):
    """
    Trigger institutional evidence acquisition for an
    authenticated provider connection.
    """

    return service.synchronize_connection(

        workspace_id=workspace_id,

        connection_id=connection_id,

    )


# ============================================================================
# Desktop Verification
# ============================================================================

@router.post(
    "/{connection_id}/verify",
    response_model=DesktopConnectionVerificationResponse,
    summary="Verify Desktop Provider Connection",
)
def verify_desktop_connection(
    workspace_id: int,
    connection_id: str,
    service: ProviderConnectionsService = Depends(
        get_provider_connections_service,
    ),
):
    """
    Execute canonical Desktop Trading Engine verification
    for an authenticated Provider Connection.
    """

    try:
        return service.verify_desktop_connection(
            workspace_id=workspace_id,
            connection_id=connection_id,
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail="Provider connection not found",
        ) from exc
    except NotImplementedError as exc:
        raise HTTPException(
            status_code=501,
            detail=str(exc),
        ) from exc


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [

    "router",

]
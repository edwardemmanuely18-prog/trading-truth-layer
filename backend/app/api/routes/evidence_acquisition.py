"""
Trading Truth Layer (TTL)

Evidence Acquisition API

Canonical API for the institutional
Evidence Acquisition domain.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi import Depends

from fastapi import Header
from app.services.evidence_acquisition.desktop_trading_engine.adapters.bridges.mt4_bridge import (
    handle_mt4_bridge_message,
)

from app.services.evidence_acquisition.desktop_trading_engine.adapters.bridges.motivewave_bridge import (
    handle_motivewave_bridge_message,
)

from app.services.evidence_acquisition.bootstrap import (
    bootstrap,
)

from app.services.evidence_acquisition.service import (
    EvidenceAcquisitionService,
)

# ============================================================================
# Router
# ============================================================================

router = APIRouter(
    prefix="/workspaces/{workspace_id}/evidence-acquisition",
    tags=["Evidence Acquisition"],
)

bridge_router = APIRouter(
    prefix="/evidence-acquisition",
    tags=["Evidence Acquisition Bridge"],
)


# ============================================================================
# Dependencies
# ============================================================================


def get_evidence_acquisition_service(
) -> EvidenceAcquisitionService:
    """
    Canonical Evidence Acquisition Service.
    """

    return bootstrap.service


# ============================================================================
# Overview
# ============================================================================


@router.get(

    "/overview",

    summary="Evidence Acquisition Overview",

)

def overview(

    workspace_id: int,

    service: EvidenceAcquisitionService = Depends(

        get_evidence_acquisition_service,

    ),

):

    return service.overview()


# ============================================================================
# Sources
# ============================================================================


@router.get(

    "/sources",

    summary="Evidence Acquisition Sources",

)

def sources(

    workspace_id: int,

    service: EvidenceAcquisitionService = Depends(

        get_evidence_acquisition_service,

    ),

):

    return service.sources(
        workspace_id,
    )


# ============================================================================
# Synchronization
# ============================================================================


@router.get(

    "/synchronizations",

    summary="Evidence Acquisition Synchronizations",

)

def synchronizations(

    workspace_id: int,

    service: EvidenceAcquisitionService = Depends(

        get_evidence_acquisition_service,

    ),

):

    return service.synchronizations()


# ============================================================================
# Diagnostics
# ============================================================================


@router.get(

    "/diagnostics",

    summary="Evidence Acquisition Diagnostics",

)

def diagnostics(

    workspace_id: int,

    service: EvidenceAcquisitionService = Depends(

        get_evidence_acquisition_service,

    ),

):

    return service.diagnostics()


@bridge_router.post(
    "/mt4-bridge",
    summary="MT4 Desktop Bridge Transport",
)
def mt4_bridge_transport(
    message: dict,
    authorization: str | None = Header(
        default=None,
    ),
):
    """
    Transport-only rendezvous endpoint for the MT4 desktop bridge.

    No evidence acquisition or canonicalization occurs here.
    """

    if not isinstance(
        message,
        dict,
    ):
        return {
            "protocol_version": "1.0",
            "request_id": "",
            "operation": "unknown",
            "ok": False,
            "data": None,
            "error": {
                "code": "MT4_REQUEST_INVALID",
                "message": (
                    "MT4 bridge request must be a JSON object."
                ),
            },
        }

    return handle_mt4_bridge_message(
        message,
        authorization=authorization,
    )


@bridge_router.post(
    "/motivewave-bridge",
    summary="MotiveWave Desktop Bridge Transport",
)
def motivewave_bridge_transport(
    message: dict,
    authorization: str | None = Header(
        default=None,
    ),
):
    """
    Transport-only rendezvous endpoint for the MotiveWave desktop bridge.

    No evidence acquisition, normalization, canonicalization,
    verification, or synchronization occurs here.
    """

    if not isinstance(message, dict):
        return {
            "protocol_version": "1.0",
            "request_id": "",
            "operation": "unknown",
            "ok": False,
            "data": None,
            "error": {
                "code": "MOTIVEWAVE_REQUEST_INVALID",
                "message": (
                    "MotiveWave bridge request must be a JSON object."
                ),
            },
        }

    return handle_motivewave_bridge_message(
        message,
        authorization=authorization,
    )


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [

    "router",

]
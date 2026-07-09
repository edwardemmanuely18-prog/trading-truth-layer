from __future__ import annotations

"""
Trading Truth Layer

Trade Evidence System (TES)

Canonical public service.

Every evidence consumer inside Trading Truth
Layer should consume TES through this module.

This module performs NO evidence calculations.

It orchestrates the canonical TES contracts.
"""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.services.evidence.workspace_metrics import (
    build_workspace_evidence_metrics,
)

from app.services.evidence.evidence_models import (
    WorkspaceEvidenceMetrics,
)

#
# Existing canonical analytics producer.
#
# This is temporary.
#
# During Phase 2 the calculations currently
# inside evidence_analytics_service.py will
# migrate into TES calculators.
#
from app.services.evidence_analytics_service import (
    build_evidence_analytics,
)


# ============================================================
# CONTEXT
# ============================================================

@dataclass(frozen=True)
class WorkspaceEvidenceContext:
    """
    Canonical workspace evidence context.

    Every workspace evidence consumer
    should consume this object.
    """

    metrics: WorkspaceEvidenceMetrics


@dataclass(frozen=True)
class WorkspaceEvidenceProjection:
    """
    Canonical response projection.

    Contains the raw analytics payload
    together with the canonical metrics.

    Existing APIs can migrate gradually
    without breaking.
    """

    metrics: WorkspaceEvidenceMetrics

    analytics: dict


# ============================================================
# WORKSPACE METRICS
# ============================================================

def get_workspace_evidence_metrics(
    db: Session,
    workspace_id: int,
) -> WorkspaceEvidenceMetrics:
    """
    Canonical TES workspace metrics.

    Current implementation projects the
    existing evidence analytics into the
    TES contract.

    Future implementations will obtain
    their data directly from TES
    calculators without changing any
    consumers.
    """

    analytics = build_evidence_analytics(
        db,
        workspace_id,
    )

    return build_workspace_evidence_metrics(
        workspace_id=workspace_id,
        analytics=analytics,
    )


# ============================================================
# WORKSPACE CONTEXT
# ============================================================

def get_workspace_evidence_context(
    db: Session,
    workspace_id: int,
) -> WorkspaceEvidenceContext:
    """
    Canonical workspace evidence context.
    """

    metrics = get_workspace_evidence_metrics(
        db=db,
        workspace_id=workspace_id,
    )

    return WorkspaceEvidenceContext(
        metrics=metrics,
    )


def get_workspace_evidence_projection(
    db: Session,
    workspace_id: int,
) -> WorkspaceEvidenceProjection:
    """
    Transitional TES entry point.

    Returns both

        • canonical metrics

        • analytics payload

    Existing APIs can consume this while
    migration is in progress.
    """

    analytics = build_evidence_analytics(
        db,
        workspace_id,
    )

    metrics = build_workspace_evidence_metrics(

        workspace_id=workspace_id,

        analytics=analytics,

    )

    return WorkspaceEvidenceProjection(

        metrics=metrics,

        analytics=analytics,

    )
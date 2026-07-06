from __future__ import annotations

from app.services.verification.metric_models import (
    WorkspaceVerificationMetrics,
)


def build_workspace_verification_projection(
    metrics: WorkspaceVerificationMetrics,
) -> dict:
    """
    Canonical workspace verification projection.

    Converts WorkspaceVerificationMetrics into
    the verification payload consumed by
    workspace-level presentation layers.

    NO verification calculations occur here.

    NO database access occurs here.

    This is purely a projection layer.
    """

    verification_score = round(
        metrics.average_verification_score,
        2,
    )

    evidence_score = round(
        metrics.evidence.percentage,
        2,
    )

    integrity_score = round(
        metrics.integrity.percentage,
        2,
    )

    governance_score = round(
        metrics.governance.percentage,
        2,
    )

    network_score = round(
        metrics.network.percentage,
        2,
    )

    return {

        "verification": {

            "verification_score":
                verification_score,

            "verification_band":
                metrics.verification_band,

            "coverage":
                verification_score,

        },

        "trust": {

            "trust_score":
                verification_score,

            "network_score":
                network_score,

            "trust_band":
                metrics.network.status,

        },

        "evidence": {

            "quality_score":
                evidence_score,

            "quality_band":
                metrics.evidence.status,

            "component":
                metrics.evidence,

        },

        "integrity": {

            "integrity_score":
                integrity_score,

            "integrity_band":
                metrics.integrity.status,

            "component":
                metrics.integrity,

        },

        "governance": {

            "governance_score":
                governance_score,

            "governance_band":
                metrics.governance.status,

            "component":
                metrics.governance,

        },

        "network": {

            "network_score":
                network_score,

            "component":
                metrics.network,

        },

    }
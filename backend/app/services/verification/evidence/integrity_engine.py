from __future__ import annotations

from app.services.verification.verification_models import (
    ComponentResult,
)

from app.services.verification.scoring_weights import (
    INTEGRITY,
)

from app.services.verification.verification_context import (
    VerificationContext,
)

from app.services.verification.verification_constants import (
    INTEGRITY_VALID,
    INTEGRITY_WARNING,
    INTEGRITY_COMPROMISED,
)


# ============================================================
# HELPERS
# ============================================================

def clamp(
    value: float,
    minimum: float,
    maximum: float,
) -> float:

    return max(
        minimum,
        min(value, maximum),
    )


def compute_integrity_score(
    context: VerificationContext,
) -> ComponentResult:
    """
    TVE wrapper around TTL's existing
    integrity infrastructure.

    NOTE

    This engine intentionally does NOT
    calculate integrity itself.

    It consumes the integrity result
    already produced by the existing
    integrity services.
    """

    scan = context.integrity_scan

    alerts = context.integrity_alerts

    result = {}

    if scan is not None:

        result = {
            "status": getattr(
                scan,
                "status",
                INTEGRITY_WARNING,
            ),
            "alerts_found": getattr(
                scan,
                "alerts_found",
                len(alerts),
            ),
        }

    status = str(
        result.get(
            "status",
            INTEGRITY_WARNING,
        )
    ).lower()

    #
    # Map legacy integrity scan states
    # into canonical TVS states.
    #
    legacy_status_map = {

        "completed": INTEGRITY_VALID,

        "complete": INTEGRITY_VALID,

        "passed": INTEGRITY_VALID,

        "success": INTEGRITY_VALID,

        "healthy": INTEGRITY_VALID,

        "clean": INTEGRITY_VALID,

    }

    status = legacy_status_map.get(
        status,
        status,
    )

    # --------------------------------------------------------
    # Scan Availability (5)
    # --------------------------------------------------------

    scan_score = (
        5.0
        if scan is not None
        else 0.0
    )

    # --------------------------------------------------------
    # Integrity Status (5)
    # --------------------------------------------------------

    if status == INTEGRITY_VALID:

        status_score = 5.0

    elif status == INTEGRITY_WARNING:

        status_score = 3.0

    else:

        status_score = 0.0

    # --------------------------------------------------------
    # Alert Penalty (6)
    # --------------------------------------------------------

    alert_count = len(alerts)

    alert_score = max(

        0.0,

        6.0 - (alert_count * 0.50),

    )

    # --------------------------------------------------------
    # Coverage Confidence (2)
    # --------------------------------------------------------

    trade_count = context.claim_trade_count

    if trade_count >= 50:

        coverage_score = 2.0

    elif trade_count >= 20:

        coverage_score = 1.5

    elif trade_count >= 10:

        coverage_score = 1.0

    elif trade_count > 0:

        coverage_score = 0.5

    else:

        coverage_score = 0.0

    # --------------------------------------------------------
    # Final Integrity Score
    # --------------------------------------------------------

    earned = round(

        clamp(

            scan_score

            + status_score

            + alert_score

            + coverage_score,

            0.0,

            INTEGRITY,

        ),

        2,

    )

    reason=(
        "Based on integrity scans, "
        "alerts and claim validation."
    )

    return ComponentResult(

        name="Integrity",

        earned_points=earned,

        maximum_points=INTEGRITY,

        status=status.title(),

        reason=reason,

        details={

            **result,

            "trade_count":
                trade_count,

            "alert_count":
                alert_count,

            "scan_score":
                scan_score,

            "status_score":
                status_score,

            "alert_score":
                alert_score,

            "coverage_score":
                coverage_score,

        },

    )
def calculate_integrity_score(alerts):
    """
    Institutional TTL integrity scoring.

    Rules:

    - Resolved findings do not penalize score
    - Open findings penalize score
    - Severity impact is capped
    - Score never collapses to zero from historical noise
    """

    score = 100

    warning = 0
    high = 0
    critical = 0
    fatal = 0

    for alert in alerts:

        status = (
            str(alert.status or "")
            .lower()
        )

        if status == "resolved":
            continue

        severity = (
            str(alert.severity or "")
            .upper()
        )

        if severity == "WARNING":
            warning += 1

        elif severity == "HIGH":
            high += 1

        elif severity == "CRITICAL":
            critical += 1

        elif severity == "FATAL":
            fatal += 1

    score -= min(warning, 20) * 0.25
    score -= min(high, 15) * 0.75
    score -= min(critical, 10) * 2
    score -= min(fatal, 5) * 4

    resolved_count = len(
        [
            a
            for a in alerts
            if (
                str(a.status or "").lower()
                == "resolved"
            )
        ]
    )

    score += min(
        resolved_count,
        20,
    ) * 0.5

    return max(score, 0)


def get_integrity_band(
    score: int,
):
    if score >= 90:
        return "HEALTHY"

    elif score >= 75:
        return "MONITORING"

    elif score >= 60:
        return "DEGRADED"

    elif score >= 40:
        return "CRITICAL"

    return "COMPROMISED"
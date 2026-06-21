def calculate_integrity_score(alerts):
    score = 100

    for alert in alerts:

        severity = (
            str(alert.severity or "")
            .upper()
        )

        if severity == "WARNING":
            score -= 5

        elif severity == "HIGH":
            score -= 10

        elif severity == "CRITICAL":
            score -= 25

        elif severity == "FATAL":
            score -= 50

    return max(score, 0)


def get_integrity_band(
    score: int,
):
    if score >= 95:
        return "HEALTHY"

    elif score >= 80:
        return "MONITORING"

    elif score >= 60:
        return "DEGRADED"

    elif score >= 30:
        return "CRITICAL"

    return "COMPROMISED"
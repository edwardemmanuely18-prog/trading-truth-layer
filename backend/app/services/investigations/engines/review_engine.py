from __future__ import annotations

from typing import Any

from ..models import (
    InvestigationDomain,
    InvestigationFinding,
    InvestigationSeverity,
)


class ReviewEngine:
    """
    Institutional Review Investigation Engine.

    Investigates canonical review statements produced by the
    ReviewProvider.

    This engine NEVER:

    - queries the database
    - creates review statements
    - modifies reviews

    It only investigates review coverage and review integrity.
    """

    ENGINE_NAME = "Review"

    @classmethod
    def build(
        cls,
        *,
        context: Any,
    ) -> InvestigationDomain:

        provider_payloads = getattr(
            context,
            "provider_payloads",
            {},
        )

        reviews = provider_payloads.get(
            "reviews"
        )

        findings: list[InvestigationFinding] = []

        confidence = 100.0

        metadata: dict[str, Any] = {}

        # ----------------------------------------------------
        # Provider availability
        # ----------------------------------------------------

        if reviews is None:

            findings.append(
                InvestigationFinding(
                    id="REVIEW-001",
                    title="Review provider unavailable",
                    description=(
                        "The ReviewProvider did not return a "
                        "canonical payload."
                    ),
                    severity=InvestigationSeverity.CRITICAL,
                    confidence=100.0,
                    recommendation=(
                        "Verify ReviewProvider registration "
                        "and execution."
                    ),
                )
            )

            return InvestigationDomain(
                name="Review",
                confidence=0.0,
                findings=findings,
                metadata=metadata,
            )

        review_count = len(reviews)

        metadata["review_count"] = review_count

        # ----------------------------------------------------
        # Coverage checks
        # ----------------------------------------------------

        if review_count == 0:

            findings.append(
                InvestigationFinding(
                    id="REVIEW-002",
                    title="No review statements",
                    description=(
                        "No institutional review statements "
                        "exist for this workspace."
                    ),
                    severity=InvestigationSeverity.MEDIUM,
                    confidence=100.0,
                    recommendation=(
                        "Complete at least one institutional "
                        "review."
                    ),
                )
            )

            confidence -= 25.0

        else:

            findings.append(
                InvestigationFinding(
                    id="REVIEW-000",
                    title="Review investigation completed",
                    description=(
                        f"{review_count} review statement(s) "
                        "available for investigation."
                    ),
                    severity=InvestigationSeverity.INFORMATION,
                    confidence=100.0,
                    recommendation="No action required.",
                )
            )

        confidence = max(
            0.0,
            min(
                confidence,
                100.0,
            ),
        )

        return InvestigationDomain(
            name="Review",
            confidence=confidence,
            findings=findings,
            metadata=metadata,
        )
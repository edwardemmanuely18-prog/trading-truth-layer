from __future__ import annotations

from typing import Any

from ..models import (
    InvestigationDomain,
    InvestigationFinding,
    InvestigationSeverity,
)


class VerificationEngine:
    """
    Institutional Verification Investigation Engine.

    This engine DOES NOT perform verification.

    Verification belongs exclusively to TVS.

    IIS interprets the canonical TVS verification
    in the context of institutional investigations.
    """

    ENGINE_NAME = "Verification"

    @classmethod
    def build(
        cls,
        *,
        context: Any,
        evidence: InvestigationDomain | None = None,
        governance: InvestigationDomain | None = None,
        broker: InvestigationDomain | None = None,
        synchronization: InvestigationDomain | None = None,
        review: InvestigationDomain | None = None,
        behavior: InvestigationDomain | None = None,
        execution: InvestigationDomain | None = None,
    ) -> InvestigationDomain:

        provider_payloads = getattr(
            context,
            "provider_payloads",
            {},
        )

        default_impact = {

            "claims": len(
                provider_payloads.get(
                    "claims",
                    [],
                ),
            ),

            "trades": len(
                provider_payloads
                .get(
                    "sync",
                    {},
                )
                .get(
                    "trades",
                    [],
                ),
            ),

            "members": len(
                provider_payloads.get(
                    "members",
                    [],
                ),
            ),

            "accounts": len(
                provider_payloads.get(
                    "brokers",
                    [],
                ),
            ),

            "sync_jobs": len(
                provider_payloads
                .get(
                    "sync",
                    {},
                )
                .get(
                    "jobs",
                    [],
                ),
            ),

        }

        tvs = provider_payloads.get("tvs")

        verification = provider_payloads.get("verification")

        findings: list[InvestigationFinding] = []

        metadata: dict[str, Any] = {}

        confidence = 100.0

        # --------------------------------------------------
        # Canonical TVS
        # --------------------------------------------------

        if tvs is None:

            findings.append(
                InvestigationFinding(
                    id="VERIFY-001",
                    title="TVS snapshot unavailable",
                    description=(
                        "Institutional verification could not "
                        "be interpreted because the canonical "
                        "TVS snapshot is unavailable."
                    ),
                    severity=InvestigationSeverity.CRITICAL,
                    confidence=100.0,
                    recommendation=(
                        "Restore canonical TVS availability."
                    ),

                    impact=default_impact.copy(),
                )
            )

            return InvestigationDomain(
                name="Verification",
                confidence=0.0,
                findings=findings,
                metadata=metadata,
            )

        metadata["tvs_available"] = True
        metadata["verification_available"] = verification is not None

        # --------------------------------------------------
        # Cross-domain confidence
        # --------------------------------------------------

        domains = [
            evidence,
            governance,
            broker,
            synchronization,
            review,
            behavior,
            execution,
        ]

        available = [
            domain
            for domain in domains
            if domain is not None
        ]

        metadata["supporting_domains"] = len(available)

        if not available:

            findings.append(
                InvestigationFinding(
                    id="VERIFY-002",
                    title="No supporting investigations",
                    description=(
                        "TVS verification exists but IIS has "
                        "no completed investigation domains "
                        "to interpret the result."
                    ),
                    severity=InvestigationSeverity.HIGH,
                    confidence=100.0,
                    recommendation=(
                        "Complete investigation engines before "
                        "issuing institutional conclusions."
                    ),

                    impact=default_impact.copy(),
                )
            )

            confidence -= 40.0

        else:

            average = (
                sum(
                    domain.confidence
                    for domain in available
                )
                / len(available)
            )

            metadata["average_domain_confidence"] = round(
                average,
                2,
            )

            confidence = min(
                confidence,
                average,
            )

        # --------------------------------------------------
        # Institutional interpretation
        # --------------------------------------------------

        if confidence >= 90:

            findings.append(
                InvestigationFinding(
                    id="VERIFY-000",
                    title="Verification strongly supported",
                    description=(
                        "Independent investigation domains "
                        "support the canonical TVS "
                        "verification."
                    ),
                    severity=InvestigationSeverity.INFORMATION,
                    confidence=confidence,
                    recommendation="No action required.",

                    impact=default_impact.copy(),
                )
            )

        elif confidence >= 70:

            findings.append(
                InvestigationFinding(
                    id="VERIFY-003",
                    title="Verification partially supported",
                    description=(
                        "TVS verification is supported, but "
                        "some investigation domains require "
                        "additional review."
                    ),
                    severity=InvestigationSeverity.MEDIUM,
                    confidence=confidence,
                    recommendation=(
                        "Review investigation findings before "
                        "making institutional decisions."
                    ),

                    impact=default_impact.copy(),
                )
            )

        else:

            findings.append(
                InvestigationFinding(
                    id="VERIFY-004",
                    title="Weak institutional support",
                    description=(
                        "The investigation domains do not "
                        "provide sufficient confidence to "
                        "strongly support the TVS result."
                    ),
                    severity=InvestigationSeverity.HIGH,
                    confidence=confidence,
                    recommendation=(
                        "Resolve investigation findings before "
                        "institutional acceptance."
                    ),

                    impact=default_impact.copy(),
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
            name="Verification",
            confidence=confidence,
            findings=findings,
            metadata=metadata,
        )
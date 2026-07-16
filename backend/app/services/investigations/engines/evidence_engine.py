from __future__ import annotations

from typing import Any

from ..models import (
    InvestigationDomain,
    InvestigationFinding,
    InvestigationSeverity,
)


class EvidenceEngine:
    """
    Institutional Evidence Investigation Engine.

    Responsibilities
    ----------------
    • Investigate canonical evidence already collected by providers.
    • Never query the database.
    • Never calculate verification.
    • Never modify provider payloads.
    • Produce structured evidence findings.
    """

    ENGINE_NAME = "Evidence"

    @classmethod
    def build(
        cls,
        context: Any,
    ) -> InvestigationDomain:
        """
        Build the institutional evidence investigation.

        Parameters
        ----------
        context
            Canonical InvestigationContext produced by the
            InvestigationContextBuilder.

        Returns
        -------
        InvestigationDomain
        """

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

        confidence = 100.0

        metadata: dict[str, Any] = {
            "tvs_available": tvs is not None,
            "verification_available": verification is not None,
        }

        # ----------------------------------------------------
        # TVS Availability
        # ----------------------------------------------------

        if tvs is None:

            findings.append(
                InvestigationFinding(
                    id="EVIDENCE-001",
                    title="TVS evidence unavailable",
                    description=(
                        "The canonical TVS payload was not "
                        "available during the investigation."
                    ),
                    severity=InvestigationSeverity.CRITICAL,
                    confidence=100.0,
                    recommendation=(
                        "Restore TVS availability before relying "
                        "on investigation results."
                    ),

                    impact=default_impact.copy(),
                )
            )

            confidence -= 40.0

        # ----------------------------------------------------
        # Verification Availability
        # ----------------------------------------------------

        if verification is None:

            findings.append(
                InvestigationFinding(
                    id="EVIDENCE-002",
                    title="Verification payload unavailable",
                    description=(
                        "Verification provider returned no "
                        "canonical payload."
                    ),
                    severity=InvestigationSeverity.HIGH,
                    confidence=100.0,
                    recommendation=(
                        "Verify that the Verification Provider "
                        "is operating correctly."
                    ),

                    impact=default_impact.copy(),
                )
            )

            confidence -= 20.0

        # ----------------------------------------------------
        # TVS Snapshot Integrity
        # ----------------------------------------------------

        if tvs is not None:

            if hasattr(tvs, "__dict__"):
                snapshot_size = len(vars(tvs))
            elif isinstance(tvs, dict):
                snapshot_size = len(tvs)
            else:
                snapshot_size = 1

            metadata["snapshot_size"] = snapshot_size

            if snapshot_size == 0:

                findings.append(
                    InvestigationFinding(
                        id="EVIDENCE-003",
                        title="Empty TVS snapshot",
                        description=(
                            "The canonical TVS snapshot contains no "
                            "institutional verification data."
                        ),
                        severity=InvestigationSeverity.HIGH,
                        confidence=100.0,
                        recommendation=(
                            "Verify canonical TVS metric generation."
                        ),

                        impact=default_impact.copy(),
                    )
                )

                confidence -= 20.0

        # ----------------------------------------------------
        # Healthy investigation
        # ----------------------------------------------------

        if not findings:

            findings.append(
                InvestigationFinding(
                    id="EVIDENCE-000",
                    title="Evidence investigation passed",
                    description=(
                        "Canonical evidence is available and no "
                        "evidence integrity issues were detected."
                    ),
                    severity=InvestigationSeverity.INFORMATION,
                    confidence=100.0,
                    recommendation="No action required.",

                    impact=default_impact.copy(),
                )
            )

        confidence = max(0.0, min(confidence, 100.0))

        return InvestigationDomain(
            name="Evidence",
            confidence=confidence,
            findings=findings,
            metadata=metadata,
        )
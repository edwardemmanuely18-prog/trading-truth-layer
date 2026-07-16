from __future__ import annotations

from typing import Any

from ..execution.execution_replay import (
    ExecutionReplayPackage,
)

from ..execution.models import (
    IntegrityLevel,
)

from ..models import (
    InvestigationDomain,
    InvestigationFinding,
    InvestigationSeverity,
)


class ExecutionEngine:
    """
    ===========================================================
    Institutional Execution Investigation Engine
    ===========================================================

    Responsibilities
    ----------------

    • Investigates the canonical ExecutionReplayPackage.

    • Never queries the database.

    • Never reconstructs executions.

    • Never calculates execution metrics.

    • Never mutates execution state.

    • Produces an InvestigationDomain consumed by IIS.

    Investigation Flow
    ------------------

    ExecutionProvider

            ↓

    ExecutionReplayPackage

            ↓

    Integrity Investigation

            ↓

    Replay Investigation

            ↓

    Metrics Investigation

            ↓

    InvestigationDomain
    """

    ENGINE_NAME = "Execution"

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

        package = provider_payloads.get(
            "execution",
        )

        findings: list[
            InvestigationFinding
        ] = []

        confidence = 100.0

        metadata: dict[
            str,
            Any,
        ] = {}

        # =====================================================
        # Provider Availability
        # =====================================================

        if package is None:

            findings.append(

                InvestigationFinding(

                    id="EXECUTION-001",

                    title="Execution provider unavailable",

                    description=(
                        "ExecutionProvider did not return a "
                        "canonical ExecutionReplayPackage."
                    ),

                    severity=InvestigationSeverity.CRITICAL,

                    confidence=100.0,

                    recommendation=(
                        "Verify ExecutionProvider registration "
                        "and replay generation."
                    ),

                    impact=default_impact.copy(),

                )

            )

            return InvestigationDomain(

                name="Execution",

                confidence=0.0,

                findings=findings,

                metadata=metadata,

            )

        package = package

        required_attributes = (
            "sequence",
            "integrity",
            "replay",
            "metrics",
        )

        if any(
            not hasattr(package, attribute)
            for attribute in required_attributes
        ):
            findings.append(
                InvestigationFinding(
                    id="EXECUTION-002",
                    title="Invalid execution payload",
                    description=(
                        "ExecutionProvider returned an "
                        "unexpected execution payload."
                    ),
                    severity=InvestigationSeverity.CRITICAL,
                    confidence=100.0,
                    recommendation=(
                        "ExecutionProvider must return an object "
                        "containing sequence, integrity, replay "
                        "and metrics."
                    ),

                    impact=default_impact.copy(),
                )
            )

            return InvestigationDomain(
                name="Execution",
                confidence=0.0,
                findings=findings,
                metadata=metadata,
            )

        sequence = package.sequence

        integrity = package.integrity

        replay = package.replay

        metrics = package.metrics

        metadata["total_trades"] = (
            metrics.total_trades
        )

        metadata["integrity_score"] = (
            metrics.execution_integrity_score
        )

        metadata["replay_completeness"] = (
            metrics.replay_completeness
        )

        metadata["duplicate_tickets"] = (
            metrics.duplicate_tickets
        )

        metadata["orphan_positions"] = (
            metrics.orphan_positions
        )

        metadata["open_positions"] = (
            metrics.open_positions
        )

        metadata["closed_positions"] = (
            metrics.closed_positions
        )

        # =====================================================
        # Integrity Investigation
        # =====================================================

        if integrity.level == IntegrityLevel.FAILED:

            findings.append(

                InvestigationFinding(

                    id="EXECUTION-100",

                    title="Execution integrity failed",

                    description=(
                        "Execution reconstruction failed "
                        "integrity validation."
                    ),

                    severity=InvestigationSeverity.CRITICAL,

                    confidence=100.0,

                    recommendation=(
                        "Resolve execution integrity issues "
                        "before relying on investigation."
                    ),

                    impact=default_impact.copy(),

                )

            )

            confidence -= 60.0

        elif integrity.level == IntegrityLevel.WARNING:

            findings.append(

                InvestigationFinding(

                    id="EXECUTION-101",

                    title="Execution integrity warning",

                    description=(
                        "Execution replay contains integrity "
                        "warnings."
                    ),

                    severity=InvestigationSeverity.HIGH,

                    confidence=100.0,

                    recommendation=(
                        "Review execution integrity findings."
                    ),

                    impact=default_impact.copy(),

                )

            )

            confidence -= 25.0

        # =====================================================
        # Duplicate Tickets
        # =====================================================

        if integrity.duplicate_count > 0:

            findings.append(

                InvestigationFinding(

                    id="EXECUTION-102",

                    title="Duplicate execution tickets",

                    description=(
                        f"{integrity.duplicate_count} duplicate "
                        "execution ticket(s) were detected."
                    ),

                    severity=InvestigationSeverity.HIGH,

                    confidence=100.0,

                    recommendation=(
                        "Investigate duplicated executions "
                        "before publishing verification."
                    ),

                    impact=default_impact.copy(),

                )

            )

            confidence -= min(
                integrity.duplicate_count * 2.0,
                20.0,
            )

        # =====================================================
        # Orphan Positions
        # =====================================================

        if integrity.orphan_count > 0:

            findings.append(

                InvestigationFinding(

                    id="EXECUTION-103",

                    title="Orphan positions detected",

                    description=(
                        f"{integrity.orphan_count} orphan "
                        "position(s) were reconstructed."
                    ),

                    severity=InvestigationSeverity.MEDIUM,

                    confidence=100.0,

                    recommendation=(
                        "Investigate orphan positions and "
                        "verify execution continuity."
                    ),

                    impact=default_impact.copy(),

                )

            )

            confidence -= min(
                integrity.orphan_count * 2.0,
                15.0,
            )

        # =====================================================
        # Missing Timestamps
        # =====================================================

        if integrity.missing_timestamp_count > 0:

            findings.append(

                InvestigationFinding(

                    id="EXECUTION-104",

                    title="Missing execution timestamps",

                    description=(
                        f"{integrity.missing_timestamp_count} "
                        "execution(s) have incomplete "
                        "timestamps."
                    ),

                    severity=InvestigationSeverity.MEDIUM,

                    confidence=100.0,

                    recommendation=(
                        "Synchronize broker history to recover "
                        "missing execution timestamps."
                    ),

                    impact=default_impact.copy(),

                )

            )

            confidence -= min(
                integrity.missing_timestamp_count,
                10.0,
            )

        # =====================================================
        # Replay Completeness
        # =====================================================

        if metrics.replay_completeness < 100.0:

            findings.append(

                InvestigationFinding(

                    id="EXECUTION-105",

                    title="Execution replay incomplete",

                    description=(
                        f"Replay completeness is "
                        f"{metrics.replay_completeness:.2f}%."
                    ),

                    severity=InvestigationSeverity.LOW,

                    confidence=100.0,

                    recommendation=(
                        "Complete broker synchronization "
                        "before institutional review."
                    ),

                    impact=default_impact.copy(),

                )

            )

            confidence -= (
                100.0
                - metrics.replay_completeness
            ) * 0.20

        # =====================================================
        # Replay Timeline
        # =====================================================

        metadata["timeline_points"] = len(
            getattr(
                replay,
                "timeline",
                [],
            )
        )

        metadata["replay_duration_seconds"] = (
            metrics.replay_duration_seconds
        )

        metadata["average_equity"] = (
            metrics.average_equity
        )

        metadata["peak_equity"] = (
            metrics.peak_equity
        )

        metadata["average_exposure"] = (
            metrics.average_exposure
        )

        metadata["peak_exposure"] = (
            metrics.peak_exposure
        )

        # =====================================================
        # Healthy Investigation
        # =====================================================

        if not findings:

            findings.append(

                InvestigationFinding(

                    id="EXECUTION-000",

                    title="Execution investigation passed",

                    description=(
                        "Execution replay, integrity and "
                        "metrics completed without material "
                        "issues."
                    ),

                    severity=InvestigationSeverity.INFORMATION,

                    confidence=100.0,

                    recommendation="No action required.",

                    impact=default_impact.copy(),

                )

            )

        # =====================================================
        # Final Confidence
        # =====================================================

        confidence = max(
            0.0,
            min(
                confidence,
                100.0,
            ),
        )

        metadata["confidence"] = confidence

        metadata["integrity_level"] = getattr(
            integrity.level,
            "value",
            str(integrity.level),
        )

        metadata["finding_count"] = len(
            findings,
        )

        metadata["engine"] = cls.ENGINE_NAME

        metadata["version"] = "2.0"

        # =====================================================
        # Canonical Investigation Domain
        # =====================================================

        return InvestigationDomain(

            name="Execution",

            confidence=confidence,

            findings=findings,

            metadata=metadata,

        )
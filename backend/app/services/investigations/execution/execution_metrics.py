from __future__ import annotations

from datetime import timedelta

from .models import (
    ExecutionIntegrity,
    ExecutionMetrics,
    ExecutionReplay,
)


# ============================================================
# Institutional Execution Metrics Engine
# ============================================================

class ExecutionMetricsEngine:

    """
    Computes execution metrics from the reconstructed
    execution replay.

    This engine NEVER queries the database.

    Inputs

        ExecutionReplay

        ExecutionIntegrity

    Output

        ExecutionMetrics
    """

    @staticmethod
    def build(

        replay: ExecutionReplay,

        integrity: ExecutionIntegrity,

    ) -> ExecutionMetrics:

        timeline = replay.timeline

        total_points = len(timeline)

        if total_points == 0:

            return ExecutionMetrics(

                total_trades=0,

                open_positions=0,

                closed_positions=0,

                duplicate_tickets=integrity.duplicate_count,

                orphan_positions=integrity.orphan_count,

                execution_integrity_score=integrity.score,

            )

        peak_open_positions = max(

            point.open_positions

            for point in timeline

        )

        average_open_positions = (

            sum(

                point.open_positions

                for point in timeline

            )

            / total_points

        )

        peak_exposure = max(

            point.exposure

            for point in timeline

        )

        average_exposure = (

            sum(

                point.exposure

                for point in timeline

            )

            / total_points

        )

        peak_margin = max(

            point.margin

            for point in timeline

        )

        average_margin = (

            sum(

                point.margin

                for point in timeline

            )

            / total_points

        )

        peak_equity = max(

            point.equity

            for point in timeline

        )

        average_equity = (

            sum(

                point.equity

                for point in timeline

            )

            / total_points

        )

        peak_floating = max(

            point.floating_pnl

            for point in timeline

        )

        average_floating = (

            sum(

                point.floating_pnl

                for point in timeline

            )

            / total_points

        )

        replay_duration = timedelta()

        if total_points > 1:

            replay_duration = (

                timeline[-1].timestamp

                -

                timeline[0].timestamp

            )

        replay_completeness = 100.0

        if integrity.score < 100:

            replay_completeness = integrity.score

        return ExecutionMetrics(

            total_trades=total_points,

            open_positions=peak_open_positions,

            closed_positions=max(

                0,

                total_points

                -

                peak_open_positions,

            ),

            duplicate_tickets=integrity.duplicate_count,

            orphan_positions=integrity.orphan_count,

            execution_integrity_score=integrity.score,

            average_open_positions=round(
                average_open_positions,
                2,
            ),

            peak_exposure=round(
                peak_exposure,
                2,
            ),

            average_exposure=round(
                average_exposure,
                2,
            ),

            peak_margin=round(
                peak_margin,
                2,
            ),

            average_margin=round(
                average_margin,
                2,
            ),

            peak_equity=round(
                peak_equity,
                2,
            ),

            average_equity=round(
                average_equity,
                2,
            ),

            peak_floating_pnl=round(
                peak_floating,
                2,
            ),

            average_floating_pnl=round(
                average_floating,
                2,
            ),

            replay_duration_seconds=int(
                replay_duration.total_seconds()
            ),

            replay_completeness=round(
                replay_completeness,
                2,
            ),

        )
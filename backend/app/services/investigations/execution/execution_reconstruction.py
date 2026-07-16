from __future__ import annotations

from .models import (
    ExecutionReplay,
    ExecutionReplayPoint,
    ExecutionSequence,
)


# ============================================================
# Institutional Execution Reconstruction Engine
# ============================================================

class ExecutionReconstructionEngine:

    """
    Reconstructs the execution history into a
    chronological account-state timeline.

    This engine NEVER queries the database.

    Input:
        ExecutionSequence

    Output:
        ExecutionReplay
    """

    @staticmethod
    def reconstruct(
        sequence: ExecutionSequence,
    ) -> ExecutionReplay:

        timeline: list[
            ExecutionReplayPoint
        ] = []

        realized_equity = 0.0

        floating_equity = 0.0

        open_positions = 0

        exposure = 0.0

        margin = 0.0

        executions = sorted(

            sequence.executions,

            key=lambda e: (

                e.opened_at

                or

                e.closed_at

            ),

        )

        for execution in executions:

            # ----------------------------------------
            # Position Lifecycle
            # ----------------------------------------

            if execution.closed_at is None:

                open_positions += 1

            else:

                realized_equity += (

                    execution.realized_pnl

                )

            floating_equity += (

                execution.floating_pnl

            )

            exposure += (

                execution.quantity

            )

            margin += (

                abs(

                    execution.quantity

                )

                *

                execution.entry_price

            )

            timestamp = (

                execution.closed_at

                or

                execution.opened_at

            )

            if timestamp is None:

                continue

            timeline.append(

                ExecutionReplayPoint(

                    timestamp=timestamp,

                    equity=realized_equity,

                    exposure=exposure,

                    floating_pnl=floating_equity,

                    margin=margin,

                    open_positions=open_positions,

                )

            )

        timeline.sort(

            key=lambda point: point.timestamp

        )

        return ExecutionReplay(

            timeline=timeline,

        )
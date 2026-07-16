from __future__ import annotations

from dataclasses import dataclass

from .execution_state_builder import (
    ExecutionStateBuilder,
)

from .execution_integrity import (
    ExecutionIntegrityEngine,
)

from .execution_reconstruction import (
    ExecutionReconstructionEngine,
)

from .execution_metrics import (
    ExecutionMetricsEngine,
)

from .models import (
    ExecutionIntegrity,
    ExecutionMetrics,
    ExecutionReplay,
    ExecutionSequence,
)


# ============================================================
# Canonical Replay Package
# ============================================================

@dataclass(slots=True)
class ExecutionReplayPackage:

    """
    Canonical execution artifact.

    Every IIS engine consumes this object.

    Timeline Engine

    Risk Engine

    Governance Engine

    Evidence Engine

    Recommendation Engine

    Verification Engine
    """

    sequence: ExecutionSequence

    integrity: ExecutionIntegrity

    replay: ExecutionReplay

    metrics: ExecutionMetrics


# ============================================================
# Replay Service
# ============================================================

class ExecutionReplayService:

    """
    Canonical execution pipeline.

    Trade Models

        ↓

    Execution States

        ↓

    Integrity

        ↓

    Replay

        ↓

    Metrics

        ↓

    Replay Package
    """

    @staticmethod
    def build(

        trades,

    ) -> ExecutionReplayPackage:

        sequence = (

            ExecutionStateBuilder.build(

                trades,

            )

        )

        integrity = (

            ExecutionIntegrityEngine.evaluate(

                sequence,

            )

        )

        replay = (

            ExecutionReconstructionEngine.reconstruct(

                sequence,

            )

        )

        metrics = (

            ExecutionMetricsEngine.build(

                replay,

                integrity,

            )

        )

        return ExecutionReplayPackage(

            sequence=sequence,

            integrity=integrity,

            replay=replay,

            metrics=metrics,

        )
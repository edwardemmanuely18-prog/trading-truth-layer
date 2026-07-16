from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict
from typing import List
from typing import Optional


# ============================================================
# Investigation Engine Categories
# ============================================================


class InvestigationStage(str, Enum):
    FOUNDATION = "foundation"
    RECONSTRUCTION = "reconstruction"
    ANALYSIS = "analysis"
    INTELLIGENCE = "intelligence"
    REPORTING = "reporting"


# ============================================================
# Engine Descriptor
# ============================================================


@dataclass(frozen=True)
class InvestigationEngineDescriptor:
    """
    Canonical description of an IIS engine.

    This object contains metadata only.

    It never executes an engine.
    """

    name: str

    stage: InvestigationStage

    execution_order: int

    enabled: bool = True

    required: bool = True

    description: str = ""

    depends_on: Optional[List[str]] = None


# ============================================================
# Canonical IIS Pipeline
# ============================================================


_ENGINE_PIPELINE: List[InvestigationEngineDescriptor] = [

    InvestigationEngineDescriptor(
        name="execution",
        stage=InvestigationStage.RECONSTRUCTION,
        execution_order=100,
        description="Reconstruct execution history.",
    ),

    InvestigationEngineDescriptor(
        name="evidence",
        stage=InvestigationStage.ANALYSIS,
        execution_order=200,
        description="Investigate TES evidence.",
        depends_on=["execution"],
    ),

    InvestigationEngineDescriptor(
        name="verification",
        stage=InvestigationStage.ANALYSIS,
        execution_order=300,
        description="Investigate TVS verification outputs.",
        depends_on=["evidence"],
    ),

    InvestigationEngineDescriptor(
        name="governance",
        stage=InvestigationStage.ANALYSIS,
        execution_order=400,
        description="Investigate governance integrity.",
        depends_on=["verification"],
    ),

    InvestigationEngineDescriptor(
        name="broker",
        stage=InvestigationStage.ANALYSIS,
        execution_order=500,
        description="Investigate broker reliability.",
        depends_on=["governance"],
    ),

    InvestigationEngineDescriptor(
        name="synchronization",
        stage=InvestigationStage.ANALYSIS,
        execution_order=600,
        description="Investigate synchronization health.",
        depends_on=["broker"],
    ),

    InvestigationEngineDescriptor(
        name="review",
        stage=InvestigationStage.ANALYSIS,
        execution_order=700,
        description="Investigate review integrity.",
        depends_on=["synchronization"],
    ),

    InvestigationEngineDescriptor(
        name="behavior",
        stage=InvestigationStage.INTELLIGENCE,
        execution_order=800,
        description="Investigate behavioural patterns.",
        depends_on=["review"],
    ),

    InvestigationEngineDescriptor(
        name="allocator",
        stage=InvestigationStage.INTELLIGENCE,
        execution_order=900,
        description="Produce allocator decision.",
        depends_on=[
            "behavior",
        ],
    ),
]


# ============================================================
# Registry
# ============================================================


class InvestigationEngineRegistry:
    """
    Canonical registry describing IIS engines.

    This registry never instantiates engines.

    It only describes pipeline order.
    """

    @classmethod
    def pipeline(
        cls,
    ) -> List[InvestigationEngineDescriptor]:

        return sorted(
            _ENGINE_PIPELINE,
            key=lambda engine: engine.execution_order,
        )

    @classmethod
    def engine_names(
        cls,
    ) -> List[str]:

        return [
            engine.name
            for engine in cls.pipeline()
        ]

    @classmethod
    def descriptor(
        cls,
        name: str,
    ) -> InvestigationEngineDescriptor:

        for engine in _ENGINE_PIPELINE:

            if engine.name == name:

                return engine

        raise KeyError(
            f"Unknown investigation engine: {name}"
        )

    @classmethod
    def as_dict(
        cls,
    ) -> Dict[str, InvestigationEngineDescriptor]:

        return {

            engine.name: engine

            for engine in cls.pipeline()

        }
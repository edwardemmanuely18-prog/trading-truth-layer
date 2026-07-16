from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .context_builder import InvestigationContext
from .models import (
    InvestigationFinding,
    InvestigationRecommendation,
)


# ============================================================
# Investigation Engine Contract
# ============================================================

@dataclass(slots=True)
class InvestigationEngine:

    name: str

    findings: Callable[
        [InvestigationContext],
        list[InvestigationFinding],
    ]

    recommendations: Callable[
        [
            InvestigationContext,
            list[InvestigationFinding],
        ],
        list[InvestigationRecommendation],
    ]


# ============================================================
# Registry
# ============================================================

_ENGINE_REGISTRY: list[
    InvestigationEngine
] = []


def register_engine(
    engine: InvestigationEngine,
) -> None:

    _ENGINE_REGISTRY.append(
        engine,
    )


def registered_engines(
) -> tuple[
    InvestigationEngine,
    ...
]:

    return tuple(
        _ENGINE_REGISTRY,
    )


# ============================================================
# Execution
# ============================================================

def execute_registered_engines(
    context: InvestigationContext,
):

    findings: list[
        InvestigationFinding
    ] = []

    recommendations: list[
        InvestigationRecommendation
    ] = []

    for engine in _ENGINE_REGISTRY:

        findings, recommendations = (
            engine.execute(
                context,
            )
        )

        findings.extend(
            engine_findings,
        )

        recommendations.extend(

            engine.recommendations(
                context,
                engine_findings,
            )

        )

    return findings, recommendations
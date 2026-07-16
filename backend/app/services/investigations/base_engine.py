from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from .context_builder import (
    InvestigationContext,
)

from .models import (
    InvestigationFinding,
    InvestigationRecommendation,
)


# ============================================================
# Institutional Investigation Engine
# ============================================================

class InvestigationEngine(ABC):

    """
    Base class for every Institutional Investigation engine.

    Every investigation inside IIS must inherit this class.

    Engines must be deterministic.

    Engines must never mutate InvestigationContext.

    Engines must never write to the database.

    Engines only perform institutional analysis.
    """

    name: str = "Unnamed Engine"

    version: str = "1.0"

    priority: int = 100

    enabled: bool = True

    # --------------------------------------------------------

    @abstractmethod
    def collect_findings(
        self,
        context: InvestigationContext,
    ) -> list[InvestigationFinding]:
        ...

    # --------------------------------------------------------

    @abstractmethod
    def build_recommendations(
        self,
        context: InvestigationContext,
        findings: list[
            InvestigationFinding
        ],
    ) -> list[
        InvestigationRecommendation
    ]:
        ...

    # --------------------------------------------------------

    def validate(
        self,
        context: InvestigationContext,
    ) -> None:

        """
        Optional validation hook.

        Override when required.
        """

        return

    # --------------------------------------------------------

    def before_run(
        self,
        context: InvestigationContext,
    ) -> None:

        """
        Optional preprocessing hook.
        """

        return

    # --------------------------------------------------------

    def after_run(
        self,
        context: InvestigationContext,
        findings: list[
            InvestigationFinding
        ],
    ) -> None:

        """
        Optional post-processing hook.
        """

        return

    # --------------------------------------------------------

    def execute(
        self,
        context: InvestigationContext,
    ) -> tuple[
        list[InvestigationFinding],
        list[InvestigationRecommendation],
    ]:

        self.validate(
            context,
        )

        self.before_run(
            context,
        )

        findings = self.collect_findings(
            context,
        )

        recommendations = (
            self.build_recommendations(
                context,
                findings,
            )
        )

        self.after_run(
            context,
            findings,
        )

        return (
            findings,
            recommendations,
        )
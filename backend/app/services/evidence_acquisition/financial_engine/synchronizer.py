"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

Synchronizer

Institutional synchronization pipeline for the Financial
Infrastructure Engine.

The synchronizer coordinates canonical evidence acquisition from
registered providers.

Pipeline

Provider
    │
Acquire
    │
Translate
    │
Validate
    │
Register
    │
Synchronization Result
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from uuid import uuid4

from datetime import datetime

from typing import List
from typing import Optional

from .models import (
    CanonicalFinancialEvidence,
    FinancialSynchronizationBatch,
)

from .provider import FinancialProvider

from .registry import FinancialRegistryService

from .translators import TranslationService

from .validators import ValidationService


# ============================================================================
# Synchronization Session
# ============================================================================


@dataclass(slots=True)
class SynchronizationSession:
    """
    Represents a single synchronization lifecycle.
    """

    session_id: str

    provider: str

    started_at: datetime

    completed_at: datetime | None = None

    successful: bool = False

    batch: FinancialSynchronizationBatch | None = None

    error: Exception | None = None

    @classmethod
    def create(
        cls,
        provider: str,
    ) -> "SynchronizationSession":

        return cls(
            session_id=str(uuid4()),
            provider=provider,
            started_at=datetime.utcnow(),
        )

    def complete(
        self,
        batch: FinancialSynchronizationBatch,
    ) -> None:

        self.batch = batch

        self.completed_at = datetime.utcnow()

        self.successful = True

    def fail(
        self,
        error: Exception,
    ) -> None:

        self.error = error

        self.completed_at = datetime.utcnow()

        self.successful = False


# ============================================================================
# Synchronization Statistics
# ============================================================================


@dataclass(slots=True)
class SynchronizationStatistics:
    """
    Runtime synchronization statistics.
    """

    acquired: int = 0

    translated: int = 0

    validated: int = 0

    registered: int = 0

    failed: int = 0


# ============================================================================
# Synchronization Result
# ============================================================================


@dataclass(slots=True)
class SynchronizationResult:
    """
    Result of a synchronization cycle.
    """

    provider: str

    started_at: datetime

    completed_at: Optional[datetime] = None

    successful: bool = False

    batch: Optional[
        FinancialSynchronizationBatch
    ] = None

    statistics: SynchronizationStatistics = field(
        default_factory=SynchronizationStatistics
    )

    errors: List[str] = field(
        default_factory=list
    )


# ============================================================================
# Financial Synchronizer
# ============================================================================


class FinancialSynchronizer:
    """
    Coordinates canonical evidence synchronization.
    """

    def __init__(
        self,
        registry: FinancialRegistryService,
        translators: TranslationService,
        validators: ValidationService,
    ) -> None:

        self.registry = registry

        self.translators = translators

        self.validators = validators

    # ------------------------------------------------------------------
    # Synchronization
    # ------------------------------------------------------------------

    def synchronize(
        self,
        provider: FinancialProvider,
    ) -> SynchronizationSession:
        """
        Execute a complete synchronization cycle.

        Returns a SynchronizationSession containing the resulting
        FinancialSynchronizationBatch.
        """

        session = SynchronizationSession.create(
            provider=provider.name(),
        )

        try:

            native_objects = provider.acquire()

            translated: list[
                CanonicalFinancialEvidence
            ] = []

            for native in native_objects:

                translation = self.translators.translate(
                    native.__class__,
                    native,
                )

                if not translation.translated:
                    continue

                validation = self.validators.validate(
                    translation.evidence,
                )

                validation.raise_if_invalid()

                translated.append(
                    translation.evidence,
                )

            batch = FinancialSynchronizationBatch(

                provider=provider.provider(),

                evidences=translated,
            )

            self.registry.register_batch(
                batch,
            )

            session.complete(
                batch,
            )

            return session

        except Exception as exc:

            session.fail(
                exc,
            )

            raise

    # ------------------------------------------------------------------
    # Convenience Helpers
    # ------------------------------------------------------------------

    def synchronize_batch(
        self,
        provider: FinancialProvider,
    ) -> FinancialSynchronizationBatch:
        """
        Synchronize and return only the canonical batch.
        """

        session = self.synchronize(
            provider,
        )

        if session.batch is None:

            raise RuntimeError(
                "Synchronization produced no batch."
            )

        return session.batch

    def health_check(
        self,
        provider: FinancialProvider,
    ) -> bool:

        return provider.is_connected()


# ============================================================================
# Batch Synchronizer
# ============================================================================


class BatchSynchronizer:
    """
    Synchronizes multiple Financial providers.
    """

    def __init__(
        self,
        synchronizer: FinancialSynchronizer,
    ) -> None:

        self.synchronizer = synchronizer

    def synchronize(
        self,
        providers: list[FinancialProvider],
    ) -> list[SynchronizationSession]:

        results = []

        for provider in providers:

            results.append(

                self.synchronizer.synchronize(
                    provider,
                )

            )

        return results

    def successful(
        self,
        sessions: list[SynchronizationSession],
    ) -> list[SynchronizationSession]:

        return [

            session

            for session in sessions

            if session.successful

        ]

    def failed(
        self,
        sessions: list[SynchronizationSession],
    ) -> list[SynchronizationSession]:

        return [

            session

            for session in sessions

            if not session.successful

        ]

    def batches(
        self,
        sessions: list[SynchronizationSession],
    ) -> list[FinancialSynchronizationBatch]:

        return [

            session.batch

            for session in sessions

            if session.successful
            and session.batch is not None

        ]


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [

    "SynchronizationSession",

    "SynchronizationStatistics",

    "SynchronizationResult",

    "FinancialSynchronizer",

    "BatchSynchronizer",
]
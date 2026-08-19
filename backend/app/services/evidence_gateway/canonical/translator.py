"""
Canonical Evidence Translator

Provider-specific objects are translated into broker-neutral
CanonicalEvidence objects here.

This module must not contain provider communication logic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .evidence import CanonicalEvidence


class EvidenceTranslator(ABC):
    """
    Base contract for provider → canonical translation.
    """

    @abstractmethod
    def translate(
        self,
        native_object: Any,
        *,
        evidence_id: str,
        workspace_id: int | None = None,
    ) -> CanonicalEvidence:
        raise NotImplementedError


class TranslatorRegistry:
    """
    Registry of canonical translators.

    Providers register translators here.
    """

    def __init__(self) -> None:
        self._translators: dict[str, EvidenceTranslator] = {}

    def register(
        self,
        provider_type: str,
        translator: EvidenceTranslator,
    ) -> None:
        if provider_type in self._translators:
            raise ValueError(
                f"Translator '{provider_type}' is already registered."
            )

        self._translators[provider_type] = translator

    def get(
        self,
        provider_type: str,
    ) -> EvidenceTranslator:
        try:
            return self._translators[provider_type]
        except KeyError as exc:
            raise KeyError(
                f"No canonical evidence translator registered "
                f"for provider '{provider_type}'."
            ) from exc

    def exists(
        self,
        provider_type: str,
    ) -> bool:
        return provider_type in self._translators

    def all(self) -> dict[str, EvidenceTranslator]:
        return dict(self._translators)
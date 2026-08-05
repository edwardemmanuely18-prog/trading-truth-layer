"""
Trading Truth Layer (TTL)

Gateway Engine

Canonical Translators

Provider-independent translation framework.

Native provider objects are translated into canonical Gateway Engine
evidence before entering the remainder of Trading Truth Layer.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Dict
from typing import Optional
from typing import Type

from .exceptions import MissingTranslatorError
from .exceptions import TranslationError
from .models import Evidence

from .normalizer import NormalizationResult


# ============================================================================
# Base Translator
# ============================================================================


class BaseTranslator(ABC):
    """
    Base class for every canonical translator.
    """

    evidence_type: Optional[Type[Evidence]] = None

    @abstractmethod
    def translate(
        self,
        native_object: Any,
    ) -> Evidence:
        """
        Translate a provider-native object into a canonical
        Gateway Engine evidence object.
        """
        raise NotImplementedError


# ============================================================================
# Translator Registry
# ============================================================================


class TranslatorRegistry:
    """
    Registry of canonical translators.
    """

    def __init__(self) -> None:

        self._translators: Dict[
            Type[Evidence],
            BaseTranslator,
        ] = {}

    def register(
        self,
        translator: BaseTranslator,
    ) -> None:

        evidence_type = translator.evidence_type

        if evidence_type is None:

            raise TranslationError(
                "Translator does not define evidence_type."
            )

        self._translators[evidence_type] = translator

    def unregister(
        self,
        evidence_type: Type[Evidence],
    ) -> None:

        self._translators.pop(
            evidence_type,
            None,
        )

    def get(
        self,
        evidence_type: Type[Evidence],
    ) -> BaseTranslator:

        translator = self._translators.get(
            evidence_type
        )

        if translator is None:

            raise MissingTranslatorError(
                f"No translator registered for "
                f"{evidence_type.__name__}"
            )

        return translator

    def registered_types(self):

        return tuple(
            self._translators.keys()
        )

    def clear(self) -> None:

        self._translators.clear()


# ============================================================================
# Translation Manager
# ============================================================================


class GatewayTranslatorManager:
    """
    Coordinates canonical translation.
    """

    def __init__(
        self,
        registry: Optional[
            TranslatorRegistry
        ] = None,
    ) -> None:

        self.registry = (
            registry
            or TranslatorRegistry()
        )

    def register(
        self,
        translator: BaseTranslator,
    ) -> None:

        self.registry.register(
            translator
        )

    def translate(
        self,
        evidence_type: Type[Evidence],
        native_object: Any,
    ) -> Evidence:

        translator = self.registry.get(
            evidence_type
        )

        return translator.translate(
            native_object
        )


from .models import (
    AccountEvidence,
    AuthenticationEvidence,
    ConnectionEvidence,
    EndpointEvidence,
    ExecutionEvidence,
    GatewayEvidence,
    InstrumentEvidence,
    MarketDataEvidence,
    OrderEvidence,
    PositionEvidence,
    QuoteEvidence,
    SessionEvidence,
    TradeEvidence,
)


# ============================================================================
# Base Dictionary Translator
# ============================================================================


class DictionaryTranslator(BaseTranslator):
    """
    Default translator for dictionary-like native objects.

    Provider adapters are expected to normalize native SDK/API objects
    into dictionaries before invoking these translators.
    """

    evidence_type = None

    def build(self, native_object: dict) -> Evidence:
        raise NotImplementedError

    def translate(
        self,
        native_object: Any,
    ) -> Evidence:

        if native_object is None:

            raise TranslationError(
                "Cannot translate None.",
            )

        # ---------------------------------------------------------
        # NormalizationResult
        # ---------------------------------------------------------

        if isinstance(
            native_object,
            NormalizationResult,
        ):

            if not native_object.successful:

                raise TranslationError(

                    "; ".join(
                        native_object.errors,
                    )

                )

            native_object = native_object.data

        # ---------------------------------------------------------
        # Canonical Dictionary
        # ---------------------------------------------------------

        if not isinstance(
            native_object,
            dict,
        ):

            raise TranslationError(

                f"Expected dict but received "

                f"{type(native_object).__name__}"

            )

        return self.build(
            native_object,
        )


class CanonicalEvidenceTranslator(DictionaryTranslator):
    """
    Institutional translator.

    Creates an empty canonical evidence object and populates it from the
    normalized dictionary.

    Individual translators only define the evidence class.
    """

    evidence_type = None

    def build(self, data: dict):

        evidence = self.evidence_type()

        self.populate(
            evidence,
            data,
        )

        return evidence

    def populate(
        self,
        evidence,
        data: dict,
    ) -> None:

        #
        # Populate only attributes that actually exist on the
        # canonical evidence model.
        #

        for key, value in data.items():

            if hasattr(
                evidence,
                key,
            ):

                setattr(
                    evidence,
                    key,
                    value,
                )


# ============================================================================
# Infrastructure Translators
# ============================================================================


class GatewayEvidenceTranslator(
    CanonicalEvidenceTranslator,
):

    evidence_type = GatewayEvidence


class SessionEvidenceTranslator(
    CanonicalEvidenceTranslator,
):

    evidence_type = SessionEvidence


class AuthenticationEvidenceTranslator(
    CanonicalEvidenceTranslator,
):

    evidence_type = AuthenticationEvidence


class EndpointEvidenceTranslator(
    CanonicalEvidenceTranslator,
):

    evidence_type = EndpointEvidence


class ConnectionEvidenceTranslator(
    CanonicalEvidenceTranslator,
):

    evidence_type = ConnectionEvidence


class AccountEvidenceTranslator(
    CanonicalEvidenceTranslator,
):

    evidence_type = AccountEvidence


# ============================================================================
# Market Translators
# ============================================================================


class InstrumentEvidenceTranslator(
    CanonicalEvidenceTranslator,
):

    evidence_type = InstrumentEvidence


class MarketDataEvidenceTranslator(
    CanonicalEvidenceTranslator,
):

    evidence_type = MarketDataEvidence


class QuoteEvidenceTranslator(
    CanonicalEvidenceTranslator,
):

    evidence_type = QuoteEvidence


class OrderEvidenceTranslator(
    CanonicalEvidenceTranslator,
):

    evidence_type = OrderEvidence


class ExecutionEvidenceTranslator(
    CanonicalEvidenceTranslator,
):

    evidence_type = ExecutionEvidence


class PositionEvidenceTranslator(
    CanonicalEvidenceTranslator,
):

    evidence_type = PositionEvidence


class TradeEvidenceTranslator(
    CanonicalEvidenceTranslator,
):

    evidence_type = TradeEvidence



from .models import GatewayEvidencePackage


# ============================================================================
# Default Translator Registration
# ============================================================================


def register_default_translators(
    registry: TranslatorRegistry,
) -> TranslatorRegistry:
    """
    Register every canonical Gateway translator.

    This function should be called once during engine startup.
    """

    registry.register(
        GatewayEvidenceTranslator()
    )

    registry.register(
        SessionEvidenceTranslator()
    )

    registry.register(
        AuthenticationEvidenceTranslator()
    )

    registry.register(
        EndpointEvidenceTranslator()
    )

    registry.register(
        ConnectionEvidenceTranslator()
    )

    registry.register(
        AccountEvidenceTranslator()
    )

    registry.register(
        InstrumentEvidenceTranslator()
    )

    registry.register(
        MarketDataEvidenceTranslator()
    )

    registry.register(
        QuoteEvidenceTranslator()
    )

    registry.register(
        OrderEvidenceTranslator()
    )

    registry.register(
        ExecutionEvidenceTranslator()
    )

    registry.register(
        PositionEvidenceTranslator()
    )

    registry.register(
        TradeEvidenceTranslator()
    )

    return registry


# ============================================================================
# Package Translator
# ============================================================================


class GatewayEvidencePackageTranslator:
    """
    Constructs a canonical GatewayEvidencePackage from
    already-translated evidence objects.

    This class deliberately performs orchestration only.
    Individual evidence translation is delegated to the
    registered translators.
    """

    def build_package(
        self,
        *,
        gateway=None,
        session=None,
        authentication=None,
        endpoint=None,
        connection=None,
        account=None,
        instruments=None,
        market_data=None,
        quotes=None,
        orders=None,
        executions=None,
        positions=None,
        trades=None,
        summary=None,
        metadata=None,
    ) -> GatewayEvidencePackage:

        return GatewayEvidencePackage(

            summary=summary,

            gateway=gateway,

            session=session,

            authentication=authentication,

            endpoint=endpoint,

            connection=connection,

            account=account,

            instruments=instruments or [],

            market_data=market_data or [],

            quotes=quotes or [],

            orders=orders or [],

            executions=executions or [],

            positions=positions or [],

            trades=trades or [],

            metadata=metadata or {},
        )


# ============================================================================
# Factory
# ============================================================================


def create_translation_manager(
) -> GatewayTranslatorManager:
    """
    Create a fully configured translation manager.
    """

    registry = TranslatorRegistry()

    register_default_translators(
        registry
    )

    return GatewayTranslatorManager(
        registry
    )


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [

    # Base
    "BaseTranslator",
    "DictionaryTranslator",

    # Registry
    "TranslatorRegistry",

    # Manager
    "GatewayTranslatorManager",

    # Factory
    "create_translation_manager",
    "register_default_translators",

    # Package
    "GatewayEvidencePackageTranslator",

    # Individual Translators
    "GatewayEvidenceTranslator",
    "SessionEvidenceTranslator",
    "AuthenticationEvidenceTranslator",
    "EndpointEvidenceTranslator",
    "ConnectionEvidenceTranslator",
    "AccountEvidenceTranslator",
    "InstrumentEvidenceTranslator",
    "MarketDataEvidenceTranslator",
    "QuoteEvidenceTranslator",
    "OrderEvidenceTranslator",
    "ExecutionEvidenceTranslator",
    "PositionEvidenceTranslator",
    "TradeEvidenceTranslator",
]
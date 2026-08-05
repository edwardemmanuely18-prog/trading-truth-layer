"""
Trading Truth Layer (TTL)

Gateway Evidence Acquisition Engine

Normalizer

Institutional normalization layer.

Every gateway adapter returns native provider objects.

Normalizers transform provider-specific objects into canonical
normalized dictionaries before translation into GatewayEvidence.

Pipeline

Gateway Adapter
        │
Native Provider Object
        │
Gateway Normalizer
        │
Canonical Dictionary
        │
Gateway Translator
        │
Gateway Evidence
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from dataclasses import dataclass, field

from typing import Any
from typing import Dict
from typing import Type


# ============================================================================
# Normalization Result
# ============================================================================


@dataclass(slots=True)
class NormalizationResult:
    """
    Result returned by every Gateway normalizer.
    """

    normalized: bool

    data: Dict[str, Any] | None = None

    warnings: list[str] = field(
        default_factory=list,
    )

    errors: list[str] = field(
        default_factory=list,
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict,
    )

    @property
    def successful(
        self,
    ) -> bool:

        return (
            self.normalized
            and not self.errors
        )


# ============================================================================
# Base Normalizer
# ============================================================================


class BaseNormalizer(
    ABC,
):
    """
    Base class for every Gateway normalizer.
    """

    @property
    @abstractmethod
    def evidence_type(
        self,
    ) -> str:
        """
        Canonical evidence category handled by this normalizer.

        Examples
        --------
        gateways
        accounts
        positions
        orders
        executions
        trades
        """

    @abstractmethod
    def normalize(
        self,
        *,
        evidence_type: str,
        obj: Any,
    ) -> NormalizationResult:
        """
        Normalize a provider object into a canonical dictionary.
        """


# ============================================================================
# Registry
# ============================================================================


class GatewayNormalizerRegistry:
    """
    Registry of Gateway normalizers.
    """

    def __init__(
        self,
    ) -> None:

        self._normalizers: dict[
            str,
            BaseNormalizer,
        ] = {}

    def register(
        self,
        normalizer: BaseNormalizer,
    ) -> None:

        self._normalizers[
            normalizer.evidence_type
        ] = normalizer

    def unregister(
        self,
        evidence_type: str,
    ) -> None:

        self._normalizers.pop(
            evidence_type,
            None,
        )

    def get(
        self,
        evidence_type: str,
    ) -> BaseNormalizer | None:

        return self._normalizers.get(
            evidence_type,
        )

    def supports(
        self,
        evidence_type: str,
    ) -> bool:

        return evidence_type in self._normalizers

    def registered_types(
        self,
    ) -> list[str]:

        return sorted(
            self._normalizers.keys(),
        )


# ============================================================================
# Normalization Manager
# ============================================================================


class GatewayNormalizationManager:
    """
    Coordinates Gateway normalization.
    """

    def __init__(
        self,
        registry: GatewayNormalizerRegistry,
    ) -> None:

        self.registry = registry

    def normalize(
        self,
        *,
        evidence_type: str,
        obj: Any,
    ) -> NormalizationResult:
        """
        Normalize a provider object using the canonical evidence type.
        """

        normalizer = self.registry.get(
            evidence_type,
        )

        if normalizer is None:

            return NormalizationResult(

                normalized=False,

                errors=[
                    (
                        "No Gateway normalizer registered "
                        f"for '{evidence_type}'."
                    )
                ],

            )

        return normalizer.normalize(
            obj=obj,
        )


# ============================================================================
# Dictionary Normalizer
# ============================================================================


class DictionaryNormalizer(
    BaseNormalizer,
):
    """
    Base normalizer for provider objects that can be represented
    as canonical dictionaries.

    Concrete provider normalizers inherit from this class and
    implement build_dictionary().
    """

    def normalize(
        self,
        *,
        obj: Any,
        evidence_type: str = "",
    ) -> NormalizationResult:

        if obj is None:

            return NormalizationResult(

                normalized=False,

                errors=[
                    "Cannot normalize a None object.",
                ],

            )

        try:

            data = self.build_dictionary(
                obj,
            )

            if not isinstance(
                data,
                dict,
            ):

                return NormalizationResult(

                    normalized=False,

                    errors=[
                        "Normalizer did not return a dictionary.",
                    ],

                )

            data = self.clean_dictionary(
                data,
            )

            return NormalizationResult(

                normalized=True,

                data=data,

            )

        except Exception as exc:

            return NormalizationResult(

                normalized=False,

                errors=[
                    str(
                        exc,
                    ),
                ],

            )

    # ------------------------------------------------------------------
    # Dictionary Construction
    # ------------------------------------------------------------------

    @abstractmethod
    def build_dictionary(
        self,
        obj: Any,
    ) -> Dict[str, Any]:
        """
        Convert the native provider object into a canonical dictionary.
        """

    # ------------------------------------------------------------------
    # Shared Cleanup
    # ------------------------------------------------------------------

    def clean_dictionary(
        self,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:

        cleaned: Dict[str, Any] = {}

        for key, value in data.items():

            if value is None:

                continue

            if isinstance(
                value,
                str,
            ):

                value = value.strip()

            cleaned[key] = value

        return cleaned

    # ------------------------------------------------------------------
    # Shared Helpers
    # ------------------------------------------------------------------

    def as_string(
        self,
        obj: Any,
        key: str,
    ) -> str | None:

        value = self.value(
            obj,
            key,
        )

        if value is None:
            return None

        return str(value).strip()

    # ------------------------------------------------------------------
    # Dictionary Helpers
    # ------------------------------------------------------------------

    def value(
        self,
        obj: Any,
        key: str,
    ) -> Any:
        """
        Read a value from a canonical dictionary.

        Future adapters may provide objects instead of dictionaries.
        This helper supports both without changing every normalizer.
        """

        if isinstance(obj, dict):
            return obj.get(key)

        return getattr(
            obj,
            key,
            None,
        )

    def as_float(
        self,
        obj: Any,
        key: str,
    ) -> float | None:

        value = self.value(
            obj,
            key,
        )

        if value is None:
            return None

        return float(value)

    def as_integer(
        self,
        obj: Any,
        key: str,
    ) -> int | None:

        value = self.value(
            obj,
            key,
        )

        if value is None:
            return None

        return int(value)

    def as_boolean(
        self,
        obj: Any,
        key: str,
    ) -> bool | None:

        value = self.value(
            obj,
            key,
        )

        if value is None:
            return None

        return bool(value)


# ============================================================================
# Infrastructure Normalizers
# ============================================================================


class GatewayNormalizer(
    DictionaryNormalizer,
):
    """
    Canonical Gateway normalizer.
    """

    @property
    def evidence_type(self) -> str:

        return "gateways"


    def build_dictionary(
        self,
        obj: Any,
    ) -> Dict[str, Any]:

        return {

            "gateway_id": self.as_string(
                obj,
                "gateway_id",
            ),

            "gateway_name": self.as_string(
                obj,
                "gateway_name",
            ),

            "gateway_type": self.as_string(
                obj,
                "gateway_type",
            ),

            "provider": self.as_string(
                obj,
                "provider",
            ),

            "version": self.as_string(
                obj,
                "version",
            ),

        }


class SessionNormalizer(
    DictionaryNormalizer,
):
    """
    Canonical session normalizer.
    """

    @property
    def evidence_type(self) -> str:

        return "sessions"

    def build_dictionary(
        self,
        obj: Any,
    ) -> Dict[str, Any]:

        return {

            "session_id": self.as_string(
                obj,
                "session_id",
            ),

            "state": self.as_string(
                obj,
                "state",
            ),

            "connected": self.as_boolean(
                obj,
                "connected",
            ),

            "authenticated": self.as_boolean(
                obj,
                "authenticated",
            ),

        }


class AuthenticationNormalizer(
    DictionaryNormalizer,
):
    """
    Canonical authentication normalizer.
    """

    @property
    def evidence_type(self) -> str:

        return "authentications"

    def build_dictionary(
        self,
        obj: Any,
    ) -> Dict[str, Any]:

        return {

            "user": self.as_string(
                obj,
                "user",
            ),

            "account": self.as_string(
                obj,
                "account",
            ),

            "authenticated": self.as_boolean(
                obj,
                "authenticated",
            ),

            "authentication_method": self.as_string(
                obj,
                "authentication_method",
            ),

        }


class EndpointNormalizer(
    DictionaryNormalizer,
):
    """
    Canonical endpoint normalizer.
    """

    @property
    def evidence_type(self) -> str:

        return "endpoints"

    def build_dictionary(
        self,
        obj: Any,
    ) -> Dict[str, Any]:

        return {

            "host": self.as_string(
                obj,
                "host",
            ),

            "port": self.as_integer(
                obj,
                "port",
            ),

            "protocol": self.as_string(
                obj,
                "protocol",
            ),

            "environment": self.as_string(
                obj,
                "environment",
            ),

        }


class ConnectionNormalizer(
    DictionaryNormalizer,
):
    """
    Canonical connection normalizer.
    """

    @property
    def evidence_type(self) -> str:

        return "connections"

    def build_dictionary(
        self,
        obj: Any,
    ) -> Dict[str, Any]:

        return {

            "status": self.as_string(
                obj,
                "status",
            ),

            "latency_ms": self.as_float(
                obj,
                "latency_ms",
            ),

            "healthy": self.as_boolean(
                obj,
                "healthy",
            ),

            "last_heartbeat": self.value(
                obj,
                "last_heartbeat",
            ),

        }


class AccountNormalizer(
    DictionaryNormalizer,
):
    """
    Canonical account normalizer.
    """

    @property
    def evidence_type(self) -> str:

        return "accounts"

    def build_dictionary(
        self,
        obj: Any,
    ) -> Dict[str, Any]:

        return {

            "account_id": self.as_string(
                obj,
                "account_id",
            ),

            "account_name": self.as_string(
                obj,
                "account_name",
            ),

            "account_type": self.as_string(
                obj,
                "account_type",
            ),

            "currency": self.as_string(
                obj,
                "currency",
            ),

            "broker": self.as_string(
                obj,
                "broker",
            ),

        }


# ============================================================================
# Market Normalizers
# ============================================================================


class InstrumentNormalizer(
    DictionaryNormalizer,
):
    """
    Canonical instrument normalizer.
    """

    @property
    def evidence_type(self) -> str:

        return "instruments"

    def build_dictionary(
        self,
        obj: Any,
    ) -> Dict[str, Any]:

        return {

            "symbol": self.as_string(
                obj,
                "symbol",
            ),

            "description": self.as_string(
                obj,
                "description",
            ),

            "asset_class": self.as_string(
                obj,
                "asset_class",
            ),

            "exchange": self.as_string(
                obj,
                "exchange",
            ),

            "currency": self.as_string(
                obj,
                "currency",
            ),

        }


class MarketDataNormalizer(
    DictionaryNormalizer,
):
    """
    Canonical market data normalizer.
    """

    @property
    def evidence_type(self) -> str:

        return "market_data"

    def build_dictionary(
        self,
        obj: Any,
    ) -> Dict[str, Any]:

        return {

            "symbol": self.as_string(
                obj,
                "symbol",
            ),

            "bid": self.as_float(
                obj,
                "bid",
            ),

            "ask": self.as_float(
                obj,
                "ask",
            ),

            "last": self.as_float(
                obj,
                "last",
            ),

            "volume": self.as_float(
                obj,
                "volume",
            ),

            "timestamp": self.value(
                obj,
                "timestamp",
            ),

        }


class QuoteNormalizer(
    DictionaryNormalizer,
):
    """
    Canonical quote normalizer.
    """

    @property
    def evidence_type(self) -> str:

        return "quotes"

    def build_dictionary(
        self,
        obj: Any,
    ) -> Dict[str, Any]:

        return {

            "symbol": self.as_string(
                obj,
                "symbol",
            ),

            "bid": self.as_float(
                obj,
                "bid",
            ),

            "ask": self.as_float(
                obj,
                "ask",
            ),

            "spread": self.as_float(
                obj,
                "spread",
            ),

            "timestamp": self.value(
                obj,
                "timestamp",
            ),

        }


class OrderNormalizer(
    DictionaryNormalizer,
):
    """
    Canonical order normalizer.
    """

    @property
    def evidence_type(self) -> str:

        return "orders"

    def build_dictionary(
        self,
        obj: Any,
    ) -> Dict[str, Any]:

        return {

            "order_id": self.as_string(
                obj,
                "order_id",
            ),

            "symbol": self.as_string(
                obj,
                "symbol",
            ),

            "side": self.as_string(
                obj,
                "side",
            ),

            "order_type": self.as_string(
                obj,
                "order_type",
            ),

            "quantity": self.as_float(
                obj,
                "quantity",
            ),

            "price": self.as_float(
                obj,
                "price",
            ),

            "status": self.as_string(
                obj,
                "status",
            ),

        }


class ExecutionNormalizer(
    DictionaryNormalizer,
):
    """
    Canonical execution normalizer.
    """

    @property
    def evidence_type(self) -> str:

        return "executions"

    def build_dictionary(
        self,
        obj: Any,
    ) -> Dict[str, Any]:

        return {

            "execution_id": self.as_string(
                obj,
                "execution_id",
            ),

            "order_id": self.as_string(
                obj,
                "order_id",
            ),

            "symbol": self.as_string(
                obj,
                "symbol",
            ),

            "side": self.as_string(
                obj,
                "side",
            ),

            "price": self.as_float(
                obj,
                "price",
            ),

            "quantity": self.as_float(
                obj,
                "quantity",
            ),

            "timestamp": self.value(
                obj,
                "timestamp",
            ),

        }


class PositionNormalizer(
    DictionaryNormalizer,
):
    """
    Canonical position normalizer.
    """

    @property
    def evidence_type(self) -> str:

        return "positions"

    def build_dictionary(
        self,
        obj: Any,
    ) -> Dict[str, Any]:

        return {

            "position_id": self.as_string(
                obj,
                "position_id",
            ),

            "symbol": self.as_string(
                obj,
                "symbol",
            ),

            "side": self.as_string(
                obj,
                "side",
            ),

            "quantity": self.as_float(
                obj,
                "quantity",
            ),

            "average_price": self.as_float(
                obj,
                "average_price",
            ),

            "unrealized_pnl": self.as_float(
                obj,
                "unrealized_pnl",
            ),

        }


class TradeNormalizer(
    DictionaryNormalizer,
):
    """
    Canonical trade normalizer.
    """

    @property
    def evidence_type(self) -> str:

        return "trades"

    def build_dictionary(
        self,
        obj: Any,
    ) -> Dict[str, Any]:

        return {

            "trade_id": self.as_string(
                obj,
                "trade_id",
            ),

            "order_id": self.as_string(
                obj,
                "order_id",
            ),

            "execution_id": self.as_string(
                obj,
                "execution_id",
            ),

            "symbol": self.as_string(
                obj,
                "symbol",
            ),

            "side": self.as_string(
                obj,
                "side",
            ),

            "quantity": self.as_float(
                obj,
                "quantity",
            ),

            "price": self.as_float(
                obj,
                "price",
            ),

            "commission": self.as_float(
                obj,
                "commission",
            ),

            "fees": self.as_float(
                obj,
                "fees",
            ),

            "realized_pnl": self.as_float(
                obj,
                "realized_pnl",
            ),

            "timestamp": self.value(
                obj,
                "timestamp",
            ),

        }


# ============================================================================
# Default Registration
# ============================================================================


def register_default_normalizers(
    registry: GatewayNormalizerRegistry,
) -> GatewayNormalizerRegistry:
    """
    Register every canonical Gateway normalizer.

    This function should be called once during engine startup.
    """

    registry.register(
        GatewayNormalizer()
    )

    registry.register(
        SessionNormalizer()
    )

    registry.register(
        AuthenticationNormalizer()
    )

    registry.register(
        EndpointNormalizer()
    )

    registry.register(
        ConnectionNormalizer()
    )

    registry.register(
        AccountNormalizer()
    )

    registry.register(
        InstrumentNormalizer()
    )

    registry.register(
        MarketDataNormalizer()
    )

    registry.register(
        QuoteNormalizer()
    )

    registry.register(
        OrderNormalizer()
    )

    registry.register(
        ExecutionNormalizer()
    )

    registry.register(
        PositionNormalizer()
    )

    registry.register(
        TradeNormalizer()
    )

    return registry


# ============================================================================
# Factory
# ============================================================================


def create_normalization_manager(
) -> GatewayNormalizationManager:
    """
    Create a fully configured normalization manager.
    """

    registry = GatewayNormalizerRegistry()

    register_default_normalizers(
        registry,
    )

    return GatewayNormalizationManager(
        registry,
    )


# ============================================================================
# Public Exports
# ============================================================================

__all__ = [

    "NormalizationResult",

    "BaseNormalizer",

    "GatewayNormalizerRegistry",

    "GatewayNormalizationManager",

    "register_default_normalizers",

    "create_normalization_manager",

    "DictionaryNormalizer",

    "GatewayNormalizer",

    "SessionNormalizer",

    "AuthenticationNormalizer",

    "EndpointNormalizer",

    "ConnectionNormalizer",

    "AccountNormalizer",

    "InstrumentNormalizer",

    "MarketDataNormalizer",

    "QuoteNormalizer",

    "OrderNormalizer",

    "ExecutionNormalizer",

    "PositionNormalizer",

    "TradeNormalizer",

]
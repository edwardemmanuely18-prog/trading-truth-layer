"""
Trading Truth Layer (TTL)

Universal Evidence Adapter (UEA)

Canonical Translation Layer
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional

from .exceptions import TranslationError
from .models import DesktopEvidencePackage
from .models import Evidence
from .models import (
    AccountEvidence,
    AccountState,
    BrokerEvidence,
    ConnectionStatus,
    PlatformType,
    ServerEvidence,
    TerminalEvidence,
    UserEvidence,
    BalanceEvidence,
    MarginEvidence,
    EquityEvidence,
    BuyingPowerEvidence,
    SymbolEvidence,
    PriceEvidence,
    OrderEvidence,
    ExecutionEvidence,
    DealEvidence,
    TradeEvidence,
    PositionEvidence,
    HistoryEvidence,
    ActivityEvidence,
)


# ============================================================================
# Base Translator
# ============================================================================


class BaseTranslator(ABC):
    """
    Abstract translator for converting native provider
    objects into canonical UEA evidence.

    Every provider translator should inherit from this class.
    """

    provider_name: str = "unknown"

    provider_version: str = "unknown"

    @abstractmethod
    def translate(
        self,
        source: Any,
    ) -> DesktopEvidencePackage:
        """
        Translate a provider payload into a
        DesktopEvidencePackage.
        """
        raise NotImplementedError

    def translate_collection(
        self,
        collection: Iterable[Any],
    ) -> List[Evidence]:
        """
        Translate a collection of provider objects.
        """

        translated: List[Evidence] = []

        for item in collection:
            translated.append(
                self.translate_item(item)
            )

        return translated

    @abstractmethod
    def translate_item(
        self,
        item: Any,
    ) -> Evidence:
        """
        Translate a single provider object.
        """
        raise NotImplementedError


# ============================================================================
# Translation Helpers
# ============================================================================


class TranslationContext:
    """
    Shared translation context.

    Carries provider metadata and arbitrary state across a
    translation cycle.
    """

    def __init__(
        self,
        *,
        provider: str,
        version: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.provider = provider

        self.version = version

        self.metadata: Dict[str, Any] = metadata or {}


class TranslationHelper:
    """
    Common helper utilities for translators.

    These helpers intentionally remain provider-neutral.
    """

    @staticmethod
    def require(
        value: Any,
        field_name: str,
    ) -> Any:
        """
        Ensure a required value exists.
        """

        if value is None:
            raise TranslationError(
                f"Missing required field: {field_name}"
            )

        return value

    @staticmethod
    def optional(
        value: Any,
        default: Any = None,
    ) -> Any:
        """
        Return a default value when the source value is None.
        """

        return default if value is None else value

    @staticmethod
    def as_string(
        value: Any,
    ) -> Optional[str]:
        """
        Convert a value to a string.
        """

        if value is None:
            return None

        return str(value)

    @staticmethod
    def as_identifier(
        value: Any,
    ) -> Optional[str]:
        """
        Normalize broker/provider identifiers.

        Empty values and numeric/string zero sentinels are treated
        as absent identifiers. Genuine identifier values are preserved.
        """

        if value is None:
            return None

        if isinstance(value, str):
            normalized = value.strip()

            if not normalized or normalized == "0":
                return None

            return normalized

        if isinstance(value, (int, float)):
            if value == 0:
                return None

            return str(value)

        normalized = str(value).strip()

        if not normalized or normalized == "0":
            return None

        return normalized

    @staticmethod
    def as_float(
        value: Any,
    ) -> Optional[float]:
        """
        Convert a value to a float.
        """

        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError) as exc:
            raise TranslationError(
                f"Unable to convert '{value}' to float."
            ) from exc

    @staticmethod
    def as_int(
        value: Any,
    ) -> Optional[int]:
        """
        Convert a value to an integer.
        """

        if value is None:
            return None

        try:
            return int(value)
        except (TypeError, ValueError) as exc:
            raise TranslationError(
                f"Unable to convert '{value}' to int."
            ) from exc

    @classmethod
    def as_datetime(
        cls,
        source: Any,
        attribute: str,
        default: Any = None,
    ) -> Any:
        """
        Return a canonical datetime value from the acquisition contract.

        Provider-specific adapters are responsible for normalizing native
        timestamp representations before the shared translation layer.
        """

        value = cls.get(
            source,
            attribute,
            default,
        )

        return value

    @staticmethod
    def as_bool(
        value: Any,
    ) -> Optional[bool]:
        """
        Convert a value to a boolean.
        """

        if value is None:
            return None

        if isinstance(value, bool):
            return value

        if isinstance(value, (int, float)):
            return bool(value)

        if isinstance(value, str):
            value = value.strip().lower()

            if value in {"true", "1", "yes", "y"}:
                return True

            if value in {"false", "0", "no", "n"}:
                return False

        raise TranslationError(
            f"Unable to convert '{value}' to bool."
        )


    @staticmethod
    def as_dict(
        value: Any,
    ) -> Dict[str, Any]:
        """
        Convert a mapping-like object into a dictionary.
        """

        if value is None:
            return {}

        if isinstance(value, dict):
            return value

        raise TranslationError(
            "Expected a dictionary-compatible object."
        )


# ============================================================================
# Translation Accessor
# ============================================================================


class TranslationAccessor:
    """
    Provider-neutral object accessor.

    This class hides differences between SDK objects,
    dataclasses, dictionaries and future provider-native
    objects.

    DesktopTranslator should never access provider
    objects directly.
    """

    @staticmethod
    def get(
        source: Any,
        attribute: str,
        default: Any = None,
    ) -> Any:

        if source is None:
            return default

        if isinstance(source, dict):
            return source.get(attribute, default)

        return getattr(
            source,
            attribute,
            default,
        )

    @classmethod
    def as_string(
        cls,
        source: Any,
        attribute: str,
        default: str | None = None,
    ) -> str | None:

        value = cls.get(
            source,
            attribute,
            default,
        )

        return TranslationHelper.as_string(value)

    @classmethod
    def as_identifier(
        cls,
        source: Any,
        attribute: str,
        default: str | None = None,
    ) -> str | None:

        value = cls.get(
            source,
            attribute,
            default,
        )

        return TranslationHelper.as_identifier(value)

    @classmethod
    def as_float(
        cls,
        source: Any,
        attribute: str,
        default: float | None = None,
    ) -> float | None:

        value = cls.get(
            source,
            attribute,
            default,
        )

        return TranslationHelper.as_float(value)

    @classmethod
    def as_int(
        cls,
        source: Any,
        attribute: str,
        default: int | None = None,
    ) -> int | None:

        value = cls.get(
            source,
            attribute,
            default,
        )

        return TranslationHelper.as_int(value)

    @classmethod
    def as_datetime(
        cls,
        source: Any,
        attribute: str,
        default: Any = None,
    ) -> Any:
        """
        Return a canonical datetime value from the acquisition contract.

        Provider-specific adapters are responsible for normalizing native
        timestamp representations before the shared translation layer.
        """

        value = cls.get(
            source,
            attribute,
            default,
        )

        return value

    @classmethod
    def as_bool(
        cls,
        source: Any,
        attribute: str,
        default: bool | None = None,
    ) -> bool | None:

        value = cls.get(
            source,
            attribute,
            default,
        )

        return TranslationHelper.as_bool(value)


# ============================================================================
# Translation Pipeline
# ============================================================================


class TranslationPipeline:
    """
    Canonical translation pipeline.

    Coordinates translation without containing any
    provider-specific mapping logic.
    """

    def __init__(
        self,
        translator: BaseTranslator,
    ) -> None:
        self.translator = translator

    def run(
        self,
        source: Any,
    ) -> DesktopEvidencePackage:
        """
        Execute a complete translation cycle.
        """

        package = self.translator.translate(source)

        if not isinstance(package, DesktopEvidencePackage):
            raise TranslationError(
                "Translator did not return a DesktopEvidencePackage."
            )

        return package

    def run_many(
        self,
        sources: Iterable[Any],
    ) -> List[DesktopEvidencePackage]:
        """
        Translate multiple provider payloads.
        """

        packages: List[DesktopEvidencePackage] = []

        for source in sources:
            packages.append(
                self.run(source)
            )

        return packages


# ============================================================================
# Translation Registry
# ============================================================================


class TranslatorRegistry:
    """
    Registry of available translators.

    Provider implementations register themselves here so
    higher layers remain provider-independent.
    """

    def __init__(self) -> None:
        self._translators: Dict[str, BaseTranslator] = {}

    def register(
        self,
        translator: BaseTranslator,
    ) -> None:
        provider = translator.provider_name.lower()

        if provider in self._translators:
            raise TranslationError(
                f"Translator already registered for provider '{provider}'."
            )

        self._translators[provider] = translator

    def get(
        self,
        provider: str,
    ) -> BaseTranslator:
        provider = provider.lower()

        try:
            return self._translators[provider]
        except KeyError as exc:
            raise TranslationError(
                f"No translator registered for provider '{provider}'."
            ) from exc

    def registered_providers(self) -> List[str]:
        """
        Return registered provider names.
        """

        return sorted(self._translators.keys())


# ============================================================================
# Desktop Translator
# ============================================================================


class DesktopTranslator(BaseTranslator):
    """
    Canonical Desktop Trading Engine translator.

    Converts the canonical desktop acquisition contract into a
    DesktopEvidencePackage.

    The translator is completely provider-independent.

    Every desktop adapter must emit the canonical acquisition
    contract expected by this translator.
    """

    provider_name = "desktop"

    provider_version = "1.0"

    @staticmethod
    def _resolve_platform(
        *,
        provider_name: str | None,
        terminal: dict[str, Any],
    ) -> PlatformType:
        """
        Resolve the canonical desktop platform from the normalized
        acquisition contract.

        Provider-specific acquisition remains outside the translator.
        This method only interprets canonical connector/platform identity.
        """

        values = [
            provider_name or "",
            terminal.get("terminal_name") or "",
            terminal.get("platform_build") or "",
        ]

        normalized = " ".join(
            str(value).strip().lower()
            for value in values
            if value
        )

        if (
            "metatrader 5" in normalized
            or "meta trader 5" in normalized
            or "mt5" in normalized
        ):
            return PlatformType.MT5

        if (
            "metatrader 4" in normalized
            or "meta trader 4" in normalized
            or "mt4" in normalized
        ):
            return PlatformType.MT4

        if "ctrader" in normalized or "c trader" in normalized:
            return PlatformType.CTRADER

        if "ninjatrader" in normalized:
            return PlatformType.NINJATRADER

        if "tradestation" in normalized:
            return PlatformType.TRADESTATION

        if "sierra chart" in normalized:
            return PlatformType.SIERRA_CHART

        if "multicharts" in normalized:
            return PlatformType.MULTICHARTS

        if "quantower" in normalized:
            return PlatformType.QUANTOWER

        if "cqg" in normalized:
            return PlatformType.CQG

        if "dxtrade" in normalized:
            return PlatformType.DXTRADE

        if "matchtrader" in normalized:
            return PlatformType.MATCHTRADER

        if "motivewave" in normalized:
            return PlatformType.MOTIVEWAVE

        return PlatformType.UNKNOWN

    def _apply_identity_context(
        self,
        package: DesktopEvidencePackage,
        payload: Dict[str, Any],
    ) -> None:
        """
        Populate the canonical EvidenceIdentity for every evidence
        object produced during this translation cycle.

        Identity is derived from the canonical desktop acquisition
        contract and applied once at the package boundary.

        This does not create synchronization IDs. Synchronization
        identity is owned by DesktopEvidencePackage.
        """

        account = TranslationHelper.as_dict(
            payload.get("account"),
        )

        terminal = TranslationHelper.as_dict(
            payload.get("terminal"),
        )

        provider_name = (
            TranslationAccessor.as_string(
                payload,
                "connector_name",
            )
            or self.provider_name
        )

        provider_version = (
            TranslationAccessor.as_string(
                payload,
                "connector_version",
            )
            or self.provider_version
        )

        account_id = TranslationAccessor.as_string(
            account,
            "broker_account_id",
        )

        account_number = (
            TranslationAccessor.as_string(
                account,
                "broker_account_id",
            )
            or account_id
        )

        server = TranslationHelper.as_dict(
            payload.get("server"),
        )

        server_name = TranslationAccessor.as_string(
            server,
            "server_name",
        )

        platform_name = self._resolve_platform(
            provider_name=provider_name,
            terminal=terminal,
        )

        account_state = AccountState.UNKNOWN

        explicit_account_state = TranslationAccessor.as_string(
            account,
            "account_state",
        )

        if explicit_account_state:
            normalized_state = (
                explicit_account_state.strip().lower()
            )

            if normalized_state in {
                "live",
                "real",
                "production",
            }:
                account_state = AccountState.LIVE

            elif normalized_state in {
                "demo",
                "paper",
                "simulation",
            }:
                account_state = AccountState.DEMO

        else:
            trade_mode = TranslationAccessor.as_int(
                account,
                "account_type",
            )

            if trade_mode == 2:
                account_state = AccountState.LIVE

            elif trade_mode in {0, 1}:
                account_state = AccountState.DEMO

        # --------------------------------------------------------------
        # Provider connection-context fallback
        #
        # MotiveWave does not currently expose a native account-state
        # value through the acquisition surface. Therefore, when the
        # native account does not provide an explicit state, use the
        # canonical TTL connection environment supplied by the adapter.
        #
        # This is derived connection context, not fabricated native
        # account evidence.
        # --------------------------------------------------------------

        if account_state == AccountState.UNKNOWN:
            connection_context = TranslationHelper.as_dict(
                payload.get("connection_context"),
            )

            connection_environment = (
                TranslationAccessor.as_string(
                    connection_context,
                    "environment",
                )
                or ""
            ).strip().lower()

            if connection_environment in {
                "production",
                "prod",
                "live",
            }:
                account_state = AccountState.LIVE

            elif connection_environment in {
                "development",
                "dev",
                "demo",
                "sandbox",
                "paper",
            }:
                account_state = AccountState.DEMO

        for evidence in package.iter_evidence():

            evidence.identity.provider_name = provider_name

            evidence.identity.platform_name = platform_name

            evidence.identity.platform_version = provider_version

            evidence.identity.account_id = account_id

            evidence.identity.account_number = account_number

            evidence.identity.account_state = account_state

            evidence.identity.server_name = server_name

    def translate(
        self,
        source: Any,
    ) -> DesktopEvidencePackage:
        """
        Translate the canonical desktop acquisition contract
        into a DesktopEvidencePackage.
        """

        payload = TranslationHelper.as_dict(source)

        package = DesktopEvidencePackage()

        package.connector_name = TranslationHelper.as_string(
            payload.get("connector_name")
        )

        package.connector_version = TranslationHelper.as_string(
            payload.get("connector_version")
        )

        package.terminal = self._translate_terminal(
            payload.get("terminal")
        )

        package.user = self._translate_user(
            payload.get("user")
        )

        package.broker = self._translate_broker(
            payload.get("broker")
        )

        package.server = self._translate_server(
            payload.get("server")
        )

        financial = TranslationHelper.as_dict(
            payload.get("financial"),
        )

        connection_context = TranslationHelper.as_dict(
            payload.get("connection_context"),
        )

        connection_environment = (
            TranslationAccessor.as_string(
                connection_context,
                "environment",
            )
        )

        package.account = self._translate_account(
            payload.get("account"),
            connection_environment=connection_environment,
        )

        package.balance = self._translate_balance(
            financial,
        )

        package.margin = self._translate_margin(
            financial,
        )

        package.equity = self._translate_equity(
            financial,
        )

        package.buying_power = self._translate_buying_power(
            financial,
        )

        package.symbols = self._translate_symbols(
            payload.get("symbols", [])
        )

        package.prices = self._translate_prices(
            payload.get("prices", [])
        )

        package.orders = self._translate_orders(
            payload.get("orders", [])
        )

        package.executions = self._translate_executions(
            payload.get("executions", [])
        )

        package.deals = self._translate_deals(
            payload.get("deals", [])
        )

        package.trades = self._translate_trades(
            payload.get("trades", [])
        )

        package.positions = self._translate_positions(
            payload.get("positions", [])
        )

        package.history = self._translate_history(
            payload.get("history")
        )

        package.activities = self._translate_activities(
            payload.get("activity", [])
        )

        # --------------------------------------------------------------
        # Canonical Evidence Identity
        # --------------------------------------------------------------

        self._apply_identity_context(
            package,
            payload,
        )

        return package

    def translate_item(
        self,
        item: Any,
    ) -> Evidence:
        """
        Item translation is handled by the dedicated
        DesktopEvidence builders.
        """

        raise NotImplementedError(
            "DesktopTranslator.translate_item() is not used."
        )

    # ------------------------------------------------------------------
    # Infrastructure
    # ------------------------------------------------------------------

    def _translate_terminal(
        self,
        terminal: Any,
    ) -> TerminalEvidence | None:
        """
        Translate canonical terminal information.

        This translator is provider-independent.

        Every desktop adapter is responsible for exposing a
        canonical terminal object before translation.
        """

        if terminal is None:
            return None

        return TerminalEvidence(

            terminal_id=TranslationAccessor.as_string(
                terminal,
                "terminal_id",
            ),

            terminal_name=(
                TranslationAccessor.as_string(
                    terminal,
                    "terminal_name",
                )
                or
                ""
            ),

            platform_build=TranslationAccessor.as_string(
                terminal,
                "platform_build",
            ),

            executable_path=TranslationAccessor.as_string(
                terminal,
                "executable_path",
            ),

            installation_directory=TranslationAccessor.as_string(
                terminal,
                "installation_directory",
            ),

            operating_system=None,

            architecture=None,

            language=TranslationAccessor.as_string(
                terminal,
                "language",
            ),

            timezone=None,

            connection_status=(
                ConnectionStatus.CONNECTED
                if TranslationAccessor.as_bool(
                    terminal,
                    "connected",
                    False,
                )
                else ConnectionStatus.DISCONNECTED
            ),

            connected_at=None,

            disconnected_at=None,

            last_heartbeat=None,

            last_synchronization=None,

            session_id=None,

            session_active=TranslationAccessor.as_bool(
                terminal,
                "session_active",
                False,
            ),
        )


    def _translate_user(
        self,
        user: dict | None,
    ) -> UserEvidence | None:

        if not user:
            return None

        return UserEvidence(

            user_id=TranslationAccessor.as_string(
                user,
                "user_id",
            ),

            login=TranslationAccessor.as_string(
                user,
                "user_name",
            ),

            display_name=TranslationAccessor.as_string(
                user,
                "full_name",
            ),

            email=TranslationAccessor.as_string(
                user,
                "email",
            ),

            locale=TranslationAccessor.as_string(
                user,
                "timezone",
            ),
        )


    def _translate_broker(
        self,
        broker: dict | None,
    ) -> BrokerEvidence | None:

        if not broker:
            return None

        return BrokerEvidence(

            broker_id=TranslationAccessor.as_string(
                broker,
                "broker_id",
            ),

            broker_name=(
                TranslationAccessor.as_string(
                    broker,
                    "broker_name",
                )
                or
                ""
            ),

            legal_name=TranslationAccessor.as_string(
                broker,
                "broker_company",
            ),

            broker_type=TranslationAccessor.as_string(
                broker,
                "broker_type",
            ),

            country=TranslationAccessor.as_string(
                broker,
                "broker_country",
            ),
        )


    def _translate_server(
        self,
        server: dict | None,
    ) -> ServerEvidence | None:

        if not server:
            return None

        return ServerEvidence(

            server_id=TranslationAccessor.as_string(
                server,
                "server_id",
            ),

            server_name=(
                TranslationAccessor.as_string(
                    server,
                    "server_name",
                )
                or
                ""
            ),

            server_region=TranslationAccessor.as_string(
                server,
                "server_region",
            ),

            server_timezone=TranslationAccessor.as_string(
                server,
                "server_timezone",
            ),

            server_address=TranslationAccessor.as_string(
                server,
                "server_location",
            ),
        )


    def _translate_account(
        self,
        account: dict | None,
        *,
        connection_environment: str | None = None,
    ) -> AccountEvidence | None:

        if not account:
            return None

        account_type = TranslationAccessor.as_string(
            account,
            "account_type",
        )

        explicit_account_state = TranslationAccessor.as_string(
            account,
            "account_state",
        )

        account_state = AccountState.UNKNOWN

        if explicit_account_state:
            normalized_state = (
                explicit_account_state.strip().lower()
            )

            if normalized_state in {
                "live",
                "real",
                "production",
            }:
                account_state = AccountState.LIVE

            elif normalized_state in {
                "demo",
                "paper",
                "simulation",
            }:
                account_state = AccountState.DEMO

        else:
            trade_mode = TranslationAccessor.as_int(
                account,
                "account_type",
            )

            if trade_mode == 2:
                account_state = AccountState.LIVE

            elif trade_mode in {0, 1}:
                account_state = AccountState.DEMO

            if account_state == AccountState.UNKNOWN:
                normalized_environment = (
                    connection_environment or ""
                ).strip().lower()

                if normalized_environment in {
                    "production",
                    "prod",
                    "live",
                }:
                    account_state = AccountState.LIVE

                elif normalized_environment in {
                    "development",
                    "dev",
                    "demo",
                    "sandbox",
                    "paper",
                }:
                    account_state = AccountState.DEMO

        return AccountEvidence(
            broker_account_id=TranslationAccessor.as_string(
                account,
                "broker_account_id",
            ),

            account_name=TranslationAccessor.as_string(
                account,
                "account_name",
            ),

            account_type=account_type,

            account_state=account_state,

            currency=TranslationAccessor.as_string(
                account,
                "currency",
            ),

            leverage=TranslationAccessor.as_int(
                account,
                "leverage",
            ),
        )


    # ------------------------------------------------------------------
    # Financial
    # ------------------------------------------------------------------

    def _translate_balance(
        self,
        financial: dict | None,
    ) -> BalanceEvidence | None:

        if not financial:
            return None

        balance = TranslationAccessor.as_float(
            financial,
            "balance",
        )

        equity = TranslationAccessor.as_float(
            financial,
            "equity",
        )

        buying_power = TranslationAccessor.as_float(
            financial,
            "buying_power",
        )

        return BalanceEvidence(
            balance=balance,
            equity=equity,
            buying_power=buying_power,
            available_funds=buying_power,
            cash=balance,
            account_value=equity,
        )

    def _translate_margin(
        self,
        financial: dict | None,
    ) -> MarginEvidence | None:

        if not financial:
            return None

        margin_used = TranslationAccessor.as_float(
            financial,
            "margin",
        )

        free_margin = TranslationAccessor.as_float(
            financial,
            "buying_power",
        )

        return MarginEvidence(
            margin_used=margin_used,
            free_margin=free_margin,
            available_margin=free_margin,
        )

    def _translate_equity(
        self,
        financial: dict | None,
    ) -> EquityEvidence | None:

        if not financial:
            return None

        balance = TranslationAccessor.as_float(
            financial,
            "balance",
        )

        equity = TranslationAccessor.as_float(
            financial,
            "equity",
        )

        return EquityEvidence(
            opening_balance=balance,
            current_balance=balance,
            current_equity=equity,
        )

    def _translate_buying_power(
        self,
        financial: dict | None,
    ) -> BuyingPowerEvidence | None:

        if not financial:
            return None

        buying_power = TranslationAccessor.as_float(
            financial,
            "buying_power",
        )

        equity = TranslationAccessor.as_float(
            financial,
            "equity",
        )

        return BuyingPowerEvidence(
            buying_power=buying_power,
            available_margin=buying_power,
            available_equity=equity,
        )

    # ------------------------------------------------------------------
    # Market
    # ------------------------------------------------------------------

    def _translate_symbols(
        self,
        values,
    ) -> list[SymbolEvidence]:

        values = values or []

        symbols: list[SymbolEvidence] = []

        for value in values:

            symbol = (
                TranslationAccessor.as_string(
                    value,
                    "name",
                )
                or TranslationAccessor.as_string(
                    value,
                    "symbol",
                )
                or TranslationAccessor.as_string(
                    value,
                    "symbol_name",
                )
                or TranslationAccessor.as_string(
                    value,
                    "code",
                )
            )

            symbols.append(
                SymbolEvidence(
                    symbol=symbol,

                    symbol_id=symbol,

                    display_name=symbol,

                    description=TranslationAccessor.as_string(
                        value,
                        "description",
                    ),

                    base_currency=TranslationAccessor.as_string(
                        value,
                        "currency_base",
                    ),

                    quote_currency=TranslationAccessor.as_string(
                        value,
                        "currency_profit",
                    ),

                    margin_currency=TranslationAccessor.as_string(
                        value,
                        "currency_margin",
                    ),

                    contract_size=TranslationAccessor.as_float(
                        value,
                        "trade_contract_size",
                    ),

                    point_size=TranslationAccessor.as_float(
                        value,
                        "point",
                    ),

                    tick_size=TranslationAccessor.as_float(
                        value,
                        "trade_tick_size",
                    ),

                    tick_value=TranslationAccessor.as_float(
                        value,
                        "trade_tick_value",
                    ),

                    minimum_volume=TranslationAccessor.as_float(
                        value,
                        "volume_min",
                    ),

                    maximum_volume=TranslationAccessor.as_float(
                        value,
                        "volume_max",
                    ),

                    volume_step=TranslationAccessor.as_float(
                        value,
                        "volume_step",
                    ),

                    trading_enabled=bool(
                        TranslationAccessor.as_int(
                            value,
                            "trade_mode",
                            0,
                        )
                    ),
                )
            )

        return symbols


    def _translate_prices(
        self,
        values,
    ) -> list[PriceEvidence]:

        values = values or []

        prices: list[PriceEvidence] = []

        for value in values:

            bid = TranslationAccessor.as_float(
                value,
                "bid",
            )

            ask = TranslationAccessor.as_float(
                value,
                "ask",
            )

            midpoint = None

            if bid is not None and ask is not None:
                midpoint = (bid + ask) / 2.0

            prices.append(

                PriceEvidence(

                    price_id=TranslationAccessor.as_string(
                        value,
                        "name",
                    ),

                    bid=bid,

                    ask=ask,

                    last=TranslationAccessor.as_float(
                        value,
                        "last",
                    ),

                    high=TranslationAccessor.as_float(
                        value,
                        "askhigh",
                    ),

                    low=TranslationAccessor.as_float(
                        value,
                        "asklow",
                    ),

                    spread=TranslationAccessor.as_float(
                        value,
                        "spread",
                    ),

                    volume=TranslationAccessor.as_float(
                        value,
                        "volume_real",
                    ),

                    midpoint=midpoint,
                )
            )

        return prices

    # ------------------------------------------------------------------
    # Trading
    # ------------------------------------------------------------------

    def _translate_orders(
        self,
        values,
    ) -> list[OrderEvidence]:

        values = values or []

        orders: list[OrderEvidence] = []

        for value in values:

            volume = TranslationAccessor.as_float(
                value,
                "volume_initial",
            )

            current_volume = TranslationAccessor.as_float(
                value,
                "volume_current",
            )

            filled = (
                volume - current_volume
                if volume is not None and current_volume is not None
                else None
            )

            orders.append(
                OrderEvidence(
                    order_id=TranslationAccessor.as_identifier(
                        value,
                        "order_id",
                    )
                    or TranslationAccessor.as_identifier(
                        value,
                        "ticket",
                    ),

                    client_order_id=TranslationAccessor.as_identifier(
                        value,
                        "client_order_id",
                    ),

                    parent_order_id=TranslationAccessor.as_identifier(
                        value,
                        "parent_order_id",
                    ),

                    order_type=TranslationAccessor.as_string(
                        value,
                        "order_type",
                    )
                    or TranslationAccessor.as_string(
                        value,
                        "type",
                    ),

                    side=TranslationAccessor.as_string(
                        value,
                        "side",
                    ),

                    status=TranslationAccessor.as_string(
                        value,
                        "status",
                    )
                    or TranslationAccessor.as_string(
                        value,
                        "state",
                    ),

                    time_in_force=TranslationAccessor.as_string(
                        value,
                        "time_in_force",
                    ),

                    symbol=TranslationAccessor.as_string(
                        value,
                        "symbol",
                    ),

                    quantity=volume,

                    filled_quantity=filled,

                    remaining_quantity=current_volume,

                    limit_price=TranslationAccessor.as_float(
                        value,
                        "limit_price",
                    )
                    or TranslationAccessor.as_float(
                        value,
                        "price_open",
                    ),

                    stop_price=TranslationAccessor.as_float(
                        value,
                        "stop_price",
                    )
                    or TranslationAccessor.as_float(
                        value,
                        "price_stoplimit",
                    ),

                    average_fill_price=TranslationAccessor.as_float(
                        value,
                        "average_fill_price",
                    ),

                    commission=TranslationAccessor.as_float(
                        value,
                        "commission",
                    ),

                    swap=TranslationAccessor.as_float(
                        value,
                        "swap",
                    ),

                    comment=TranslationAccessor.as_string(
                        value,
                        "comment",
                    ),

                    strategy_id=TranslationAccessor.as_string(
                        value,
                        "strategy_id",
                    ),
                )
            )

        return orders


    def _translate_executions(
        self,
        values,
    ) -> list[ExecutionEvidence]:

        values = values or []

        executions: list[ExecutionEvidence] = []

        for value in values:

            executions.append(
                ExecutionEvidence(
                    execution_id=TranslationAccessor.as_identifier(
                        value,
                        "execution_id",
                    )
                    or TranslationAccessor.as_identifier(
                        value,
                        "ticket",
                    ),

                    order_id=TranslationAccessor.as_identifier(
                        value,
                        "order_id",
                    )
                    or TranslationAccessor.as_identifier(
                        value,
                        "order",
                    ),

                    execution_type=TranslationAccessor.as_string(
                        value,
                        "execution_type",
                    ),

                    execution_price=TranslationAccessor.as_float(
                        value,
                        "execution_price",
                    )
                    or TranslationAccessor.as_float(
                        value,
                        "price",
                    ),

                    execution_quantity=TranslationAccessor.as_float(
                        value,
                        "execution_quantity",
                    )
                    or TranslationAccessor.as_float(
                        value,
                        "volume",
                    ),

                    execution_time=(
                        TranslationAccessor.get(
                            value,
                            "execution_time",
                        )
                        or TranslationAccessor.get(
                            value,
                            "time",
                        )
                    ),

                    liquidity=TranslationAccessor.as_string(
                        value,
                        "liquidity",
                    ),

                    venue=TranslationAccessor.as_string(
                        value,
                        "venue",
                    ),

                    execution_reference=TranslationAccessor.as_identifier(
                        value,
                        "execution_reference",
                    ),

                    commission=TranslationAccessor.as_float(
                        value,
                        "commission",
                    ),

                    fees=TranslationAccessor.as_float(
                        value,
                        "fees",
                    )
                    if TranslationAccessor.get(value, "fees") is not None
                    else TranslationAccessor.as_float(
                        value,
                        "fee",
                    ),

                    slippage=TranslationAccessor.as_float(
                        value,
                        "slippage",
                    ),
                )
            )

        return executions


    def _translate_deals(
        self,
        values,
    ) -> list[DealEvidence]:

        values = values or []

        deals: list[DealEvidence] = []

        for value in values:

            deals.append(
                DealEvidence(
                    deal_id=TranslationAccessor.as_identifier(
                        value,
                        "deal_id",
                    )
                    or TranslationAccessor.as_identifier(
                        value,
                        "ticket",
                    ),

                    execution_id=TranslationAccessor.as_identifier(
                        value,
                        "execution_id",
                    ),

                    order_id=TranslationAccessor.as_identifier(
                        value,
                        "order_id",
                    )
                    or TranslationAccessor.as_identifier(
                        value,
                        "order",
                    ),

                    deal_type=TranslationAccessor.as_string(
                        value,
                        "deal_type",
                    ),

                    side=TranslationAccessor.as_string(
                        value,
                        "side",
                    ),

                    symbol=TranslationAccessor.as_string(
                        value,
                        "symbol",
                    ),

                    quantity=TranslationAccessor.as_float(
                        value,
                        "volume",
                    ),

                    price=TranslationAccessor.as_float(
                        value,
                        "price",
                    ),

                    realized_pnl=TranslationAccessor.as_float(
                        value,
                        "realized_pnl",
                    )
                    or TranslationAccessor.as_float(
                        value,
                        "profit",
                    ),

                    commission=TranslationAccessor.as_float(
                        value,
                        "commission",
                    ),

                    swap=TranslationAccessor.as_float(
                        value,
                        "swap",
                    ),

                    fee=TranslationAccessor.as_float(
                        value,
                        "fee",
                    )
                    if TranslationAccessor.get(value, "fee") is not None
                    else TranslationAccessor.as_float(
                        value,
                        "fees",
                    ),

                    deal_time=(
                        TranslationAccessor.get(
                            value,
                            "deal_time",
                        )
                        or TranslationAccessor.get(
                            value,
                            "time",
                        )
                    ),

                    external_reference=TranslationAccessor.as_identifier(
                        value,
                        "external_reference",
                    ),
                )
            )

        return deals


    def _translate_trades(
        self,
        values,
    ) -> list[TradeEvidence]:

        values = values or []

        trades: list[TradeEvidence] = []

        for value in values:

            trades.append(
                TradeEvidence(
                    trade_id=TranslationAccessor.as_identifier(
                        value,
                        "trade_id",
                    )
                    or TranslationAccessor.as_identifier(
                        value,
                        "ticket",
                    ),

                    broker_trade_id=TranslationAccessor.as_identifier(
                        value,
                        "broker_trade_id",
                    ),

                    order_id=TranslationAccessor.as_identifier(
                        value,
                        "order_id",
                    ),

                    execution_id=TranslationAccessor.as_identifier(
                        value,
                        "execution_id",
                    ),

                    deal_id=TranslationAccessor.as_identifier(
                        value,
                        "deal_id",
                    ),

                    broker_ticket=TranslationAccessor.as_identifier(
                        value,
                        "broker_ticket",
                    )
                    or TranslationAccessor.as_identifier(
                        value,
                        "ticket",
                    ),

                    symbol=TranslationAccessor.as_string(
                        value,
                        "symbol",
                    ),

                    side=TranslationAccessor.as_string(
                        value,
                        "side",
                    ),

                    trade_status=TranslationAccessor.as_string(
                        value,
                        "trade_status",
                    ),

                    quantity=TranslationAccessor.as_float(
                        value,
                        "volume",
                    ),

                    entry_price=TranslationAccessor.as_float(
                        value,
                        "entry_price",
                    )
                    or TranslationAccessor.as_float(
                        value,
                        "price",
                    ),

                    exit_price=TranslationAccessor.as_float(
                        value,
                        "exit_price",
                    ),

                    average_entry_price=TranslationAccessor.as_float(
                        value,
                        "average_entry_price",
                    ),

                    average_exit_price=TranslationAccessor.as_float(
                        value,
                        "average_exit_price",
                    ),

                    stop_loss=TranslationAccessor.as_float(
                        value,
                        "stop_loss",
                    ),

                    take_profit=TranslationAccessor.as_float(
                        value,
                        "take_profit",
                    ),

                    realized_pnl=TranslationAccessor.as_float(
                        value,
                        "realized_pnl",
                    )
                    or TranslationAccessor.as_float(
                        value,
                        "profit",
                    ),

                    unrealized_pnl=TranslationAccessor.as_float(
                        value,
                        "unrealized_pnl",
                    ),

                    gross_pnl=TranslationAccessor.as_float(
                        value,
                        "gross_pnl",
                    ),

                    net_pnl=TranslationAccessor.as_float(
                        value,
                        "net_pnl",
                    ),

                    commission=TranslationAccessor.as_float(
                        value,
                        "commission",
                    ),

                    swap=TranslationAccessor.as_float(
                        value,
                        "swap",
                    ),

                    fees=TranslationAccessor.as_float(
                        value,
                        "fees",
                    )
                    if TranslationAccessor.get(value, "fees") is not None
                    else TranslationAccessor.as_float(
                        value,
                        "fee",
                    ),

                    slippage=TranslationAccessor.as_float(
                        value,
                        "slippage",
                    ),

                    strategy_id=TranslationAccessor.as_identifier(
                        value,
                        "strategy_id",
                    ),

                    strategy_name=TranslationAccessor.as_string(
                        value,
                        "strategy_name",
                    ),

                    trade_reference=TranslationAccessor.as_identifier(
                        value,
                        "trade_reference",
                    ),
                )
            )

        return trades


    def _translate_positions(
        self,
        values,
    ) -> list[PositionEvidence]:

        values = values or []

        positions: list[PositionEvidence] = []

        for value in values:

            positions.append(
                PositionEvidence(
                    position_id=TranslationAccessor.as_identifier(
                        value,
                        "position_id",
                    )
                    or TranslationAccessor.as_identifier(
                        value,
                        "ticket",
                    ),

                    broker_position_id=TranslationAccessor.as_identifier(
                        value,
                        "broker_position_id",
                    )
                    or TranslationAccessor.as_identifier(
                        value,
                        "identifier",
                    ),

                    trade_id=TranslationAccessor.as_identifier(
                        value,
                        "trade_id",
                    ),

                    side=TranslationAccessor.as_string(
                        value,
                        "side",
                    ),

                    position_status=TranslationAccessor.as_string(
                        value,
                        "position_status",
                    ),

                    symbol=TranslationAccessor.as_string(
                        value,
                        "symbol",
                    ),

                    quantity=TranslationAccessor.as_float(
                        value,
                        "volume",
                    ),

                    open_price=TranslationAccessor.as_float(
                        value,
                        "open_price",
                    )
                    or TranslationAccessor.as_float(
                        value,
                        "price_open",
                    ),

                    current_price=TranslationAccessor.as_float(
                        value,
                        "current_price",
                    )
                    or TranslationAccessor.as_float(
                        value,
                        "price_current",
                    ),

                    average_price=TranslationAccessor.as_float(
                        value,
                        "average_price",
                    ),

                    stop_loss=TranslationAccessor.as_float(
                        value,
                        "stop_loss",
                    )
                    or TranslationAccessor.as_float(
                        value,
                        "sl",
                    ),

                    take_profit=TranslationAccessor.as_float(
                        value,
                        "take_profit",
                    )
                    or TranslationAccessor.as_float(
                        value,
                        "tp",
                    ),

                    unrealized_pnl=TranslationAccessor.as_float(
                        value,
                        "unrealized_pnl",
                    )
                    or TranslationAccessor.as_float(
                        value,
                        "profit",
                    ),

                    realized_pnl=TranslationAccessor.as_float(
                        value,
                        "realized_pnl",
                    ),

                    gross_pnl=TranslationAccessor.as_float(
                        value,
                        "gross_pnl",
                    ),

                    net_pnl=TranslationAccessor.as_float(
                        value,
                        "net_pnl",
                    ),

                    margin_used=TranslationAccessor.as_float(
                        value,
                        "margin_used",
                    ),

                    exposure=TranslationAccessor.as_float(
                        value,
                        "exposure",
                    ),

                    overnight_swap=TranslationAccessor.as_float(
                        value,
                        "overnight_swap",
                    )
                    if TranslationAccessor.get(
                        value,
                        "overnight_swap",
                    ) is not None
                    else TranslationAccessor.as_float(
                        value,
                        "swap",
                    ),

                    liquidation_price=TranslationAccessor.as_float(
                        value,
                        "liquidation_price",
                    ),

                    risk_percentage=TranslationAccessor.as_float(
                        value,
                        "risk_percentage",
                    ),

                    account_exposure_pct=TranslationAccessor.as_float(
                        value,
                        "account_exposure_pct",
                    ),

                    floating_drawdown=TranslationAccessor.as_float(
                        value,
                        "floating_drawdown",
                    ),

                    highest_profit=TranslationAccessor.as_float(
                        value,
                        "highest_profit",
                    ),

                    maximum_drawdown=TranslationAccessor.as_float(
                        value,
                        "maximum_drawdown",
                    ),

                    hedge_group=TranslationAccessor.as_string(
                        value,
                        "hedge_group",
                    ),
                )
            )

        return positions


    def _translate_history(
        self,
        values,
    ) -> HistoryEvidence | None:

        values = values or []

        if not values:
            return None

        order_ids: list[str] = []

        for value in values:
            identifier = (
                TranslationAccessor.as_identifier(
                    value,
                    "order_id",
                )
                or
                TranslationAccessor.as_identifier(
                    value,
                    "ticket",
                )
            )

            if identifier:
                order_ids.append(identifier)

        return HistoryEvidence(
            orders=order_ids,
            total_orders=len(order_ids),
            history_status="synchronized",
        )


    def _translate_activities(
        self,
        values,
    ) -> list[ActivityEvidence]:

        values = values or []

        activities: list[ActivityEvidence] = []

        for value in values:

            activities.append(

                ActivityEvidence(

                    activity_type="desktop",

                    category="platform",

                    message=TranslationAccessor.as_string(
                        value,
                        "comment",
                    ),

                    details={},
                )
            )

        return activities


# ============================================================================
# Public Exports
# ============================================================================

__all__ = [
    "BaseTranslator",
    "TranslationContext",
    "TranslationHelper",
    "TranslationAccessor",
    "TranslationPipeline",
    "DesktopTranslator",
]
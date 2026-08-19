"""
Trading Truth Layer (TTL)

Universal Evidence Adapter (UEA)

MetaTrader 4 Desktop Adapter
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Dict

from .base_adapter import BaseDesktopAdapter
from .bridges.mt4_bridge import MT4Bridge
from ..normalizer import desktop_evidence_normalizer
from ..verification import VerificationSnapshot


class MT4Adapter(BaseDesktopAdapter):
    """
    Thin adapter for MetaTrader 4.

    MT4 has no official Python API equivalent to MT5.

    Therefore this adapter communicates with an external
    bridge (EA / ZeroMQ / TCP / Named Pipe / etc.).

    The bridge implementation is intentionally outside TTL.

    This adapter performs only native evidence acquisition.

    It does not perform:

        • Translation
        • Validation
        • Verification
        • Business Logic
    """

    @staticmethod
    def _read_value(
        source: Any,
        *keys: str,
        default: Any = None,
    ) -> Any:
        """
        Read a value from either a mapping or an object without
        exposing provider-native objects downstream.
        """

        if source is None:
            return default

        if isinstance(source, dict):
            for key in keys:
                value = source.get(key)
                if value is not None:
                    return value
            return default

        for key in keys:
            value = getattr(source, key, None)
            if value is not None:
                return value

        return default

    @staticmethod
    def _to_utc(value: Any) -> datetime | None:
        """
        Convert supported MT4/bridge timestamps into explicit UTC.
        """

        if value is None:
            return None

        if isinstance(value, datetime):
            if value.tzinfo is None:
                return value.replace(tzinfo=UTC)
            return value.astimezone(UTC)

        try:
            return datetime.fromtimestamp(
                float(value),
                tz=UTC,
            )
        except (
            TypeError,
            ValueError,
            OSError,
            OverflowError,
        ):
            return None

    @staticmethod
    def _to_record(
        value: Any,
    ) -> Dict[str, Any]:
        """
        Convert a bridge object into a plain dictionary.

        Provider-native objects must not escape the adapter boundary.
        Existing dictionaries are copied so downstream code cannot
        accidentally mutate bridge-owned structures.
        """

        if value is None:
            return {}

        if isinstance(value, dict):
            return dict(value)

        try:
            return dict(vars(value))
        except TypeError:
            return {"value": value}

    @classmethod
    def _to_records(
        cls,
        values: Any,
    ) -> list[Dict[str, Any]]:
        """
        Convert an iterable of bridge records into plain dictionaries.
        """

        if values is None:
            return []

        if isinstance(values, dict):
            return [dict(values)]

        if isinstance(values, (str, bytes)):
            return [{"value": values}]

        try:
            return [
                cls._to_record(value)
                for value in values
            ]
        except TypeError:
            return [cls._to_record(values)]

    def __init__(
        self,
        *,
        login: int | str | None = None,
        password: str | None = None,
        server: str | None = None,
        path: str | None = None,
        bridge: Any = None,
    ) -> None:
        """
        Construct the MT4 adapter using the canonical Desktop Engine
        connection boundary.

        The Provider Connections layer supplies the canonical MT4
        connection parameters.

        The MT4 bridge is provider-specific and is constructed here.
        """

        self.login_id = (
            int(login)
            if login not in (None, "")
            else None
        )

        self.password = password
        self.server = server
        self.path = path

        self.bridge = bridge or MT4Bridge(
            login=self.login_id,
            password=self.password,
            server=self.server,
            path=self.path,
        )

    # ------------------------------------------------------------------
    # Provider Information
    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:
        return "MetaTrader 4"

    @property
    def provider_version(self) -> str:
        if self.bridge is None:
            return "unknown"

        version = getattr(
            self.bridge,
            "version",
            None,
        )

        if callable(version):
            version = version()

        return str(version) if version is not None else "unknown"

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def connect(self) -> None:
        """
        Connect to the provider-specific MT4 bridge.
        """

        self.bridge.connect()

    def disconnect(self) -> None:
        """
        Disconnect from the provider-specific MT4 bridge.
        """

        self.bridge.disconnect()

    def is_connected(self) -> bool:
        """
        Determine whether the MT4 bridge is connected.
        """

        return bool(self.bridge.is_connected())

    # ------------------------------------------------------------------
    # Infrastructure Builders
    # ------------------------------------------------------------------

    def _build_terminal(self):

        terminal = self._to_record(
            self.bridge.terminal()
        )

        return {
            "terminal_id": self._read_value(
                terminal,
                "terminal_id",
                "id",
            ),
            "terminal_name": self._read_value(
                terminal,
                "terminal_name",
                "name",
            ),
            "platform_build": self._read_value(
                terminal,
                "platform_build",
                "build",
                "version",
            ),
            "executable_path": self._read_value(
                terminal,
                "executable_path",
                "path",
            ),
            "operating_system": self._read_value(
                terminal,
                "operating_system",
                "os",
            ),
            "architecture": self._read_value(
                terminal,
                "architecture",
            ),
            "language": self._read_value(
                terminal,
                "language",
            ),
            "timezone": self._read_value(
                terminal,
                "timezone",
            ),
        }

    def _build_user(self):

        user = getattr(
            self.bridge,
            "user",
            lambda: None,
        )()

        user = self._to_record(user)

        return {
            "user_id": self._read_value(
                user,
                "user_id",
                "id",
            ),
            "login": self._read_value(
                user,
                "login",
                "username",
                "account_id",
            ),
            "display_name": self._read_value(
                user,
                "display_name",
                "name",
            ),
            "email": self._read_value(
                user,
                "email",
            ),
            "company": self._read_value(
                user,
                "company",
            ),
            "authenticated": self.is_connected(),
        }

    def _build_broker(self):

        broker = getattr(
            self.bridge,
            "broker",
            lambda: None,
        )()

        broker = self._to_record(broker)

        return {
            "broker_id": self._read_value(
                broker,
                "broker_id",
                "id",
            ),
            "broker_name": self._read_value(
                broker,
                "broker_name",
                "name",
                "company",
            ),
        }

    def _build_server(self):

        server = getattr(
            self.bridge,
            "server",
            lambda: None,
        )()

        server = self._to_record(server)

        return {
            "server_id": self._read_value(
                server,
                "server_id",
                "id",
            ),
            "server_name": self._read_value(
                server,
                "server_name",
                "name",
                "server",
            ),
            "server_address": self._read_value(
                server,
                "server_address",
                "address",
                "host",
            ),
            "server_region": self._read_value(
                server,
                "server_region",
                "region",
            ),
            "server_timezone": self._read_value(
                server,
                "server_timezone",
                "timezone",
            ),
            "server_version": self._read_value(
                server,
                "server_version",
                "version",
            ),
        }

    def _build_account(self):

        account = self._to_record(
            self.bridge.account()
        )

        return {
            "broker_account_id": self._read_value(
                account,
                "broker_account_id",
                "account_id",
                "account_number",
                "login",
                "id",
            ),
            "account_name": self._read_value(
                account,
                "account_name",
                "name",
            ),
            "account_alias": self._read_value(
                account,
                "account_alias",
                "alias",
            ),
            "account_type": self._read_value(
                account,
                "account_type",
                "type",
            ),
            "currency": self._read_value(
                account,
                "currency",
            ),
            "leverage": self._read_value(
                account,
                "leverage",
            ),
            "owner_name": self._read_value(
                account,
                "owner_name",
                "owner",
                "name",
            ),
            "trading_enabled": self._read_value(
                account,
                "trading_enabled",
                default=True,
            ),
            "read_only": self._read_value(
                account,
                "read_only",
                default=False,
            ),
            "hedging_enabled": self._read_value(
                account,
                "hedging_enabled",
            ),
            "netting_enabled": self._read_value(
                account,
                "netting_enabled",
            ),
            "margin_mode": self._read_value(
                account,
                "margin_mode",
            ),
            "account_state": self._read_value(
                account,
                "account_state",
            ),
        }

    # ------------------------------------------------------------------
    # Financial Builders
    # ------------------------------------------------------------------

    def _build_financial(self):

        financial = self._to_record(
            self.bridge.financial()
        )

        return {
            "balance": self._read_value(
                financial,
                "balance",
            ),
            "equity": self._read_value(
                financial,
                "equity",
            ),
            "margin": self._read_value(
                financial,
                "margin",
                "margin_used",
            ),
            "buying_power": self._read_value(
                financial,
                "buying_power",
                "margin_free",
                "available_funds",
                "free_margin",
            ),
        }

    # ------------------------------------------------------------------
    # Market Builders
    # ------------------------------------------------------------------

    def _build_symbols(self):

        symbols = self.bridge.symbols()

        normalized = []

        for symbol in self._to_records(symbols):
            normalized.append(
                {
                    "name": self._read_value(
                        symbol,
                        "name",
                        "symbol",
                        "symbol_name",
                    ),
                    "description": self._read_value(
                        symbol,
                        "description",
                        "symbol_description",
                    ),
                    "path": self._read_value(
                        symbol,
                        "path",
                    ),
                    "currency_base": self._read_value(
                        symbol,
                        "currency_base",
                        "base_currency",
                    ),
                    "currency_profit": self._read_value(
                        symbol,
                        "currency_profit",
                        "quote_currency",
                        "profit_currency",
                    ),
                    "currency_margin": self._read_value(
                        symbol,
                        "currency_margin",
                        "margin_currency",
                    ),
                    "trade_mode": self._read_value(
                        symbol,
                        "trade_mode",
                    ),
                    "digits": self._read_value(
                        symbol,
                        "digits",
                    ),
                    "point": self._read_value(
                        symbol,
                        "point",
                        "point_size",
                    ),
                    "trade_contract_size": self._read_value(
                        symbol,
                        "trade_contract_size",
                        "contract_size",
                    ),
                    "trade_tick_size": self._read_value(
                        symbol,
                        "trade_tick_size",
                        "tick_size",
                    ),
                    "trade_tick_value": self._read_value(
                        symbol,
                        "trade_tick_value",
                        "tick_value",
                    ),
                    "volume_min": self._read_value(
                        symbol,
                        "volume_min",
                        "minimum_volume",
                        "min_volume",
                    ),
                    "volume_max": self._read_value(
                        symbol,
                        "volume_max",
                        "maximum_volume",
                        "max_volume",
                    ),
                    "volume_step": self._read_value(
                        symbol,
                        "volume_step",
                        "volume_increment",
                    ),
                }
            )

        return normalized

    def _build_prices(self):

        prices = self.bridge.prices()

        normalized = []

        for price in self._to_records(prices):
            normalized.append(
                {
                    "name": self._read_value(
                        price,
                        "name",
                        "symbol",
                        "symbol_name",
                    ),
                    "time": self._to_utc(
                        self._read_value(
                            price,
                            "time",
                            "timestamp",
                            "price_time",
                        )
                    ),
                    "bid": self._read_value(
                        price,
                        "bid",
                        "bid_price",
                    ),
                    "ask": self._read_value(
                        price,
                        "ask",
                        "ask_price",
                    ),
                    "last": self._read_value(
                        price,
                        "last",
                        "last_price",
                    ),
                    "volume": self._read_value(
                        price,
                        "volume",
                    ),
                    "volume_real": self._read_value(
                        price,
                        "volume_real",
                    ),
                }
            )

        return normalized

    # ------------------------------------------------------------------
    # Trading Builders
    # ------------------------------------------------------------------

    def _build_orders(self):

        orders = self.bridge.orders()

        normalized = []

        for order in self._to_records(orders):
            order_id = self._read_value(
                order,
                "order_id",
                "ticket",
                "id",
            )

            normalized.append(
                {
                    "order_id": (
                        str(order_id)
                        if order_id is not None
                        else None
                    ),
                    "symbol": self._read_value(
                        order,
                        "symbol",
                        "name",
                    ),
                    "volume_initial": self._read_value(
                        order,
                        "volume_initial",
                        "initial_volume",
                        "volume",
                    ),
                    "volume_current": self._read_value(
                        order,
                        "volume_current",
                        "remaining_volume",
                    ),
                    "order_type": self._read_value(
                        order,
                        "order_type",
                        "type",
                    ),
                    "side": self._read_value(
                        order,
                        "side",
                        "direction",
                    ),
                    "price_open": self._read_value(
                        order,
                        "price_open",
                        "open_price",
                        "price",
                    ),
                    "price_current": self._read_value(
                        order,
                        "price_current",
                        "current_price",
                    ),
                    "price_stoplimit": self._read_value(
                        order,
                        "price_stoplimit",
                        "stop_limit_price",
                    ),
                    "stop_loss": self._read_value(
                        order,
                        "stop_loss",
                        "sl",
                    ),
                    "take_profit": self._read_value(
                        order,
                        "take_profit",
                        "tp",
                    ),
                    "comment": self._read_value(
                        order,
                        "comment",
                    ),
                    "time": self._to_utc(
                        self._read_value(
                            order,
                            "time",
                            "time_setup",
                            "created_at",
                            "created_time",
                        )
                    ),
                    "time_done": self._to_utc(
                        self._read_value(
                            order,
                            "time_done",
                            "closed_at",
                            "completed_at",
                        )
                    ),
                }
            )

        return normalized

    def _build_executions(self):

        executions = self.bridge.executions()

        return self._to_records(executions)

    def _build_deals(self):

        deals = self.bridge.deals()

        normalized = []

        for deal in self._to_records(deals):
            deal_id = self._read_value(
                deal,
                "deal_id",
                "ticket",
                "id",
            )

            order_id = self._read_value(
                deal,
                "order_id",
                "order",
                "order_ticket",
            )

            normalized.append(
                {
                    "deal_id": (
                        str(deal_id)
                        if deal_id is not None
                        else None
                    ),
                    "order_id": (
                        str(order_id)
                        if order_id is not None
                        else None
                    ),
                    "execution_id": self._read_value(
                        deal,
                        "execution_id",
                        "execution",
                    ),
                    "deal_type": self._read_value(
                        deal,
                        "deal_type",
                        "type",
                    ),
                    "side": self._read_value(
                        deal,
                        "side",
                        "direction",
                    ),
                    "symbol": self._read_value(
                        deal,
                        "symbol",
                        "name",
                    ),
                    "volume": self._read_value(
                        deal,
                        "volume",
                        "quantity",
                    ),
                    "price": self._read_value(
                        deal,
                        "price",
                        "execution_price",
                    ),
                    "profit": self._read_value(
                        deal,
                        "profit",
                        "pnl",
                    ),
                    "realized_pnl": self._read_value(
                        deal,
                        "realized_pnl",
                        "realized_profit",
                        "profit",
                    ),
                    "commission": self._read_value(
                        deal,
                        "commission",
                    ),
                    "swap": self._read_value(
                        deal,
                        "swap",
                    ),
                    "fee": self._read_value(
                        deal,
                        "fee",
                        "fees",
                    ),
                    "deal_time": self._to_utc(
                        self._read_value(
                            deal,
                            "deal_time",
                            "time",
                            "timestamp",
                        )
                    ),
                    "comment": self._read_value(
                        deal,
                        "comment",
                    ),
                    "external_reference": self._read_value(
                        deal,
                        "external_reference",
                        "external_id",
                    ),
                }
            )

        return normalized

    def _build_trades(self):

        trades = self.bridge.trades()

        return self._to_records(trades)

    def _build_positions(self):

        positions = self.bridge.positions()

        normalized = []

        for position in self._to_records(positions):
            position_id = self._read_value(
                position,
                "position_id",
                "ticket",
                "id",
            )

            broker_position_id = self._read_value(
                position,
                "broker_position_id",
                "identifier",
                "broker_id",
            )

            normalized.append(
                {
                    "position_id": (
                        str(position_id)
                        if position_id is not None
                        else None
                    ),
                    "broker_position_id": (
                        str(broker_position_id)
                        if broker_position_id is not None
                        else None
                    ),
                    "side": self._read_value(
                        position,
                        "side",
                        "direction",
                    ),
                    "symbol": self._read_value(
                        position,
                        "symbol",
                        "name",
                    ),
                    "volume": self._read_value(
                        position,
                        "volume",
                        "quantity",
                    ),
                    "open_price": self._read_value(
                        position,
                        "open_price",
                        "price_open",
                    ),
                    "current_price": self._read_value(
                        position,
                        "current_price",
                        "price_current",
                    ),
                    "stop_loss": self._read_value(
                        position,
                        "stop_loss",
                        "sl",
                    ),
                    "take_profit": self._read_value(
                        position,
                        "take_profit",
                        "tp",
                    ),
                    "unrealized_pnl": self._read_value(
                        position,
                        "unrealized_pnl",
                        "floating_profit",
                        "profit",
                    ),
                    "overnight_swap": self._read_value(
                        position,
                        "overnight_swap",
                        "swap",
                    ),
                    "comment": self._read_value(
                        position,
                        "comment",
                    ),
                    "external_reference": self._read_value(
                        position,
                        "external_reference",
                        "external_id",
                    ),
                    "time": self._to_utc(
                        self._read_value(
                            position,
                            "time",
                            "open_time",
                            "created_at",
                        )
                    ),
                    "time_update": self._to_utc(
                        self._read_value(
                            position,
                            "time_update",
                            "updated_at",
                        )
                    ),
                }
            )

        return normalized

    # ------------------------------------------------------------------
    # History Builders
    # ------------------------------------------------------------------

    def _build_history(self):

        return self._to_records(
            self.bridge.history()
        )

    def _build_activity(self):

        return self._to_records(
            self.bridge.activity()
        )

    # ------------------------------------------------------------------
    # Verification
    # ------------------------------------------------------------------

    def get_verification_snapshot(
        self,
    ) -> VerificationSnapshot:
        """
        Return provider-neutral verification facts.

        This method performs provider-native observation only.
        Verification decisions remain in the shared
        Desktop Verification Engine.
        """

        terminal = self._build_terminal()
        user = self._build_user()
        broker = self._build_broker()
        server = self._build_server()
        account = self._build_account()

        connected = self.is_connected()

        def read_value(source, *keys):
            if source is None:
                return None

            if isinstance(source, dict):
                for key in keys:
                    value = source.get(key)
                    if value is not None:
                        return value

            for key in keys:
                value = getattr(source, key, None)
                if value is not None:
                    return value

            if isinstance(source, (str, int)):
                return source

            return None

        account_id = read_value(
            account,
            "account_id",
            "account_number",
            "login",
            "id",
            "number",
        )

        if account_id is None:
            account_id = read_value(
                user,
                "account_id",
                "account_number",
                "login",
                "id",
                "number",
            )

        broker_value = read_value(
            broker,
            "name",
            "company",
            "broker",
            "broker_name",
        )

        if broker_value is None and isinstance(
            broker,
            (str, int),
        ):
            broker_value = str(broker)

        server_value = read_value(
            server,
            "name",
            "server",
            "server_name",
        )

        if server_value is None and isinstance(
            server,
            (str, int),
        ):
            server_value = str(server)

        terminal_version = read_value(
            terminal,
            "version",
            "version_string",
            "terminal_version",
            "build",
        )

        if terminal_version is None:
            terminal_version = self.provider_version

        return VerificationSnapshot(
            provider=self.provider_name,
            provider_version=self.provider_version,
            connected=connected,
            account_id=(
                str(account_id)
                if account_id is not None
                else None
            ),
            broker=(
                str(broker_value)
                if broker_value is not None
                else None
            ),
            server=(
                str(server_value)
                if server_value is not None
                else None
            ),
            terminal=self.provider_name,
            terminal_version=(
                str(terminal_version)
                if terminal_version is not None
                else None
            ),
            metadata={
                "terminal_available": terminal is not None,
                "user_available": user is not None,
                "broker_available": broker is not None,
                "server_available": server is not None,
                "account_available": account is not None,
            },
        )

    # ------------------------------------------------------------------
    # Evidence Acquisition
    # ------------------------------------------------------------------

    def acquire(self) -> Dict[str, Any]:
        """
        Acquire the complete MT4 native evidence surface.

        The returned payload is broker-independent and follows
        the canonical Desktop Trading Engine acquisition contract.
        """

        terminal = self._build_terminal()

        user = self._build_user()

        broker = self._build_broker()

        server = self._build_server()

        account = self._build_account()

        financial = self._build_financial()

        symbols = self._build_symbols()

        prices = self._build_prices()

        orders = self._build_orders()

        executions = self._build_executions()

        deals = self._build_deals()

        trades = self._build_trades()

        positions = self._build_positions()

        history = self._build_history()

        activity = self._build_activity()

        payload = {

            # ----------------------------------------------------------
            # Connector Metadata
            # ----------------------------------------------------------

            "connector_name": self.provider_name,

            "connector_version": self.provider_version,

            "schema_version": "1.0",

            # ----------------------------------------------------------
            # Infrastructure
            # ----------------------------------------------------------

            "terminal": terminal,

            "user": user,

            "broker": broker,

            "server": server,

            "account": account,

            # ----------------------------------------------------------
            # Financial
            # ----------------------------------------------------------

            "financial": financial,

            # ----------------------------------------------------------
            # Market
            # ----------------------------------------------------------

            "symbols": symbols,

            "prices": prices,

            # ----------------------------------------------------------
            # Trading
            # ----------------------------------------------------------

            "orders": orders,

            "executions": executions,

            "deals": deals,

            "trades": trades,

            "positions": positions,

            # ----------------------------------------------------------
            # History
            # ----------------------------------------------------------

            "history": history,

            "activity": activity,
        }

        return desktop_evidence_normalizer.normalize(
            payload,
        )
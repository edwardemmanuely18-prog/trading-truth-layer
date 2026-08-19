"""
Trading Truth Layer (TTL)

Universal Evidence Adapter (UEA)

MetaTrader 5 Desktop Adapter
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Dict, Optional

import MetaTrader5 as mt5

from .base_adapter import BaseDesktopAdapter

from ..normalizer import desktop_evidence_normalizer

from ..verification import VerificationSnapshot


class MT5Adapter(BaseDesktopAdapter):
    """
    Thin adapter over the official MetaTrader 5 Python API.

    This adapter performs only native evidence acquisition.

    It does not perform:

        • Translation
        • Validation
        • Verification
        • Business Logic
    """

    def __init__(
        self,
        *,
        login: Optional[int] = None,
        password: Optional[str] = None,
        server: Optional[str] = None,
        path: Optional[str] = None,
    ) -> None:
        self.login_id = login
        self.password = password
        self.server = server
        self.path = path

        print("=" * 80)
        print("MT5 __INIT__")
        print("=" * 80)
        print("login :", login)
        print("server:", server)
        print("path  :", path)
        print("=" * 80)

    # ------------------------------------------------------------------
    # Provider Information
    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:
        return "MetaTrader 5"

    @property
    def provider_version(self) -> str:
        version = mt5.version()

        if version:
            return ".".join(map(str, version))

        return "unknown"

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def connect(self) -> None:
        """
        Initialize the MT5 terminal.
        """

        if not mt5.initialize(path=self.path):
            raise RuntimeError(
                f"MT5 initialization failed: {mt5.last_error()}"
            )

        if self.login_id is not None:

            if not mt5.login(
                login=self.login_id,
                password=self.password,
                server=self.server,
            ):
                raise RuntimeError(
                    f"MT5 login failed: {mt5.last_error()}"
                )

    def disconnect(self) -> None:
        """
        Shutdown MT5.
        """

        mt5.shutdown()

    def is_connected(self) -> bool:
        """
        Determine whether MT5 is connected.
        """

        return mt5.terminal_info() is not None

    # ------------------------------------------------------------------
    # Verification
    # ------------------------------------------------------------------

    def get_verification_snapshot(
        self,
    ) -> VerificationSnapshot:
        """
        Return provider-neutral verification facts from MT5.

        This method performs provider-native observation only.
        Verification decisions remain in the shared
        Desktop Verification Engine.
        """

        terminal = mt5.terminal_info()
        account = mt5.account_info()

        connected = terminal is not None

        account_id = None
        broker = None
        server = self.server

        if account is not None:
            account_login = getattr(
                account,
                "login",
                None,
            )

            if account_login is not None:
                account_id = str(account_login)

            broker = getattr(
                account,
                "company",
                None,
            )

            account_server = getattr(
                account,
                "server",
                None,
            )

            if account_server:
                server = account_server

        terminal_version = None

        version = mt5.version()

        if version:
            terminal_version = ".".join(
                map(str, version)
            )

        return VerificationSnapshot(
            provider=self.provider_name,
            provider_version=self.provider_version,
            connected=connected,
            account_id=account_id,
            broker=broker,
            server=server,
            terminal="MetaTrader 5",
            terminal_version=terminal_version,
            metadata={
                "terminal_available": terminal is not None,
                "account_available": account is not None,
            },
        )

    # ------------------------------------------------------------------
    # Evidence Acquisition
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Infrastructure Builders
    # ------------------------------------------------------------------

    def _build_terminal(self):

        return mt5.terminal_info()


    def _build_account(self):

        return mt5.account_info()


    # ------------------------------------------------------------------
    # Market Builders
    # ------------------------------------------------------------------

    def _build_symbols(self):
        symbols = mt5.symbols_get()

        if symbols is None:
            return []

        normalized = []

        for symbol in symbols:
            normalized.append(
                {
                    "name": getattr(
                        symbol,
                        "name",
                        None,
                    ),

                    "description": getattr(
                        symbol,
                        "description",
                        None,
                    ),

                    "path": getattr(
                        symbol,
                        "path",
                        None,
                    ),

                    "currency_base": getattr(
                        symbol,
                        "currency_base",
                        None,
                    ),

                    "currency_profit": getattr(
                        symbol,
                        "currency_profit",
                        None,
                    ),

                    "currency_margin": getattr(
                        symbol,
                        "currency_margin",
                        None,
                    ),

                    "trade_mode": getattr(
                        symbol,
                        "trade_mode",
                        None,
                    ),

                    "digits": getattr(
                        symbol,
                        "digits",
                        None,
                    ),

                    "point": getattr(
                        symbol,
                        "point",
                        None,
                    ),

                    "trade_contract_size": getattr(
                        symbol,
                        "trade_contract_size",
                        None,
                    ),

                    "trade_tick_size": getattr(
                        symbol,
                        "trade_tick_size",
                        None,
                    ),

                    "trade_tick_value": getattr(
                        symbol,
                        "trade_tick_value",
                        None,
                    ),

                    "volume_min": getattr(
                        symbol,
                        "volume_min",
                        None,
                    ),

                    "volume_max": getattr(
                        symbol,
                        "volume_max",
                        None,
                    ),

                    "volume_step": getattr(
                        symbol,
                        "volume_step",
                        None,
                    ),
                }
            )

        return normalized

    def _build_prices(
        self,
        symbols,
    ):
        prices = []

        for symbol in symbols or []:

            if isinstance(symbol, dict):
                symbol_name = (
                    symbol.get("name")
                    or symbol.get("symbol")
                    or symbol.get("symbol_name")
                )
            else:
                symbol_name = getattr(
                    symbol,
                    "name",
                    None,
                )

            if not symbol_name:
                continue

            tick = mt5.symbol_info_tick(
                symbol_name,
            )

            if tick is None:
                continue

            prices.append(
                {
                    "name": symbol_name,
                    "time": self._map_mt5_time(
                        getattr(
                            tick,
                            "time",
                            None,
                        )
                    ),
                    "bid": getattr(
                        tick,
                        "bid",
                        None,
                    ),
                    "ask": getattr(
                        tick,
                        "ask",
                        None,
                    ),
                    "last": getattr(
                        tick,
                        "last",
                        None,
                    ),
                    "volume": getattr(
                        tick,
                        "volume",
                        None,
                    ),
                    "volume_real": getattr(
                        tick,
                        "volume_real",
                        None,
                    ),
                }
            )

        return prices

    # ------------------------------------------------------------------
    # Canonical Trading Mappers
    # ------------------------------------------------------------------

    @staticmethod
    def _map_mt5_side(
        value: Any,
    ) -> str | None:
        """
        Convert the MT5 position/deal direction enum into the
        provider-neutral canonical side.

        MT5:
            0 -> BUY
            1 -> SELL
        """

        if value is None:
            return None

        if value == getattr(mt5, "ORDER_TYPE_BUY", 0):
            return "BUY"

        if value == getattr(mt5, "ORDER_TYPE_SELL", 1):
            return "SELL"

        return None

    @staticmethod
    def _map_mt5_position_side(
        value: Any,
    ) -> str | None:
        """
        Convert MT5 position direction into canonical side.
        """

        if value is None:
            return None

        if value == getattr(
            mt5,
            "POSITION_TYPE_BUY",
            0,
        ):
            return "BUY"

        if value == getattr(
            mt5,
            "POSITION_TYPE_SELL",
            1,
        ):
            return "SELL"

        return None

    @staticmethod
    def _map_mt5_deal_side(
        value: Any,
    ) -> str | None:
        """
        Convert MT5 deal direction into canonical side.

        Non-directional deal types such as BALANCE are intentionally
        returned as None.
        """

        if value is None:
            return None

        if value == getattr(
            mt5,
            "DEAL_TYPE_BUY",
            0,
        ):
            return "BUY"

        if value == getattr(
            mt5,
            "DEAL_TYPE_SELL",
            1,
        ):
            return "SELL"

        return None

    @staticmethod
    def _map_mt5_order_type(
        value: Any,
    ) -> str | None:
        """
        Preserve MT5 order/deal type information without exposing
        provider-specific enum values downstream.
        """

        if value is None:
            return None

        mapping = {
            getattr(mt5, "ORDER_TYPE_BUY", 0): "BUY",
            getattr(mt5, "ORDER_TYPE_SELL", 1): "SELL",
            getattr(mt5, "ORDER_TYPE_BUY_LIMIT", 2): "BUY_LIMIT",
            getattr(mt5, "ORDER_TYPE_SELL_LIMIT", 3): "SELL_LIMIT",
            getattr(mt5, "ORDER_TYPE_BUY_STOP", 4): "BUY_STOP",
            getattr(mt5, "ORDER_TYPE_SELL_STOP", 5): "SELL_STOP",
            getattr(mt5, "ORDER_TYPE_BUY_STOP_LIMIT", 6): "BUY_STOP_LIMIT",
            getattr(mt5, "ORDER_TYPE_SELL_STOP_LIMIT", 7): "SELL_STOP_LIMIT",
        }

        return mapping.get(
            value,
            str(value),
        )

    @staticmethod
    def _map_mt5_time(
        value: Any,
    ) -> datetime | None:
        """
        Convert an MT5 unix timestamp into an explicit UTC datetime.
        """

        if value is None:
            return None

        if isinstance(value, datetime):
            if value.tzinfo is None:
                return value.replace(
                    tzinfo=UTC
                )

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

    def _build_orders(self):

        orders = mt5.orders_get()

        if orders is None:
            return []

        normalized = []

        for order in orders:

            order_id = getattr(
                order,
                "ticket",
                None,
            )

            normalized.append(
                {
                    "order_id": (
                        str(order_id)
                        if order_id is not None
                        else None
                    ),

                    "symbol": getattr(
                        order,
                        "symbol",
                        None,
                    ),

                    "volume_initial": getattr(
                        order,
                        "volume_initial",
                        None,
                    ),

                    "volume_current": getattr(
                        order,
                        "volume_current",
                        None,
                    ),

                    "order_type": self._map_mt5_order_type(
                        getattr(
                            order,
                            "type",
                            None,
                        )
                    ),

                    "side": self._map_mt5_side(
                        getattr(
                            order,
                            "type",
                            None,
                        )
                    ),

                    "price_open": getattr(
                        order,
                        "price_open",
                        None,
                    ),

                    "price_current": getattr(
                        order,
                        "price_current",
                        None,
                    ),

                    "price_stoplimit": getattr(
                        order,
                        "price_stoplimit",
                        None,
                    ),

                    "stop_loss": getattr(
                        order,
                        "sl",
                        None,
                    ),

                    "take_profit": getattr(
                        order,
                        "tp",
                        None,
                    ),

                    "comment": getattr(
                        order,
                        "comment",
                        None,
                    ),

                    "time": self._map_mt5_time(
                        getattr(
                            order,
                            "time_setup",
                            None,
                        )
                    ),

                    "time_done": self._map_mt5_time(
                        getattr(
                            order,
                            "time_done",
                            None,
                        )
                    ),
                }
            )

        return normalized


    def _build_positions(self):

        positions = mt5.positions_get()

        if positions is None:
            return []

        normalized = []

        for position in positions:

            position_id = getattr(
                position,
                "ticket",
                None,
            )

            normalized.append(
                {
                    "position_id": (
                        str(position_id)
                        if position_id is not None
                        else None
                    ),

                    "broker_position_id": (
                        str(
                            getattr(
                                position,
                                "identifier",
                                ""
                            )
                        )
                        if getattr(
                            position,
                            "identifier",
                            None,
                        ) is not None
                        else None
                    ),

                    "side": self._map_mt5_position_side(
                        getattr(
                            position,
                            "type",
                            None,
                        )
                    ),

                    "symbol": getattr(
                        position,
                        "symbol",
                        None,
                    ),

                    "volume": getattr(
                        position,
                        "volume",
                        None,
                    ),

                    "open_price": getattr(
                        position,
                        "price_open",
                        None,
                    ),

                    "current_price": getattr(
                        position,
                        "price_current",
                        None,
                    ),

                    "stop_loss": getattr(
                        position,
                        "sl",
                        None,
                    ),

                    "take_profit": getattr(
                        position,
                        "tp",
                        None,
                    ),

                    "unrealized_pnl": getattr(
                        position,
                        "profit",
                        None,
                    ),

                    "overnight_swap": getattr(
                        position,
                        "swap",
                        None,
                    ),

                    "comment": getattr(
                        position,
                        "comment",
                        None,
                    ),

                    "external_reference": getattr(
                        position,
                        "external_id",
                        None,
                    ),

                    "time": self._map_mt5_time(
                        getattr(
                            position,
                            "time",
                            None,
                        )
                    ),

                    "time_update": self._map_mt5_time(
                        getattr(
                            position,
                            "time_update",
                            None,
                        )
                    ),
                }
            )

        return normalized


    # ------------------------------------------------------------------
    # History Builders
    # ------------------------------------------------------------------

    def _build_deals(
        self,
        start_time,
        end_time,
    ):

        deals = mt5.history_deals_get(
            start_time,
            end_time,
        )

        if deals is None:
            raise RuntimeError(
                f"history_deals_get failed: {mt5.last_error()}"
            )

        normalized = []

        for deal in deals:

            deal_id = getattr(
                deal,
                "ticket",
                None,
            )

            order_id = getattr(
                deal,
                "order",
                None,
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

                    "execution_id": None,

                    "deal_type": self._map_mt5_order_type(
                        getattr(
                            deal,
                            "type",
                            None,
                        )
                    ),

                    "side": self._map_mt5_deal_side(
                        getattr(
                            deal,
                            "type",
                            None,
                        )
                    ),

                    "symbol": getattr(
                        deal,
                        "symbol",
                        None,
                    ),

                    "volume": getattr(
                        deal,
                        "volume",
                        None,
                    ),

                    "price": getattr(
                        deal,
                        "price",
                        None,
                    ),

                    "profit": getattr(
                        deal,
                        "profit",
                        None,
                    ),

                    "realized_pnl": getattr(
                        deal,
                        "profit",
                        None,
                    ),

                    "commission": getattr(
                        deal,
                        "commission",
                        None,
                    ),

                    "swap": getattr(
                        deal,
                        "swap",
                        None,
                    ),

                    "fee": getattr(
                        deal,
                        "fee",
                        None,
                    ),

                    "deal_time": self._map_mt5_time(
                        getattr(
                            deal,
                            "time",
                            None,
                        )
                    ),

                    "comment": getattr(
                        deal,
                        "comment",
                        None,
                    ),

                    "external_reference": getattr(
                        deal,
                        "external_id",
                        None,
                    ),
                }
            )

        return normalized


    def _build_history(
        self,
        start_time,
        end_time,
    ):

        history = mt5.history_orders_get(
            start_time,
            end_time,
        )

        if history is None:

            raise RuntimeError(

                f"history_orders_get failed: {mt5.last_error()}"

            )

        return history


    def acquire(self) -> Dict[str, Any]:
        """
        Acquire the complete MT5 native evidence surface.

        The returned payload is broker-independent and follows
        the canonical Desktop Trading Engine acquisition contract.
        """

        end_time = datetime.now(UTC)

        start_time = datetime(
            1970,
            1,
            1,
            tzinfo=UTC,
        )

        terminal = self._build_terminal()

        account = self._build_account()

        financial = {

            "balance": getattr(account, "balance", None),

            "equity": getattr(account, "equity", None),

            "margin": getattr(account, "margin", None),

            "buying_power": getattr(
                account,
                "margin_free",
                None,
            ),

        }

        symbols = self._build_symbols()

        prices = self._build_prices(
            symbols,
        )

        orders = self._build_orders()

        positions = self._build_positions()

        deals = self._build_deals(
            start_time,
            end_time,
        )

        history = self._build_history(
            start_time,
            end_time,
        )

        if history is None:
            raise RuntimeError(
                f"history_orders_get failed: {mt5.last_error()}"
            )

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

            "account": account,

            # ----------------------------------------------------------
            # Financial
            # ----------------------------------------------------------

            "financial": {

                "balance": getattr(account, "balance", None),

                "equity": getattr(account, "equity", None),

                "margin": getattr(account, "margin", None),

                "buying_power": getattr(
                    account,
                    "margin_free",
                    None,
                ),

            },

            # ----------------------------------------------------------
            # Market
            # ----------------------------------------------------------

            "symbols": symbols,

            "prices": prices,

            "orders": orders,

            "executions": None,

            "deals": deals,

            "trades": None,

            "positions": positions,

            "history": history,

            "activity": None,
        }

        return desktop_evidence_normalizer.normalize(
            payload,
        )
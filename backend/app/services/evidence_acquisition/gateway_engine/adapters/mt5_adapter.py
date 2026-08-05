"""
Trading Truth Layer (TTL)

Gateway Engine

MetaTrader 5 Adapter

Official MetaTrader 5 Python Integration adapter.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import MetaTrader5 as mt5

from ..models import (
    GatewayType,
)

from ..registry import (
    ProviderDescriptor,
)

from .base_adapter import BaseGatewayAdapter


# ============================================================================
# Snapshot
# ============================================================================


@dataclass(slots=True)
class MT5GatewaySnapshot:
    """
    Raw evidence acquired from a MetaTrader 5 terminal.

    The synchronizer is responsible for converting this snapshot
    into canonical GatewayEvidencePackage objects.
    """

    gateways: List[dict]

    accounts: List[dict]

    instruments: List[dict]

    positions: List[dict]

    orders: List[dict]

    trades: List[dict]

    executions: List[dict]

    market_data: List[dict]

    errors: List[dict]


# ============================================================================
# MT5 Adapter
# ============================================================================


class MT5Adapter(BaseGatewayAdapter):
    """
    Canonical MetaTrader 5 Gateway adapter.

    Uses the official MetaTrader5 Python package while exposing
    canonical Gateway Engine evidence.
    """

    def __init__(
        self,
        *,
        terminal_path: Optional[str] = None,
        login: Optional[int] = None,
        password: Optional[str] = None,
        server: Optional[str] = None,
        timeout: int = 60000,
        portable: bool = False,
    ) -> None:

        super().__init__(
            provider_name="metatrader5",
            gateway_type=GatewayType.MT5,
        )

        self.descriptor = ProviderDescriptor(

            provider_name="metatrader5",

            gateway_type=GatewayType.MT5,

            provider_version="1.0",

            vendor="MetaQuotes",

            description="MetaTrader 5 Gateway",

            supports_streaming=False,

            supports_historical_data=True,

            supports_order_submission=True,

            supports_positions=True,

            supports_trades=True,

            supports_market_data=True,

            supports_account_information=True,

            supports_multi_account=False,

            supports_reconnection=True,

            supported_protocols=[
                "MetaTrader5 Python API",
            ],

            supported_asset_classes=[
                "Forex",
                "CFDs",
                "Metals",
                "Indices",
                "Commodities",
                "Crypto",
                "Stocks",
                "Futures",
            ],
        )

        self.terminal_path = terminal_path

        self.login = login

        self.password = password

        self.server = server

        self.timeout = timeout

        self.portable = portable

        #
        # Runtime state
        #

        self.connected = False

        self.gateway = None

        self.account = None

        self.instruments = []

        self.positions = []

        self.orders = []

        self.trades = []

        self.executions = []

        self.market_data = []

        self.errors = []


# ============================================================================
# Lifecycle
# ============================================================================


    def initialize(
        self,
    ) -> None:
        """
        Initialize the MetaTrader 5 terminal.
        """

        initialized = mt5.initialize(
            path=self.terminal_path,
            login=self.login,
            password=self.password,
            server=self.server,
            timeout=self.timeout,
            portable=self.portable,
        )

        if not initialized:

            self.errors.append(
                {
                    "operation": "initialize",
                    "error": str(
                        mt5.last_error(),
                    ),
                }
            )

            raise RuntimeError(
                f"MT5 initialization failed: {mt5.last_error()}"
            )

        self.mark_initialized()


    def connect(
        self,
    ) -> None:
        """
        Validate terminal connectivity.
        """

        account = mt5.account_info()

        if account is None:

            self.errors.append(
                {
                    "operation": "connect",
                    "error": str(
                        mt5.last_error(),
                    ),
                }
            )

            raise RuntimeError(
                f"Unable to access account: {mt5.last_error()}"
            )

        self.connected = True

        self.mark_connected()


    def disconnect(
        self,
    ) -> None:

        mt5.shutdown()

        self.connected = False

        self.mark_disconnected()


# ============================================================================
# Terminal
# ============================================================================

    def _acquire_terminal(self):

        return mt5.terminal_info()


# ============================================================================
# Account
# ============================================================================

    def _acquire_account(self):

        return mt5.account_info()


# ============================================================================
# Symbols
# ============================================================================

    def _acquire_symbols(self):

        return mt5.symbols_get()


# ============================================================================
# Positions
# ============================================================================

    def _acquire_positions(self):

        return mt5.positions_get()


# ============================================================================
# Orders
# ============================================================================

    def _acquire_orders(self):

        return mt5.orders_get()


# ============================================================================
# Deal History
# ============================================================================

    def _acquire_deals(self):

        return mt5.history_deals_get()


# ============================================================================
# Normalization
# ============================================================================

    @staticmethod
    def _normalize(value):

        if value is None:
            return None

        if hasattr(value, "_asdict"):
            return value._asdict()

        if isinstance(value, (list, tuple)):

            normalized = []

            for item in value:

                if hasattr(item, "_asdict"):
                    normalized.append(item._asdict())
                else:
                    normalized.append(item)

            return normalized

        return value


# ============================================================================
# Snapshot Collection
# ============================================================================

    def _collect_snapshot(
        self,
    ) -> MT5GatewaySnapshot:

        terminal = self._normalize(
            self._acquire_terminal()
        )

        account = self._normalize(
            self._acquire_account()
        )

        symbols = self._normalize(
            self._acquire_symbols()
        )

        positions = self._normalize(
            self._acquire_positions()
        )

        orders = self._normalize(
            self._acquire_orders()
        )

        deals = self._normalize(
            self._acquire_deals()
        )

        self.gateway = {

            "provider": self.provider_name,

            "connected": self.connected,

            "terminal": terminal,
        }

        self.account = account

        self.instruments = symbols or []

        self.positions = positions or []

        self.orders = orders or []

        self.trades = deals or []

        self.executions = []

        self.market_data = []

        return MT5GatewaySnapshot(

            gateways=[
                self.gateway,
            ],

            accounts=(
                [self.account]
                if self.account
                else []
            ),

            instruments=self.instruments,

            positions=self.positions,

            orders=self.orders,

            trades=self.trades,

            executions=self.executions,

            market_data=self.market_data,

            errors=self.errors,
        )


# ============================================================================
# Canonical Acquisition
# ============================================================================

    def acquire(
        self,
    ) -> MT5GatewaySnapshot:
        """
        Acquire a canonical MT5 snapshot.

        Synchronization into GatewayEvidencePackage
        is performed by the GatewaySynchronizer.
        """

        self.record_acquisition()

        return self._collect_snapshot()


# ============================================================================
# Normalization
# ============================================================================

    @staticmethod
    def _normalize(value):
        """
        Normalize MT5 SDK objects into plain Python structures.

        The Gateway Engine should never expose MetaTrader5 SDK
        objects outside the adapter boundary.
        """

        if value is None:
            return None

        if hasattr(value, "_asdict"):
            return value._asdict()

        if isinstance(value, (list, tuple)):

            normalized = []

            for item in value:

                if hasattr(item, "_asdict"):
                    normalized.append(item._asdict())
                else:
                    normalized.append(item)

            return normalized

        return value


# ============================================================================
# Collection
# ============================================================================

    def _collect_evidence(

        self,

        terminal,

        account,

        symbols,

        positions,

        orders,

        deals,

    ) -> Dict[str, Any]:

        terminal = self._normalize(terminal)

        account = self._normalize(account)

        symbols = self._normalize(symbols)

        positions = self._normalize(positions)

        orders = self._normalize(orders)

        deals = self._normalize(deals)

        return {

            "gateways": [

                {

                    "provider": self.provider_name,

                    "connected": self.is_connected,

                    "terminal": terminal,

                }

            ],

            "accounts":

                [account] if account else [],

            "instruments":

                symbols or [],

            "positions":

                positions or [],

            "orders":

                orders or [],

            "trades":

                deals or [],

            "market_data": [],

            "quotes": [],

            "executions": [],
        }


# ============================================================================
# Capabilities
# ============================================================================

    def capabilities(
        self,
    ) -> dict:

        capabilities = super().capabilities()

        capabilities.update(

            {

                "provider_name": self.provider_name,

                "gateway": True,

                "terminal": True,

                "streaming": False,

                "historical_data": True,

                "market_data": True,

                "orders": True,

                "positions": True,

                "trades": True,

                "portfolio": True,

                "account_summary": True,

                "symbols": True,

            }

        )

        return capabilities


# ============================================================================
# Diagnostics
# ============================================================================

    def diagnostics(
        self,
    ) -> dict:

        diagnostics = super().diagnostics()

        diagnostics["mt5"] = {

            "terminal_path":

                self.terminal_path,

            "login":

                self.login,

            "server":

                self.server,

            "portable":

                self.portable,

            "connected":

                self.connected,

            "account":

                self.account,

            "instruments":

                len(self.instruments),

            "positions":

                len(self.positions),

            "orders":

                len(self.orders),

            "trades":

                len(self.trades),

            "executions":

                len(self.executions),

            "market_data":

                len(self.market_data),

            "errors":

                len(self.errors),

        }

        return diagnostics


# ============================================================================
# Cleanup
# ============================================================================

    def close(
        self,
    ) -> None:

        if self.connected:

            mt5.shutdown()

        self.connected = False

        self.mark_closed()


# ============================================================================
# Public Exports
# ============================================================================

__all__ = [

    "MT5GatewaySnapshot",

    "MT5Adapter",

]
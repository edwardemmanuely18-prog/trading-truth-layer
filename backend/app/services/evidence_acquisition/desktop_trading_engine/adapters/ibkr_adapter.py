"""
Trading Truth Layer (TTL)

Universal Evidence Adapter (UEA)

Interactive Brokers Desktop Adapter
"""

from __future__ import annotations

from typing import Any, Dict
import threading

from ibapi.client import EClient
from ibapi.wrapper import EWrapper

from .base_adapter import BaseDesktopAdapter
from ..normalizer import desktop_evidence_normalizer


class _IBKRApplication(EWrapper, EClient):
    """
    Thin wrapper around the official Interactive Brokers
    TWS / Gateway API.

    This class only stores native evidence received from
    the API.
    """

    def __init__(self) -> None:

        EClient.__init__(self, self)

        self.terminal = None

        self.account = {}

        self.financial = {}

        self.symbols = []

        self.prices = []

        self.orders = []

        self.executions = []

        self.deals = []

        self.trades = []

        self.positions = []

        self.history = []

        self.activity = []

        self.connected_event = threading.Event()

        self.next_order_id = None

        self.server_version = None

        self.last_error = None

        self.account_summary_complete = threading.Event()

        self.positions_complete = threading.Event()

        self.open_orders_complete = threading.Event()

    # ----------------------------------------------------------
    # Account Summary
    # ----------------------------------------------------------

    def accountSummary(
        self,
        reqId,
        account,
        tag,
        value,
        currency,
    ):

        self.account.setdefault(
            account,
            {},
        )[tag] = value

        self.financial[tag] = value

    def accountSummaryEnd(
        self,
        reqId: int,
    ):

        self.account_summary_complete.set()

    # ----------------------------------------------------------
    # Positions
    # ----------------------------------------------------------

    def position(
        self,
        account,
        contract,
        position,
        avgCost,
    ):

        self.positions.append(
            {
                "account": account,
                "symbol": contract.symbol,
                "security_type": contract.secType,
                "exchange": contract.exchange,
                "currency": contract.currency,
                "position": position,
                "average_cost": avgCost,
            }
        )

    def positionEnd(self):

        self.positions_complete.set()

    # ----------------------------------------------------------
    # Orders
    # ----------------------------------------------------------

    def openOrderEnd(self):

        self.open_orders_complete.set()

    # ----------------------------------------------------------
    # Connection
    # ----------------------------------------------------------

    def nextValidId(
        self,
        orderId: int,
    ):

        self.next_order_id = orderId

        self.server_version = self.serverVersion()

        self.connected_event.set()

    def error(
        self,
        reqId,
        errorCode,
        errorString,
        advancedOrderRejectJson="",
    ):

        self.last_error = (
            f"[{errorCode}] {errorString}"
        )


class IBKRAdapter(BaseDesktopAdapter):
    """
    Thin adapter over the official Interactive Brokers
    TWS / Gateway API.

    This adapter performs only native evidence acquisition.

    It does not perform:

        • Translation
        • Validation
        • Verification
        • Business Logic
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 7497,
        client_id: int = 1,
    ) -> None:

        self.host = host

        self.port = port

        self.client_id = client_id

        self.app = _IBKRApplication()

        self.thread = None

    # ------------------------------------------------------------------
    # Provider Information
    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:
        return "Interactive Brokers"

    @property
    def provider_version(self) -> str:

        if self.app.server_version is None:
            return "unknown"

        return str(
            self.app.server_version,
        )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def connect(self) -> None:

        self.app.connected_event.clear()

        self.app.connect(
            self.host,
            self.port,
            self.client_id,
        )

        self.thread = threading.Thread(
            target=self.app.run,
            daemon=True,
        )

        self.thread.start()

        if not self.app.connected_event.wait(timeout=10):

            raise RuntimeError(
                f"Timed out waiting for IBKR connection. "
                f"Last API error: {self.app.last_error}"
            )

        self.app.terminal = {

            "provider": self.provider_name,

            "server_version": self.provider_version,

            "host": self.host,

            "port": self.port,

            "client_id": self.client_id,

        }

    def disconnect(self) -> None:

        if self.app.isConnected():

            self.app.disconnect()

        if self.thread is not None:

            self.thread.join(timeout=2)

        self.thread = None

    def is_connected(self) -> bool:

        return self.app.isConnected()

    # ------------------------------------------------------------------
    # Native Requests
    # ------------------------------------------------------------------

    def _request_account_summary(self):

        self.app.account_summary_complete.clear()

        self.app.reqAccountSummary(
            1,
            "All",
            "$LEDGER,NetLiquidation,EquityWithLoanValue,AvailableFunds",
        )

    def _request_positions(self):

        self.app.positions.clear()

        self.app.positions_complete.clear()

        self.app.reqPositions()

    # ------------------------------------------------------------------
    # Infrastructure Builders
    # ------------------------------------------------------------------

    def _build_terminal(self):

        return self.app.terminal

    def _build_user(self):

        return None

    def _build_broker(self):

        return None

    def _build_server(self):

        return None

    def _build_account(self):

        return self.app.account

    # ------------------------------------------------------------------
    # Financial Builders
    # ------------------------------------------------------------------

    def _build_financial(self):

        return {

            "balance": self.app.financial.get(
                "NetLiquidation",
            ),

            "equity": self.app.financial.get(
                "EquityWithLoanValue",
            ),

            "margin": None,

            "buying_power": self.app.financial.get(
                "AvailableFunds",
            ),

        }

    # ------------------------------------------------------------------
    # Market Builders
    # ------------------------------------------------------------------

    def _build_symbols(self):

        return self.app.symbols

    def _build_prices(self):

        return self.app.prices

    # ------------------------------------------------------------------
    # Trading Builders
    # ------------------------------------------------------------------

    def _build_orders(self):

        return self.app.orders

    def _build_executions(self):

        return self.app.executions

    def _build_deals(self):

        return self.app.deals

    def _build_trades(self):

        return self.app.trades

    def _build_positions(self):

        return self.app.positions

    # ------------------------------------------------------------------
    # History Builders
    # ------------------------------------------------------------------

    def _build_history(self):

        return self.app.history

    def _build_activity(self):

        return self.app.activity

    # ------------------------------------------------------------------
    # Evidence Acquisition
    # ------------------------------------------------------------------

    def acquire(self) -> Dict[str, Any]:
        """
        Acquire the complete native IBKR evidence surface.

        The returned payload is broker-independent and follows
        the canonical Desktop Trading Engine acquisition contract.
        """

        self._request_account_summary()

        if not self.app.account_summary_complete.wait(
            timeout=10,
        ):

            raise RuntimeError(
                "Timed out waiting for account summary."
            )

        self.app.cancelAccountSummary(1)

        self._request_positions()

        if not self.app.positions_complete.wait(
            timeout=10,
        ):

            raise RuntimeError(
                "Timed out waiting for positions."
            )

        self.app.cancelPositions()

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
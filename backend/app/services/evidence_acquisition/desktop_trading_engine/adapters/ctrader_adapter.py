"""
Trading Truth Layer (TTL)

Universal Evidence Adapter (UEA)

cTrader Desktop Adapter
"""

from __future__ import annotations

from typing import Any, Dict

from .base_adapter import BaseDesktopAdapter
from ..normalizer import desktop_evidence_normalizer


class CTraderAdapter(BaseDesktopAdapter):
    """
    Thin adapter over the official cTrader Open API.

    This adapter performs only native evidence acquisition.

    It does not perform:

        • Translation
        • Validation
        • Verification
        • Business Logic
    """

    def __init__(
        self,
        client: Any,
    ) -> None:

        self.client = client

    # ------------------------------------------------------------------
    # Provider Information
    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:
        return "cTrader"

    @property
    def provider_version(self) -> str:

        version = getattr(
            self.client,
            "version",
            None,
        )

        return version or "unknown"

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def connect(self) -> None:
        """
        Connect to the cTrader Open API.
        """

        self.client.connect()

    def disconnect(self) -> None:
        """
        Disconnect from cTrader.
        """

        self.client.disconnect()

    def is_connected(self) -> bool:
        """
        Determine connection status.
        """

        return self.client.is_connected()

    # ------------------------------------------------------------------
    # Infrastructure Builders
    # ------------------------------------------------------------------

    def _build_terminal(self):

        return self.client.terminal()

    def _build_user(self):

        return getattr(
            self.client,
            "user",
            lambda: None,
        )()

    def _build_broker(self):

        return getattr(
            self.client,
            "broker",
            lambda: None,
        )()

    def _build_server(self):

        return getattr(
            self.client,
            "server",
            lambda: None,
        )()

    def _build_account(self):

        return self.client.account()

    # ------------------------------------------------------------------
    # Financial Builders
    # ------------------------------------------------------------------

    def _build_financial(self):

        return self.client.financial()

    # ------------------------------------------------------------------
    # Market Builders
    # ------------------------------------------------------------------

    def _build_symbols(self):

        return self.client.symbols()

    def _build_prices(self):

        return self.client.prices()

    # ------------------------------------------------------------------
    # Trading Builders
    # ------------------------------------------------------------------

    def _build_orders(self):

        return self.client.orders()

    def _build_executions(self):

        return self.client.executions()

    def _build_deals(self):

        return self.client.deals()

    def _build_trades(self):

        return self.client.trades()

    def _build_positions(self):

        return self.client.positions()

    # ------------------------------------------------------------------
    # History Builders
    # ------------------------------------------------------------------

    def _build_history(self):

        return self.client.history()

    def _build_activity(self):

        return self.client.activity()

    # ------------------------------------------------------------------
    # Evidence Acquisition
    # ------------------------------------------------------------------

    def acquire(self) -> Dict[str, Any]:
        """
        Acquire the complete native cTrader evidence surface.

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
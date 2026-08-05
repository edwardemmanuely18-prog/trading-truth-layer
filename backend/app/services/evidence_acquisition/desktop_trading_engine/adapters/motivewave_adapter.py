"""
Trading Truth Layer (TTL)

Universal Evidence Adapter (UEA)

MotiveWave Desktop Adapter
"""

from __future__ import annotations

from typing import Any, Dict

from .base_adapter import BaseDesktopAdapter
from ..normalizer import desktop_evidence_normalizer


class MotiveWaveAdapter(BaseDesktopAdapter):
    """
    Thin adapter for MotiveWave Desktop.

    MotiveWave exposes trading functionality through
    its native SDK and broker integration framework.
    TTL communicates through an external bridge supplied
    to this adapter.

    This adapter performs only native evidence acquisition.

    It does not perform:

        • Translation
        • Validation
        • Verification
        • Business Logic
    """

    def __init__(
        self,
        bridge: Any,
    ) -> None:

        self.bridge = bridge

    # ------------------------------------------------------------------
    # Provider Information
    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:
        return "MotiveWave"

    @property
    def provider_version(self) -> str:

        version = getattr(
            self.bridge,
            "version",
            None,
        )

        return version or "unknown"

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def connect(self) -> None:
        """
        Connect to the MotiveWave bridge.
        """

        self.bridge.connect()

    def disconnect(self) -> None:
        """
        Disconnect from the MotiveWave bridge.
        """

        self.bridge.disconnect()

    def is_connected(self) -> bool:
        """
        Determine whether the MotiveWave bridge
        is connected.
        """

        return self.bridge.is_connected()

    # ------------------------------------------------------------------
    # Infrastructure Builders
    # ------------------------------------------------------------------

    def _build_terminal(self):

        return self.bridge.terminal()

    def _build_user(self):

        return getattr(
            self.bridge,
            "user",
            lambda: None,
        )()

    def _build_broker(self):

        return getattr(
            self.bridge,
            "broker",
            lambda: None,
        )()

    def _build_server(self):

        return getattr(
            self.bridge,
            "server",
            lambda: None,
        )()

    def _build_account(self):

        return self.bridge.account()

    # ------------------------------------------------------------------
    # Financial Builders
    # ------------------------------------------------------------------

    def _build_financial(self):

        return self.bridge.financial()

    # ------------------------------------------------------------------
    # Market Builders
    # ------------------------------------------------------------------

    def _build_symbols(self):

        return self.bridge.symbols()

    def _build_prices(self):

        return self.bridge.prices()

    # ------------------------------------------------------------------
    # Trading Builders
    # ------------------------------------------------------------------

    def _build_orders(self):

        return self.bridge.orders()

    def _build_executions(self):

        return self.bridge.executions()

    def _build_deals(self):

        return self.bridge.deals()

    def _build_trades(self):

        return self.bridge.trades()

    def _build_positions(self):

        return self.bridge.positions()

    # ------------------------------------------------------------------
    # History Builders
    # ------------------------------------------------------------------

    def _build_history(self):

        return self.bridge.history()

    def _build_activity(self):

        return self.bridge.activity()

    # ------------------------------------------------------------------
    # Evidence Acquisition
    # ------------------------------------------------------------------

    def acquire(self) -> Dict[str, Any]:
        """
        Acquire the complete MotiveWave native evidence
        surface.

        The returned payload is broker-independent and
        follows the canonical Desktop Trading Engine
        acquisition contract.
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
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

        return mt5.symbols_get()

    def _build_prices(
        self,
        symbols,
    ):

        prices = []

        for symbol in symbols or []:

            tick = mt5.symbol_info_tick(
                symbol.name,
            )

            if tick is not None:
                prices.append(tick)

        return prices


    def _build_orders(self):

        return mt5.orders_get()


    def _build_positions(self):

        return mt5.positions_get()


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

        return deals


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
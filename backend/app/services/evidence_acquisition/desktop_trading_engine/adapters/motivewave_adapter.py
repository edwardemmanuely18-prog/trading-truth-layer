"""
Trading Truth Layer (TTL)

Universal Evidence Adapter (UEA)

MotiveWave Desktop Adapter
"""

from __future__ import annotations

from typing import Any, Dict

from .base_adapter import BaseDesktopAdapter
from ..normalizer import desktop_evidence_normalizer
from ..verification import VerificationSnapshot


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

    @classmethod
    def from_connection_config(
        cls,
        *,
        credentials: dict[str, Any],
        environment: str,
    ) -> "MotiveWaveAdapter":
        """
        Construct MotiveWave from the canonical provider connection
        configuration.

        MotiveWave does not use MetaTrader-style login/password/server/path
        credentials. The adapter receives only bridge/session configuration.

        Supported connection modes:
            local  -> local MotiveWave bridge
            remote -> TTL production/rendezvous bridge

        The trading environment remains independent:
            development / demo
            production / live

        The active MotiveWave account remains provider-native evidence.
        account_id is therefore retained as requested connection context but
        is NOT passed as a fake constructor credential to MotiveWaveBridge.
        """

        from .bridges.motivewave_bridge import MotiveWaveBridge

        credentials = credentials or {}

        connection_mode = (
            str(
                credentials.get(
                    "connection_mode",
                    "local",
                )
            )
            .strip()
            .lower()
        )

        if connection_mode not in {
            "local",
            "remote",
        }:
            raise ValueError(
                "MotiveWave connection_mode must be "
                "'local' or 'remote'."
            )

        normalized_environment = (
            str(
                environment
                or "development"
            )
            .strip()
            .lower()
        )

        if normalized_environment in {
            "demo",
            "sandbox",
            "development",
            "dev",
            "paper",
        }:
            normalized_environment = "development"

        elif normalized_environment in {
            "live",
            "production",
            "prod",
        }:
            normalized_environment = "production"

        else:
            raise ValueError(
                "Unsupported MotiveWave trading environment "
                f"'{environment}'. Expected demo/development "
                "or live/production."
            )

        configured_endpoint = (
            credentials.get(
                "bridge_endpoint"
            )
            or None
        )

        pairing_token = (
            credentials.get(
                "pairing_token"
            )
            or None
        )

        requested_account_id = (
            credentials.get(
                "account_id"
            )
            or None
        )

        #
        # Endpoint policy
        # ----------------
        #
        # Local development:
        #   explicit endpoint if supplied,
        #   otherwise 127.0.0.1:17841.
        #
        # Remote/live infrastructure:
        #   explicit endpoint if supplied,
        #   otherwise the bridge's configured production endpoint.
        #
        if connection_mode == "local":
            endpoint = (
                configured_endpoint
                or MotiveWaveBridge.DEFAULT_LOCAL_ENDPOINT
            )

        else:
            endpoint = (
                configured_endpoint
                or MotiveWaveBridge.DEFAULT_PRODUCTION_ENDPOINT
            )

            if not endpoint:
                raise ValueError(
                    "MotiveWave remote connection requires a "
                    "production bridge endpoint."
                )

        bridge = MotiveWaveBridge(
            endpoint=endpoint,
            environment=normalized_environment,
            pairing_token=pairing_token,
        )

        #
        # Keep account selection as connection context.
        #
        # We do NOT pass this into MotiveWaveBridge because account identity
        # must come from MotiveWave-native evidence unless/ until the native
        # bridge exposes an explicit account-selection operation.
        #
        adapter = cls(
            bridge=bridge,
        )

        adapter.requested_account_id = (
            str(requested_account_id)
            if requested_account_id not in (
                None,
                "",
            )
            else None
        )

        adapter.connection_mode = connection_mode
        adapter.environment = normalized_environment

        return adapter

    def __init__(
        self,
        bridge: Any,
    ) -> None:

        self.bridge = bridge

        #
        # Provider connection context.
        #
        # These values describe how TTL reached MotiveWave.
        # They do not replace MotiveWave-native evidence.
        #
        self.requested_account_id: str | None = None
        self.connection_mode: str = "local"
        self.environment: str = "development"

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

    @property
    def evidence_capabilities(self) -> Dict[str, Any]:
        """
        MotiveWave evidence capabilities exposed by the native SDK.

        These describe evidence availability and scope. They do not
        synthesize or alter provider-native evidence.
        """

        return {
            "orders": {
                "supported": True,
                "scope": "active_order_context",
                "manual_external_orders": False,
                "reason": (
                    "MotiveWave public OrderContext exposes "
                    "getActiveOrders(), but the public SDK does not "
                    "expose a separate account-wide working-order "
                    "collection for externally submitted orders."
                ),
            },
            "executions": {
                "supported": True,
                "scope": "provider_native",
            },
            "trades": {
                "supported": True,
                "scope": "provider_native_or_execution_derived",
            },
            "positions": {
                "supported": True,
                "scope": "account_native",
            },
            "deals": {
                "supported": False,
                "scope": "unsupported",
                "reason": (
                    "MotiveWave public SDK does not expose "
                    "a separate Deal object."
                ),
            },
            "history": {
                "supported": False,
                "scope": "unsupported",
                "reason": (
                    "MotiveWave public OrderContext does not expose "
                    "generic historical order/deal collections."
                ),
            },
            "activity": {
                "supported": False,
                "scope": "unsupported",
                "reason": (
                    "MotiveWave public SDK does not expose "
                    "a generic provider activity surface."
                ),
            },
        }

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

                #
                # Connection context
                #
                "connection_mode": self.connection_mode,
                "environment": self.environment,
                "requested_account_id": (
                    self.requested_account_id
                    if self.requested_account_id
                    else None
                ),

                #
                # Native account identity remains authoritative.
                #
                "account_identity_source": (
                    "MotiveWave"
                    if account_id is not None
                    else "unavailable"
                ),

                "account_identity_confidence": (
                    "observed"
                    if account_id is not None
                    else "unavailable"
                ),
            },
        )

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
            # Connection Context
            #
            # These values describe the TTL → MotiveWave connection.
            # They do NOT replace MotiveWave-native account evidence.
            # ----------------------------------------------------------

            "connection_context": {
                "connection_mode": self.connection_mode,
                "environment": self.environment,
                "requested_account_id": (
                    self.requested_account_id
                    if self.requested_account_id
                    else None
                ),
            },

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
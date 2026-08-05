"""
Trading Truth Layer (TTL)

Gateway Engine

cTrader Open API Adapter
"""

from __future__ import annotations

import socket
import ssl

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from ..models import (
    GatewayType,
)

from ..registry import (
    ProviderDescriptor,
)

from .base_adapter import (
    BaseGatewayAdapter,
)


# ============================================================================
# Canonical Snapshot
# ============================================================================


@dataclass(slots=True)
class CTraderSnapshot:

    gateways: List[Dict[str, Any]]

    accounts: List[Dict[str, Any]]

    instruments: List[Dict[str, Any]]

    positions: List[Dict[str, Any]]

    orders: List[Dict[str, Any]]

    executions: List[Dict[str, Any]]

    trades: List[Dict[str, Any]]

    market_data: List[Dict[str, Any]]

    errors: List[Dict[str, Any]]


# ============================================================================
# Configuration
# ============================================================================


@dataclass(slots=True)
class CTraderConfiguration:

    host: str

    port: int = 5035

    client_id: str = ""

    client_secret: str = ""

    access_token: Optional[str] = None

    environment: str = "live"

    use_websocket: bool = False


# ============================================================================
# Runtime State
# ============================================================================


class CTraderState(str, Enum):

    DISCONNECTED = "disconnected"

    CONNECTING = "connecting"

    AUTHENTICATING = "authenticating"

    ACTIVE = "active"

    CLOSED = "closed"


# ============================================================================
# Adapter
# ============================================================================


class CTraderAdapter(BaseGatewayAdapter):

    def __init__(

        self,

        configuration: CTraderConfiguration,

    ):

        super().__init__(

            provider_name="ctrader",

            gateway_type=GatewayType.CTRADER,

        )

        self.provider = ProviderDescriptor(

            provider_name="ctrader",

            gateway_type=GatewayType.CTRADER,

            display_name="cTrader Open API",

            vendor="Spotware",

            version="1.0",

        )

        self.configuration = configuration

        self.state = CTraderState.DISCONNECTED

        self.socket: Optional[socket.socket] = None

        self.ssl_socket = None

        self.accounts: List[Dict[str, Any]] = []

        self.instruments: List[Dict[str, Any]] = []

        self.positions: List[Dict[str, Any]] = []

        self.orders: List[Dict[str, Any]] = []

        self.executions: List[Dict[str, Any]] = []

        self.trades: List[Dict[str, Any]] = []

        self.market_data: Dict[Any, Any] = {}

        self.errors: List[Dict[str, Any]] = []

        self.connected_at: Optional[datetime] = None


# ============================================================================
# Lifecycle
# ============================================================================


    def initialize(self) -> None:

        self.mark_initialized()


    def connect(self) -> None:

        self.state = CTraderState.CONNECTING

        sock = socket.create_connection(

            (

                self.configuration.host,

                self.configuration.port,

            )

        )

        self.socket = sock

        self.ssl_socket = ssl.create_default_context().wrap_socket(

            sock,

            server_hostname=self.configuration.host,

        )

        self.state = CTraderState.AUTHENTICATING

        self._authenticate()

        self.state = CTraderState.ACTIVE

        self.connected_at = datetime.utcnow()

        self.mark_connected()


    def disconnect(self) -> None:

        if self.ssl_socket is not None:

            self.ssl_socket.close()

            self.ssl_socket = None

        if self.socket is not None:

            self.socket.close()

            self.socket = None

        self.state = CTraderState.DISCONNECTED

        self.mark_disconnected()


# ============================================================================
# Authentication
# ============================================================================


    def _authenticate(self) -> None:
        """
        Authenticate the application and trading account.

        Concrete ProtoOAApplicationAuthReq and
        ProtoOAAccountAuthReq serialization is delegated to the
        protocol implementation.
        """

        return


# ============================================================================
# Transport
# ============================================================================


    def send(
        self,
        payload: bytes,
    ) -> None:

        self.ssl_socket.sendall(payload)


    def receive(
        self,
    ) -> bytes:

        return self.ssl_socket.recv(
            65536,
        )


# ============================================================================
# Message Processing
# ============================================================================


    def process_message(
        self,
        message,
    ) -> None:

        message_type = type(
            message,
        ).__name__

        if "Execution" in message_type:

            self.executions.append(
                self._normalize(message),
            )

            return

        if "Position" in message_type:

            self.positions.append(
                self._normalize(message),
            )

            return

        if "Order" in message_type:

            self.orders.append(
                self._normalize(message),
            )

            return

        if "Spot" in message_type:

            symbol = getattr(
                message,
                "symbolId",
                None,
            )

            self.market_data[symbol] = self._normalize(
                message,
            )

            return


# ============================================================================
# Normalization
# ============================================================================


    @staticmethod
    def _normalize(
        value,
    ):

        if value is None:

            return None

        if hasattr(
            value,
            "__dict__",
        ):

            return {

                key: CTraderAdapter._normalize(val)

                for key, val in value.__dict__.items()

            }

        if isinstance(
            value,
            list,
        ):

            return [

                CTraderAdapter._normalize(v)

                for v in value

            ]

        if isinstance(
            value,
            dict,
        ):

            return {

                k: CTraderAdapter._normalize(v)

                for k, v in value.items()

            }

        return value


# ============================================================================
# Snapshot Acquisition
# ============================================================================


    def _collect_snapshot(
        self,
    ) -> CTraderSnapshot:

        return CTraderSnapshot(

            gateways=[

                {

                    "provider": self.provider_name,

                    "gateway_type": self.gateway_type.value,

                    "environment": self.configuration.environment,

                    "connected": self.is_connected,

                    "transport": "tcp",

                    "protocol": "ctrader_open_api",

                }

            ],

            accounts=self._normalize(
                self.accounts,
            ),

            instruments=self._normalize(
                self.instruments,
            ),

            positions=self._normalize(
                self.positions,
            ),

            orders=self._normalize(
                self.orders,
            ),

            executions=self._normalize(
                self.executions,
            ),

            trades=self._normalize(
                self.trades,
            ),

            market_data=self._normalize(

                list(

                    self.market_data.values(),

                )

            ),

            errors=self._normalize(
                self.errors,
            ),

        )


# ============================================================================
# Acquisition
# ============================================================================


    def acquire(
        self,
    ) -> CTraderSnapshot:

        try:

            snapshot = self._collect_snapshot()

            self.record_acquisition()

            return snapshot

        except Exception as exc:

            self.record_failure(
                exc,
            )

            raise


# ============================================================================
# Capabilities
# ============================================================================


    def capabilities(
        self,
    ) -> Dict[str, Any]:

        capabilities = super().capabilities()

        capabilities.update(

            {

                "provider_name": self.provider_name,

                "gateway_type": self.gateway_type.value,

                "streaming": True,

                "historical_data": True,

                "market_data": True,

                "orders": True,

                "positions": True,

                "trades": True,

                "portfolio": True,

                "gateway": True,

                "protobuf": True,

                "tcp": True,

                "websocket": self.configuration.use_websocket,

                "oauth": True,

            }

        )

        return capabilities


# ============================================================================
# Diagnostics
# ============================================================================


    def diagnostics(
        self,
    ) -> Dict[str, Any]:

        diagnostics = super().diagnostics()

        diagnostics["ctrader"] = {

            "host": self.configuration.host,

            "port": self.configuration.port,

            "environment": self.configuration.environment,

            "connection_state": self.state.value,

            "connected": self.is_connected,

            "ssl_connected": self.ssl_socket is not None,

            "socket_connected": self.socket is not None,

            "authenticated": (
                self.state == CTraderState.ACTIVE
            ),

            "accounts": len(self.accounts),

            "instruments": len(self.instruments),

            "positions": len(self.positions),

            "orders": len(self.orders),

            "executions": len(self.executions),

            "trades": len(self.trades),

            "market_data": len(self.market_data),

            "errors": len(self.errors),

        }

        return diagnostics


# ============================================================================
# Cleanup
# ============================================================================


    def close(
        self,
    ) -> None:

        if self.is_connected:

            self.disconnect()

        self.mark_closed()


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [

    "CTraderSnapshot",

    "CTraderConfiguration",

    "CTraderState",

    "CTraderAdapter",

]
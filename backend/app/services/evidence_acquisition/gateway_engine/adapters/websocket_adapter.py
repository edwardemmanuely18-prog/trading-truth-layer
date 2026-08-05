"""
Trading Truth Layer (TTL)

Gateway Engine

Generic WebSocket Adapter

Canonical provider-agnostic WebSocket transport adapter.
"""

from __future__ import annotations

import json
import threading
import time

from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional

import websocket

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
class WebSocketSnapshot:

    gateways: List[Dict[str, Any]]

    messages: List[Any]

    errors: List[Any]


# ============================================================================
# Configuration
# ============================================================================


@dataclass(slots=True)
class WebSocketConfiguration:

    url: str

    headers: Dict[str, str] = field(
        default_factory=dict,
    )

    subscriptions: List[Dict[str, Any]] = field(
        default_factory=list,
    )

    heartbeat_interval: int = 30

    reconnect: bool = True

    reconnect_delay: int = 5

    provider_name: str = "websocket"

    environment: str = "stream"


# ============================================================================
# Runtime State
# ============================================================================


class WebSocketState(str, Enum):

    DISCONNECTED = "disconnected"

    CONNECTING = "connecting"

    ACTIVE = "active"

    CLOSED = "closed"


# ============================================================================
# Adapter
# ============================================================================


class WebSocketAdapter(BaseGatewayAdapter):

    def __init__(

        self,

        configuration: WebSocketConfiguration,

    ):

        super().__init__(

            provider_name=configuration.provider_name,

            gateway_type=GatewayType.WEBSOCKET,

        )

        self.provider = ProviderDescriptor(

            provider_name=configuration.provider_name,

            gateway_type=GatewayType.WEBSOCKET,

            display_name="Generic WebSocket",

            vendor="Trading Truth Layer",

            version="1.0",

        )

        self.configuration = configuration

        self.state = WebSocketState.DISCONNECTED

        self.ws: Optional[websocket.WebSocketApp] = None

        self.messages: List[Any] = []

        self.errors: List[Any] = []

        self.callbacks: List[Callable] = []

        self._running = False

        self._heartbeat_thread: Optional[threading.Thread] = None

        self.connected_at: Optional[datetime] = None


# ============================================================================
# Lifecycle
# ============================================================================


    def initialize(
        self,
    ) -> None:

        self.mark_initialized()


    def connect(
        self,
    ) -> None:

        self.state = WebSocketState.CONNECTING

        self._running = True

        self.ws = websocket.WebSocketApp(

            self.configuration.url,

            header=self.configuration.headers,

            on_open=self._on_open,

            on_message=self._on_message,

            on_error=self._on_error,

            on_close=self._on_close,

        )

        threading.Thread(

            target=self.ws.run_forever,

            daemon=True,

        ).start()

        self.state = WebSocketState.ACTIVE

        self.connected_at = datetime.utcnow()

        self.mark_connected()

        self._start_heartbeat()


    def disconnect(
        self,
    ) -> None:

        self._running = False

        if self.ws:

            self.ws.close()

            self.ws = None

        self.state = WebSocketState.DISCONNECTED

        self.mark_disconnected()


# ============================================================================
# Internal Events
# ============================================================================


    def _on_open(

        self,

        ws,

    ):

        for subscription in self.configuration.subscriptions:

            ws.send(

                json.dumps(

                    subscription,

                )

            )


    def _on_message(

        self,

        ws,

        message,

    ):

        try:

            data = json.loads(

                message,

            )

        except Exception:

            data = message

        normalized = self._normalize(

            data,

        )

        self.messages.append(

            normalized,

        )

        for callback in self.callbacks:

            callback(

                normalized,

            )


    def _on_error(

        self,

        ws,

        error,

    ):

        self.errors.append(

            str(

                error,

            )

        )


    def _on_close(

        self,

        ws,

        status,

        message,

    ):

        self.state = WebSocketState.DISCONNECTED

        if (

            self.configuration.reconnect

            and self._running

        ):

            time.sleep(

                self.configuration.reconnect_delay,

            )

            self.connect()


# ============================================================================
# Public API
# ============================================================================


    def subscribe(

        self,

        payload: Dict[str, Any],

    ) -> None:

        if self.ws:

            self.ws.send(

                json.dumps(

                    payload,

                )

            )


    def send(

        self,

        payload: Dict[str, Any],

    ) -> None:

        if self.ws:

            self.ws.send(

                json.dumps(

                    payload,

                )

            )


    def register_callback(

        self,

        callback: Callable,

    ) -> None:

        self.callbacks.append(

            callback,

        )


# ============================================================================
# Heartbeat
# ============================================================================


    def _heartbeat_loop(

        self,

    ) -> None:

        while self._running:

            time.sleep(

                self.configuration.heartbeat_interval,

            )

            try:

                self.send(

                    {

                        "type": "ping",

                    }

                )

            except Exception:

                pass


    def _start_heartbeat(

        self,

    ) -> None:

        self._heartbeat_thread = threading.Thread(

            target=self._heartbeat_loop,

            daemon=True,

        )

        self._heartbeat_thread.start()


# ============================================================================
# Normalization
# ============================================================================


    @staticmethod
    def _normalize(

        value,

    ):

        if value is None:

            return None

        if isinstance(

            value,

            dict,

        ):

            return {

                k: WebSocketAdapter._normalize(v)

                for k, v in value.items()

            }

        if isinstance(

            value,

            list,

        ):

            return [

                WebSocketAdapter._normalize(v)

                for v in value

            ]

        if hasattr(

            value,

            "__dict__",

        ):

            return {

                k: WebSocketAdapter._normalize(v)

                for k, v in vars(value).items()

            }

        return value


# ============================================================================
# Canonical Snapshot Acquisition
# ============================================================================


    def _collect_snapshot(

        self,

    ) -> WebSocketSnapshot:

        return WebSocketSnapshot(

            gateways=[

                {

                    "provider": self.provider_name,

                    "gateway_type": self.gateway_type.value,

                    "environment": self.configuration.environment,

                    "connected": self.is_connected,

                    "transport": "websocket",

                    "protocol": "ws",

                }

            ],

            messages=list(

                self.messages,

            ),

            errors=list(

                self.errors,

            ),

        )


# ============================================================================
# Public Acquisition
# ============================================================================


    def acquire(

        self,

    ) -> WebSocketSnapshot:

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

                "websocket": True,

                "streaming": True,

                "subscriptions": True,

                "heartbeat": True,

                "reconnect": True,

                "callbacks": True,

                "provider_agnostic": True,

                "gateway": True,

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

        diagnostics["websocket"] = {

            "provider": self.provider_name,

            "url": self.configuration.url,

            "environment": self.configuration.environment,

            "connection_state": self.state.value,

            "connected": self.is_connected,

            "heartbeat_interval": self.configuration.heartbeat_interval,

            "reconnect": self.configuration.reconnect,

            "reconnect_delay": self.configuration.reconnect_delay,

            "messages": len(self.messages),

            "callbacks": len(self.callbacks),

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

    "WebSocketSnapshot",

    "WebSocketConfiguration",

    "WebSocketState",

    "WebSocketAdapter",

]
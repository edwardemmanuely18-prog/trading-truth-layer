"""
Trading Truth Layer (TTL)

Gateway Engine

Generic gRPC Adapter

Canonical provider-agnostic gRPC transport adapter.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import grpc

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
class GRPCSnapshot:

    gateways: List[Dict[str, Any]]

    messages: List[Any]

    errors: List[Any]


# ============================================================================
# Configuration
# ============================================================================


@dataclass(slots=True)
class GRPCConfiguration:

    host: str

    port: int

    secure: bool = False

    provider_name: str = "grpc"

    environment: str = "grpc"

    options: List[tuple] | None = None


# ============================================================================
# Runtime State
# ============================================================================


class GRPCState(str, Enum):

    DISCONNECTED = "disconnected"

    CONNECTING = "connecting"

    ACTIVE = "active"

    CLOSED = "closed"


# ============================================================================
# Adapter
# ============================================================================


class GRPCAdapter(BaseGatewayAdapter):

    def __init__(

        self,

        configuration: GRPCConfiguration,

    ):

        super().__init__(

            provider_name=configuration.provider_name,

            gateway_type=GatewayType.GRPC,

        )

        self.provider = ProviderDescriptor(

            provider_name=configuration.provider_name,

            gateway_type=GatewayType.GRPC,

            display_name="Generic gRPC",

            vendor="Trading Truth Layer",

            version="1.0",

        )

        self.configuration = configuration

        self.state = GRPCState.DISCONNECTED

        self.channel: Optional[grpc.Channel] = None

        self.messages: List[Any] = []

        self.errors: List[Any] = []

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

        self.state = GRPCState.CONNECTING

        address = (

            f"{self.configuration.host}:"

            f"{self.configuration.port}"

        )

        if self.configuration.secure:

            credentials = grpc.ssl_channel_credentials()

            self.channel = grpc.secure_channel(

                address,

                credentials,

                options=self.configuration.options,

            )

        else:

            self.channel = grpc.insecure_channel(

                address,

                options=self.configuration.options,

            )

        grpc.channel_ready_future(

            self.channel,

        ).result(

            timeout=30,

        )

        self.state = GRPCState.ACTIVE

        self.connected_at = datetime.utcnow()

        self.mark_connected()


    def disconnect(
        self,
    ) -> None:

        if self.channel:

            self.channel.close()

            self.channel = None

        self.state = GRPCState.DISCONNECTED

        self.mark_disconnected()

# ============================================================================
# RPC Operations
# ============================================================================


    def unary(

        self,

        stub: Any,

        method: str,

        request: Any,

    ):

        rpc = getattr(

            stub,

            method,

        )

        response = rpc(

            request,

        )

        normalized = self._normalize(

            response,

        )

        self.messages.append(

            normalized,

        )

        return normalized


    def server_stream(

        self,

        stub: Any,

        method: str,

        request: Any,

    ):

        rpc = getattr(

            stub,

            method,

        )

        for response in rpc(

            request,

        ):

            normalized = self._normalize(

                response,

            )

            self.messages.append(

                normalized,

            )

            yield normalized


    def client_stream(

        self,

        stub: Any,

        method: str,

        requests,

    ):

        rpc = getattr(

            stub,

            method,

        )

        response = rpc(

            requests,

        )

        normalized = self._normalize(

            response,

        )

        self.messages.append(

            normalized,

        )

        return normalized


    def bidirectional_stream(

        self,

        stub: Any,

        method: str,

        requests,

    ):

        rpc = getattr(

            stub,

            method,

        )

        for response in rpc(

            requests,

        ):

            normalized = self._normalize(

                response,

            )

            self.messages.append(

                normalized,

            )

            yield normalized


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

                key: GRPCAdapter._normalize(val)

                for key, val in vars(value).items()

            }

        if isinstance(

            value,

            dict,

        ):

            return {

                k: GRPCAdapter._normalize(v)

                for k, v in value.items()

            }

        if isinstance(

            value,

            list,

        ):

            return [

                GRPCAdapter._normalize(v)

                for v in value

            ]

        return value


# ============================================================================
# Canonical Snapshot Acquisition
# ============================================================================


    def _collect_snapshot(

        self,

    ) -> GRPCSnapshot:

        return GRPCSnapshot(

            gateways=[

                {

                    "provider": self.provider_name,

                    "gateway_type": self.gateway_type.value,

                    "environment": self.configuration.environment,

                    "connected": self.is_connected,

                    "transport": "grpc",

                    "protocol": "http2",

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

    ) -> GRPCSnapshot:

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

                "grpc": True,

                "http2": True,

                "protobuf": True,

                "unary_rpc": True,

                "server_stream": True,

                "client_stream": True,

                "bidirectional_stream": True,

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

        diagnostics["grpc"] = {

            "provider": self.provider_name,

            "host": self.configuration.host,

            "port": self.configuration.port,

            "secure": self.configuration.secure,

            "environment": self.configuration.environment,

            "connection_state": self.state.value,

            "connected": self.is_connected,

            "messages": len(self.messages),

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

    "GRPCSnapshot",

    "GRPCConfiguration",

    "GRPCState",

    "GRPCAdapter",

]
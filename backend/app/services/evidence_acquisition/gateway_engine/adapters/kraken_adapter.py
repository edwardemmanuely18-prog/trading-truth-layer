"""
Trading Truth Layer (TTL)

Gateway Engine

Kraken Spot Adapter
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import time

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from urllib.parse import urlencode

import requests

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
class KrakenSnapshot:

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
class KrakenConfiguration:

    api_key: str

    api_secret: str

    base_url: str = "https://api.kraken.com"

    public_ws: str = "wss://ws.kraken.com"

    private_ws: str = "wss://ws-auth.kraken.com"

    environment: str = "spot"


# ============================================================================
# Runtime State
# ============================================================================


class KrakenState(str, Enum):

    DISCONNECTED = "disconnected"

    AUTHENTICATING = "authenticating"

    ACTIVE = "active"

    CLOSED = "closed"


# ============================================================================
# Adapter
# ============================================================================


class KrakenAdapter(BaseGatewayAdapter):

    def __init__(

        self,

        configuration: KrakenConfiguration,

    ):

        super().__init__(

            provider_name="kraken",

            gateway_type=GatewayType.KRAKEN,

        )

        self.provider = ProviderDescriptor(

            provider_name="kraken",

            gateway_type=GatewayType.KRAKEN,

            display_name="Kraken Spot",

            vendor="Kraken",

            version="1.0",

        )

        self.configuration = configuration

        self.state = KrakenState.DISCONNECTED

        self.session = requests.Session()

        self.websocket_token: Optional[Dict[str, Any]] = None

        self.accounts: List[Dict[str, Any]] = []

        self.instruments: List[Dict[str, Any]] = []

        self.positions: List[Dict[str, Any]] = []

        self.orders: List[Dict[str, Any]] = []

        self.executions: List[Dict[str, Any]] = []

        self.trades: List[Dict[str, Any]] = []

        self.market_data: List[Dict[str, Any]] = []

        self.errors: List[Dict[str, Any]] = []

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

        self.state = KrakenState.AUTHENTICATING

        self.websocket_token = self._get_websocket_token()

        self.state = KrakenState.ACTIVE

        self.connected_at = datetime.utcnow()

        self.mark_connected()


    def disconnect(
        self,
    ) -> None:

        self.session.close()

        self.state = KrakenState.DISCONNECTED

        self.mark_disconnected()


# ============================================================================
# Signing
# ============================================================================


    def _headers(

        self,

        endpoint: str,

        data: Optional[Dict[str, Any]] = None,

    ):

        payload = dict(

            data or {},

        )

        nonce = str(

            int(

                time.time() * 1000,

            )

        )

        payload["nonce"] = nonce

        encoded = urlencode(

            payload,

        )

        message = (

            endpoint.encode()

            + hashlib.sha256(

                (nonce + encoded).encode()

            ).digest()

        )

        signature = base64.b64encode(

            hmac.new(

                base64.b64decode(

                    self.configuration.api_secret,

                ),

                message,

                hashlib.sha512,

            ).digest()

        ).decode()

        return {

            "API-Key":

                self.configuration.api_key,

            "API-Sign":

                signature,

        }, payload


# ============================================================================
# REST
# ============================================================================


    def _post(

        self,

        endpoint: str,

        payload: Optional[Dict[str, Any]] = None,

    ):

        headers, payload = self._headers(

            endpoint,

            payload,

        )

        response = self.session.post(

            self.configuration.base_url + endpoint,

            headers=headers,

            data=payload,

            timeout=30,

        )

        response.raise_for_status()

        return response.json()


# ============================================================================
# Snapshot Acquisition
# ============================================================================


    def _acquire_balance(
        self,
    ):

        return self._post(

            "/0/private/Balance",

        )


    def _acquire_open_orders(
        self,
    ):

        return self._post(

            "/0/private/OpenOrders",

        )


    def _acquire_open_positions(
        self,
    ):

        return self._post(

            "/0/private/OpenPositions",

        )


    def _acquire_asset_pairs(
        self,
    ):

        response = self.session.get(

            self.configuration.base_url

            + "/0/public/AssetPairs",

            timeout=30,

        )

        response.raise_for_status()

        return response.json()


    def _get_websocket_token(
        self,
    ):

        return self._post(

            "/0/private/GetWebSocketsToken",

        )


# ============================================================================
# WebSocket
# ============================================================================


    def websocket_subscription(

        self,

        feed: str = "openOrders",

    ) -> Dict[str, Any]:

        token = None

        if isinstance(

            self.websocket_token,

            dict,

        ):

            token = (

                self.websocket_token.get(

                    "result",

                    {},

                ).get(

                    "token",

                )

            )

        return {

            "event": "subscribe",

            "subscription": {

                "name": feed,

                "token": token,

            },

        }


# ============================================================================
# Heartbeat
# ============================================================================


    @staticmethod
    def heartbeat() -> Dict[str, Any]:

        return {

            "event": "ping",

        }


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

                k: KrakenAdapter._normalize(v)

                for k, v in value.items()

            }

        if isinstance(

            value,

            list,

        ):

            return [

                KrakenAdapter._normalize(v)

                for v in value

            ]

        return value


# ============================================================================
# Snapshot Acquisition
# ============================================================================


    def _collect_snapshot(

        self,

    ) -> KrakenSnapshot:

        balances = self._normalize(

            self._acquire_balance(),

        )

        positions = self._normalize(

            self._acquire_open_positions(),

        )

        orders = self._normalize(

            self._acquire_open_orders(),

        )

        assets = self._normalize(

            self._acquire_asset_pairs(),

        )

        self.accounts = [

            balances,

        ]

        self.positions = (

            positions.get(

                "result",

                {},

            )

            if isinstance(

                positions,

                dict,

            )

            else []

        )

        self.orders = (

            orders.get(

                "result",

                {},

            )

            if isinstance(

                orders,

                dict,

            )

            else []

        )

        self.executions = []

        self.trades = []

        self.instruments = (

            assets.get(

                "result",

                {},

            )

            if isinstance(

                assets,

                dict,

            )

            else []

        )

        self.market_data = [

            assets,

        ]

        return KrakenSnapshot(

            gateways=[

                {

                    "provider": self.provider_name,

                    "gateway_type": self.gateway_type.value,

                    "environment": self.configuration.environment,

                    "connected": self.is_connected,

                    "transport": "https",

                    "protocol": "kraken_rest",

                }

            ],

            accounts=self.accounts,

            instruments=self.instruments,

            positions=self.positions,

            orders=self.orders,

            executions=self.executions,

            trades=self.trades,

            market_data=self.market_data,

            errors=self.errors,

        )


# ============================================================================
# Public Acquisition
# ============================================================================


    def acquire(

        self,

    ) -> KrakenSnapshot:

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

                "crypto_exchange": True,

                "rest": True,

                "public_websocket": True,

                "private_websocket": True,

                "streaming": True,

                "market_data": True,

                "orders": True,

                "positions": True,

                "balances": True,

                "executions": True,

                "trades": True,

                "websocket_token": True,

                "portfolio": True,

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

        diagnostics["kraken"] = {

            "base_url": self.configuration.base_url,

            "public_ws": self.configuration.public_ws,

            "private_ws": self.configuration.private_ws,

            "environment": self.configuration.environment,

            "connection_state": self.state.value,

            "connected": self.is_connected,

            "authenticated": (

                self.state == KrakenState.ACTIVE

            ),

            "websocket_token": (

                self.websocket_token is not None

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

    "KrakenSnapshot",

    "KrakenConfiguration",

    "KrakenState",

    "KrakenAdapter",

]
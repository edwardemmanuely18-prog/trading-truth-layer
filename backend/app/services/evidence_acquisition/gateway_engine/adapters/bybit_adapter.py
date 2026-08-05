"""
Trading Truth Layer (TTL)

Gateway Engine

Bybit V5 Adapter
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

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
class BybitSnapshot:

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
class BybitConfiguration:

    api_key: str

    api_secret: str

    base_url: str = "https://api.bybit.com"

    websocket_url: str = "wss://stream.bybit.com/v5/private"

    environment: str = "mainnet"

    recv_window: int = 5000


# ============================================================================
# Runtime State
# ============================================================================


class BybitState(str, Enum):

    DISCONNECTED = "disconnected"

    AUTHENTICATING = "authenticating"

    ACTIVE = "active"

    CLOSED = "closed"


# ============================================================================
# Adapter
# ============================================================================


class BybitAdapter(BaseGatewayAdapter):

    def __init__(

        self,

        configuration: BybitConfiguration,

    ):

        super().__init__(

            provider_name="bybit",

            gateway_type=GatewayType.BYBIT,

        )

        self.provider = ProviderDescriptor(

            provider_name="bybit",

            gateway_type=GatewayType.BYBIT,

            display_name="Bybit V5",

            vendor="Bybit",

            version="1.0",

        )

        self.configuration = configuration

        self.state = BybitState.DISCONNECTED

        self.session = requests.Session()

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

        self.state = BybitState.AUTHENTICATING

        self.session.headers.update(

            {

                "X-BAPI-API-KEY":

                    self.configuration.api_key,

            }

        )

        self.state = BybitState.ACTIVE

        self.connected_at = datetime.utcnow()

        self.mark_connected()


    def disconnect(
        self,
    ) -> None:

        self.session.close()

        self.state = BybitState.DISCONNECTED

        self.mark_disconnected()


# ============================================================================
# Authentication
# ============================================================================


    def _timestamp(
        self,
    ) -> str:

        return str(

            int(

                time.time() * 1000,

            )

        )


    def _signature(

        self,

        timestamp: str,

        query: str,

    ) -> str:

        payload = (

            timestamp
            + self.configuration.api_key
            + str(self.configuration.recv_window)
            + query

        )

        return hmac.new(

            self.configuration.api_secret.encode(),

            payload.encode(),

            hashlib.sha256,

        ).hexdigest()


# ============================================================================
# REST
# ============================================================================


    def _get(

        self,

        endpoint: str,

        params: Optional[Dict[str, Any]] = None,

        authenticated: bool = True,

    ):

        params = dict(

            params or {},

        )

        headers = {}

        if authenticated:

            timestamp = self._timestamp()

            query = "&".join(

                f"{k}={v}"

                for k, v in sorted(params.items())

            )

            headers = {

                "X-BAPI-API-KEY":

                    self.configuration.api_key,

                "X-BAPI-TIMESTAMP":

                    timestamp,

                "X-BAPI-RECV-WINDOW":

                    str(

                        self.configuration.recv_window,

                    ),

                "X-BAPI-SIGN":

                    self._signature(

                        timestamp,

                        query,

                    ),

            }

        response = self.session.get(

            self.configuration.base_url + endpoint,

            params=params,

            headers=headers,

            timeout=30,

        )

        response.raise_for_status()

        return response.json()


# ============================================================================
# WebSocket Authentication
# ============================================================================


    def websocket_auth_payload(
        self,
    ) -> Dict[str, Any]:

        expires = int(

            time.time() * 1000,

        ) + 10000

        signature = hmac.new(

            self.configuration.api_secret.encode(),

            f"GET/realtime{expires}".encode(),

            hashlib.sha256,

        ).hexdigest()

        return {

            "op": "auth",

            "args": [

                self.configuration.api_key,

                expires,

                signature,

            ],

        }


# ============================================================================
# Evidence Acquisition
# ============================================================================


    def _acquire_wallet(
        self,
    ):

        return self._get(

            "/v5/account/wallet-balance",

            {

                "accountType": "UNIFIED",

            },

        )


    def _acquire_orders(
        self,
    ):

        return self._get(

            "/v5/order/realtime",

            {

                "category": "linear",

            },

        )


    def _acquire_instruments(
        self,
    ):

        return self._get(

            "/v5/market/instruments-info",

            {

                "category": "linear",

            },

            authenticated=False,

        )


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

                k: BybitAdapter._normalize(v)

                for k, v in value.items()

            }

        if isinstance(

            value,

            list,

        ):

            return [

                BybitAdapter._normalize(v)

                for v in value

            ]

        return value


# ============================================================================
# Snapshot Acquisition
# ============================================================================


    def _collect_snapshot(
        self,
    ) -> BybitSnapshot:

        wallet = self._normalize(

            self._acquire_wallet(),

        )

        orders = self._normalize(

            self._acquire_orders(),

        )

        instruments = self._normalize(

            self._acquire_instruments(),

        )

        self.accounts = [

            wallet,

        ]

        self.positions = (

            wallet.get(

                "result",

                {},

            )

            .get(

                "list",

                [],

            )

        )

        self.orders = (

            orders.get(

                "result",

                {},

            )

            .get(

                "list",

                [],

            )

        )

        self.executions = []

        self.trades = []

        self.instruments = (

            instruments.get(

                "result",

                {},

            )

            .get(

                "list",

                [],

            )

        )

        self.market_data = [

            instruments,

        ]

        return BybitSnapshot(

            gateways=[

                {

                    "provider": self.provider_name,

                    "gateway_type": self.gateway_type.value,

                    "environment": self.configuration.environment,

                    "connected": self.is_connected,

                    "transport": "https",

                    "protocol": "bybit_v5_rest",

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
    ) -> BybitSnapshot:

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

                "websocket": True,

                "streaming": True,

                "historical_data": True,

                "market_data": True,

                "orders": True,

                "positions": True,

                "balances": True,

                "executions": True,

                "trades": True,

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

        diagnostics["bybit"] = {

            "base_url": self.configuration.base_url,

            "websocket_url": self.configuration.websocket_url,

            "environment": self.configuration.environment,

            "connection_state": self.state.value,

            "connected": self.is_connected,

            "authenticated": (

                self.state == BybitState.ACTIVE

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

    "BybitSnapshot",

    "BybitConfiguration",

    "BybitState",

    "BybitAdapter",

]
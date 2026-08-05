"""
Trading Truth Layer (TTL)

Gateway Engine

Binance Spot Adapter
"""

from __future__ import annotations

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
class BinanceSnapshot:

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
class BinanceConfiguration:

    api_key: str

    api_secret: str

    base_url: str = "https://api.binance.com"

    environment: str = "spot"


# ============================================================================
# Runtime State
# ============================================================================


class BinanceState(str, Enum):

    DISCONNECTED = "disconnected"

    AUTHENTICATING = "authenticating"

    ACTIVE = "active"

    CLOSED = "closed"


# ============================================================================
# Adapter
# ============================================================================


class BinanceAdapter(BaseGatewayAdapter):

    def __init__(

        self,

        configuration: BinanceConfiguration,

    ):

        super().__init__(

            provider_name="binance",

            gateway_type=GatewayType.BINANCE,

        )

        self.provider = ProviderDescriptor(

            provider_name="binance",

            gateway_type=GatewayType.BINANCE,

            display_name="Binance Spot",

            vendor="Binance",

            version="1.0",

        )

        self.configuration = configuration

        self.state = BinanceState.DISCONNECTED

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

        self.state = BinanceState.AUTHENTICATING

        self.session.headers.update(

            {

                "X-MBX-APIKEY":

                    self.configuration.api_key,

            }

        )

        self.state = BinanceState.ACTIVE

        self.connected_at = datetime.utcnow()

        self.mark_connected()


    def disconnect(
        self,
    ) -> None:

        self.session.close()

        self.state = BinanceState.DISCONNECTED

        self.mark_disconnected()


# ============================================================================
# Signature
# ============================================================================


    def _signed_params(

        self,

        params: Optional[Dict[str, Any]] = None,

    ) -> Dict[str, Any]:

        params = dict(params or {})

        params["timestamp"] = int(

            time.time() * 1000,

        )

        query = urlencode(

            params,

        )

        params["signature"] = hmac.new(

            self.configuration.api_secret.encode(),

            query.encode(),

            hashlib.sha256,

        ).hexdigest()

        return params


# ============================================================================
# REST
# ============================================================================


    def _get(

        self,

        endpoint: str,

        params: Optional[Dict[str, Any]] = None,

        signed: bool = True,

    ):

        if signed:

            params = self._signed_params(

                params,

            )

        response = self.session.get(

            self.configuration.base_url + endpoint,

            params=params,

            timeout=30,

        )

        response.raise_for_status()

        return response.json()


# ============================================================================
# Evidence Acquisition
# ============================================================================


    def _acquire_account(
        self,
    ):

        return self._get(

            "/api/v3/account",

        )


    def _acquire_open_orders(
        self,
    ):

        return self._get(

            "/api/v3/openOrders",

        )


    def _acquire_exchange_info(
        self,
    ):

        return self._get(

            "/api/v3/exchangeInfo",

            signed=False,

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

                k: BinanceAdapter._normalize(v)

                for k, v in value.items()

            }

        if isinstance(

            value,

            list,

        ):

            return [

                BinanceAdapter._normalize(v)

                for v in value

            ]

        return value


# ============================================================================
# Snapshot Acquisition
# ============================================================================


    def _collect_snapshot(

        self,

    ) -> BinanceSnapshot:

        account = self._normalize(

            self._acquire_account(),

        )

        orders = self._normalize(

            self._acquire_open_orders(),

        )

        exchange = self._normalize(

            self._acquire_exchange_info(),

        )

        self.accounts = [

            account,

        ]

        self.positions = account.get(

            "balances",

            [],

        )

        self.orders = orders

        self.executions = []

        self.trades = []

        self.instruments = exchange.get(

            "symbols",

            [],

        )

        self.market_data = [

            exchange,

        ]

        return BinanceSnapshot(

            gateways=[

                {

                    "provider": self.provider_name,

                    "gateway_type": self.gateway_type.value,

                    "environment": self.configuration.environment,

                    "connected": self.is_connected,

                    "transport": "https",

                    "protocol": "binance_rest",

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

    ) -> BinanceSnapshot:

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

        diagnostics["binance"] = {

            "base_url": self.configuration.base_url,

            "environment": self.configuration.environment,

            "connection_state": self.state.value,

            "connected": self.is_connected,

            "authenticated": (

                self.state == BinanceState.ACTIVE

            ),

            "accounts": len(self.accounts),

            "instruments": len(self.instruments),

            "balances": len(self.positions),

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

    "BinanceSnapshot",

    "BinanceConfiguration",

    "BinanceState",

    "BinanceAdapter",

]
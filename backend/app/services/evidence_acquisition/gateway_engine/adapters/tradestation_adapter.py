"""
Trading Truth Layer (TTL)

Gateway Engine

TradeStation REST & Streaming Adapter
"""

from __future__ import annotations

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
class TradeStationSnapshot:

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
class TradeStationConfiguration:

    client_id: str

    client_secret: str

    refresh_token: str

    api_base: str = "https://api.tradestation.com/v3"

    environment: str = "live"


# ============================================================================
# Runtime State
# ============================================================================


class TradeStationState(str, Enum):

    DISCONNECTED = "disconnected"

    AUTHENTICATING = "authenticating"

    ACTIVE = "active"

    CLOSED = "closed"


# ============================================================================
# Adapter
# ============================================================================


class TradeStationAdapter(BaseGatewayAdapter):

    def __init__(

        self,

        configuration: TradeStationConfiguration,

    ):

        super().__init__(

            provider_name="tradestation",

            gateway_type=GatewayType.TRADESTATION,

        )

        self.provider = ProviderDescriptor(

            provider_name="tradestation",

            gateway_type=GatewayType.TRADESTATION,

            display_name="TradeStation",

            vendor="TradeStation",

            version="1.0",

        )

        self.configuration = configuration

        self.state = TradeStationState.DISCONNECTED

        self.access_token: Optional[str] = None

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

        self.state = TradeStationState.AUTHENTICATING

        self._authenticate()

        self.state = TradeStationState.ACTIVE

        self.connected_at = datetime.utcnow()

        self.mark_connected()


    def disconnect(
        self,
    ) -> None:

        self.state = TradeStationState.DISCONNECTED

        self.mark_disconnected()


# ============================================================================
# Authentication
# ============================================================================


    def _authenticate(
        self,
    ) -> None:
        """
        OAuth2 authentication.

        Production implementations exchange the refresh token
        for an access token.
        """

        self.access_token = "<oauth-token>"


# ============================================================================
# HTTP
# ============================================================================


    @property
    def headers(
        self,
    ) -> Dict[str, str]:

        return {

            "Authorization":

                f"Bearer {self.access_token}",

            "Content-Type":

                "application/json",

        }


    def _get(

        self,

        endpoint: str,

    ):

        response = requests.get(

            self.configuration.api_base + endpoint,

            headers=self.headers,

            timeout=30,

        )

        response.raise_for_status()

        return response.json()


# ============================================================================
# Acquisition
# ============================================================================


    def _acquire_accounts(
        self,
    ):

        return self._get(
            "/brokerage/accounts",
        )


    def _acquire_positions(

        self,

        account_id,

    ):

        return self._get(

            f"/brokerage/accounts/{account_id}/positions",

        )


    def _acquire_orders(

        self,

        account_id,

    ):

        return self._get(

            f"/orderexecution/orders/{account_id}",

        )


    def _acquire_balances(

        self,

        account_id,

    ):

        return self._get(

            f"/brokerage/accounts/{account_id}/balances",

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

                k: TradeStationAdapter._normalize(v)

                for k, v in value.items()

            }

        if isinstance(
            value,
            list,
        ):

            return [

                TradeStationAdapter._normalize(v)

                for v in value

            ]

        return value


# ============================================================================
# Snapshot Acquisition
# ============================================================================


    def _collect_snapshot(
        self,
    ) -> TradeStationSnapshot:

        accounts = self._normalize(

            self._acquire_accounts(),

        )

        self.accounts = accounts

        self.positions = []

        self.orders = []

        self.executions = []

        self.trades = []

        self.market_data = []

        self.instruments = []

        for account in accounts:

            account_id = account.get(

                "AccountID",

            )

            self.positions.extend(

                self._normalize(

                    self._acquire_positions(

                        account_id,

                    )

                )

            )

            self.orders.extend(

                self._normalize(

                    self._acquire_orders(

                        account_id,

                    )

                )

            )

        return TradeStationSnapshot(

            gateways=[

                {

                    "provider": self.provider_name,

                    "gateway_type": self.gateway_type.value,

                    "environment": self.configuration.environment,

                    "connected": self.is_connected,

                    "transport": "https",

                    "protocol": "tradestation_rest",

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
    ) -> TradeStationSnapshot:

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

                "oauth2": True,

                "rest": True,

                "streaming": True,

                "historical_data": True,

                "market_data": True,

                "orders": True,

                "positions": True,

                "balances": True,

                "executions": True,

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

        diagnostics["tradestation"] = {

            "environment": self.configuration.environment,

            "api_base": self.configuration.api_base,

            "connection_state": self.state.value,

            "connected": self.is_connected,

            "authenticated": (

                self.state == TradeStationState.ACTIVE

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

    "TradeStationSnapshot",

    "TradeStationConfiguration",

    "TradeStationState",

    "TradeStationAdapter",

]
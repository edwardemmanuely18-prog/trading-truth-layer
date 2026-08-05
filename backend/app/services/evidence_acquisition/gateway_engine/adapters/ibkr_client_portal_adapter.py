"""
Trading Truth Layer (TTL)

Gateway Engine

Interactive Brokers Client Portal Adapter
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict
from typing import Optional

import requests

from ..models import GatewayType
from .base_adapter import BaseGatewayAdapter
from ..provider import (
    ProviderDescriptor,
)


# ============================================================================
# Configuration
# ============================================================================

@dataclass(slots=True)
class IBKRClientPortalConfiguration:

    gateway_url: str = "https://localhost:5000/v1/api"

    username: Optional[str] = None

    password: Optional[str] = None

    environment: str = "client_portal"


# ============================================================================
# Runtime State
# ============================================================================

class IBKRClientPortalState(str, Enum):

    DISCONNECTED = "disconnected"

    AUTHENTICATING = "authenticating"

    ACTIVE = "active"

    CLOSED = "closed"


# ============================================================================
# Adapter
# ============================================================================

class IBKRClientPortalAdapter(BaseGatewayAdapter):

    def __init__(

        self,

        configuration: IBKRClientPortalConfiguration,

    ):

        super().__init__(

            provider_name="interactive_brokers_client_portal",

            gateway_type=GatewayType.IBKR_CLIENT_PORTAL,

        )

        self.configuration = configuration

        self.descriptor = ProviderDescriptor(

            provider_name=self.provider_name,

            gateway_type=self.gateway_type,

            provider_version="1.0",

            vendor="Interactive Brokers",

            description="Interactive Brokers Client Portal Gateway",

            supports_streaming=False,

            supports_historical_data=True,

            supports_order_submission=True,

            supports_positions=True,

            supports_trades=True,

            supports_market_data=True,

            supports_account_information=True,

            supports_multi_account=True,

            supports_reconnection=True,

            supported_protocols=[

                "HTTPS",

                "REST",

            ],

            supported_asset_classes=[

                "Equities",

                "Options",

                "Futures",

                "Forex",

                "Bonds",

            ],

        )

        self.state = IBKRClientPortalState.DISCONNECTED

        self.session = requests.Session()

        self.accounts = []

        self.positions = []

        self.orders = []

        self.executions = []

        self.market_data = []

        self.errors = []


# ============================================================================
# Lifecycle
# ============================================================================

    def initialize(self):

        self.mark_initialized()


    def connect(self):

        self.state = IBKRClientPortalState.AUTHENTICATING

        self._authenticate()

        self.state = IBKRClientPortalState.ACTIVE

        self.mark_connected()


    def disconnect(self):

        self.session.close()

        self.state = IBKRClientPortalState.DISCONNECTED

        self.mark_disconnected()


# ============================================================================
# Authentication
# ============================================================================

    def _authenticate(self):

        """
        Session establishment.

        Client Portal Gateway maintains the
        authenticated browser session.

        Authentication verification is handled
        by the gateway endpoints.
        """

        self._get("/iserver/auth/status")


# ============================================================================
# REST
# ============================================================================

    def _get(

        self,

        endpoint,

        params=None,

    ):

        response = self.session.get(

            self.configuration.gateway_url + endpoint,

            params=params,

            verify=False,

            timeout=30,

        )

        response.raise_for_status()

        return response.json()


# ============================================================================
# Snapshot Acquisition
# ============================================================================

    def _acquire_accounts(self):

        return self._get(

            "/portfolio/accounts"

        )


    def _acquire_positions(

        self,

        account_id,

    ):

        return self._get(

            f"/portfolio/{account_id}/positions/0"

        )


    def _acquire_orders(self):

        return self._get(

            "/iserver/account/orders"

        )


    def _acquire_account_summary(

        self,

        account_id,

    ):

        return self._get(

            f"/portfolio/{account_id}/summary"

        )


# ============================================================================
# Normalization
# ============================================================================

    @staticmethod
    def _normalize(value):

        if value is None:

            return None

        if isinstance(value, dict):

            return {

                k: IBKRClientPortalAdapter._normalize(v)

                for k, v in value.items()

            }

        if isinstance(value, list):

            return [

                IBKRClientPortalAdapter._normalize(v)

                for v in value

            ]

        return value


# ============================================================================
# Evidence Collection
# ============================================================================

    def _collect_evidence(self):

        accounts = self._normalize(

            self._acquire_accounts()

        )

        self.accounts = accounts

        self.positions = []

        self.orders = self._normalize(

            self._acquire_orders()

        )

        self.market_data = []

        for account in accounts:

            account_id = account.get("id")

            summary = self._normalize(

                self._acquire_account_summary(

                    account_id,

                )

            )

            positions = self._normalize(

                self._acquire_positions(

                    account_id,

                )

            )

            account["summary"] = summary

            self.positions.extend(

                positions

            )

        return {

            "gateways":[

                {

                    "provider":

                        self.provider_name,

                    "environment":

                        self.configuration.environment,

                    "connected":

                        self.is_connected,

                }

            ],

            "accounts":

                self.accounts,

            "positions":

                self.positions,

            "orders":

                self.orders,

            "executions":

                self.executions,

            "market_data":

                self.market_data,

            "errors":

                self.errors,

        }


    def acquire(self):

        snapshot = self._collect_evidence()

        self.record_acquisition()

        return snapshot


# ============================================================================
# Capabilities
# ============================================================================

    def capabilities(self):

        capabilities = super().capabilities()

        capabilities.update({

            "rest": True,

            "https": True,

            "session_auth": True,

            "portfolio": True,

            "account_summary": True,

            "orders": True,

            "positions": True,

            "market_data": True,

            "websocket_notifications": True,

        })

        return capabilities


# ============================================================================
# Diagnostics
# ============================================================================

    def diagnostics(self):

        diagnostics = super().diagnostics()

        diagnostics["ibkr_client_portal"] = {

            "environment":

                self.configuration.environment,

            "gateway":

                self.configuration.gateway_url,

            "connection_state":

                self.state.value,

            "accounts":

                len(self.accounts),

            "positions":

                len(self.positions),

            "orders":

                len(self.orders),

            "executions":

                len(self.executions),

        }

        return diagnostics


# ============================================================================
# Cleanup
# ============================================================================

    def close(self):

        self.session.close()

        self.state = IBKRClientPortalState.CLOSED

        self.mark_closed()


# ============================================================================
# Public Exports
# ============================================================================

__all__ = [

    "IBKRClientPortalConfiguration",

    "IBKRClientPortalState",

    "IBKRClientPortalAdapter",

]
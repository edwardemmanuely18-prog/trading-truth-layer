"""
Trading Truth Layer (TTL)

Gateway Engine

NinjaTrader 8 Desktop Adapter
"""

from __future__ import annotations

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
class NinjaTraderSnapshot:

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
class NinjaTraderConfiguration:

    installation_path: Optional[str] = None

    workspace: Optional[str] = None

    environment: str = "desktop"


# ============================================================================
# Runtime State
# ============================================================================


class NinjaTraderState(str, Enum):

    DISCONNECTED = "disconnected"

    INITIALIZING = "initializing"

    ACTIVE = "active"

    CLOSED = "closed"


# ============================================================================
# Adapter
# ============================================================================


class NinjaTraderAdapter(BaseGatewayAdapter):

    def __init__(

        self,

        configuration: NinjaTraderConfiguration,

    ):

        super().__init__(

            provider_name="ninjatrader",

            gateway_type=GatewayType.NINJATRADER,

        )

        self.provider = ProviderDescriptor(

            provider_name="ninjatrader",

            gateway_type=GatewayType.NINJATRADER,

            display_name="NinjaTrader 8",

            vendor="NinjaTrader LLC",

            version="1.0",

        )

        self.configuration = configuration

        self.state = NinjaTraderState.DISCONNECTED

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


    def initialize(
        self,
    ) -> None:

        self.state = NinjaTraderState.INITIALIZING

        self.mark_initialized()


    def connect(
        self,
    ) -> None:
        """
        Connection is established through the
        NinjaTrader AddOn runtime.
        """

        self.state = NinjaTraderState.ACTIVE

        self.connected_at = datetime.utcnow()

        self.mark_connected()


    def disconnect(
        self,
    ) -> None:

        self.state = NinjaTraderState.DISCONNECTED

        self.mark_disconnected()


# ============================================================================
# Event Handlers
# ============================================================================


    def on_account_update(

        self,

        account: Dict[str, Any],

    ) -> None:

        self.accounts = [

            self._normalize(

                account,

            )

        ]


    def on_position_update(

        self,

        position: Dict[str, Any],

    ) -> None:

        self.positions.append(

            self._normalize(

                position,

            )

        )


    def on_order_update(

        self,

        order: Dict[str, Any],

    ) -> None:

        self.orders.append(

            self._normalize(

                order,

            )

        )


    def on_execution_update(

        self,

        execution: Dict[str, Any],

    ) -> None:

        self.executions.append(

            self._normalize(

                execution,

            )

        )


    def on_trade_update(

        self,

        trade: Dict[str, Any],

    ) -> None:

        self.trades.append(

            self._normalize(

                trade,

            )

        )


    def on_market_data(

        self,

        instrument,

        quote,

    ) -> None:

        self.market_data[instrument] = self._normalize(

            quote,

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

                k: NinjaTraderAdapter._normalize(v)

                for k, v in value.items()

            }

        if isinstance(

            value,

            list,

        ):

            return [

                NinjaTraderAdapter._normalize(v)

                for v in value

            ]

        if hasattr(

            value,

            "__dict__",

        ):

            return {

                k: NinjaTraderAdapter._normalize(v)

                for k, v in vars(value).items()

            }

        return value


# ============================================================================
# Snapshot Acquisition
# ============================================================================


    def _collect_snapshot(

        self,

    ) -> NinjaTraderSnapshot:

        return NinjaTraderSnapshot(

            gateways=[

                {

                    "provider": self.provider_name,

                    "gateway_type": self.gateway_type.value,

                    "environment": self.configuration.environment,

                    "workspace": self.configuration.workspace,

                    "connected": self.is_connected,

                    "transport": "desktop",

                    "protocol": "ninjatrader_addon",

                }

            ],

            accounts=list(

                self.accounts,

            ),

            instruments=list(

                self.instruments,

            ),

            positions=list(

                self.positions,

            ),

            orders=list(

                self.orders,

            ),

            executions=list(

                self.executions,

            ),

            trades=list(

                self.trades,

            ),

            market_data=list(

                self.market_data.values(),

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

    ) -> NinjaTraderSnapshot:

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

                "desktop": True,

                "addon": True,

                "streaming": True,

                "market_data": True,

                "orders": True,

                "positions": True,

                "executions": True,

                "trades": True,

                "accounts": True,

                "portfolio": True,

                "workspace": True,

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

        diagnostics["ninjatrader"] = {

            "installation_path": self.configuration.installation_path,

            "workspace": self.configuration.workspace,

            "environment": self.configuration.environment,

            "connection_state": self.state.value,

            "connected": self.is_connected,

            "authenticated": (

                self.state == NinjaTraderState.ACTIVE

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

    "NinjaTraderSnapshot",

    "NinjaTraderConfiguration",

    "NinjaTraderState",

    "NinjaTraderAdapter",

]
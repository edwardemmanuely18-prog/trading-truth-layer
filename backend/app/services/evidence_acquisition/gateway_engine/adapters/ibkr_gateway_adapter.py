"""
Trading Truth Layer (TTL)

Gateway Engine

Interactive Brokers Gateway Adapter

Official Interactive Brokers TWS / IB Gateway adapter.
"""

from __future__ import annotations

import threading
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from dataclasses import dataclass
from dataclasses import field

from ibapi.client import EClient
from ibapi.contract import Contract
from ibapi.wrapper import EWrapper

from ..models import GatewayType
from .base_adapter import BaseGatewayAdapter

from ..registry import ProviderDescriptor
from ..models import GatewayType


# ============================================================================
# Provider Snapshot Models
# ============================================================================


@dataclass(slots=True)
class IBKRGatewaySnapshot:
    """
    Complete acquisition snapshot from an IBKR Gateway session.
    """

    gateways: list[dict[str, Any]] = field(
        default_factory=list,
    )

    accounts: list[Any] = field(
        default_factory=list,
    )

    positions: list[Any] = field(
        default_factory=list,
    )

    orders: list[Any] = field(
        default_factory=list,
    )

    executions: list[Any] = field(
        default_factory=list,
    )

    market_data: list[Any] = field(
        default_factory=list,
    )

    errors: list[Any] = field(
        default_factory=list,
    )


# ============================================================================
# Internal Session
# ============================================================================


class IBKRGatewaySession(
    EWrapper,
    EClient,
):
    """
    Internal IBKR session.

    Owns the socket connection and accumulates callback data.
    """

    def __init__(self):

        EWrapper.__init__(self)

        EClient.__init__(self, self)

        self.connected = False

        self.connection_event = threading.Event()

        self.next_order_id = None

        self.managed_accounts: List[str] = []

        self.positions: List[Dict[str, Any]] = []

        self.orders: List[Dict[str, Any]] = []

        self.executions: List[Dict[str, Any]] = []

        self.market_data: Dict[
            int,
            Dict[str, Any],
        ] = {}

        self.errors: List[Dict[str, Any]] = []

        self._thread: Optional[
            threading.Thread
        ] = None

        self.position_event = threading.Event()

        self.order_event = threading.Event()

        self.account_summary_event = threading.Event()

        self.execution_event = threading.Event()

        self.account_summary: Dict[str, Any] = {}


# ============================================================================
# Connection
# ============================================================================


    def start(
        self,
    ) -> None:
        """
        Start the IB message loop.
        """

        self._thread = threading.Thread(
            target=self.run,
            daemon=True,
        )

        self._thread.start()


# ============================================================================
# Core Callbacks
# ============================================================================


    def nextValidId(
        self,
        orderId,
    ):

        self.connected = True

        self.next_order_id = orderId

        self.connection_event.set()


    def managedAccounts(
        self,
        accountsList,
    ):

        self.managed_accounts = [

            account.strip()

            for account in accountsList.split(",")

            if account.strip()

        ]


    def error(
        self,
        reqId,
        errorCode,
        errorString,
        advancedOrderReject="",
    ):
        """
        Handles API errors.

        Compatible with current IB API releases.
        """

        self.errors.append(

            {

                "request_id": reqId,

                "code": errorCode,

                "message": errorString,

                "advanced_reject": advancedOrderReject,

            }

        )


# ============================================================================
# Account Summary
# ============================================================================

    def accountSummary(
        self,
        reqId,
        account,
        tag,
        value,
        currency,
    ):

        self.account_summary[tag] = {

            "account": account,

            "value": value,

            "currency": currency,

        }


    def accountSummaryEnd(
        self,
        reqId,
    ):

        self.account_summary_event.set()


# ============================================================================
# Position Evidence
# ============================================================================

    def position(
        self,
        account,
        contract: Contract,
        position,
        avgCost,
    ):

        self.positions.append({

            "account": account,

            "symbol": contract.symbol,

            "security_type": contract.secType,

            "exchange": contract.exchange,

            "currency": contract.currency,

            "quantity": position,

            "average_cost": avgCost,

        })


# ============================================================================
# Order Evidence
# ============================================================================

    def openOrder(
        self,
        orderId,
        contract,
        order,
        orderState,
    ):

        self.orders.append({

            "order_id": orderId,

            "symbol": contract.symbol,

            "security_type": contract.secType,

            "action": order.action,

            "order_type": order.orderType,

            "quantity": order.totalQuantity,

            "status": orderState.status,

        })


# ============================================================================
# Order Completion
# ============================================================================

    def openOrderEnd(
        self,
    ):

        self.order_event.set()


# ============================================================================
# Execution Evidence
# ============================================================================

    def execDetails(
        self,
        reqId,
        contract,
        execution,
    ):

        self.executions.append({

            "execution_id": execution.execId,

            "order_id": execution.orderId,

            "account": execution.acctNumber,

            "symbol": contract.symbol,

            "side": execution.side,

            "shares": execution.shares,

            "price": execution.price,

            "time": execution.time,

        })


# ============================================================================
# Execution Completion
# ============================================================================

    def execDetailsEnd(
        self,
        reqId,
    ):

        self.execution_event.set()  

# ============================================================================
# Market Evidence
# ============================================================================

    def tickPrice(
        self,
        reqId,
        tickType,
        price,
        attrib,
    ):

        quote = self.market_data.setdefault(

            reqId,

            {},

        )

        quote[str(tickType)] = price

    # ============================================================================
    # Position Completion
    # ============================================================================

    def positionEnd(
        self,
    ):

        self.position_event.set()


# ============================================================================
# IBKR Gateway Adapter
# ============================================================================


class IBKRGatewayAdapter(BaseGatewayAdapter):
    """
    Interactive Brokers Gateway adapter.
    """

    def __init__(
        self,
        *,
        host: str = "127.0.0.1",
        port: int = 4002,
        client_id: int = 1,
    ) -> None:

        super().__init__(
            provider_name="interactive_brokers",
            gateway_type=GatewayType.IBKR_GATEWAY,
        )

        self.host = host

        self.port = port

        self.client_id = client_id

        self.session = IBKRGatewaySession()

        self.descriptor = ProviderDescriptor(

            provider_name=self.provider_name,

            gateway_type=GatewayType.IBKR_GATEWAY,

            provider_version="1.0",

            vendor="Interactive Brokers",

            description="Interactive Brokers Gateway",

            supports_streaming=True,

            supports_historical_data=True,

            supports_order_submission=True,

            supports_positions=True,

            supports_trades=True,

            supports_market_data=True,

            supports_account_information=True,

            supports_multi_account=True,

            supports_reconnection=True,

            supported_protocols=[
                "IB Gateway",
                "TWS API",
            ],

            supported_asset_classes=[
                "Equities",
                "Options",
                "Futures",
                "Forex",
                "Bonds",
            ],
        )


# ============================================================================
# Lifecycle
# ============================================================================


    def initialize(self) -> None:

        self.mark_initialized()


    def connect(self) -> None:

        self.session.connect(

            self.host,

            self.port,

            self.client_id,

        )

        self.session.start()

        #
        # Wait until the IB API handshake completes.
        #

        print()
        print("Waiting for IBKR handshake...")
        print("Host:", self.host)
        print("Port:", self.port)
        print("Client ID:", self.client_id)

        connected = self.session.connection_event.wait(timeout=10)

        print("Handshake completed:", connected)
        print("API connected:", self.session.isConnected())
        print("Session connected flag:", self.session.connected)

        if not connected:

            print("Errors:", self.session.errors)

            raise TimeoutError(
                "Timed out waiting for IBKR API handshake."
            )

            raise TimeoutError(
                "Timed out waiting for IBKR API handshake."
            )

        self.mark_connected()


    def disconnect(self) -> None:

        self.session.disconnect()

        self.session.connected = False

        self.session.connection_event.clear()

        self.mark_disconnected()


# ============================================================================
# Acquisition Requests
# ============================================================================


    def _request_accounts(
        self,
    ) -> None:

        self.session.account_summary_event.clear()

        self.session.account_summary.clear()

        self.session.reqManagedAccts()

        self.session.reqAccountSummary(

            1,

            "All",

            "NetLiquidation,BuyingPower,"
            "CashBalance,AvailableFunds,"
            "ExcessLiquidity,EquityWithLoanValue",

        )


    def _request_positions(
        self,
    ) -> None:

        self.session.position_event.clear()

        self.session.positions.clear()

        self.session.reqPositions()


    def _request_orders(
        self,
    ) -> None:

        self.session.order_event.clear()

        self.session.orders.clear()

        self.session.reqOpenOrders()


    def _request_executions(
        self,
    ) -> None:

        self.session.execution_event.clear()

        self.session.executions.clear()

        from ibapi.execution import ExecutionFilter

        self.session.reqExecutions(

            2,

            ExecutionFilter(),

        )


# ============================================================================
# Market Data
# ============================================================================


    def _request_market_data(self) -> None:
        """
        Placeholder.

        Market data requests require a Contract and
        are performed on demand.
        """

        pass


# ============================================================================
# Collection
# ============================================================================


    def _collect_evidence(
        self,
    ) -> IBKRGatewaySnapshot:

        return IBKRGatewaySnapshot(

            gateways=[

                {

                    "provider": self.provider_name,

                    "connected": self.session.connected,

                }

            ],

            accounts=list(
                self.session.managed_accounts,
            ),

            positions=list(
                self.session.positions,
            ),

            orders=list(
                self.session.orders,
            ),

            executions=list(
                self.session.executions,
            ),

            market_data=list(
                self.session.market_data.values(),
            ),

            errors=list(
                self.session.errors,
            ),

        )


# ============================================================================
# Canonical Acquisition
# ============================================================================


    def acquire(
        self,
    ) -> Dict[str, Any]:
        """
        Acquire normalized IBKR evidence.
        """

        #
        # Account discovery
        #

        self._request_accounts()

        self.session.account_summary_event.wait(
            timeout=10,
        )

        #
        # Position discovery
        #

        self._request_positions()

        self.session.position_event.wait(
            timeout=10,
        )

        #
        # Open orders
        #

        self._request_orders()

        self.session.order_event.wait(
            timeout=10,
        )

        #
        # Executions
        #

        self._request_executions()

        self.session.execution_event.wait(
            timeout=10,
        )

        #
        # Market data
        #

        self._request_market_data()

        self.record_acquisition()

        return self._collect_evidence()

        return self._collect_evidence()


# ============================================================================
# Adapter Capabilities
# ============================================================================


    def capabilities(
        self,
    ) -> dict:

        capabilities = super().capabilities()

        capabilities.update({

            "streaming": True,

            "historical_data": True,

            "market_data": True,

            "orders": True,

            "positions": True,

            "trades": True,

            "portfolio": True,

            "gateway": True,

        })

        return capabilities


# ============================================================================
# Diagnostics
# ============================================================================


    def diagnostics(
        self,
    ) -> dict:

        diagnostics = super().diagnostics()

        diagnostics["ibkr"] = {

            "host": self.host,

            "port": self.port,

            "client_id": self.client_id,

            "connected": self.session.connected,

            "managed_accounts":

                len(self.session.managed_accounts),

            "positions":

                len(self.session.positions),

            "orders":

                len(self.session.orders),

            "executions":

                len(self.session.executions),

            "market_data":

                len(self.session.market_data),

            "errors":

                len(self.session.errors),

        }

        return diagnostics


# ============================================================================
# Cleanup
# ============================================================================


    def close(
        self,
    ) -> None:
        """
        Release all IBKR resources.
        """

        if self.session.isConnected():

            self.session.disconnect()

        self.session.connected = False

        self.session.connection_event.clear()

        self.mark_closed()


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [

    "IBKRGatewaySnapshot",

    "IBKRGatewaySession",

    "IBKRGatewayAdapter",

]
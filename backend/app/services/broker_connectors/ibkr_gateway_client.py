import threading
import time

from ibapi.client import EClient
from ibapi.wrapper import EWrapper

from ibapi.execution import (
    ExecutionFilter,
)



class IBKRApp(
    EWrapper,
    EClient,
):

    def __init__(self):

        EClient.__init__(
            self,
            self,
        )

        self.accounts = []

        self.connected_event = (
            threading.Event()
        )

        self.account_summary = {}

        self.positions = []

        self.summary_event = (
            threading.Event()
        )

        self.positions_event = (
            threading.Event()
        )

        self.executions = []

        self.executions_event = (
            threading.Event()
        )

    def nextValidId(
        self,
        orderId,
    ):

        self.connected_event.set()

    def managedAccounts(
        self,
        accountsList,
    ):

        self.accounts = [
            account.strip()
            for account in accountsList.split(
                ","
            )
            if account.strip()
        ]

    def accountSummary(
        self,
        reqId,
        account,
        tag,
        value,
        currency,
    ):

        self.account_summary[tag] = value


    def accountSummaryEnd(
        self,
        reqId,
    ):

        self.summary_event.set()

    def position(
        self,
        account,
        contract,
        position,
        avgCost,
    ):

        self.positions.append(
            {
                "account": account,
                "symbol": contract.symbol,
                "quantity": position,
                "avg_cost": avgCost,
            }
        )


    def positionEnd(
        self,
    ):

        self.positions_event.set()

    def execDetails(
        self,
        reqId,
        contract,
        execution,
    ):

        self.executions.append(
            {
                "execution_id":
                    execution.execId,

                "account_id":
                    execution.acctNumber,

                "symbol":
                    contract.symbol,

                "side":
                    execution.side,

                "quantity":
                    execution.shares,

                "price":
                    execution.price,

                "executed_at":
                    execution.time,
            }
        )

    def execDetailsEnd(
        self,
        reqId,
    ):

        self.executions_event.set()

    def error(
        self,
        reqId,
        errorCode,
        errorString,
        advancedOrderRejectJson="",
    ):

        print(
            "IBKR ERROR",
            reqId,
            errorCode,
            errorString,
        )


class IBKRGatewayClient:

    from ibapi.execution import (
        ExecutionFilter,
    )

    def __init__(
        self,
        host,
        port,
        client_id,
    ):

        self.host = host
        self.port = port
        self.client_id = client_id

        self.app = None

        self.thread = None

    def connect(self):

        self.app = IBKRApp()

        self.app.connect(
            self.host,
            self.port,
            self.client_id,
        )

        self.thread = threading.Thread(
            target=self.app.run,
            daemon=True,
        )

        self.thread.start()

        connected = (
            self.app.connected_event.wait(
                timeout=10
            )
        )

        return connected

    def disconnect(self):

        if self.app:

            self.app.disconnect()

    def list_accounts(self):

        self.app.reqManagedAccts()

        time.sleep(2)

        return [
            {
                "account_id": account,
                "account_name": account,
                "environment": "paper",
                "currency": "USD",
            }
            for account in self.app.accounts
        ]

    def get_account_summary(
        self,
    ):

        self.app.account_summary = {}

        self.app.summary_event.clear()

        self.app.reqAccountSummary(
            1,
            "All",
            "NetLiquidation,"
            "AvailableFunds,"
            "CashBalance",
        )

        self.app.summary_event.wait(
            timeout=10
        )

        return (
            self.app.account_summary
        )

    def get_positions(
        self,
    ):

        self.app.positions = []

        self.app.positions_event.clear()

        self.app.reqPositions()

        self.app.positions_event.wait(
            timeout=10
        )

        return self.app.positions

    def list_executions(
        self,
    ):

        self.app.executions = []

        self.app.executions_event.clear()

        self.app.reqManagedAccts()

        time.sleep(2)

        print(
            "accounts:",
            self.app.accounts,
        )

        execution_filter = ExecutionFilter()

        if self.app.accounts:

            execution_filter.acctCode = (
                self.app.accounts[0]
            )

        self.app.reqExecutions(
            1,
            execution_filter,
        )

        self.app.executions_event.wait(
            timeout=15
        )

        return self.app.executions
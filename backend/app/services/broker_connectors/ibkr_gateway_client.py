class IBKRGatewayClient:

    def __init__(
        self,
        host,
        port,
        client_id,
    ):
        self.host = host
        self.port = port
        self.client_id = client_id

        self.connected = False

    def connect(self):

        self.connected = True

        return True

    def disconnect(self):

        self.connected = False

    def list_accounts(self):

        if not self.connected:
            return []

        return [
            {
                "account_id": "DU123456",
                "account_name": "IBKR Demo",
                "environment": "paper",
                "currency": "USD",
            }
        ]

    def get_account_summary(self):

        if not self.connected:
            return {}

        return {

            "account_id": "DU123456",

            "balance": 100000.00,

            "equity": 100000.00,

            "net_liquidation": 100000.00,

            "buying_power": 400000.00,

            "currency": "USD",
        }


    def get_positions(self):

        if not self.connected:
            return []

        return []


    def get_executions(self):

        if not self.connected:
            return []

        return []


    def get_trades(self):

        return self.get_executions()


    def list_executions(
        self,
    ):
        """
        Temporary execution feed.

        Will later be replaced
        by real IBKR Gateway API.
        """

        if not self.connected:
            return []

        return [
            {
                "execution_id":
                    "EXEC001",

                "account_id":
                    "DU123456",

                "symbol":
                    "AAPL",

                "side":
                    "BUY",

                "quantity":
                    100,

                "price":
                    210.50,

                "executed_at":
                    "2026-06-15T10:00:00",
            }
        ]
from app.services.broker_connectors.base_connector import (
    BaseBrokerConnector,
)


class IBKRConnector(BaseBrokerConnector):

    def __init__(self, credential):
        self.credential = credential

    def verify(
        self,
        payload: dict,
    ):

        from app.services.broker_connectors.ibkr_gateway_client import (
            IBKRGatewayClient,
        )

        client = IBKRGatewayClient(
            host=payload.get(
                "host",
                "127.0.0.1",
            ),
            port=int(
                payload.get(
                    "port",
                    7497,
                )
            ),
            client_id=int(
                payload.get(
                    "client_id",
                    1,
                )
            ),
        )

        connected = client.connect()

        if not connected:
            return {
                "success": False,
                "error": "Unable to connect to gateway",
            }

        try:

            accounts = client.list_accounts()

            if not accounts:
                return {
                    "success": False,
                    "error": "No accounts discovered",
                }

            account = accounts[0]

            return {
                "success": True,
                "account_id":
                    account["account_id"],
                "account_name":
                    account["account_name"],
                "account_environment":
                    account["environment"],
                "currency":
                    account["currency"],
            }

        finally:

            client.disconnect()

    def discover_accounts(self):
        
        from app.services.broker_connectors.ibkr_gateway_client import (
            IBKRGatewayClient,
        )

        client = IBKRGatewayClient(
            host="127.0.0.1",
            port=7497,
            client_id=1,
        )

        client.connect()

        try:

            accounts = client.list_accounts()

            return [
                BrokerAccount(
                    account_id=a["account_id"],
                    account_name=a["account_name"],
                    environment=a["environment"],
                    currency=a["currency"],
                )
                for a in accounts
            ]

        finally:

            client.disconnect()

    def sync_trades(self):
        pass

    def sync_positions(self):
        pass

    def sync_account_state(self):
        pass
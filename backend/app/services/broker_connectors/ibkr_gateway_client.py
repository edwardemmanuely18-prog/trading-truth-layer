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
class IBKRGatewayClient:

    def __init__(
        self,
        host: str,
        port: int,
        client_id: int,
    ):
        self.host = host
        self.port = port
        self.client_id = client_id

    def connect(self):
        pass

    def disconnect(self):
        pass

    def list_accounts(self):
        return []
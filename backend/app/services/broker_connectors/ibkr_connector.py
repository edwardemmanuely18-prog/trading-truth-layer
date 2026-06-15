from app.services.broker_connectors.base_connector import (
    BaseBrokerConnector,
)


class IBKRConnector(BaseBrokerConnector):

    def __init__(self, credential):
        self.credential = credential

    def verify(self, payload: dict):
        pass

    def discover_accounts(self):
        pass

    def sync_trades(self):
        pass

    def sync_positions(self):
        pass

    def sync_account_state(self):
        pass
from app.services.broker_connectors.base_connector import (
    BaseBrokerConnector,
)

from app.services.broker_connectors.account_models import (
    BrokerAccount,
)


class MT5Connector(BaseBrokerConnector):

    def __init__(
        self,
        credential,
    ):
        self.credential = credential

    def verify(
        self,
        payload: dict,
    ):
        pass

    def discover_accounts(
        self,
    ) -> list[BrokerAccount]:

        return []

    def sync_trades(
        self,
    ):
        return []

    def sync_positions(
        self,
    ):
        return []

    def sync_account_state(
        self,
    ):
        return {}
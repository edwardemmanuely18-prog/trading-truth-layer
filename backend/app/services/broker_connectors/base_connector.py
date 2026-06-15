from abc import ABC
from abc import abstractmethod

from app.services.broker_connectors.account_models import (
    BrokerAccount,
)


class BaseBrokerConnector(ABC):

    @abstractmethod
    def verify(
        self,
        payload: dict,
    ):
        pass

    @abstractmethod
    def discover_accounts(
        self,
    ) -> list[BrokerAccount]:
        pass

    @abstractmethod
    def sync_trades(
        self,
    ):
        pass

    @abstractmethod
    def sync_positions(
        self,
    ):
        pass

    @abstractmethod
    def sync_account_state(
        self,
    ):
        pass
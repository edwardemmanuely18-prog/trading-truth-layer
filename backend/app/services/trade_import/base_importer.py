from abc import ABC, abstractmethod


class BaseTradeImporter(ABC):

    @abstractmethod
    def import_trades(
        self,
        connection,
        credential,
        sync_job,
    ):
        pass
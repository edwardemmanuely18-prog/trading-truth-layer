from abc import ABC, abstractmethod


class BaseTradeImporter(ABC):

    @abstractmethod
    def import_trades(
        self,
        db,
        connection,
        credential,
        sync_job,
    ):
        pass
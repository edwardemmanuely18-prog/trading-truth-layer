from app.services.trade_import.base_importer import (
    BaseTradeImporter,
)


class IBKRImporter(BaseTradeImporter):

    def import_trades(
        self,
        connection,
        credential,
        sync_job,
    ):
        return {
            "success": True,
            "records_detected": 0,
            "records_imported": 0,
        }
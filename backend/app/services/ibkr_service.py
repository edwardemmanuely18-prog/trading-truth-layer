from typing import Dict


class IBKRService:

    @staticmethod
    def verify_credentials(
        username: str,
        password: str,
    ) -> Dict:

        #
        # Real IBKR API integration
        # will be inserted here later
        #

        return {
            "success": True,
            "environment": "live",
            "broker_account_id": "DU123456",
            "broker_server": "IBKR Gateway",
            "currency": "USD",
            "leverage": "1:30",
            "balance": "100000",
            "equity": "100000",
        }
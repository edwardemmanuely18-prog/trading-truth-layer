from app.services.paddle_service import (
    paddle_request,
    paddle_is_ready,
)


class PaddleProvider:

    provider_name = "paddle"

    @staticmethod
    def is_ready():
        return paddle_is_ready()

    @staticmethod
    def create_transaction(payload):
        return paddle_request(
            "POST",
            "/transactions",
            payload,
        )
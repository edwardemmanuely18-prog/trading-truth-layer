from app.services.lemon_service import (
    create_lemon_checkout,
    lemon_is_ready,
)


class LemonProvider:

    provider_name = "lemon"

    @staticmethod
    def is_ready():
        return lemon_is_ready()

    @staticmethod
    def create_checkout(**kwargs):
        return create_lemon_checkout(
            **kwargs
        )
from app.services.adapters.adapter_registry import (
    ADAPTER_REGISTRY,
)


def get_trade_adapter(source_type: str):
    normalized = (
        source_type
        .strip()
        .lower()
    )

    adapter_class = ADAPTER_REGISTRY.get(
        normalized
    )

    if not adapter_class:
        raise ValueError(
            f"Unsupported broker source: {source_type}"
        )

    return adapter_class()
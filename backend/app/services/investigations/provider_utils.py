from __future__ import annotations

from typing import Any


def payload(
    context: Any,
    provider_name: str,
) -> Any:
    """
    Retrieve a canonical provider payload.

    Engines should always retrieve provider payloads
    through this helper rather than accessing
    context.provider_payloads directly.

    Parameters
    ----------
    context
        InvestigationContext.

    provider_name
        Canonical provider name.

    Returns
    -------
    Provider payload or None.
    """

    provider_payloads = getattr(
        context,
        "provider_payloads",
        {},
    )

    return provider_payloads.get(
        provider_name,
    )
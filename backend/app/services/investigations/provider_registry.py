from __future__ import annotations

from sqlalchemy.orm import Session

from .base_provider import (
    InvestigationProvider,
)

_PROVIDER_REGISTRY: list[
    InvestigationProvider
] = []


def register_provider(

    provider: InvestigationProvider,

) -> None:

    _PROVIDER_REGISTRY.append(
        provider,
    )


def providers():

    return tuple(
        _PROVIDER_REGISTRY,
    )


def collect_provider_payloads(

    *,

    db: Session,

    workspace_id: int,

):

    payloads = {}

    for provider in sorted(

        _PROVIDER_REGISTRY,

        key=lambda p: p.priority,

    ):

        payload = provider.collect(

            db=db,

            workspace_id=workspace_id,

        )

        provider.validate(
            payload,
        )

        payloads[
            provider.name
        ] = payload

    return payloads
from __future__ import annotations

from app.services.verification.registry.registry_models import (
    VerificationSnapshot,
)


class VerificationRegistry:
    """
    Canonical storage abstraction for
    verification snapshots.

    Initial implementation is in-memory.

    Later this will persist into the
    Verification Registry database.
    """

    def __init__(self):

        self._registry = {}

    def register(
        self,
        snapshot: VerificationSnapshot,
    ):

        self._registry[
            snapshot.claim_id
        ] = snapshot

    def get(
        self,
        claim_id: int,
    ):

        return self._registry.get(
            claim_id
        )

    def exists(
        self,
        claim_id: int,
    ):

        return claim_id in self._registry


verification_registry = VerificationRegistry()
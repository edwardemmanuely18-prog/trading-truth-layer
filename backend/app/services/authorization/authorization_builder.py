from __future__ import annotations

from app.services.authorization.authorization_models import (
    AuthorizationSnapshot,
)


def build_authorization_snapshot(

    role: str,

    commercial_plan: str,

    billing_active: bool,

    pages: dict,

    features: dict,

    limits: dict,

) -> AuthorizationSnapshot:

    return AuthorizationSnapshot(

        role=role,

        commercial_plan=commercial_plan,

        billing_active=billing_active,

        pages=pages,

        features=features,

        limits=limits,

    )
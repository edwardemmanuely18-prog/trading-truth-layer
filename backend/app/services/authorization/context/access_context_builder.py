from __future__ import annotations

from sqlalchemy.orm import Session

from app.services.authorization.identity.workspace_identity_builder import (
    WorkspaceIdentityBuilder,
)

from app.services.entitlements import (
    build_entitlement_snapshot,
)

from .access_context import AccessContext


class AccessContextBuilder:

    @staticmethod
    def build(
        db: Session,
        workspace_id: int,
        user_id: int,
    ) -> AccessContext:

        identity = WorkspaceIdentityBuilder.build(
            db=db,
            workspace_id=workspace_id,
            user_id=user_id,
        )

        snapshot = build_entitlement_snapshot(
            workspace_id=workspace_id,
            db=db,
        )

        pages = snapshot.get(
            "pages",
            {},
        )

        features = snapshot.get(
            "features",
            {},
        )

        access = snapshot.get(
            "access",
            {},
        )

        return AccessContext(

            identity=identity,

            commercial_plan=snapshot["plan_code"],

            billing_active=access.get(
                "has_active_access",
                False,
            ),

            enabled_features=frozenset(

                key

                for key, enabled in features.items()

                if enabled

            ),

            enabled_pages=frozenset(

                key

                for key, enabled in pages.items()

                if enabled

            ),

        )
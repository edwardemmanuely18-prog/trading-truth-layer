from __future__ import annotations

from sqlalchemy.orm import Session

from app.services.authorization.context.access_context_builder import (
    AccessContextBuilder,
)

from app.services.authorization.authorization_builder import (
    build_authorization_snapshot,
)


def get_workspace_authorization(

    db: Session,

    workspace_id: int,

    user_id: int,

):

    context = AccessContextBuilder.build(

        db=db,

        workspace_id=workspace_id,

        user_id=user_id,

    )

    return build_authorization_snapshot(

        role=context.identity.role,

        commercial_plan=context.commercial_plan,

        billing_active=context.billing_active,

        pages={

            page: page in context.enabled_pages

            for page in context.enabled_pages

        },

        features={

            feature: feature in context.enabled_features

            for feature in context.enabled_features

        },

        limits={},

    )
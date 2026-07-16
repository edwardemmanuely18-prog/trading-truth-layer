from __future__ import annotations

from ..provider_registry import (
    register_provider,
)

from .workspace_provider import (
    WorkspaceProvider,
)

from .claim_provider import (
    ClaimProvider,
)

from .execution_provider import (
    ExecutionProvider,
)

from .member_provider import (
    MemberProvider,
)

from .verification_provider import (
    VerificationProvider,
)

from .tvs_provider import (
    TVSProvider,
)

from .sync_job_provider import (
    SyncJobProvider,
)

from .audit_provider import (
    AuditProvider,
)

from .review_provider import (
    ReviewProvider,
)

from .broker_provider import (
    BrokerProvider,
)


# ============================================================
# Canonical Provider Registration
# ============================================================

_PROVIDER_BOOTSTRAPPED = False


def bootstrap_providers() -> None:

    global _PROVIDER_BOOTSTRAPPED

    if _PROVIDER_BOOTSTRAPPED:
        return

    register_provider(
        WorkspaceProvider(),
    )

    register_provider(
        ClaimProvider(),
    )

    register_provider(
        ExecutionProvider(),
    )

    register_provider(
        MemberProvider(),
    )

    register_provider(
        VerificationProvider(),
    )

    register_provider(
        TVSProvider(),
    )

    register_provider(
        SyncJobProvider(),
    )

    register_provider(
        AuditProvider(),
    )

    register_provider(
        ReviewProvider(),
    )

    register_provider(
        BrokerProvider(),
    )

    _PROVIDER_BOOTSTRAPPED = True
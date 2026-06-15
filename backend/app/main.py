import os

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from app.core.db import Base, engine, SessionLocal

# Import models so SQLAlchemy registers them
from app.models import (
    Workspace,
    Trade,
    ClaimSchema,
    ImportBatch,
    AuditEvent,
    User,
    WorkspaceMembership,
    WorkspaceInvite,
    ClaimDispute,
    BrokerConnection,
)
from app.models.import_job import ImportJob

# Routers
from app.api.routes import verify
from app.api.routes.health import router as health_router
from app.api.routes.auth import router as auth_router
from app.api.routes.workspaces import router as workspaces_router
from app.api.routes.trades import router as trades_router
from app.api.routes.claim_schemas import router as claim_schemas_router
from app.api.routes.imports import router as imports_router
from app.api.routes.audit import router as audit_router
from app.api.routes.invites import router as invites_router
from app.api.routes.billing import router as billing_router
from app.api.routes.platform import router as platform_router
from app.api.routes.claim_disputes import router as claim_disputes_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes import workspace_members
from app.api.routes import billing

from app.api.routes import aurum

from app.core.security import hash_password

from app.core.rate_limit import limiter

from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler




# =========================
# SENTRY
# =========================

SENTRY_DSN = os.getenv("SENTRY_DSN")

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,

        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
        ],

        traces_sample_rate=1.0,

        profiles_sample_rate=1.0,

        send_default_pii=False,

        environment=os.getenv("ENVIRONMENT", "development"),
    )


# =========================
# APP INIT
# =========================
app = FastAPI(title="Trading Truth Layer API")

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)



# =========================
# CORS (FINAL CLEAN VERSION)
# =========================

origins = os.getenv(
    "CORS_ALLOW_ORIGINS",
    ",".join([
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "https://tradingtruthlayer.com",
        "https://www.tradingtruthlayer.com",
        "https://trading-truth-layer.vercel.app",
    ])
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.routes import public

app.include_router(trades_router, prefix="/api")

# =========================
# SAFE STARTUP (CRITICAL)
# =========================
@app.on_event("startup")
def on_startup():
    print("=== STARTING APPLICATION ===", flush=True)

    # ✅ ONLY SAFE OPERATION
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        inspector = inspect(engine)

        columns = [
            col["name"]
            for col in inspector.get_columns("workspaces")
        ]

        workspace_patches = {
            "lemon_customer_id": "ALTER TABLE workspaces ADD COLUMN lemon_customer_id VARCHAR",
            "lemon_subscription_id": "ALTER TABLE workspaces ADD COLUMN lemon_subscription_id VARCHAR",
            "lemon_order_id": "ALTER TABLE workspaces ADD COLUMN lemon_order_id VARCHAR",
            "lemon_product_id": "ALTER TABLE workspaces ADD COLUMN lemon_product_id VARCHAR",
            "lemon_variant_id": "ALTER TABLE workspaces ADD COLUMN lemon_variant_id VARCHAR",
            "is_internal_workspace": "ALTER TABLE workspaces ADD COLUMN is_internal_workspace BOOLEAN DEFAULT FALSE",
            "subscription_source": "ALTER TABLE workspaces ADD COLUMN subscription_source VARCHAR",
        }

        for column_name, sql in workspace_patches.items():
            if column_name not in columns:
                db.execute(text(sql))
                db.commit()

        trade_columns = [
            col["name"]
            for col in inspector.get_columns("trades")
        ]

        trade_patches = {
            "trade_fingerprint":
                "ALTER TABLE trades ADD COLUMN trade_fingerprint VARCHAR",

            "source_system":
                "ALTER TABLE trades ADD COLUMN source_system VARCHAR",

            "strategy_tag":
                "ALTER TABLE trades ADD COLUMN strategy_tag VARCHAR",
        }

        for column_name, sql in trade_patches.items():
            if column_name not in trade_columns:
                db.execute(text(sql))
                db.commit()

        user_columns = [
            col["name"]
            for col in inspector.get_columns("users")
        ]

        user_patches = {
            "email_verified":
                "ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT FALSE",

            "email_verification_token":
                "ALTER TABLE users ADD COLUMN email_verification_token VARCHAR",

            "email_verification_expires_at":
                "ALTER TABLE users ADD COLUMN email_verification_expires_at TIMESTAMP",

            "password_reset_token":
                "ALTER TABLE users ADD COLUMN password_reset_token VARCHAR",

            "password_reset_expires_at":
                "ALTER TABLE users ADD COLUMN password_reset_expires_at TIMESTAMP",
        }

        for column_name, sql in user_patches.items():
            if column_name not in user_columns:
                db.execute(text(sql))
                db.commit()        

    finally:
        db.close()

    db = SessionLocal()
    try:
        # -------------------------
        # Ensure default workspace
        # -------------------------
        workspace = db.query(Workspace).filter_by(id=1).first()
        if not workspace:
            workspace = Workspace(
                id=1,
                name="Verification Sandbox",
                plan_code="starter",
                billing_status="inactive",
                claim_limit=5,
                trade_limit=1000,
                member_limit=3,
                storage_limit_mb=500,
            )
            db.add(workspace)
            db.commit()

        # -------------------------
        # Ensure default users
        # -------------------------
        owner = db.query(User).filter_by(id=1).first()
        if not owner:
            owner = User(
                id=1,
                email="owner@tradingtruthlayer.com",
                name="Owner",
                role="owner",
                password_hash=hash_password("OwnerPass123!"),
            )
            db.add(owner)
            db.commit()

        operator = db.query(User).filter_by(id=2).first()
        if not operator:
            operator = User(
                id=2,
                email="operator@tradingtruthlayer.com",
                name="Operator",
                role="operator",
                password_hash=hash_password("OperatorPass123!"),
            )
            db.add(operator)
            db.commit()

        # -------------------------
        # Ensure memberships
        # -------------------------
        owner_m = (
            db.query(WorkspaceMembership)
            .filter_by(workspace_id=1, user_id=1)
            .first()
        )
        if not owner_m:
            db.add(
                WorkspaceMembership(
                    workspace_id=1,
                    user_id=1,
                    role="owner",
                )
            )
            db.commit()

        operator_m = (
            db.query(WorkspaceMembership)
            .filter_by(workspace_id=1, user_id=2)
            .first()
        )
        if not operator_m:
            db.add(
                WorkspaceMembership(
                    workspace_id=1,
                    user_id=2,
                    role="operator",
                )
            )
            db.commit()

    finally:
        db.close()


# =========================
# ROUTES
# =========================

app.include_router(verify.router)
app.include_router(health_router)
app.include_router(auth_router)

# ALL WORKSPACE APIs MUST BE UNDER /api
app.include_router(workspaces_router, prefix="/api")
app.include_router(trades_router, prefix="/api")
app.include_router(claim_schemas_router, prefix="/api")
app.include_router(imports_router, prefix="/api")
app.include_router(audit_router, prefix="/api")
app.include_router(invites_router, prefix="/api")
app.include_router(billing_router, prefix="/api")
app.include_router(platform_router, prefix="/api")
app.include_router(claim_disputes_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(public.router, prefix="/api")
app.include_router(aurum.router)

# IMPORTANT: prefix for API routes
app.include_router(workspace_members.router, prefix="/api")

# =========================
# BASIC ENDPOINTS
# =========================
@app.get("/")
def root():
    return {"message": "Trading Truth Layer API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}
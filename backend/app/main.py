import os

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
)

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
from app.api.routes import workspace_members
from app.api.routes import billing

from app.core.security import hash_password

# =========================
# APP INIT
# =========================
app = FastAPI(title="Trading Truth Layer API")

# =========================
# CORS
# =========================
def parse_cors_origins():
    raw = os.getenv(
        "CORS_ALLOW_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    )
    return [o.strip() for o in raw.split(",") if o.strip()]


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://trading-truth-layer.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
import os

from fastapi import FastAPI
from app.api.routes import verify
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from app.core.db import Base, engine, SessionLocal
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
from app.core.security import hash_password


def parse_cors_origins() -> list[str]:
    raw = os.getenv(
        "CORS_ALLOW_ORIGINS",
        ",".join(
            [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "https://impartial-empathy-production-0186.up.railway.app",
            ]
        ),
    )
    return [origin.strip().rstrip("/") for origin in raw.split(",") if origin.strip()]


def ensure_claim_schema_columns():
    inspector = inspect(engine)

    if "claim_schemas" not in inspector.get_table_names():
        return

    existing_columns = {col["name"] for col in inspector.get_columns("claim_schemas")}

    with engine.begin() as conn:
        if "locked_trade_ids_json" not in existing_columns:
            conn.execute(
                text(
                    "ALTER TABLE claim_schemas "
                    "ADD COLUMN locked_trade_ids_json TEXT NOT NULL DEFAULT '[]'"
                )
            )

        if "claim_hash" not in existing_columns:
            conn.execute(
                text(
                    "ALTER TABLE claim_schemas "
                    "ADD COLUMN claim_hash VARCHAR"
                )
            )


def ensure_claim_dispute_table():
    inspector = inspect(engine)

    if "claim_disputes" in inspector.get_table_names():
        return

    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS claim_disputes (
                    id INTEGER PRIMARY KEY,
                    claim_schema_id INTEGER NOT NULL,
                    workspace_id INTEGER NOT NULL,
                    status VARCHAR NOT NULL DEFAULT 'open',
                    challenge_type VARCHAR NOT NULL DEFAULT 'general_review',
                    reason_code VARCHAR NOT NULL DEFAULT 'other',
                    summary VARCHAR NOT NULL,
                    evidence_note TEXT NOT NULL DEFAULT '',
                    reporter_user_id INTEGER NOT NULL,
                    reviewer_user_id INTEGER,
                    resolution_note TEXT,
                    opened_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    resolved_at DATETIME
                )
                """
            )
        )

        
def backfill_claim_hashes():
    from app.api.routes.claim_schemas import compute_claim_hash

    db = SessionLocal()
    try:
        claims = db.query(ClaimSchema).all()
        changed = False

        for claim in claims:
            if not claim.claim_hash:
                claim.claim_hash = compute_claim_hash(claim)
                changed = True

        if changed:
            db.commit()
    finally:
        db.close()


app = FastAPI(title="Trading Truth Layer API")
app.include_router(verify.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    ensure_claim_schema_columns()
    ensure_claim_dispute_table()
    backfill_claim_hashes()

    db = SessionLocal()
    try:
        existing_workspace = db.query(Workspace).filter(Workspace.id == 1).first()
        if not existing_workspace:
            existing_workspace = Workspace(
                id=1,
                name="Verification Sandbox",
                plan_code="starter",
                billing_status="inactive",
                claim_limit=5,
                trade_limit=1000,
                member_limit=3,
                storage_limit_mb=500,
            )
            db.add(existing_workspace)
            db.commit()
            db.refresh(existing_workspace)

        default_owner = db.query(User).filter(User.id == 1).first()
        if not default_owner:
            db.add(
                User(
                    id=1,
                    email="owner@tradingtruthlayer.com",
                    name="Default Owner",
                    role="owner",
                    password_hash=hash_password("OwnerPass123!"),
                )
            )
            db.commit()
        else:
            changed = False
            if default_owner.email != "owner@tradingtruthlayer.com":
                default_owner.email = "owner@tradingtruthlayer.com"
                changed = True
            if not default_owner.password_hash:
                default_owner.password_hash = hash_password("OwnerPass123!")
                changed = True
            if changed:
                db.commit()

        default_operator = db.query(User).filter(User.id == 2).first()
        if not default_operator:
            db.add(
                User(
                    id=2,
                    email="operator@tradingtruthlayer.com",
                    name="Default Operator",
                    role="operator",
                    password_hash=hash_password("OperatorPass123!"),
                )
            )
            db.commit()
        else:
            changed = False
            if default_operator.email != "operator@tradingtruthlayer.com":
                default_operator.email = "operator@tradingtruthlayer.com"
                changed = True
            if not default_operator.password_hash:
                default_operator.password_hash = hash_password("OperatorPass123!")
                changed = True
            if changed:
                db.commit()

        owner_membership = (
            db.query(WorkspaceMembership)
            .filter(
                WorkspaceMembership.workspace_id == 1,
                WorkspaceMembership.user_id == 1,
            )
            .first()
        )
        if not owner_membership:
            db.add(
                WorkspaceMembership(
                    workspace_id=1,
                    user_id=1,
                    role="owner",
                )
            )
            db.commit()

        operator_membership = (
            db.query(WorkspaceMembership)
            .filter(
                WorkspaceMembership.workspace_id == 1,
                WorkspaceMembership.user_id == 2,
            )
            .first()
        )
        if not operator_membership:
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


@app.get("/")
def root():
    return {"message": "Trading Truth Layer API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(health_router)
app.include_router(auth_router)
app.include_router(workspaces_router)
app.include_router(trades_router)
app.include_router(claim_schemas_router)
app.include_router(imports_router)
app.include_router(audit_router)
app.include_router(invites_router)
app.include_router(billing_router)
app.include_router(platform_router)
app.include_router(claim_disputes_router)
app.include_router(workspace_members.router, prefix="/api", tags=["workspace-members"])
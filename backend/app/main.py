import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
)
from app.api.routes.health import router as health_router
from app.api.routes.workspaces import router as workspaces_router
from app.api.routes.trades import router as trades_router
from app.api.routes.claim_schemas import router as claim_schemas_router
from app.api.routes.imports import router as imports_router
from app.api.routes.audit import router as audit_router
from app.api.routes.invites import router as invites_router


def parse_cors_origins() -> list[str]:
    raw = os.getenv(
        "CORS_ALLOW_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    )
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


app = FastAPI(title="Trading Truth Layer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=parse_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        existing_workspace = db.query(Workspace).filter(Workspace.id == 1).first()
        if not existing_workspace:
            db.add(Workspace(id=1, name="Verification Sandbox"))
            db.commit()

        default_owner = db.query(User).filter(User.id == 1).first()
        if not default_owner:
            db.add(
                User(
                    id=1,
                    email="owner@tradingtruthlayer.local",
                    name="Default Owner",
                    role="owner",
                )
            )
            db.commit()

        default_operator = db.query(User).filter(User.id == 2).first()
        if not default_operator:
            db.add(
                User(
                    id=2,
                    email="operator@tradingtruthlayer.local",
                    name="Default Operator",
                    role="operator",
                )
            )
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


app.include_router(health_router)
app.include_router(workspaces_router)
app.include_router(trades_router)
app.include_router(claim_schemas_router)
app.include_router(imports_router)
app.include_router(audit_router)
app.include_router(invites_router)
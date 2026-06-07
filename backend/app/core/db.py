from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings


# =========================
# ENGINE CONFIG
# =========================
connect_args = {}

if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

from sqlalchemy import create_engine

engine = create_engine(
    settings.DATABASE_URL,

    connect_args=connect_args,

    pool_pre_ping=True,
    pool_recycle=300,

    pool_size=5,
    max_overflow=10,

    future=True,
)

# =========================
# SESSION
# =========================
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# =========================
# BASE
# =========================
Base = declarative_base()


# =========================
# DEPENDENCY
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
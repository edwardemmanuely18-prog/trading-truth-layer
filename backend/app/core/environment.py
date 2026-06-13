import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]

TTL_ENV = os.getenv(
    "TTL_ENV",
    "production",
)

if TTL_ENV == "refactor":
    ENV_FILE = BASE_DIR / "backend" / ".env.refactor"
else:
    ENV_FILE = BASE_DIR / "backend" / ".env"

os.environ["TTL_ENV_FILE"] = str(ENV_FILE)
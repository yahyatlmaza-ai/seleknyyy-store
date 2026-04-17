"""Application configuration loaded from environment."""
import os
from pathlib import Path


def _env(name: str, default: str) -> str:
    value = os.environ.get(name)
    return value if value else default


# Database: use /data/app.db in production (persistent volume), local file in dev.
DATA_DIR = Path(_env("AUTOFLOW_DATA_DIR", "/data"))
DB_PATH = DATA_DIR / "app.db"
if not DATA_DIR.exists():
    # Local dev fallback: write to ./dev.db inside backend/
    DATA_DIR = Path(__file__).resolve().parent.parent
    DB_PATH = DATA_DIR / "dev.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

# JWT
JWT_SECRET = _env(
    "AUTOFLOW_JWT_SECRET",
    "change-me-in-production-autoflow-" + os.urandom(8).hex(),
)
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Trial
TRIAL_DAYS = 14

# Platform
PLATFORM_NAME = "auto Flow"
SUPPORT_WHATSAPP = "+213794157508"

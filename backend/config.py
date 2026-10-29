
import os
from pathlib import Path
from dotenv import load_dotenv

# =====================================================
# PROJECT PATHS
# =====================================================

# backend/config.py -> backend -> project root
BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / "backend"

ROOT_ENV = BASE_DIR / ".env"
BACKEND_ENV = BACKEND_DIR / ".env"

# Load the root .env first.
if ROOT_ENV.is_file():
    load_dotenv(ROOT_ENV)

# If backend/.env exists, let its values take priority.
if BACKEND_ENV.is_file():
    load_dotenv(BACKEND_ENV, override=True)


# =====================================================
# GEMINI CONFIGURATION
# =====================================================

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)

MAX_REPAIRS = int(
    os.getenv("MAX_REPAIRS", "3")
)

MAX_BUTTONS_TO_TEST = 15
MAX_LINKS_TO_CHECK = 30


# =====================================================
# DATABASE
# =====================================================

# Uses the existing checkpoints.sqlite in your project root.
DATABASE_PATH = BASE_DIR / "checkpoints.sqlite"


# =====================================================
# WEBSITE DIRECTORIES
# =====================================================

PREVIEW_ROOT = BASE_DIR / "preview_website"
OUTPUT_ROOT = BASE_DIR / "generated_website"

# Create output folders automatically.
PREVIEW_ROOT.mkdir(parents=True, exist_ok=True)
OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)


# =====================================================
# VALIDATION
# =====================================================

if not GOOGLE_API_KEY:
    raise RuntimeError(
        "GOOGLE_API_KEY is missing. "
        "Add it to the project-root .env file "
        "or backend/.env."
    )

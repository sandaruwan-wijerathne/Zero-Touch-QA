import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
WORKSPACE_ROOT = Path(os.environ.get("QA_WORKSPACE", str(PROJECT_ROOT / "qa_workspace"))).resolve()
TEST_APP_URL = os.environ.get("TEST_APP_URL", "http://localhost:5173")

PATHS = {
    "plans": WORKSPACE_ROOT / "plans",
    "reports": WORKSPACE_ROOT / "reports",
    "screenshots": WORKSPACE_ROOT / "screenshots",
    "wrike_reports": WORKSPACE_ROOT / "wrike_reports",
}


def init_workspace():
    WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)
    for path in PATHS.values():
        path.mkdir(parents=True, exist_ok=True)
    return WORKSPACE_ROOT


def get_path(name: str) -> Path:
    path = PATHS.get(name, WORKSPACE_ROOT)
    return path.resolve()


def get_test_app_url() -> str:
    return TEST_APP_URL

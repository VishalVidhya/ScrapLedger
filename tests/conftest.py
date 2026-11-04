import os

os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"
os.environ["OFFLINE_EMBEDDINGS"] = "1"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.config import Settings, get_settings  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def client():
    app.dependency_overrides[get_settings] = lambda: Settings(
        app_name="ScrapLedger",
        environment="test",
    )
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

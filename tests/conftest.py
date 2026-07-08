# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from main import app  # 👈 引入你最外層的 app
from unittest.mock import MagicMock
from app.features.apps.dependencies import get_apps_service


@pytest.fixture
def client():
    """提供一個乾淨的 FastAPI TestClient"""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_apps_service():
    """建立一個乾淨的 mock service，並在測試結束後自動復原 overrides"""
    mock = MagicMock()
    app.dependency_overrides[get_apps_service] = lambda: mock
    yield mock  # 👈 這裡把 mock 借給測試案例
    app.dependency_overrides.clear()  # 👈 測試執行完，自動在這裡清理！

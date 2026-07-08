# tests/features/test_apps.py
import pytest
from unittest.mock import MagicMock
from fastapi import status

# 根據你實際的 import 路徑引入
from app.features.apps.dependencies import get_apps_service
from main import app

# 模擬一份符合 FactoryApp 模型的假資料
MOCK_APPS_DATA = [
    {
        "app_name": "App A",
        "package_name": "package A",
        "version_name": "1.0.1",
        "description": "App A",
        "icon_url": "A.png",
        "apk_url": "http://123.123.123.123/file/App_A.apk",
        "is_latest": True,
    },
    {
        "app_name": "App B",
        "package_name": "package B",
        "version_name": "1.0.2",
        "description": "App B",
        "icon_url": "B.png",
        "apk_url": "http://123.123.123.123/file/App_B.apk",
        "is_latest": False,
    },
]

MOCK_APPS_DATA2 = [
    {
        "app_name": "App A",
        "package_name": "package A",
        "version_name": "1.0.1",
        "description": "App A",
        "icon_url": "A.png",
        "apk_url": "http://123.123.123.123/file/App_A.apk",
        "is_latest": True,
    },
    {
        "app_name": "App B",
        "package_name": "package B",
        "version_name": "1.0.2",
        "description": "App B",
        "icon_url": "B.png",
        "apk_url": "http://123.123.123.123/file/App_B.apk",
        "is_latest": True,
    },
]


def test_get_factory_apps_success(client):
    """測試成功取得工廠 App 列表的情境"""
    # 1. 建立一個假的 AppsService 物件
    mock_service = MagicMock()
    # 讓它的 get_factory_apps_service 方法回傳我們的假資料
    mock_service.get_factory_apps_service.return_value = MOCK_APPS_DATA

    # 2. ⚡ 關鍵：將原本的 get_apps_service 依賴，替換成回傳假 Service 的函式
    app.dependency_overrides[get_apps_service] = lambda: mock_service

    try:
        # 3. 發送請求，並帶上自訂的 X-Forwarded-For Header
        headers = {"X-Forwarded-For": "203.0.113.195"}
        response = client.post("/api/store/apps", headers=headers)

        # 4. 斷言（Assert）結果
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        # 檢查回傳的數量是不是跟假資料一樣多
        assert len(response_data) == len(MOCK_APPS_DATA)

        # 精準檢查重要核心欄位，避免被 Pydantic 的欄位順序或自動轉型干擾
        assert response_data[0]["app_name"] == "App A"
        assert response_data[0]["is_latest"] is True

        assert response_data[1]["app_name"] == "App B"
        assert response_data[1]["is_latest"] is False

        # 驗證 Router 是不是真的有把解析出來的 IP 丟給 Service
        mock_service.get_factory_apps_service.assert_called_once_with(
            user_ip="203.0.113.195"
        )

    finally:
        # 5. 測試結束後，一定要清除覆蓋設定，避免影響到其他測試
        app.dependency_overrides.clear()


def test_get_factory_apps_server_error(client):
    """測試當 Service 發生未知異常時，Router 是否會正確安全地噴出 500"""
    mock_service = MagicMock()
    # 模擬 Service 執行時大崩潰（例如資料庫斷線、語法錯、或是任何 Exception）
    mock_service.get_factory_apps_service.side_effect = Exception("Database crash!")

    app.dependency_overrides[get_apps_service] = lambda: mock_service

    try:
        response = client.post("/api/store/apps")

        # 驗證是否被 try-except 攔截，並安全地轉成 500 狀態碼
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        # 驗證回傳的訊息是否為你設定的模糊安全文字
        assert response.json() == {"detail": "系統發生內部錯誤，請稍後再試或聯絡管理員。"}

    finally:
        app.dependency_overrides.clear()


def test_get_factory_apps_empty_data(client):
    """測試當資料庫查無版本紀錄時（empty），所有 App 的 is_latest 是否皆為 True"""
    # 1. 建立一個假的 AppsService 物件
    mock_service = MagicMock()
    # 讓它的 get_factory_apps_service 方法回傳我們的假資料
    mock_service.get_factory_apps_service.return_value = MOCK_APPS_DATA2

    # 2. ⚡ 關鍵：將原本的 get_apps_service 依賴，替換成回傳假 Service 的函式
    app.dependency_overrides[get_apps_service] = lambda: mock_service

    try:
        # 3. 發送請求，並帶上自訂的 X-Forwarded-For Header
        headers = {"X-Forwarded-For": "203.0.113.195"}
        response = client.post("/api/store/apps", headers=headers)

        # 4. 斷言（Assert）結果
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        # 檢查回傳的數量是不是跟假資料一樣多
        assert len(response_data) == len(MOCK_APPS_DATA2)

        # 精準檢查重要核心欄位，避免被 Pydantic 的欄位順序或自動轉型干擾

        assert response_data[0]["is_latest"] is True

        assert response_data[1]["is_latest"] is True

    finally:
        # 5. 測試結束後，一定要清除覆蓋設定，避免影響到其他測試
        app.dependency_overrides.clear()

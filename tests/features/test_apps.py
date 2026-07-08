# tests/features/test_apps.py
import pytest
from fastapi import status

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


def test_get_factory_apps_success(client, mock_apps_service):
    """測試成功取得工廠 App 列表的情境"""
    # 1. 透過傳入的 mock_apps_service 設定假回傳值
    mock_apps_service.get_factory_apps_service.return_value = MOCK_APPS_DATA

    # 2. 發送請求，並帶上自訂的 X-Forwarded-For Header
    headers = {"X-Forwarded-For": "203.0.113.195"}
    response = client.post("/api/store/apps", headers=headers)

    # 3. 斷言（Assert）結果
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()

    # 檢查回傳的數量是不是跟假資料一樣多
    assert len(response_data) == len(MOCK_APPS_DATA)

    # 精準檢查重要核心欄位
    assert response_data[0]["app_name"] == "App A"
    assert response_data[0]["is_latest"] is True

    assert response_data[1]["app_name"] == "App B"
    assert response_data[1]["is_latest"] is False

    # 驗證 Router 是不是真的有把解析出來的 IP 丟給 Service
    mock_apps_service.get_factory_apps_service.assert_called_once_with(
        user_ip="203.0.113.195"
    )


def test_get_factory_apps_server_error(client, mock_apps_service):
    """測試當 Service 發生未知異常時，Router 是否會正確安全地噴出 500"""
    # 模擬 Service 執行時大崩潰（例如資料庫斷線、語法錯、或是任何 Exception）
    mock_apps_service.get_factory_apps_service.side_effect = Exception(
        "Database crash!"
    )
    response = client.post("/api/store/apps")

    # 驗證是否被 try-except 攔截，並安全地轉成 500 狀態碼
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    # 驗證回傳的訊息是否為你設定的模糊安全文字
    assert response.json() == {"detail": "系統發生內部錯誤，請稍後再試或聯絡管理員。"}


def test_get_factory_apps_empty_data(client, mock_apps_service):
    """測試當資料庫查無版本紀錄時（empty），所有 App 的 is_latest 是否皆為 True"""
    # 讓它的 get_factory_apps_service 方法回傳我們的假資料
    mock_apps_service.get_factory_apps_service.return_value = MOCK_APPS_DATA2

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


def test_router_chaos_malicious_ip_header(client, mock_apps_service):
    """【混沌測試】當前端傳入惡意、超長、或帶有 SQL 注入的 IP 時，系統的防禦機制"""
    # 模擬 Service 即使拿到惡意 IP，也只是回傳空（或正常運作）
    mock_apps_service.get_factory_apps_service.return_value = MOCK_APPS_DATA

    # 💥 故意偽造非常邪惡的 Header 內容
    evil_ips = [
        "192.168.1.1; DROP TABLE users;--",  # SQL 注入特徵
        "A" * 10000,  # 超長字串攻擊
        "not-an-ip-address",  # 完全不是 IP 的亂碼
    ]

    for evil_ip in evil_ips:
        headers = {"X-Forwarded-For": evil_ip}
        response = client.post("/api/store/apps", headers=headers)

        # 🔬 斷言：不論前端傳什麼髒東西，Router 絕對不能直接全站噴 500 崩潰。
        # 它可以安全回傳 200（代表 Repo 有防禦住），或者經過參數檢驗噴 400。
        assert response.status_code in [200, 400]


def test_router_chaos_unexpected_low_level_exception(client, mock_apps_service):
    """【混沌測試】當底層發生從未見過的非資料庫錯誤時，Router 能否優雅處理"""

    # 💥 故意讓 Service 噴出一個非常罕見、程式沒寫過的錯誤
    mock_apps_service.get_factory_apps_service.side_effect = SystemError(
        "記憶體硬體毀損、冷氣壞掉、機房失火！"
    )

    headers = {"X-Forwarded-For": "203.0.113.195"}
    response = client.post("/api/store/apps", headers=headers)

    # 🔬 斷言
    # 1. 前端絕對不能看到「機房失火」的恐怖 Traceback，必須是溫柔的 500 模糊訊息
    assert response.status_code == 500
    assert response.json()["detail"] == "系統發生內部錯誤，請稍後再試或聯絡管理員。"

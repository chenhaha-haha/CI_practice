# tests/features/test_apps_service.py
import pytest
import pandas as pd
from unittest.mock import MagicMock

# 💡 請根據你實際的 import 路徑引入 AppsService
from app.features.apps.service import AppsService

# 為了方便測試，假設你的 APPS_CONFIG 裡面的內容長這樣：
# App A 的 col_name 是 col_A，version_name 是 "1.0.1"
# App B 的 col_name 是 col_B，version_name 是 "1.0.2"


def test_service_calculate_is_latest_correctly():
    """測試 Service 能夠根據 Repo 回傳的 DataFrame 正確計算出 is_latest"""

    # 1. 🛠️ 建立一個假的 Repo 物件
    mock_repo = MagicMock()

    # 2. 📊 模擬第一個情境：資料庫有資料，且 App A 版本對、App B 版本錯
    # 假設從資料庫 read 出來的 DataFrame 長這樣：
    mock_df = pd.DataFrame(
        [
            {
                "app_a_version": "2.7.6",  # 與配置相同 -> 預期 computed 後 is_latest 為 True
            },
            {
                "app_b_version": "2.4.0",  # 與配置相同 -> 預期 computed 後 is_latest 為 True
            },
        ]
    )
    mock_repo.get_apps_version_by.return_value = mock_df

    # 3. ⚙️ 實例化 Service，把假的 Repo 注入進去
    service = AppsService(mock_repo)

    # 4. 🏃 執行要測試的 Service 函式
    result = service.get_factory_apps_service(user_ip="192.168.1.1")

    # 5. 🔬 顯微鏡斷言：檢查商業邏輯計算結果
    # 驗證 Repo 確實有被呼叫，且參數正確
    mock_repo.get_apps_version_by.assert_called_once_with("192.168.1.1")

    # 驗證 Service 計算出來的 is_latest 是不是對的
    assert result[0]["app_name"] == "app_a"
    assert result[0]["is_latest"] is True  # 版本相同，必須是 True

    assert result[1]["app_name"] == "app_b"
    assert result[1]["is_latest"] is False  # 版本不同，必須是 False


def test_service_handle_empty_dataframe():
    """測試當 Repo 回傳空 DataFrame 時，Service 是否能觸發降級機制（全部為 True）"""

    mock_repo = MagicMock()

    # 📊 模擬第二個情境：資料庫查無此 IP 的紀錄，回傳空的 DataFrame
    mock_repo.get_apps_version_by.return_value = pd.DataFrame()

    service = AppsService(mock_repo)
    result = service.get_factory_apps_service(user_ip="203.0.113.1")

    # 🔬 顯微鏡斷言
    assert len(result) > 0
    # 根據你的邏輯：if apps_version.empty -> 全部都必須是 True
    for app_config in result:
        assert app_config["is_latest"] is True


def test_service_chaos_corrupted_dataframe_types():
    """【混沌測試】當 Repo 回傳的資料型態大亂（int, float, None），Service 是否能安全存活"""
    mock_repo = MagicMock()

    service = AppsService(mock_repo)

    # 💥 故意塞入各種奇怪的型態，看 Service 會不會大崩潰
    mock_df = pd.DataFrame(
        [
            {
                "col_A": 1,  # 數字 1 (你的 APPS_CONFIG 可能是字串 "1.0.1")
                "col_B": None,  # 空值
                "col_C": 1.02,  # 浮點數
            }
        ]
    )
    mock_repo.get_apps_version_by.return_value = mock_df
    service.tag_check_version_repo = mock_repo

    # 🏃 點火看它會不會噴 TypeError
    result = service.get_factory_apps_service(user_ip="192.168.1.1")

    # 🔬 斷言：我們預期它「絕對不能噴 500 錯誤」，即使型態不對，頂多是 is_latest 變成 False
    assert isinstance(result, list)
    assert result[0]["is_latest"] is False  # 字串 "1.0.1" != 數字 1，所以是 False，但不能死！

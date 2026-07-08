import sqlite3
import pandas as pd
from app.shared.utils.db_helper import read
from app.core.logging_config import get_feature_logger

logger = get_feature_logger("apps")


class AppsVersionRepo:
    def __init__(self, cursor: sqlite3.Cursor) -> None:
        self.cursor = cursor

    def get_apps_version_by(self, user_ip: str) -> pd.DataFrame:
        cols = ["app_a_version", "app_b_version"]
        cols_str = ", ".join(cols)
        params = None
        try:
            sql = f"""
                SELECT 
                {cols_str}    
                FROM apps_version
                WHERE user_ip = ?
            """
            params = (user_ip,)
            result = read(sql=sql, cursor=self.cursor, params=params)
            return result
        except Exception as exc:
            # ⚡ 加上 params={params}， debug 時可以直接把 SQL 複製出來去資料庫測試
            logger.error(
                f"❌ Repo 執行 get_apps_version_by 失敗 | 參數: {params} | 原因: {exc}",
                exc_info=True,
            )
            raise exc

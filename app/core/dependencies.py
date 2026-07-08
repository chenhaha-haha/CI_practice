from typing import Generator
from ..shared.database.sqlite_db import connect_sqlite
from ..core.logging_config import get_feature_logger


class SQLITEDependency:
    def __init__(self, db: str, feature_name: str):
        """初始化時決定要連哪一個資料庫"""
        self.db = db
        self.logger = get_feature_logger(feature_name)

    def __call__(self) -> Generator:
        """當 FastAPI 執行 Depends 時，會自動呼叫這個 __call__ 函式"""
        try:
            with connect_sqlite(self.db) as cursor:
                yield cursor
        except Exception as exc:
            raise exc

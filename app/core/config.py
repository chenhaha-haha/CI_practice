# 1. 👈 改從 pydantic_settings 引入 BaseSettings 與 SettingsConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "db"


class Settings(BaseSettings):
    ENV: str  # 👈 新增這行 (值會是 "development" 或 "production")
    APP_A_LATEST_VERSION: str
    APP_B_LATEST_VERSION: str
    HOST: str
    PORT: int  # 👈 這裡宣告成 int，Pydantic 讀取 .env 時會自動幫你轉成數字！
    SQLITE_PHONE_DB: str = "phone.db"

    # 3. 👈 Pydantic V2 改用 model_config 取代舊的 class Config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",  # 💡 加上這行防 Windows 讀取中文亂碼
        extra="ignore",  # 選擇性加上：如果 .env 有其他變數，多出來的會自動忽略不報錯
    )

    # 💡 額外提供一個屬性，自動組合成絕對路徑
    @property
    def sqlite_absolute_path(self) -> str:
        db_path = Path(self.SQLITE_PHONE_DB)

        # 如果是絕對路徑就直接返回，如果是相對路徑就與 BASE_DIR 拼接
        if db_path.is_absolute():
            return str(db_path)
        return str(BASE_DIR / db_path)


# 實例化
settings = Settings()

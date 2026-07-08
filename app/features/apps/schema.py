from pydantic import BaseModel


class FactoryApp(BaseModel):
    app_name: str  # App 名稱 (e.g., "鋼捲倉儲管理")
    package_name: str  # Android 包名 (e.g., "com.factory.storage")
    version_name: str  # 版本號 (e.g., "v1.0.0")
    description: str  # 簡介
    icon_url: str  # Icon 圖片網址
    apk_url: str  # APK 下載網址
    is_latest: bool

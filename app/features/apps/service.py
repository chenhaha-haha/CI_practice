from .apps_version_repo import AppsVersionRepo
from app.core.config import settings
from app.core.logging_config import get_feature_logger

logger = get_feature_logger("apps")

APPS_CONFIG: list = [
    {
        "col_name": "app_a_version",
        "app_name": "app_a",
        "package_name": "com.example.app_a",
        "version_name": settings.APP_A_LATEST_VERSION,
        "description": "app a",
        "icon_url": "http://192.168.1.50/static/icons/inspection.png",
        "apk_url": "http://192.168.1.50/file/app_a.apk",
    },
    {
        "col_name": "app_b_version",
        "app_name": "app_b",
        "package_name": "com.example.app_b",
        "version_name": settings.APP_B_LATEST_VERSION,
        "description": "app b",
        "icon_url": "http://192.168.1.50/static/icons/inspection.png",
        "apk_url": "http://192.168.1.50/file/app_b.apk",
    },
]


class AppsService:
    def __init__(self, tag_chek_version_repo: AppsVersionRepo) -> None:
        self.tag_check_version_repo = tag_chek_version_repo

    def get_factory_apps_service(self, user_ip: str) -> list:
        apps_version = self.tag_check_version_repo.get_apps_version_by(user_ip)
        if apps_version.empty:
            return [{**config, "is_latest": True} for config in APPS_CONFIG]

        app_config_bak = []
        for config in APPS_CONFIG:
            new_config = config.copy()

            # ⚡ 預防性保護：萬一 DB 撈出的欄位真的少了某個 col_name，這裡可以優雅處理，而不是直接全站崩潰
            col_name = new_config["col_name"]
            if col_name not in apps_version.columns:
                logger.warning(
                    f"⚠️ IP {user_ip} 的資料中，DB 缺少配置的欄位: {col_name}，預設給予 False"
                )
                new_config["is_latest"] = False
            else:
                new_config["is_latest"] = (
                    new_config["version_name"] == apps_version[col_name].iloc[0]
                )

            app_config_bak.append(new_config)
        return app_config_bak

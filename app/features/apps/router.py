from fastapi import HTTPException, Request, APIRouter, Depends, status
from typing import List
from .schema import FactoryApp
from .service import AppsService
from .dependencies import get_apps_service
from app.core.logging_config import get_feature_logger

logger = get_feature_logger("apps")

apps = APIRouter()


@apps.post("/api/store/apps", response_model=List[FactoryApp])
def get_factory_apps(
    request: Request, apps_service: AppsService = Depends(get_apps_service)
) -> list:
    user_ip = request.headers.get("X-Forwarded-For") or (
        request.client.host if request.client else "127.0.0.1"
    )
    try:
        result = apps_service.get_factory_apps_service(user_ip=user_ip)
        return result
    except Exception as exc:
        # ⚡ 關鍵：在 raise 500 之前，把 request 的關鍵資訊與 exc 記錄下來！
        logger.error(
            f"❌ API /api/store/apps 發生未預期崩潰 | User IP: {user_ip} | 原因: {exc}",
            exc_info=True,  # 這行會自動把完整的 Traceback（哪一行錯）印出來
        )
        # 2. 回傳給前端一個乾淨、模糊化的錯誤訊息
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="系統發生內部錯誤，請稍後再試或聯絡管理員。",
        )

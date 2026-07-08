from app.core.dependencies import SQLITEDependency
from app.core.config import settings
from fastapi import Depends
from .apps_version_repo import AppsVersionRepo
from .service import AppsService

get_db_cursor = SQLITEDependency(db=settings.sqlite_absolute_path, feature_name="apps")


def get_tag_check_version_repo(
    cursor=Depends(get_db_cursor),
) -> AppsVersionRepo:
    return AppsVersionRepo(cursor=cursor)


def get_apps_service(
    tag_check_version_repo: AppsVersionRepo = Depends(get_tag_check_version_repo),
) -> AppsService:
    return AppsService(tag_chek_version_repo=tag_check_version_repo)

from fastapi import FastAPI
from app.features.apps.router import apps
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.core.config import settings
import multiprocessing
from contextlib import asynccontextmanager
from app.shared.database.sqlite_db import init_db


# 1. 定義 Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ---- 【Startup 階段】應用程式啟動時執行 ----
    # 在這裡執行你的 SQLite 初始化
    init_db()
    print("sqlite 初始化完成")

    yield  # 🚀 程式會在這裡暫停，開始接收前端的 HTTP Requests

    # ---- 【Shutdown 階段】應用程式關閉時執行 ----
    # 如果有需要關閉全域連線（如 Redis client），寫在這裡
    print("🛑 應用程式正在關閉，清理資源中...")


app = FastAPI(lifespan=lifespan)

# 允許 Vue 前端跨網域存取 (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(apps, tags=["apps"])

if __name__ == "__main__":
    # 1. 根據環境變數，決定啟動的配置
    if settings.ENV == "production":
        # 正式環境設定
        is_reload = False
        # 自動計算 Workers 數量：CPU 核心數 * 2 + 1 (例如 2 核伺服器就開 5 個 worker)
        worker_count = (multiprocessing.cpu_count() * 2) + 1
        print(f"🚨 [PROD 模式] 啟動中... 關閉 reload，開啟 {worker_count} 個 Workers")
    else:
        # 開發環境設定 (預設或 development)
        is_reload = True
        worker_count = None  # 👈 注意：uvicorn 開啟 reload 時，workers 必須為 None 或 1，否則會衝突
        print("🛠️  [DEV 模式] 啟動中... 已開啟自動重載 (reload=True)")

    # 2. 帶入動態變數
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=is_reload,  # 👈 動態切換
        workers=worker_count,  # 👈 動態切換
    )

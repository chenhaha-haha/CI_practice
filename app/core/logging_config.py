import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

# 全域的已初始化暫存，避免重複綁定 Handler 導致 Log 重複印出
_initialized_loggers = set()


def get_feature_logger(feature_name: str) -> logging.Logger:
    """動態取得並設定特定 Feature 的 Logger"""
    logger = logging.getLogger(feature_name)

    # 如果這個 feature 已經設定過 handler 了，直接回傳，不要重複綁定
    if feature_name in _initialized_loggers:
        return logger

    # 1. 使用 pathlib 設定路徑
    log_dir = Path.cwd() / "data" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = log_dir / f"{feature_name}.log"  # 👈 動態命名檔名

    # 2. 設定等級與阻斷向上傳遞
    logger.setLevel(logging.ERROR)
    logger.propagate = False

    # 3. 建立每日切換的 Handler
    date_file_handler = TimedRotatingFileHandler(
        filename=str(log_file_path),
        when="MIDNIGHT",
        interval=1,
        backupCount=30,
        encoding="utf-8",
    )
    date_file_handler.suffix = "%Y-%m-%d"

    # 4. 設定格式
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
    )
    date_file_handler.setFormatter(formatter)

    # 5. 綁定並記錄
    logger.addHandler(date_file_handler)
    _initialized_loggers.add(feature_name)

    return logger

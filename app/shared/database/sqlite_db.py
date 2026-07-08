import sqlite3
from contextlib import contextmanager
from typing import Generator
from app.core.config import settings


@contextmanager
def connect_sqlite(db: str) -> Generator:
    conn = None
    cursor = None
    try:
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        yield cursor
    except Exception as exc:
        if conn:
            conn.rollback()
        raise exc
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def init_db() -> None:
    with connect_sqlite(settings.sqlite_absolute_path) as cursor:
        # 員工分機表紀錄檔
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS apps_version (
                user_ip TEXT PRIMARY KEY,
                app_a_version TEXT,
                app_b_version TEXT
            )
        """
        )
        cursor.connection.commit()

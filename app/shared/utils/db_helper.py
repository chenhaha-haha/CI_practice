import pandas as pd
from typing import Any


def read(
    sql: str, cursor: Any, params: tuple[Any] | dict[str, Any] = None
) -> pd.DataFrame:
    if params is None:
        cursor.execute(sql)
    else:
        cursor.execute(sql, params)

    result = cursor.fetchall()
    result = [tuple(r) for r in result]
    return pd.DataFrame(result, columns=[desc[0] for desc in cursor.description])

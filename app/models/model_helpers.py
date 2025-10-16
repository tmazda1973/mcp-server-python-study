"""
モデルに関する処理を提供するヘルパー関数
"""

from typing import Any, Dict, List, Type, Union, cast

from sqlalchemy import and_, func, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.orm import Session

from .base_model import BaseModel

__all__ = [
    "soft_delete",
]


def soft_delete(
    db_session: Session,
    *,
    model_clazz: Type[BaseModel],
    conditions: Union[Any, List[Any], Dict[str, Any]],
) -> int:
    """
    指定されたモデルの論理削除を行います。

    :param db_session: DBセッション
    :param model_clazz: モデルクラス
    :param conditions: WHERE条件
    :return: None
    """

    table = model_clazz.__table__
    query = update(model_clazz).where(table.c.deleted_at.is_(None))

    if isinstance(conditions, dict):
        # 辞書形式の条件
        for column, value in conditions.items():
            if column in table.c:  # カラムの存在確認も可能
                query = query.where(table.c[column] == value)  # type: ignore

    elif isinstance(conditions, (list, tuple)):
        # リストまたはタプル形式の条件
        query = query.where(and_(*conditions))  # type: ignore
    else:
        # 単一条件
        query = query.where(conditions)  # type: ignore

    # 削除日時を設定する
    query = query.values(deleted_at=func.now())

    result = db_session.execute(query)
    return cast(int, cast(CursorResult, result).rowcount)

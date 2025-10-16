import re
from typing import Any

from sqlalchemy import TIMESTAMP, Column, DateTime, Integer, event, func, null
from sqlalchemy.orm import (
    DeclarativeBase,
    ORMExecuteState,
    Session,
    declarative_mixin,
    declared_attr,
    with_loader_criteria,
)

__all__ = [
    "BaseModel",
    "SoftDeleteMixin",
]


@declarative_mixin
class SoftDeleteMixin:
    """
    論理削除ミックスイン

    :var deleted_at: datetime | None: 削除日時
    """

    deleted_at = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        index=True,
        server_default=None,
    )

    def soft_delete(self) -> None:
        """
        データを論理削除します。

        :return: None
        """
        self.deleted_at = func.now()

    def restore(self) -> None:
        """
        論理削除を解除します。

        :return: None
        """
        self.deleted_at = None

    @property
    def is_deleted(self) -> bool:
        """削除済みかどうかを判定"""
        return self.deleted_at is not None

    @property
    def is_not_deleted(self) -> bool:
        """削除されていないかどうかを判定"""
        return self.deleted_at is None


class BaseModel(DeclarativeBase, SoftDeleteMixin):
    """
    全モデルで共有するベースクラス

    共通機能:
    - 自動的なテーブル名生成
    - 共通フィールド（id, created_at, updated_at）
    - 論理削除機能（SoftDeleteMixin継承）
    - 便利メソッド（to_dict, __repr__）
    """

    @declared_attr
    def __tablename__(cls) -> str:
        """
        テーブル名

        - クラス名からテーブル名を自動生成する
        """
        # CamelCaseをsnake_caseに変換する
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", cls.__name__)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    # Legacy annotationsの警告を回避する
    __allow_unmapped__ = True

    # 全テーブル共通フィールド
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        attrs = []
        # 主要なフィールドを表示
        if hasattr(self, "id") and self.id:
            attrs.append(f"id={self.id}")

        # モデル固有の重要フィールドを表示
        key_fields = self._get_key_fields()
        for field in key_fields:
            if hasattr(self, field):
                value = getattr(self, field)
                if isinstance(value, str):
                    attrs.append(f"{field}='{value}'")
                else:
                    attrs.append(f"{field}={value}")

        attrs_str = ", ".join(attrs)
        return f"<{class_name}({attrs_str})>"

    def _get_key_fields(self) -> list[str]:
        """
        重要フィールドを取得する

        - 各モデルでオーバーライドして重要フィールドを指定する
        """
        return []


# 自動的な論理削除フィルタ
@event.listens_for(Session, "do_orm_execute")
def _add_filtering_deleted_at(
    execute_state: ORMExecuteState,
) -> None:
    """
    論理削除用のフィルタを自動的に適用します。

    - 以下のようにすると、論理削除済のデータも含めて取得可能

    query(...).filter(...).execution_options(include_deleted=True)

    :param execute_state: SQLステートメント
    """

    if (
        execute_state.is_select
        and not execute_state.is_column_load
        and not execute_state.is_relationship_load
        and not execute_state.execution_options.get("include_deleted", False)
    ):
        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(
                SoftDeleteMixin,
                lambda cls: cls.deleted_at == null(),
                include_aliases=True,
            )
        )

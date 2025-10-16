from abc import abstractmethod
from typing import Any, Protocol, runtime_checkable

from app.api.domain.entities.mcp.data_processing import (
    DataValidateResultEntity,
)

__all__ = [
    "DataValidateRepositoryProtocol",
]


@runtime_checkable
class DataValidateRepositoryProtocol(Protocol):
    """
    リポジトリプロトコル（データ検証ツール）
    """

    @abstractmethod
    async def validate_data(
        self,
        data: str,
        schema_type: str,
        schema_definition: str,
        validation_mode: str,
        max_errors: int,
        include_warnings: bool,
        custom_rules: dict[str, Any] | None,
    ) -> DataValidateResultEntity:
        """
        データ検証を実行する

        Args:
            data: 検証対象のデータ（JSON文字列）
            schema_type: スキーマタイプ
            schema_definition: スキーマ定義
            validation_mode: 検証モード
            max_errors: 最大エラー数
            include_warnings: 警告を含めるか
            custom_rules: カスタム検証ルール

        Returns:
            検証結果エンティティ
        """
        ...

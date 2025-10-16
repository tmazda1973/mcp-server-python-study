from abc import abstractmethod
from typing import Any, Protocol, runtime_checkable

from app.api.domain.entities.mcp.data_processing import (
    DataAggregateResultEntity,
)

__all__ = [
    "DataAggregateRepositoryProtocol",
]


@runtime_checkable
class DataAggregateRepositoryProtocol(Protocol):
    """
    リポジトリプロトコル（データ集計ツール）
    """

    @abstractmethod
    async def aggregate_data(
        self,
        data: str,
        group_by: list[str],
        aggregate_functions: dict[str, str],
        filter_conditions: dict[str, Any] | None,
        sort_by: list[dict[str, str]],
        limit: int,
        include_totals: bool,
        include_metadata: bool,
        output_format: str,
    ) -> DataAggregateResultEntity:
        """
        データ集計を実行する

        Args:
            data: 集計対象のデータ（JSON配列形式）
            group_by: グループ化するフィールド名のリスト
            aggregate_functions: 集計関数の定義（フィールド名: 関数名）
            filter_conditions: フィルター条件
            sort_by: ソート条件
            limit: 結果の最大行数
            include_totals: 合計行を含めるか
            include_metadata: メタデータを含めるか
            output_format: 出力形式

        Returns:
            集計結果エンティティ
        """
        ...

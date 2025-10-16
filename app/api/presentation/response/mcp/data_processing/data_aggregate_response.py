from typing import Any

from pydantic import BaseModel, Field

from .schemas.aggregate_group_result import AggregateGroupResult
from .schemas.aggregate_statistics import AggregateStatistics

__all__ = [
    "DataAggregateResponse",
]


class DataAggregateResponse(BaseModel):
    """
    レスポンスデータ（データ集計ツール）
    """

    success: bool = Field(..., description="集計処理の成功可否")
    output_format: str = Field(..., description="出力形式")

    # 集計結果
    results: list[AggregateGroupResult] = Field(
        default_factory=list,
        description="集計結果",
    )
    totals: dict[str, Any] = Field(default_factory=dict, description="総計")

    # 統計情報
    statistics: AggregateStatistics = Field(..., description="集計統計")

    # メタデータ
    group_by_fields: list[str] = Field(
        default_factory=list, description="グループ化フィールド"
    )
    aggregate_functions_used: dict[str, str] = Field(
        default_factory=dict, description="使用された集計関数"
    )
    sort_applied: list[dict[str, str]] = Field(
        default_factory=list, description="適用されたソート"
    )

    # パフォーマンス情報
    processing_time: float = Field(..., description="処理時間（秒）")
    memory_usage: float | None = Field(None, description="メモリ使用量（MB）")

    # 追加情報
    warnings: list[str] = Field(default_factory=list, description="警告メッセージ")
    recommendations: list[str] = Field(default_factory=list, description="改善推奨事項")

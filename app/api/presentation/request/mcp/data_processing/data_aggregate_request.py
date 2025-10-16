from typing import Any

from pydantic import BaseModel, Field

__all__ = [
    "DataAggregateRequest",
]


class DataAggregateRequest(BaseModel):
    """
    リクエストデータ（データ集計ツール）
    """

    data: str = Field(
        ...,
        max_length=1_048_576,  # 1MB制限
        description="集計対象のデータ（JSON配列形式）",
    )

    group_by: list[str] = Field(
        default_factory=list,
        description="グループ化するフィールド名のリスト",
    )

    aggregate_functions: dict[str, str] = Field(
        ...,
        description="集計関数の定義（フィールド名: 関数名）",
    )

    filter_conditions: dict[str, Any] | None = Field(
        default=None,
        description="フィルター条件",
    )

    sort_by: list[dict[str, str]] = Field(
        default_factory=list,
        description="ソート条件（[{field: フィールド名, order: asc/desc}]）",
    )

    limit: int = Field(
        default=1000,
        ge=1,
        le=10000,
        description="結果の最大行数",
    )

    include_totals: bool = Field(
        default=True,
        description="合計行を含めるか",
    )

    include_metadata: bool = Field(
        default=True,
        description="メタデータを含めるか",
    )

    output_format: str = Field(
        default="detailed",
        pattern=r"^(detailed|summary|pivot)$",
        description="出力形式（detailed/summary/pivot）",
    )

    api_key: str | None = Field(default=None, description="API Key")

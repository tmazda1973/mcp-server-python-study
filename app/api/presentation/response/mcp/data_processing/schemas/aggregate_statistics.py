from pydantic import BaseModel, Field

__all__ = [
    "AggregateStatistics",
]


class AggregateStatistics(BaseModel):
    """
    集計統計情報
    """

    total_records: int = Field(..., description="総レコード数")
    processed_records: int = Field(..., description="処理済みレコード数")
    filtered_records: int = Field(..., description="フィルター後レコード数")
    groups_count: int = Field(..., description="グループ数")
    unique_values: dict[str, int] = Field(
        default_factory=dict, description="各フィールドのユニーク値数"
    )

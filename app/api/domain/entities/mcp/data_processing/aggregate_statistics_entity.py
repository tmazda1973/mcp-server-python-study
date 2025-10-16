from pydantic import BaseModel, Field

__all__ = [
    "AggregateStatisticsEntity",
]


class AggregateStatisticsEntity(BaseModel):
    """
    集計統計エンティティ
    """

    total_records: int
    processed_records: int
    filtered_records: int
    groups_count: int
    unique_values: dict[str, int] = Field(default_factory=dict)

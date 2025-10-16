from typing import Any

from pydantic import BaseModel, Field

__all__ = [
    "AggregateGroupResultEntity",
]


class AggregateGroupResultEntity(BaseModel):
    """
    集計グループ結果エンティティ
    """

    group_key: dict[str, Any] = Field(default_factory=dict)
    aggregated_values: dict[str, Any] = Field(default_factory=dict)
    record_count: int

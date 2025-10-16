"""
集計グループ結果
"""

from typing import Any

from pydantic import BaseModel, Field

__all__ = [
    "AggregateGroupResult",
]


class AggregateGroupResult(BaseModel):
    """
    集計グループ結果
    """

    group_key: dict[str, Any] = Field(
        default_factory=dict,
        description="グループキー",
    )
    aggregated_values: dict[str, Any] = Field(
        default_factory=dict,
        description="集計値",
    )
    record_count: int = Field(
        ...,
        description="グループ内レコード数",
    )

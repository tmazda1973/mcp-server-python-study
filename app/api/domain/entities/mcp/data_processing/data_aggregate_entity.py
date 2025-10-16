from typing import Any

from pydantic import BaseModel, Field

from .aggregate_group_result_entity import AggregateGroupResultEntity
from .aggregate_statistics_entity import AggregateStatisticsEntity

__all__ = [
    "DataAggregateResultEntity",
]


class DataAggregateResultEntity(BaseModel):
    """
    データ集計結果エンティティ
    """

    success: bool
    output_format: str

    results: list[AggregateGroupResultEntity] = Field(default_factory=list)
    totals: dict[str, Any] = Field(default_factory=dict)

    statistics: AggregateStatisticsEntity

    group_by_fields: list[str] = Field(default_factory=list)
    aggregate_functions_used: dict[str, str] = Field(default_factory=dict)
    sort_applied: list[dict[str, str]] = Field(default_factory=list)

    processing_time: float
    memory_usage: float | None = None

    warnings: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)

from dataclasses import dataclass
from typing import Dict, List, Optional

__all__ = [
    "DataTransformResultEntity",
]


@dataclass(frozen=True)
class DataTransformResultEntity:
    """
    ドメインエンティティ（データ変換結果）
    """

    success: bool
    transformed_data: str
    from_format: str
    to_format: str
    record_count: int
    field_count: int
    processing_time: float
    applied_mappings: Optional[Dict[str, str]] = None
    warnings: Optional[List[str]] = None
    error: Optional[str] = None

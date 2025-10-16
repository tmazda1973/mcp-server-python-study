from typing import Dict, List, Optional

from pydantic import BaseModel, Field

__all__ = [
    "DataTransformResponse",
]


class DataTransformResponse(BaseModel):
    """
    レスポンスデータ（データ変換ツール）
    """

    success: bool = Field(
        ...,
        description="変換成功",
    )
    transformed_data: str = Field(
        ...,
        description="変換後のデータ",
    )
    from_format: str = Field(
        ...,
        description="変換元フォーマット",
    )
    to_format: str = Field(
        ...,
        description="変換先フォーマット",
    )
    record_count: int = Field(
        ...,
        description="処理されたレコード数",
    )
    field_count: int = Field(
        ...,
        description="フィールド数",
    )
    processing_time: float = Field(
        ...,
        description="処理時間（秒）",
    )
    applied_mappings: Optional[Dict[str, str]] = Field(
        default=None,
        description="適用されたフィールドマッピング",
    )
    warnings: Optional[List[str]] = Field(
        default=None,
        description="警告メッセージ",
    )
    error: Optional[str] = Field(
        default=None,
        description="エラーメッセージ",
    )

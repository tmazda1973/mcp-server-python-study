from typing import Any

from pydantic import BaseModel, Field

from .schemas.validation_error import ValidationError
from .schemas.validation_summary import ValidationSummary
from .schemas.validation_warning import ValidationWarning

__all__ = [
    "DataValidateResponse",
]


class DataValidateResponse(BaseModel):
    """
    レスポンスデータ（データ検証ツール）
    """

    success: bool = Field(..., description="検証処理の成功可否")
    is_valid: bool = Field(..., description="データが有効かどうか")
    schema_type: str = Field(..., description="使用されたスキーマタイプ")
    validation_mode: str = Field(..., description="検証モード")

    summary: ValidationSummary = Field(..., description="検証サマリー")
    errors: list[ValidationError] = Field(
        default_factory=list, description="検証エラー一覧"
    )
    warnings: list[ValidationWarning] = Field(
        default_factory=list, description="検証警告一覧"
    )

    validated_data: dict[str, Any] | None = Field(
        None, description="検証済みデータ（lenientモード時）"
    )
    processing_time: float = Field(..., description="処理時間（秒）")

    # 追加情報
    schema_info: dict[str, Any] | None = Field(None, description="スキーマ情報")
    recommendations: list[str] = Field(default_factory=list, description="改善推奨事項")

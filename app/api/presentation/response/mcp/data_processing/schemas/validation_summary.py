from pydantic import BaseModel, Field

__all__ = [
    "ValidationSummary",
]


class ValidationSummary(BaseModel):
    """
    検証サマリー
    """

    total_fields: int = Field(..., description="総フィールド数")
    valid_fields: int = Field(..., description="有効フィールド数")
    invalid_fields: int = Field(..., description="無効フィールド数")
    error_count: int = Field(..., description="エラー総数")
    warning_count: int = Field(..., description="警告総数")
    validation_rate: float = Field(..., description="検証成功率（%）")

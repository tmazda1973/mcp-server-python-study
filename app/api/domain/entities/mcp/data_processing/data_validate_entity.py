from typing import Any

from pydantic import BaseModel, Field

__all__ = [
    "ValidationErrorEntity",
    "ValidationWarningEntity",
    "ValidationSummaryEntity",
    "DataValidateResultEntity",
]


class ValidationErrorEntity(BaseModel):
    """
    検証エラーエンティティ
    """

    field: str
    message: str
    error_type: str
    invalid_value: Any = None
    expected_type: str | None = None
    location: list[str | int] = Field(default_factory=list)


class ValidationWarningEntity(BaseModel):
    """
    検証警告エンティティ
    """

    field: str
    message: str
    warning_type: str
    current_value: Any = None
    suggestion: str | None = None


class ValidationSummaryEntity(BaseModel):
    """
    検証サマリーエンティティ
    """

    total_fields: int
    valid_fields: int
    invalid_fields: int
    error_count: int
    warning_count: int
    validation_rate: float


class DataValidateResultEntity(BaseModel):
    """
    データ検証結果エンティティ
    """

    success: bool
    is_valid: bool
    schema_type: str
    validation_mode: str

    summary: ValidationSummaryEntity
    errors: list[ValidationErrorEntity] = Field(default_factory=list)
    warnings: list[ValidationWarningEntity] = Field(default_factory=list)

    validated_data: dict[str, Any] | None = None
    processing_time: float

    schema_info: dict[str, Any] | None = None
    recommendations: list[str] = Field(default_factory=list)

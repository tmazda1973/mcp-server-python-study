from typing import Any

from pydantic import BaseModel, Field

__all__ = [
    "ValidationError",
]


class ValidationError(BaseModel):
    """
    検証エラー情報
    """

    field: str = Field(..., description="エラーが発生したフィールド")
    message: str = Field(..., description="エラーメッセージ")
    error_type: str = Field(..., description="エラータイプ")
    invalid_value: Any = Field(None, description="無効な値")
    expected_type: str | None = Field(None, description="期待される型")
    location: list[str | int] = Field(default_factory=list, description="エラー位置")

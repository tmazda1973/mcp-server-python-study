from typing import Any

from pydantic import BaseModel, Field

__all__ = [
    "ValidationWarning",
]


class ValidationWarning(BaseModel):
    """
    検証警告情報
    """

    field: str = Field(..., description="警告が発生したフィールド")
    message: str = Field(..., description="警告メッセージ")
    warning_type: str = Field(..., description="警告タイプ")
    current_value: Any = Field(None, description="現在の値")
    suggestion: str | None = Field(None, description="改善提案")

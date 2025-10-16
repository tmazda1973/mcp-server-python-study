"""
統一エラーレスポンススキーマ

全てのエラーレスポンスで使用する統一されたスキーマを定義します。
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "ErrorDetail",
    "ErrorResponse",
]


class ErrorDetail(BaseModel):
    """
    エラー詳細情報
    """

    field: str | None = Field(default=None, description="エラーが発生したフィールド名")
    message: str = Field(..., description="エラーメッセージ")
    type: str | None = Field(default=None, description="エラータイプ")


class ErrorResponse(BaseModel):
    """
    統一エラーレスポンス

    - 全てのエラーレスポンスはこの形式で返されます。
    """

    success: bool = Field(default=False, description="処理成功フラグ（常にfalse）")
    error_code: str = Field(..., description="エラーコード")
    message: str = Field(..., description="エラーメッセージ")
    details: dict[str, Any] | None = Field(
        default=None, description="追加のエラー詳細情報"
    )
    errors: list[ErrorDetail] | None = Field(
        default=None, description="個別のエラー詳細リスト（バリデーションエラー等）"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="エラー発生時刻（ISO 8601形式）",
    )
    path: str | None = Field(default=None, description="リクエストパス")
    request_id: str | None = Field(default=None, description="リクエストID")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": False,
                "error_code": "ValidationException",
                "message": "入力値が不正です",
                "details": {"field": "email", "reason": "Invalid email format"},
                "errors": [
                    {
                        "field": "email",
                        "message": "有効なメールアドレスを入力してください",
                        "type": "value_error.email",
                    }
                ],
                "timestamp": "2025-01-01T12:00:00.000000",
                "path": "/api/v1/users",
                "request_id": "req-123456",
            }
        }
    )

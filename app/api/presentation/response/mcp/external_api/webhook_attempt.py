from typing import Optional

from pydantic import BaseModel, Field

__all__ = [
    "WebhookAttempt",
]


class WebhookAttempt(BaseModel):
    """
    Webhook送信試行情報
    """

    attempt: int = Field(..., description="試行回数")
    status_code: int = Field(..., description="HTTPステータスコード")
    response_time: float = Field(..., description="レスポンス時間（秒）")
    success: bool = Field(..., description="送信成功")
    error: Optional[str] = Field(default=None, description="エラーメッセージ")

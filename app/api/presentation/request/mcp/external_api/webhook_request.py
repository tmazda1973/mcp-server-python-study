from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field, HttpUrl

__all__ = [
    "WebhookRequest",
]


class WebhookRequest(BaseModel):
    """
    リクエストデータ（Webhook送信ツール）
    """

    webhook_url: HttpUrl = Field(..., description="WebhookのURL")
    payload: Dict[str, Any] = Field(..., description="送信するペイロード")
    method: Literal["POST", "PUT"] = Field(default="POST", description="HTTPメソッド")
    content_type: Literal["application/json", "application/x-www-form-urlencoded"] = (
        Field(default="application/json", description="Content-Type")
    )
    headers: Optional[Dict[str, str]] = Field(default=None, description="追加ヘッダー")
    secret: Optional[str] = Field(default=None, description="Webhook署名用シークレット")
    signature_header: str = Field(
        default="X-Hub-Signature-256", description="署名ヘッダー名"
    )
    timeout: int = Field(default=30, ge=1, le=300, description="タイムアウト（秒）")
    retry_count: int = Field(default=0, ge=0, le=5, description="リトライ回数")
    retry_delay: int = Field(default=1, ge=1, le=60, description="リトライ間隔（秒）")

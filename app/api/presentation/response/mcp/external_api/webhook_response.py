from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .webhook_attempt import WebhookAttempt

__all__ = [
    "WebhookResponse",
]


class WebhookResponse(BaseModel):
    """
    レスポンスデータ（Webhook送信ツール）
    """

    success: bool = Field(..., description="Webhook送信成功")
    webhook_url: str = Field(..., description="WebhookのURL")
    method: str = Field(..., description="HTTPメソッド")
    payload_size: int = Field(..., description="ペイロードサイズ（バイト）")
    final_status_code: int = Field(..., description="最終HTTPステータスコード")
    total_attempts: int = Field(..., description="総試行回数")
    total_time: float = Field(..., description="総実行時間（秒）")
    attempts: List[WebhookAttempt] = Field(..., description="送信試行履歴")
    response_data: Optional[Dict[str, Any]] = Field(
        default=None, description="最終レスポンスデータ"
    )
    response_text: str = Field(..., description="最終レスポンステキスト")
    headers_sent: Dict[str, str] = Field(..., description="送信したヘッダー")
    signature_used: bool = Field(..., description="署名を使用したか")
    error: Optional[str] = Field(default=None, description="エラーメッセージ")
    warning: Optional[str] = Field(default=None, description="警告メッセージ")

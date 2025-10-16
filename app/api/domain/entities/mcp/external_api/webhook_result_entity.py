from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .webhook_attempt_entity import WebhookAttemptEntity

__all__ = [
    "WebhookResultEntity",
]


@dataclass(frozen=True)
class WebhookResultEntity:
    """
    ドメインエンティティ（Webhook送信結果）
    """

    success: bool
    webhook_url: str
    method: str
    payload_size: int
    final_status_code: int
    total_attempts: int
    total_time: float
    attempts: List[WebhookAttemptEntity]
    response_data: Optional[Dict[str, Any]]
    response_text: str
    headers_sent: Dict[str, str]
    signature_used: bool
    error: Optional[str] = None
    warning: Optional[str] = None

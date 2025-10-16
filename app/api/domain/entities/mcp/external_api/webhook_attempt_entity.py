from dataclasses import dataclass
from typing import Optional

__all__ = [
    "WebhookAttemptEntity",
]


@dataclass(frozen=True)
class WebhookAttemptEntity:
    """
    ドメインエンティティ（Webhook送信試行）
    """

    attempt: int
    status_code: int
    response_time: float
    success: bool
    error: Optional[str] = None

from typing import Any, Dict, Literal, Optional, Protocol, runtime_checkable

from app.api.domain.entities.mcp.external_api import WebhookResultEntity

__all__ = [
    "WebhookRepositoryProtocol",
]


@runtime_checkable
class WebhookRepositoryProtocol(Protocol):
    """
    リポジトリプロトコル（Webhook送信ツール）
    """

    async def send_webhook(
        self,
        webhook_url: str,
        payload: Dict[str, Any],
        method: Literal["POST", "PUT"] = "POST",
        content_type: Literal[
            "application/json",
            "application/x-www-form-urlencoded",
        ] = "application/json",
        headers: Optional[Dict[str, str]] = None,
        secret: Optional[str] = None,
        signature_header: str = "X-Hub-Signature-256",
        timeout: int = 30,
        retry_count: int = 0,
        retry_delay: int = 1,
    ) -> WebhookResultEntity:
        """
        Webhook を送信する

        Args:
            webhook_url: WebhookのURL
            payload: 送信するペイロード
            method: HTTPメソッド
            content_type: Content-Type
            headers: 追加ヘッダー
            secret: Webhook署名用シークレット
            signature_header: 署名ヘッダー名
            timeout: タイムアウト（秒）
            retry_count: リトライ回数
            retry_delay: リトライ間隔（秒）

        Returns:
            Webhook送信結果
        """
        ...

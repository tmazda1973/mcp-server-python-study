import asyncio
import hashlib
import hmac
import json
import time
from typing import Any, Dict, List, Literal, Optional

import httpx
from typing_extensions import override

from app.api.application.repositories.mcp.external_api import WebhookRepositoryProtocol
from app.api.domain.entities.mcp.external_api import (
    WebhookAttemptEntity,
    WebhookResultEntity,
)

__all__ = [
    "WebhookRepository",
]


class WebhookRepository(WebhookRepositoryProtocol):
    """
    リポジトリ（Webhook送信ツール）
    """

    @override
    async def send_webhook(
        self,
        webhook_url: str,
        payload: Dict[str, Any],
        method: Literal["POST", "PUT"] = "POST",
        content_type: Literal[
            "application/json", "application/x-www-form-urlencoded"
        ] = "application/json",
        headers: Optional[Dict[str, str]] = None,
        secret: Optional[str] = None,
        signature_header: str = "X-Hub-Signature-256",
        timeout: int = 30,
        retry_count: int = 0,
        retry_delay: int = 1,
    ) -> WebhookResultEntity:
        start_time = time.time()
        attempts: List[WebhookAttemptEntity] = []
        # ペイロード準備
        if content_type == "application/json":
            payload_data = json.dumps(payload, ensure_ascii=False)
            payload_bytes = payload_data.encode("utf-8")
        else:  # application/x-www-form-urlencoded
            payload_data = "&".join([f"{k}={v}" for k, v in payload.items()])
            payload_bytes = payload_data.encode("utf-8")

        payload_size = len(payload_bytes)

        # ヘッダー準備
        request_headers = headers.copy() if headers else {}
        request_headers["Content-Type"] = content_type

        # 署名生成
        signature_used = False
        if secret:
            signature = hmac.new(
                secret.encode("utf-8"), payload_bytes, hashlib.sha256
            ).hexdigest()
            request_headers[signature_header] = f"sha256={signature}"
            signature_used = True

        # リトライ込みで送信
        final_response = None
        final_status_code = 0
        for attempt in range(retry_count + 1):
            attempt_start = time.time()

            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    if content_type == "application/json":
                        response = await client.request(
                            method=method,
                            url=webhook_url,
                            headers=request_headers,
                            content=payload_data,
                        )
                    else:
                        response = await client.request(
                            method=method,
                            url=webhook_url,
                            headers=request_headers,
                            data=payload_data,
                        )

                    attempt_time = time.time() - attempt_start
                    final_status_code = response.status_code
                    final_response = response

                    # 試行記録
                    attempts.append(
                        WebhookAttemptEntity(
                            attempt=attempt + 1,
                            status_code=response.status_code,
                            response_time=attempt_time,
                            success=response.is_success,
                        )
                    )

                    # 成功した場合は終了
                    if response.is_success:
                        break

            except httpx.TimeoutException:
                attempt_time = time.time() - attempt_start
                attempts.append(
                    WebhookAttemptEntity(
                        attempt=attempt + 1,
                        status_code=408,
                        response_time=attempt_time,
                        success=False,
                        error=f"タイムアウト（{timeout}秒）",
                    )
                )
                final_status_code = 408
            except httpx.RequestError as e:
                attempt_time = time.time() - attempt_start
                attempts.append(
                    WebhookAttemptEntity(
                        attempt=attempt + 1,
                        status_code=0,
                        response_time=attempt_time,
                        success=False,
                        error=f"リクエストエラー: {str(e)}",
                    )
                )
                final_status_code = 0
            except Exception as e:
                attempt_time = time.time() - attempt_start
                attempts.append(
                    WebhookAttemptEntity(
                        attempt=attempt + 1,
                        status_code=0,
                        response_time=attempt_time,
                        success=False,
                        error=f"予期せぬエラー: {str(e)}",
                    )
                )
                final_status_code = 0

            # リトライ待機
            if attempt < retry_count:
                await asyncio.sleep(retry_delay)

        total_time = time.time() - start_time

        # 最終レスポンス処理
        response_data = None
        response_text = ""
        if final_response:
            response_text = final_response.text
            content_type_header = final_response.headers.get("content-type", "")
            if "application/json" in content_type_header:
                try:
                    response_data = final_response.json()
                except json.JSONDecodeError:
                    pass

        # 成功判定
        success = any(attempt.success for attempt in attempts)

        # エラーメッセージ
        error = None
        if not success:
            if attempts:
                last_attempt = attempts[-1]
                if last_attempt.error:
                    error = (
                        f"全ての試行が失敗しました。最後のエラー: {last_attempt.error}"
                    )
                else:
                    error = (
                        f"全ての試行が失敗しました。最終ステータス: {final_status_code}"
                    )
            else:
                error = "Webhook送信に失敗しました"

        return WebhookResultEntity(
            success=success,
            webhook_url=webhook_url,
            method=method,
            payload_size=payload_size,
            final_status_code=final_status_code,
            total_attempts=len(attempts),
            total_time=total_time,
            attempts=attempts,
            response_data=response_data,
            response_text=response_text,
            headers_sent=request_headers,
            signature_used=signature_used,
            error=error,
        )

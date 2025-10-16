from typing_extensions import override

from app.api.application.presenters import PresenterProtocol
from app.api.application.repositories.mcp.external_api import WebhookRepositoryProtocol
from app.api.application.usecases.abstract_async_usecase import AbstractAsyncUsecase
from app.api.presentation.request.mcp.external_api import WebhookRequest
from app.api.presentation.response.mcp.external_api import (
    WebhookAttempt,
    WebhookResponse,
)

__all__ = [
    "WebhookUsecase",
]


class WebhookUsecase(
    AbstractAsyncUsecase[
        PresenterProtocol[
            WebhookRequest,
            WebhookResponse,
        ],
    ]
):
    """
    ユースケース（Webhook送信ツール）
    """

    def __init__(self, repository: WebhookRepositoryProtocol) -> None:
        self._repository = repository

    @override
    async def execute(
        self,
        presenter: PresenterProtocol[
            WebhookRequest,
            WebhookResponse,
        ],
    ) -> None:
        # Webhookを送信する
        request = presenter.request
        result = await self._repository.send_webhook(
            webhook_url=str(request.webhook_url),
            payload=request.payload,
            method=request.method,
            content_type=request.content_type,
            headers=request.headers,
            secret=request.secret,
            signature_header=request.signature_header,
            timeout=request.timeout,
            retry_count=request.retry_count,
            retry_delay=request.retry_delay,
        )

        # レスポンスデータを構築する
        attempts = [
            WebhookAttempt(
                attempt=attempt.attempt,
                status_code=attempt.status_code,
                response_time=attempt.response_time,
                success=attempt.success,
                error=attempt.error,
            )
            for attempt in result.attempts
        ]
        presenter.response = WebhookResponse(
            success=result.success,
            webhook_url=result.webhook_url,
            method=result.method,
            payload_size=result.payload_size,
            final_status_code=result.final_status_code,
            total_attempts=result.total_attempts,
            total_time=result.total_time,
            attempts=attempts,
            response_data=result.response_data,
            response_text=result.response_text,
            headers_sent=result.headers_sent,
            signature_used=result.signature_used,
            error=result.error,
            warning=result.warning,
        )

from typing_extensions import override

from app.api.application.presenters import PresenterProtocol
from app.api.application.repositories.mcp.external_api import (
    HttpRequestRepositoryProtocol,
)
from app.api.application.usecases.abstract_async_usecase import AbstractAsyncUsecase
from app.api.presentation.request.mcp.external_api import HttpRequestRequest
from app.api.presentation.response.mcp.external_api import HttpRequestResponse

__all__ = [
    "HttpRequestUsecase",
]


class HttpRequestUsecase(
    AbstractAsyncUsecase[
        PresenterProtocol[
            HttpRequestRequest,
            HttpRequestResponse,
        ],
    ]
):
    """
    ユースケース（HTTPリクエストツール）
    """

    def __init__(self, repository: HttpRequestRepositoryProtocol) -> None:
        self._repository = repository

    @override
    async def execute(
        self,
        presenter: PresenterProtocol[
            HttpRequestRequest,
            HttpRequestResponse,
        ],
    ) -> None:
        # HTTPリクエストを実行する
        request = presenter.request
        result = await self._repository.send_request(
            url=str(request.url),
            method=request.method,
            headers=request.headers,
            params=request.params,
            data=request.data,
            timeout=request.timeout,
            follow_redirects=request.follow_redirects,
            verify_ssl=request.verify_ssl,
        )

        # レスポンスデータを構築する
        presenter.response = HttpRequestResponse(
            success=result.success,
            status_code=result.status_code,
            url=result.url,
            method=result.method,
            headers=result.headers,
            content=result.content,
            json_data=result.json_data,
            content_type=result.content_type,
            content_length=result.content_length,
            response_time=result.response_time,
            encoding=result.encoding,
            error=result.error,
            warning=result.warning,
        )

from typing_extensions import override

from app.api.application.presenters import PresenterProtocol
from app.api.application.repositories.mcp.external_api import RestApiRepositoryProtocol
from app.api.application.usecases.abstract_async_usecase import AbstractAsyncUsecase
from app.api.presentation.request.mcp.external_api import RestApiRequest
from app.api.presentation.response.mcp.external_api import RestApiResponse

__all__ = [
    "RestApiUsecase",
]


class RestApiUsecase(
    AbstractAsyncUsecase[
        PresenterProtocol[
            RestApiRequest,
            RestApiResponse,
        ],
    ]
):
    """
    ユースケース（REST API呼び出しツール）
    """

    def __init__(self, repository: RestApiRepositoryProtocol) -> None:
        self._repository = repository

    @override
    async def execute(
        self,
        presenter: PresenterProtocol[
            RestApiRequest,
            RestApiResponse,
        ],
    ) -> None:
        # REST API呼び出しを実行する
        request = presenter.request

        # 認証情報準備
        auth_type = request.auth_type
        auth_token = request.auth_token

        result = await self._repository.call_api(
            base_url=str(request.base_url),
            endpoint=request.endpoint,
            method=request.method,
            auth_type=auth_type,
            auth_token=auth_token,
            auth_username=request.auth_username,
            auth_password=request.auth_password,
            api_key_header=request.api_key_header,
            headers=request.headers,
            params=request.params,
            data=request.data,
            timeout=request.timeout,
        )

        # レスポンスデータを構築する
        presenter.response = RestApiResponse(
            success=result.success,
            status_code=result.status_code,
            url=result.url,
            method=result.method,
            headers=result.headers,
            response_data=result.response_data,
            response_text=result.response_text,
            content_type=result.content_type,
            response_time=result.response_time,
            auth_used=result.auth_used,
            error=result.error,
            warning=result.warning,
        )

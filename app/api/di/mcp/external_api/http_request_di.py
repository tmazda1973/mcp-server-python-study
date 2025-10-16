from fastapi import Depends

from app.api.application.presenters import PresenterProtocol
from app.api.application.repositories.mcp.external_api import (
    HttpRequestRepositoryProtocol,
)
from app.api.application.usecases.mcp.external_api import HttpRequestUsecase
from app.api.infra.repositories.mcp.external_api import HttpRequestRepository
from app.api.presentation import Presenter
from app.api.presentation.request.mcp.external_api import HttpRequestRequest
from app.api.presentation.response.mcp.external_api import HttpRequestResponse

__all__ = [
    "provide_usecase",
    "provide_presenter",
]


def provide_repository() -> HttpRequestRepositoryProtocol:
    """
    リポジトリを提供する

    Returns:
        HTTPリクエストリポジトリ
    """
    return HttpRequestRepository()


def provide_usecase(
    repository: HttpRequestRepositoryProtocol = Depends(provide_repository),
) -> HttpRequestUsecase:
    """
    ユースケースを提供する

    Args:
        repository: リポジトリ

    Returns:
        ユースケース
    """
    return HttpRequestUsecase(repository=repository)


def provide_presenter() -> (
    PresenterProtocol[
        HttpRequestRequest,
        HttpRequestResponse,
    ]
):
    """
    プレゼンターを提供する

    Returns:
        プレゼンター
    """
    return Presenter[
        HttpRequestRequest,
        HttpRequestResponse,
    ].create_presenter()

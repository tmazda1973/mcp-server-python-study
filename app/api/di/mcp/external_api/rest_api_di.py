from fastapi import Depends

from app.api.application.presenters import PresenterProtocol
from app.api.application.repositories.mcp.external_api import RestApiRepositoryProtocol
from app.api.application.usecases.mcp.external_api import RestApiUsecase
from app.api.infra.repositories.mcp.external_api import RestApiRepository
from app.api.presentation import Presenter
from app.api.presentation.request.mcp.external_api import RestApiRequest
from app.api.presentation.response.mcp.external_api import RestApiResponse

__all__ = [
    "provide_usecase",
    "provide_presenter",
]


def provide_repository() -> RestApiRepositoryProtocol:
    """
    リポジトリを提供する

    Returns:
        REST APIリポジトリ
    """
    return RestApiRepository()


def provide_usecase(
    repository: RestApiRepositoryProtocol = Depends(provide_repository),
) -> RestApiUsecase:
    """
    ユースケースを提供する

    Args:
        repository: リポジトリ

    Returns:
        ユースケース
    """
    return RestApiUsecase(repository=repository)


def provide_presenter() -> (
    PresenterProtocol[
        RestApiRequest,
        RestApiResponse,
    ]
):
    """
    プレゼンターを提供する

    Returns:
        プレゼンター
    """
    return Presenter[
        RestApiRequest,
        RestApiResponse,
    ].create_presenter()

from fastapi import Depends

from app.api.application.presenters import PresenterProtocol
from app.api.application.repositories.mcp.text import TextSearchRepositoryProtocol
from app.api.application.usecases.mcp.text import TextSearchUsecase
from app.api.infra.repositories.mcp.text import TextSearchRepository
from app.api.presentation import Presenter
from app.api.presentation.request.mcp.text import TextSearchRequest
from app.api.presentation.response.mcp.text import TextSearchResponse

__all__ = [
    "provide_usecase",
    "provide_presenter",
]


def provide_repository() -> TextSearchRepositoryProtocol:
    """
    リポジトリを提供する

    Returns:
        テキスト検索リポジトリ
    """
    return TextSearchRepository()


def provide_usecase(
    repository: TextSearchRepositoryProtocol = Depends(provide_repository),
) -> TextSearchUsecase:
    """
    ユースケースを提供する

    Args:
        repository: リポジトリ

    Returns:
        ユースケース
    """
    return TextSearchUsecase(repository=repository)


def provide_presenter() -> (
    PresenterProtocol[
        TextSearchRequest,
        TextSearchResponse,
    ]
):
    """
    プレゼンターを提供する

    Returns:
        プレゼンター
    """
    return Presenter[
        TextSearchRequest,
        TextSearchResponse,
    ].create_presenter()

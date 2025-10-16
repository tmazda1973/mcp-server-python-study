from fastapi import Depends

from app.api.application.presenters import PresenterProtocol
from app.api.application.repositories.mcp.text import TextReplaceRepositoryProtocol
from app.api.application.usecases.mcp.text import TextReplaceUsecase
from app.api.infra.repositories.mcp.text import TextReplaceRepository
from app.api.presentation import Presenter
from app.api.presentation.request.mcp.text import TextReplaceRequest
from app.api.presentation.response.mcp.text import TextReplaceResponse

__all__ = [
    "provide_usecase",
    "provide_presenter",
]


def provide_repository() -> TextReplaceRepositoryProtocol:
    """
    リポジトリを提供する

    Returns:
        テキスト置換リポジトリ
    """
    return TextReplaceRepository()


def provide_usecase(
    repository: TextReplaceRepositoryProtocol = Depends(provide_repository),
) -> TextReplaceUsecase:
    """
    ユースケースを提供する

    Args:
        repository: リポジトリ

    Returns:
        ユースケース
    """
    return TextReplaceUsecase(repository=repository)


def provide_presenter() -> (
    PresenterProtocol[
        TextReplaceRequest,
        TextReplaceResponse,
    ]
):
    """
    プレゼンターを提供する

    Returns:
        プレゼンター
    """
    return Presenter[
        TextReplaceRequest,
        TextReplaceResponse,
    ].create_presenter()

from fastapi import Depends

from app.api.application.presenters import PresenterProtocol
from app.api.application.repositories.mcp.text import TextAnalyzeRepositoryProtocol
from app.api.application.usecases.mcp.text import TextAnalyzeUsecase
from app.api.infra.repositories.mcp.text import TextAnalyzeRepository
from app.api.presentation import Presenter
from app.api.presentation.request.mcp.text import TextAnalyzeRequest
from app.api.presentation.response.mcp.text import TextAnalyzeResponse

__all__ = [
    "provide_usecase",
    "provide_presenter",
]


def provide_repository() -> TextAnalyzeRepositoryProtocol:
    """
    リポジトリを提供する

    Returns:
        テキスト分析リポジトリ
    """
    return TextAnalyzeRepository()


def provide_usecase(
    repository: TextAnalyzeRepositoryProtocol = Depends(provide_repository),
) -> TextAnalyzeUsecase:
    """
    ユースケースを提供する

    Args:
        repository: リポジトリ

    Returns:
        ユースケース
    """
    return TextAnalyzeUsecase(repository=repository)


def provide_presenter() -> (
    PresenterProtocol[
        TextAnalyzeRequest,
        TextAnalyzeResponse,
    ]
):
    """
    プレゼンターを提供する

    Returns:
        プレゼンター
    """
    return Presenter[
        TextAnalyzeRequest,
        TextAnalyzeResponse,
    ].create_presenter()

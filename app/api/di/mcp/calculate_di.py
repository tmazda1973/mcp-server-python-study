from fastapi import Depends

from app.api.application.presenters import PresenterProtocol
from app.api.application.repositories.mcp import CalculateRepositoryProtocol
from app.api.application.usecases.mcp import CalculateUsecase
from app.api.infra.repositories.mcp import CalculateRepository
from app.api.presentation.presenter import Presenter
from app.api.presentation.request.mcp import CalculateRequest
from app.api.presentation.response.mcp import CalculateResponse

__all__ = [
    "provide_calculate_presenter",
    "provide_calculate_usecase",
]


def provide_calculate_presenter() -> (
    PresenterProtocol[
        CalculateRequest,
        CalculateResponse,
    ]
):
    """
    プレゼンターを提供する

    Returns:
        プレゼンター
    """
    return Presenter[
        CalculateRequest,
        CalculateResponse,
    ].create_presenter()


def provide_repository() -> CalculateRepositoryProtocol:
    """
    リポジトリを提供する

    Returns:
        リポジトリ
    """
    return CalculateRepository()


def provide_calculate_usecase(
    repository: CalculateRepositoryProtocol = Depends(provide_repository),
) -> CalculateUsecase:
    """
    ユースケースを提供する

    Args:
        repository: リポジトリ

    Returns:
        ユースケース
    """
    return CalculateUsecase(repository=repository)

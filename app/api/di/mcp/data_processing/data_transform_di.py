from fastapi import Depends

from app.api.application.presenters import PresenterProtocol
from app.api.application.repositories.mcp.data_processing import (
    DataTransformRepositoryProtocol,
)
from app.api.application.usecases.mcp.data_processing import DataTransformUsecase
from app.api.infra.repositories.mcp.data_processing import DataTransformRepository
from app.api.presentation import Presenter
from app.api.presentation.request.mcp.data_processing import DataTransformRequest
from app.api.presentation.response.mcp.data_processing import DataTransformResponse

__all__ = [
    "provide_usecase",
    "provide_presenter",
]


def provide_repository() -> DataTransformRepositoryProtocol:
    """
    リポジトリを提供する

    Returns:
        データ変換リポジトリ
    """
    return DataTransformRepository()


def provide_usecase(
    repository: DataTransformRepositoryProtocol = Depends(provide_repository),
) -> DataTransformUsecase:
    """
    ユースケースを提供する

    Args:
        repository: リポジトリ

    Returns:
        ユースケース
    """
    return DataTransformUsecase(repository=repository)


def provide_presenter() -> (
    PresenterProtocol[
        DataTransformRequest,
        DataTransformResponse,
    ]
):
    """
    プレゼンターを提供する

    Returns:
        プレゼンター
    """
    return Presenter[
        DataTransformRequest,
        DataTransformResponse,
    ].create_presenter()

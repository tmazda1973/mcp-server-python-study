"""
データ集計DI設定
"""

from fastapi import Depends

from app.api.application.presenters import PresenterProtocol
from app.api.application.repositories.mcp.data_processing import (
    DataAggregateRepositoryProtocol,
)
from app.api.application.usecases.mcp.data_processing import (
    DataAggregateUsecase,
)
from app.api.infra.repositories.mcp.data_processing import (
    DataAggregateRepository,
)
from app.api.presentation import Presenter
from app.api.presentation.request.mcp.data_processing import (
    DataAggregateRequest,
)
from app.api.presentation.response.mcp.data_processing import (
    DataAggregateResponse,
)

__all__ = [
    "provide_usecase",
    "provide_presenter",
]


def provide_repository() -> DataAggregateRepositoryProtocol:
    """
    データ集計リポジトリを提供する

    Returns:
        リポジトリ
    """
    return DataAggregateRepository()


def provide_usecase(
    repository: DataAggregateRepositoryProtocol = Depends(provide_repository),
) -> DataAggregateUsecase:
    """
    データ集計ユースケースを提供する

    Returns:
        ユースケース
    """
    return DataAggregateUsecase(repository)


def provide_presenter() -> (
    PresenterProtocol[
        DataAggregateRequest,
        DataAggregateResponse,
    ]
):
    """
    データ集計プレゼンターを提供する

    Returns:
        プレゼンター
    """
    return Presenter[
        DataAggregateRequest,
        DataAggregateResponse,
    ].create_presenter()

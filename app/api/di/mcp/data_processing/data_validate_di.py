from fastapi import Depends

from app.api.application.presenters import PresenterProtocol
from app.api.application.repositories.mcp.data_processing import (
    DataValidateRepositoryProtocol,
)
from app.api.application.usecases.mcp.data_processing import (
    DataValidateUsecase,
)
from app.api.infra.repositories.mcp.data_processing import (
    DataValidateRepository,
)
from app.api.presentation import Presenter
from app.api.presentation.request.mcp.data_processing import (
    DataValidateRequest,
)
from app.api.presentation.response.mcp.data_processing import (
    DataValidateResponse,
)

__all__ = [
    "provide_presenter",
    "provide_usecase",
]


def provide_repository() -> DataValidateRepositoryProtocol:
    """
    リポジトリを提供する

    Returns:
        リポジトリ
    """
    return DataValidateRepository()


def provide_usecase(
    repository: DataValidateRepositoryProtocol = Depends(provide_repository),
) -> DataValidateUsecase:
    """
    ユースケースを提供する

    Args:
        repository: リポジトリ

    Returns:
        ユースケース
    """
    return DataValidateUsecase(repository)


def provide_presenter() -> (
    PresenterProtocol[
        DataValidateRequest,
        DataValidateResponse,
    ]
):
    """
    プレゼンターを提供する

    Returns:
        プレゼンター
    """
    return Presenter[
        DataValidateRequest,
        DataValidateResponse,
    ].create_presenter()

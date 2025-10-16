from fastapi import Depends

from app.api.application.presenters import PresenterProtocol
from app.api.application.repositories.mcp.external_api import WebhookRepositoryProtocol
from app.api.application.usecases.mcp.external_api import WebhookUsecase
from app.api.infra.repositories.mcp.external_api import WebhookRepository
from app.api.presentation import Presenter
from app.api.presentation.request.mcp.external_api import WebhookRequest
from app.api.presentation.response.mcp.external_api import WebhookResponse

__all__ = [
    "provide_usecase",
    "provide_presenter",
]


def provide_repository() -> WebhookRepositoryProtocol:
    """
    リポジトリを提供する

    Returns:
        Webhookリポジトリ
    """
    return WebhookRepository()


def provide_usecase(
    repository: WebhookRepositoryProtocol = Depends(provide_repository),
) -> WebhookUsecase:
    """
    ユースケースを提供する

    Args:
        repository: リポジトリ

    Returns:
        ユースケース
    """
    return WebhookUsecase(repository=repository)


def provide_presenter() -> (
    PresenterProtocol[
        WebhookRequest,
        WebhookResponse,
    ]
):
    """
    プレゼンターを提供する

    Returns:
        プレゼンター
    """
    return Presenter[
        WebhookRequest,
        WebhookResponse,
    ].create_presenter()

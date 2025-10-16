"""
依存性注入（インフラ層）
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.infra.adapters import AzureOpenAIAdapter, DatastoreAdapter
from app.core.config import settings
from app.database import get_db

__all__ = [
    "provide_datastore_adapter",
]


def provide_datastore_adapter(
    db: Session = Depends(get_db),
) -> DatastoreAdapter:
    """
    データストアアダプターを提供する

    Args:
        db: DBセッション

    Returns:
        データストアアダプター
    """
    return DatastoreAdapter(db_session=db)


def provide_azure_openai_adapter(
    api_key: str | None = None,
    api_version: str | None = None,
    azure_endpoint: str | None = None,
    deployment_name: str | None = None,
) -> AzureOpenAIAdapter:
    """
    Azure OpenAIアダプターを提供する

    Args:
        api_key: Azure OpenAI APIキー
        api_version: Azure OpenAI APIバージョン
        azure_endpoint: Azure OpenAIエンドポイント
        deployment_name: Azure OpenAIデプロイメント名

    Returns:
        Azure OpenAIアダプター
    """
    return AzureOpenAIAdapter(
        api_key=api_key or settings.AZURE_OPENAI_API_KEY,
        api_version=api_version or settings.AZURE_OPENAI_API_VERSION,
        azure_endpoint=azure_endpoint or settings.AZURE_OPENAI_ENDPOINT,
        deployment_name=deployment_name or settings.AZURE_OPENAI_DEPLOYMENT_NAME,
    )

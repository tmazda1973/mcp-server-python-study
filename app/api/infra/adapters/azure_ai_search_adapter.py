from typing import Any

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

from app.core.config import settings

__all__ = [
    "AzureAISearchAdapter",
]


class AzureAISearchAdapter:
    """
    AIアダプター（Azure AI Search）

    - 特許データのインデックス化・検索を行う
    - テキスト検索、ベクトル検索、ハイブリッド検索をサポート
    """

    def __init__(
        self,
        endpoint: str | None = None,
        api_key: str | None = None,
        index_name: str | None = None,
    ) -> None:
        """
        コンストラクタ

        Args:
            endpoint: Azure AI Searchエンドポイント（未指定時は設定値から取得）
            api_key: Azure AI Search APIキー（未指定時は設定値から取得）
            index_name: インデックス名（未指定時は設定値から取得）
        """

        self._endpoint = endpoint or settings.AZURE_SEARCH_ENDPOINT
        self._api_key = api_key or settings.AZURE_SEARCH_API_KEY
        self._index_name = index_name or settings.AZURE_SEARCH_INDEX_NAME

        if not self._endpoint:
            raise ValueError("AZURE_SEARCH_ENDPOINT is required")

        if not self._api_key:
            raise ValueError("AZURE_SEARCH_API_KEY is required")

        if not self._index_name:
            raise ValueError("AZURE_SEARCH_INDEX_NAME is required")

        self._client = SearchClient(
            endpoint=self._endpoint,
            index_name=self._index_name,
            credential=AzureKeyCredential(self._api_key),
        )

    async def search(
        self,
        query: str,
        top: int = 5,
        select: list[str] | None = None,
        filter_expression: str | None = None,
        order_by: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        テキスト検索を実行する

        Args:
            query: 検索クエリ
            top: 取得件数
            select: 取得フィールド
            filter_expression: フィルタ式（例: "category eq 'patent'"）
            order_by: ソート順

        Returns:
            検索結果のリスト
        """

        results = self._client.search(
            search_text=query,
            top=top,
            select=select,
            filter=filter_expression,
            order_by=order_by,
        )

        return [dict(result) for result in results]

    async def search_by_patent_number(
        self,
        patent_number: str,
        top: int = 1,
    ) -> dict[str, Any] | None:
        """
        特許番号で検索する

        Args:
            patent_number: 特許番号
            top: 取得件数

        Returns:
            特許情報
        """

        results = await self.search(
            query=patent_number,
            top=top,
            filter_expression=f"patent_number eq '{patent_number}'",
        )

        return results[0] if results else None

    async def search_multiple_patents(
        self,
        patent_numbers: list[str],
    ) -> dict[str, dict[str, Any]]:
        """
        複数の特許番号で一括検索する

        Args:
            patent_numbers: 特許番号のリスト

        Returns:
            特許番号をキーとした辞書
        """

        # フィルタ式を構築（OR条件）
        filter_parts = [f"patent_number eq '{num}'" for num in patent_numbers]
        filter_expression = " or ".join(filter_parts)

        results = await self.search(
            query="*",  # 全文検索なし
            top=len(patent_numbers),
            filter_expression=filter_expression,
        )

        # 特許番号でインデックス化
        return {
            result.get("patent_number"): result
            for result in results
            if result.get("patent_number")
        }

    async def vector_search(
        self,
        query_vector: list[float],
        top: int = 5,
        select: list[str] | None = None,
        filter_expression: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        ベクトル検索を実行する（セマンティック検索）

        Args:
            query_vector: クエリベクトル（Embeddingモデルで生成）
            top: 取得件数
            select: 取得フィールド
            filter_expression: フィルタ式

        Returns:
            検索結果のリスト
        """

        vector_query = VectorizedQuery(
            vector=query_vector,
            k_nearest_neighbors=top,
            fields="content_vector",  # ベクトルフィールド名
        )

        results = self._client.search(
            search_text=None,
            vector_queries=[vector_query],
            select=select,
            filter=filter_expression,
            top=top,
        )

        return [dict(result) for result in results]

    async def hybrid_search(
        self,
        query: str,
        query_vector: list[float],
        top: int = 5,
        select: list[str] | None = None,
        filter_expression: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        ハイブリッド検索を実行する（テキスト + ベクトル）

        Args:
            query: 検索クエリ
            query_vector: クエリベクトル
            top: 取得件数
            select: 取得フィールド
            filter_expression: フィルタ式

        Returns:
            検索結果のリスト
        """

        vector_query = VectorizedQuery(
            vector=query_vector,
            k_nearest_neighbors=top,
            fields="content_vector",
        )

        results = self._client.search(
            search_text=query,
            vector_queries=[vector_query],
            select=select,
            filter=filter_expression,
            top=top,
        )

        return [dict(result) for result in results]

    def close(self) -> None:
        """
        クライアントをクローズする
        """
        self._client.close()

    async def __aenter__(self) -> "AzureAISearchAdapter":
        """
        非同期コンテキストマネージャー（入場）
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        非同期コンテキストマネージャー（退場）
        """
        self.close()

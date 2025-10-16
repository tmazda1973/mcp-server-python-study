from typing import Any, Dict, Literal, Optional, Protocol, runtime_checkable

from app.api.domain.entities.mcp.external_api import RestApiResultEntity

__all__ = [
    "RestApiRepositoryProtocol",
]


@runtime_checkable
class RestApiRepositoryProtocol(Protocol):
    """
    リポジトリプロトコル（REST API呼び出しツール）
    """

    async def call_api(
        self,
        base_url: str,
        endpoint: str,
        method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"] = "GET",
        auth_type: Optional[Literal["bearer", "basic", "api_key"]] = None,
        auth_token: Optional[str] = None,
        auth_username: Optional[str] = None,
        auth_password: Optional[str] = None,
        api_key_header: str = "X-API-Key",
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
    ) -> RestApiResultEntity:
        """
        REST API を呼び出す

        Args:
            base_url: ベースURL
            endpoint: エンドポイントパス
            method: HTTPメソッド
            auth_type: 認証タイプ
            auth_token: 認証トークン
            auth_username: Basic認証ユーザー名
            auth_password: Basic認証パスワード
            api_key_header: APIキーヘッダー名
            headers: 追加ヘッダー
            params: クエリパラメータ
            data: リクエストボディ
            timeout: タイムアウト（秒）

        Returns:
            REST API呼び出し結果
        """
        ...

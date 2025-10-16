from typing import Any, Dict, Literal, Optional, Protocol, runtime_checkable

from app.api.domain.entities.mcp.external_api import HttpRequestResultEntity

__all__ = [
    "HttpRequestRepositoryProtocol",
]


@runtime_checkable
class HttpRequestRepositoryProtocol(Protocol):
    """
    リポジトリプロトコル（HTTP リクエストツール）
    """

    async def send_request(
        self,
        url: str,
        method: Literal[
            "GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"
        ] = "GET",
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
        follow_redirects: bool = True,
        verify_ssl: bool = True,
    ) -> HttpRequestResultEntity:
        """
        HTTP リクエストを送信する

        Args:
            url: リクエスト先URL
            method: HTTPメソッド
            headers: リクエストヘッダー
            params: クエリパラメータ
            data: リクエストボディ（JSON）
            timeout: タイムアウト（秒）
            follow_redirects: リダイレクトを追跡するか
            verify_ssl: SSL証明書を検証するか

        Returns:
            HTTP リクエスト結果
        """
        ...

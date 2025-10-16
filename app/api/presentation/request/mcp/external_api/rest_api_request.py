from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field, HttpUrl

__all__ = [
    "RestApiRequest",
]


class RestApiRequest(BaseModel):
    """
    リクエストデータ（REST API呼び出しツール）
    """

    base_url: HttpUrl = Field(..., description="ベースURL")
    endpoint: str = Field(..., description="エンドポイントパス")
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"] = Field(
        default="GET", description="HTTPメソッド"
    )
    auth_type: Optional[Literal["bearer", "basic", "api_key"]] = Field(
        default=None, description="認証タイプ"
    )
    auth_token: Optional[str] = Field(default=None, description="認証トークン")
    auth_username: Optional[str] = Field(
        default=None, description="Basic認証ユーザー名"
    )
    auth_password: Optional[str] = Field(
        default=None, description="Basic認証パスワード"
    )
    api_key_header: Optional[str] = Field(
        default="X-API-Key", description="APIキーヘッダー名"
    )
    headers: Optional[Dict[str, str]] = Field(default=None, description="追加ヘッダー")
    params: Optional[Dict[str, Any]] = Field(
        default=None, description="クエリパラメータ"
    )
    data: Optional[Dict[str, Any]] = Field(default=None, description="リクエストボディ")
    timeout: int = Field(default=30, ge=1, le=300, description="タイムアウト（秒）")

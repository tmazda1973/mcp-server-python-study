from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field, HttpUrl

__all__ = [
    "HttpRequestRequest",
]


class HttpRequestRequest(BaseModel):
    """
    リクエストデータ（HTTP リクエストツール）
    """

    url: HttpUrl = Field(..., description="リクエスト先URL")
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"] = Field(
        default="GET",
        description="HTTPメソッド",
    )
    headers: Optional[Dict[str, str]] = Field(
        default=None,
        description="リクエストヘッダー",
    )
    params: Optional[Dict[str, Any]] = Field(
        default=None,
        description="クエリパラメータ",
    )
    data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="リクエストボディ（JSON）",
    )
    timeout: int = Field(default=30, ge=1, le=300, description="タイムアウト（秒）")
    follow_redirects: bool = Field(default=True, description="リダイレクトを追跡するか")
    verify_ssl: bool = Field(default=True, description="SSL証明書を検証するか")

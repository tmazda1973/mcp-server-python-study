from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

__all__ = [
    "HttpRequestResponse",
]


class HttpRequestResponse(BaseModel):
    """
    レスポンスデータ（HTTP リクエストツール）
    """

    success: bool = Field(..., description="リクエスト成功")
    status_code: int = Field(..., description="HTTPステータスコード")
    url: str = Field(..., description="最終的なリクエストURL（リダイレクト後）")
    method: str = Field(..., description="HTTPメソッド")
    headers: Dict[str, str] = Field(..., description="レスポンスヘッダー")
    content: str = Field(..., description="レスポンス内容（テキスト）")
    json_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="レスポンス内容（JSON）",
    )
    content_type: Optional[str] = Field(default=None, description="Content-Type")
    content_length: Optional[int] = Field(default=None, description="Content-Length")
    response_time: float = Field(..., description="レスポンス時間（秒）")
    encoding: Optional[str] = Field(default=None, description="文字エンコーディング")
    error: Optional[str] = Field(default=None, description="エラーメッセージ")
    warning: Optional[str] = Field(default=None, description="警告メッセージ")

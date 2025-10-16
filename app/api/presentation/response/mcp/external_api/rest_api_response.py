from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

__all__ = [
    "RestApiResponse",
]


class RestApiResponse(BaseModel):
    """
    レスポンスデータ（REST API呼び出しツール）
    """

    success: bool = Field(..., description="API呼び出し成功")
    status_code: int = Field(..., description="HTTPステータスコード")
    url: str = Field(..., description="完全なリクエストURL")
    method: str = Field(..., description="HTTPメソッド")
    response_data: Optional[Dict[str, Any]] = Field(
        default=None, description="レスポンスデータ（JSON）"
    )
    response_text: str = Field(..., description="レスポンステキスト")
    headers: Dict[str, str] = Field(..., description="レスポンスヘッダー")
    content_type: Optional[str] = Field(default=None, description="Content-Type")
    response_time: float = Field(..., description="レスポンス時間（秒）")
    auth_used: Optional[str] = Field(default=None, description="使用された認証タイプ")
    error: Optional[str] = Field(default=None, description="エラーメッセージ")
    warning: Optional[str] = Field(default=None, description="警告メッセージ")

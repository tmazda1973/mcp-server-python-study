from dataclasses import dataclass
from typing import Any, Dict, Optional

__all__ = [
    "HttpRequestResultEntity",
]


@dataclass(frozen=True)
class HttpRequestResultEntity:
    """
    ドメインエンティティ（HTTP リクエスト結果）
    """

    success: bool
    status_code: int
    url: str
    method: str
    headers: Dict[str, str]
    content: str
    json_data: Optional[Dict[str, Any]] = None
    content_type: Optional[str] = None
    content_length: Optional[int] = None
    response_time: float = 0.0
    encoding: Optional[str] = None
    error: Optional[str] = None
    warning: Optional[str] = None

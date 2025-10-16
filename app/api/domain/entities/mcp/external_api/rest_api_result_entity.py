from dataclasses import dataclass
from typing import Any, Dict, Optional

__all__ = [
    "RestApiResultEntity",
]


@dataclass(frozen=True)
class RestApiResultEntity:
    """
    ドメインエンティティ（REST API結果）
    """

    success: bool
    status_code: int
    url: str
    method: str
    response_data: Optional[Dict[str, Any]]
    response_text: str
    headers: Dict[str, str]
    content_type: Optional[str] = None
    response_time: float = 0.0
    auth_used: Optional[str] = None
    error: Optional[str] = None
    warning: Optional[str] = None

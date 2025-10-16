from typing import Any

from fastapi import status

from .app_exception import AppException

__all__ = [
    "TooManyRequestsException",
]


class TooManyRequestsException(AppException):
    """
    例外クラス: レート制限エラー（429）
    """

    def __init__(
        self,
        message: str = "リクエストが多すぎます。しばらく待ってから再試行してください",
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code=error_code,
            details=details,
        )

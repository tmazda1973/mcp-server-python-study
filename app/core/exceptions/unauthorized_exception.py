from typing import Any

from fastapi import status

from .app_exception import AppException

__all__ = [
    "UnauthorizedException",
]


class UnauthorizedException(AppException):
    """
    例外クラス: 認証エラー（401）
    """

    def __init__(
        self,
        message: str = "認証に失敗しました",
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=error_code,
            details=details,
        )

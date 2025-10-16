"""
権限エラー例外（403）
"""

from typing import Any

from fastapi import status

from .app_exception import AppException


class ForbiddenException(AppException):
    """権限エラー（403）"""

    def __init__(
        self,
        message: str = "アクセスが拒否されました",
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code=error_code,
            details=details,
        )

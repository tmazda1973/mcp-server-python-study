from typing import Any

from fastapi import status

from .app_exception import AppException

__all__ = [
    "ConflictException",
]


class ConflictException(AppException):
    """
    例外クラス: 競合エラー（409）
    """

    def __init__(
        self,
        message: str = "リソースが競合しています",
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code=error_code,
            details=details,
        )

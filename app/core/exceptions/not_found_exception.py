from typing import Any

from fastapi import status

from .app_exception import AppException

__all__ = [
    "NotFoundException",
]


class NotFoundException(AppException):
    """
    例外クラス: リソースが見つからない（404）
    """

    def __init__(
        self,
        message: str = "リソースが見つかりません",
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=error_code,
            details=details,
        )

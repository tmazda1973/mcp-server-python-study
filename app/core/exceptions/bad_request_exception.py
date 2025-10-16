from typing import Any

from fastapi import status

from .app_exception import AppException

__all__ = [
    "BadRequestException",
]


class BadRequestException(AppException):
    """
    例外クラス: 不正リクエストエラー（400）
    """

    def __init__(
        self,
        message: str = "不正なリクエストです",
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=error_code,
            details=details,
        )

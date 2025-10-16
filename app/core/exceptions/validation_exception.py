from typing import Any

from fastapi import status

from .app_exception import AppException

__all__ = [
    "ValidationException",
]


class ValidationException(AppException):
    """
    例外クラス: バリデーションエラー（422）
    """

    def __init__(
        self,
        message: str = "入力値が不正です",
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code=error_code,
            details=details,
        )

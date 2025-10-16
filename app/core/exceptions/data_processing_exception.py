from typing import Any

from fastapi import status

from .app_exception import AppException

__all__ = [
    "DataProcessingException",
]


class DataProcessingException(AppException):
    """
    例外クラス: データ処理エラー（500）
    """

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=error_code or "DataProcessingError",
            details=details,
        )

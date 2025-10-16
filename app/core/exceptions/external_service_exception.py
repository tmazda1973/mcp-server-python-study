from typing import Any

from fastapi import status

from .app_exception import AppException

__all__ = [
    "ExternalServiceException",
]


class ExternalServiceException(AppException):
    """
    例外クラス: 外部サービスエラー（502）
    """

    def __init__(
        self,
        message: str,
        service_name: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        details = details or {}
        details["service_name"] = service_name
        super().__init__(
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            error_code=error_code or "ExternalServiceError",
            details=details,
        )

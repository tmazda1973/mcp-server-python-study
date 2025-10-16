from typing import Any

from fastapi import status

from .app_exception import AppException

__all__ = [
    "ServiceUnavailableException",
]


class ServiceUnavailableException(AppException):
    """
    例外クラス: サービス利用不可（503）
    """

    def __init__(
        self,
        message: str = "サービスが一時的に利用できません",
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code=error_code,
            details=details,
        )

from typing import Any

from fastapi import status

from .app_exception import AppException

__all__ = [
    "GatewayTimeoutException",
]


class GatewayTimeoutException(AppException):
    """
    例外クラス: ゲートウェイタイムアウト（504）
    """

    def __init__(
        self,
        message: str = "外部サービスへの接続がタイムアウトしました",
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            error_code=error_code,
            details=details,
        )

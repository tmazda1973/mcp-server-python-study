from typing import Any

from fastapi import status

__all__ = [
    "AppException",
]


class AppException(Exception):
    """
    アプリケーション基底例外クラス

    - 全てのカスタム例外はこのクラスを継承します。
    """

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Args:
            message: エラーメッセージ
            status_code: HTTPステータスコード
            error_code: アプリケーション固有のエラーコード
            details: 追加のエラー詳細情報
        """
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)

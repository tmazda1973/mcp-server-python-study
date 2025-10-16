from typing import Any

from fastapi import status

from .app_exception import AppException

__all__ = [
    "MCPToolException",
]


class MCPToolException(AppException):
    """
    例外クラス: MCPツール実行エラー（500）
    """

    def __init__(
        self,
        message: str,
        tool_name: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        details = details or {}
        details["tool_name"] = tool_name
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=error_code or "MCPToolError",
            details=details,
        )

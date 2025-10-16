import platform
from typing import Any, Literal

import psutil

from app.core.config import settings
from app.core.exceptions import BadRequestException

__all__ = [
    "get_server_info",
    "calculate",
    "get_system_status",
]


async def get_server_info() -> dict[str, Any]:
    """
    MCPツール（サーバー情報を取得する）
    """
    return {
        "server_name": settings.MCP_SERVER_NAME,
        "version": "1.0.0",
        "environment": settings.APP_ENV,
        "host": settings.MCP_HOST,
        "port": str(settings.MCP_PORT),
    }


async def calculate(
    a: float,
    b: float,
    operation: Literal["add", "subtract", "multiply", "divide"] = "add",
) -> dict[str, Any]:
    """
    MCPツール（二つの数値の計算を実行する）

    Args:
        a: 数値1
        b: 数値2
        operation: 演算子（add, subtract, multiply, divide）

    Returns:
        計算結果

    Raises:
        BadRequestException: ゼロ除算エラー
    """

    # 演算を実行
    if operation == "add":
        result = a + b
    elif operation == "subtract":
        result = a - b
    elif operation == "multiply":
        result = a * b
    else:  # operation == "divide"
        if b == 0:
            raise BadRequestException(
                message="ゼロで除算することはできません",
                error_code="DIVISION_BY_ZERO",
                details={"a": a, "b": b, "operation": operation},
            )
        result = a / b

    return {"operation": operation, "inputs": {"a": a, "b": b}, "result": result}


async def get_system_status() -> dict[str, Any]:
    """
    MCPツール（システムステータスを取得する）
    """
    return {
        "platform": platform.system(),
        "python_version": platform.python_version(),
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
    }

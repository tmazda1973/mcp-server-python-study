from typing import Any, Literal

from typing_extensions import override

from app.api.application.repositories.mcp import CalculateRepositoryProtocol
from app.core.mcp_tools import calculate

__all__ = [
    "CalculateRepository",
]


class CalculateRepository(CalculateRepositoryProtocol):
    """
    リポジトリ（数値計算API）
    """

    @override
    async def calculate(
        self,
        a: float,
        b: float,
        operation: Literal["add", "subtract", "multiply", "divide"],
    ) -> dict[str, Any]:
        """
        数値計算を実行する

        Args:
            a: 数値1
            b: 数値2
            operation: 演算子

        Returns:
            dict[str, Any]: 計算結果
        """
        return await calculate(a, b, operation)

from typing import Any, Literal, Protocol, runtime_checkable

__all__ = [
    "CalculateRepositoryProtocol",
]


@runtime_checkable
class CalculateRepositoryProtocol(Protocol):
    """
    リポジトリプロトコル（数値計算API）
    """

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
            計算結果
        """
        ...

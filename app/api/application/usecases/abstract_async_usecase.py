from abc import ABC, abstractmethod
from typing import Generic, TypeVar

__all__ = [
    "AbstractAsyncUsecase",
]

T = TypeVar("T")  # プレゼンター


class AbstractAsyncUsecase(ABC, Generic[T]):
    """
    SSEストリームユースケース抽象クラス

    - T: プレゼンター
    - 非同期処理を行うユースケースは、このクラスを継承してください。
    """

    @abstractmethod
    async def execute(self, presenter: T) -> None:
        """
        ユースケースを実行します。

        Args:
            presenter: プレゼンター

        Returns:
            None
        """
        pass

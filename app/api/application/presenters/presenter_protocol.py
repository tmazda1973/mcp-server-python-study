from typing import Generic, Protocol, TypeVar, runtime_checkable

T = TypeVar("T")
R = TypeVar("R")

__all__ = [
    "PresenterProtocol",
]


@runtime_checkable
class PresenterProtocol(Protocol, Generic[T, R]):
    """
    プレゼンタープロトコル
    """

    def __init__(self, request: T, response: R) -> None:
        """
        コンストラクタ

        :param request: リクエストデータ
        :param response: レスポンスデータ
        """
        ...

    @property
    def request(self) -> T:
        """
        リクエストデータを取得します。

        :return: リクエストデータ
        """
        ...

    @property
    def response(self) -> R:
        """
        レスポンスデータを取得します。

        :return: レスポンスデータ
        """
        ...

    @classmethod
    def create_presenter(cls) -> "PresenterProtocol[T, R]":
        """
        プレゼンターを生成します。

        :return: プレゼンター
        """
        ...

    @request.setter
    def request(self, request: T) -> None:
        """
        リクエストデータを設定します。

        :param request: リクエストデータ
        """
        ...

    @response.setter
    def response(self, response: R) -> None:
        """
        レスポンスデータを設定します。

        :param response: レスポンスデータ
        """
        ...

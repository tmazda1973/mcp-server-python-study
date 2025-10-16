from typing import Generic, TypeVar

T = TypeVar("T")
R = TypeVar("R")


class Presenter(Generic[T, R]):
    """
    プレゼンター

    - RequestクラスをTに、ResponseクラスをRに指定してプレゼンターを生成します。

    :var _request: リクエストデータ
    :var _response: レスポンスデータ
    """

    def __init__(self, request: T, response: R) -> None:
        """
        コンストラクタ

        :param request: リクエストデータ
        :param response: レスポンスデータ
        """
        self._response = response
        self._request = request

    @property
    def request(self) -> T:
        """
        リクエストデータを取得します。

        :return: リクエストデータ
        """
        return self._request

    @property
    def response(self) -> R:
        """
        レスポンスデータを取得します。

        :return: レスポンスデータ
        """
        return self._response

    @classmethod
    def create_presenter(cls) -> "Presenter[T, R]":
        """
        プレゼンターを生成します。

        :return: プレゼンター
        """
        return cls(cls.request, cls.response)

    @request.setter
    def request(self, request: T) -> None:
        """
        リクエストデータを設定します。

        :param request: リクエストデータ
        """
        self._request = request

    @response.setter
    def response(self, response: R) -> None:
        """
        レスポンスデータを設定します。

        :param response: レスポンスデータ
        """
        self._response = response

from app.api.application.repositories.mcp import CalculateRepositoryProtocol
from app.api.application.usecases.abstract_async_usecase import AbstractAsyncUsecase
from app.api.presentation.presenter import Presenter
from app.api.presentation.request.mcp import CalculateRequest
from app.api.presentation.response.mcp import CalculateResponse

__all__ = [
    "CalculateUsecase",
]


class CalculateUsecase(
    AbstractAsyncUsecase[
        Presenter[
            CalculateRequest,
            CalculateResponse,
        ]
    ]
):
    """
    ユースケース（数値計算API）
    """

    def __init__(self, repository: CalculateRepositoryProtocol) -> None:
        """
        コンストラクタ

        Args:
            repository: リポジトリ
        """
        self._repository = repository

    async def execute(
        self,
        presenter: Presenter[
            CalculateRequest,
            CalculateResponse,
        ],
    ) -> None:
        """
        ユースケースを実行する

        Args:
            presenter: プレゼンター
        """

        request = presenter.request

        # 数値計算を実行する
        result_data = await self._repository.calculate(
            request.a,
            request.b,
            request.operation,
        )

        # レスポンスデータを構築する
        presenter.response = CalculateResponse(
            operation=result_data["operation"],
            inputs=result_data["inputs"],
            result=result_data["result"],
            mcp_tool=True,
        )

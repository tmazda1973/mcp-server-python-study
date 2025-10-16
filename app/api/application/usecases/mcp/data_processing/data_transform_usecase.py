from typing_extensions import override

from app.api.application.presenters import PresenterProtocol
from app.api.application.repositories.mcp.data_processing import (
    DataTransformRepositoryProtocol,
)
from app.api.application.usecases.abstract_async_usecase import AbstractAsyncUsecase
from app.api.presentation.request.mcp.data_processing import DataTransformRequest
from app.api.presentation.response.mcp.data_processing import DataTransformResponse

__all__ = [
    "DataTransformUsecase",
]


class DataTransformUsecase(
    AbstractAsyncUsecase[
        PresenterProtocol[
            DataTransformRequest,
            DataTransformResponse,
        ]
    ]
):
    """
    ユースケース（データ変換ツール）
    """

    def __init__(self, repository: DataTransformRepositoryProtocol) -> None:
        self._repository = repository

    @override
    async def execute(
        self,
        presenter: PresenterProtocol[
            DataTransformRequest,
            DataTransformResponse,
        ],
    ) -> None:
        # データ変換を実行する
        request = presenter.request
        result = await self._repository.transform_data(
            data=request.data,
            from_format=request.from_format,
            to_format=request.to_format,
            options=request.options,
            field_mapping=request.field_mapping,
            include_headers=request.include_headers,
            delimiter=request.delimiter,
            encoding=request.encoding,
        )

        # エンティティからレスポンスに変換
        presenter.response = DataTransformResponse(
            success=result.success,
            transformed_data=result.transformed_data,
            from_format=result.from_format,
            to_format=result.to_format,
            record_count=result.record_count,
            field_count=result.field_count,
            processing_time=result.processing_time,
            applied_mappings=result.applied_mappings,
            warnings=result.warnings,
            error=result.error,
        )

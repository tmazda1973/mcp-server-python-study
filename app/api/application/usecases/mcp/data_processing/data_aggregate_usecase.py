from app.api.application.presenters import PresenterProtocol
from app.api.application.repositories.mcp.data_processing import (
    DataAggregateRepositoryProtocol,
)
from app.api.presentation.request.mcp.data_processing import (
    DataAggregateRequest,
)
from app.api.presentation.response.mcp.data_processing import (
    DataAggregateResponse,
)
from app.api.presentation.response.mcp.data_processing.schemas import (
    AggregateGroupResult,
    AggregateStatistics,
)

__all__ = [
    "DataAggregateUsecase",
]


class DataAggregateUsecase:
    """
    ユースケース（データ集計ツール）
    """

    def __init__(self, repository: DataAggregateRepositoryProtocol):
        self._repository = repository

    async def execute(
        self,
        presenter: PresenterProtocol[
            DataAggregateRequest,
            DataAggregateResponse,
        ],
    ) -> None:
        # データ集計を実行する
        request = presenter.request
        result_entity = await self._repository.aggregate_data(
            data=request.data,
            group_by=request.group_by,
            aggregate_functions=request.aggregate_functions,
            filter_conditions=request.filter_conditions,
            sort_by=request.sort_by,
            limit=request.limit,
            include_totals=request.include_totals,
            include_metadata=request.include_metadata,
            output_format=request.output_format,
        )

        # レスポンスデータを構築する
        response = DataAggregateResponse(
            success=result_entity.success,
            output_format=result_entity.output_format,
            results=[
                AggregateGroupResult(
                    group_key=result.group_key,
                    aggregated_values=result.aggregated_values,
                    record_count=result.record_count,
                )
                for result in result_entity.results
            ],
            totals=result_entity.totals,
            statistics=AggregateStatistics(
                total_records=result_entity.statistics.total_records,
                processed_records=result_entity.statistics.processed_records,
                filtered_records=result_entity.statistics.filtered_records,
                groups_count=result_entity.statistics.groups_count,
                unique_values=result_entity.statistics.unique_values,
            ),
            group_by_fields=result_entity.group_by_fields,
            aggregate_functions_used=result_entity.aggregate_functions_used,
            sort_applied=result_entity.sort_applied,
            processing_time=result_entity.processing_time,
            memory_usage=result_entity.memory_usage,
            warnings=result_entity.warnings,
            recommendations=result_entity.recommendations,
        )
        presenter.response = response

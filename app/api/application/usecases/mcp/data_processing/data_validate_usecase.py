from app.api.application.presenters import PresenterProtocol
from app.api.application.repositories.mcp.data_processing.data_validate_repository_protocol import (
    DataValidateRepositoryProtocol,
)
from app.api.presentation.request.mcp.data_processing import (
    DataValidateRequest,
)
from app.api.presentation.response.mcp.data_processing.data_validate_response import (
    DataValidateResponse,
    ValidationError,
    ValidationSummary,
    ValidationWarning,
)

__all__ = [
    "DataValidateUsecase",
]


class DataValidateUsecase:
    """
    ユースケース（データ検証ツール）
    """

    def __init__(self, repository: DataValidateRepositoryProtocol):
        self._repository = repository

    async def execute(
        self,
        presenter: PresenterProtocol[
            DataValidateRequest,
            DataValidateResponse,
        ],
    ) -> None:
        # データ検証を実行する
        request = presenter.request
        result_entity = await self._repository.validate_data(
            data=request.data,
            schema_type=request.schema_type,
            schema_definition=request.schema_definition,
            validation_mode=request.validation_mode,
            max_errors=request.max_errors,
            include_warnings=request.include_warnings,
            custom_rules=request.custom_rules,
        )

        # レスポンスデータを構築する
        response = DataValidateResponse(
            success=result_entity.success,
            is_valid=result_entity.is_valid,
            schema_type=result_entity.schema_type,
            validation_mode=result_entity.validation_mode,
            summary=ValidationSummary(
                total_fields=result_entity.summary.total_fields,
                valid_fields=result_entity.summary.valid_fields,
                invalid_fields=result_entity.summary.invalid_fields,
                error_count=result_entity.summary.error_count,
                warning_count=result_entity.summary.warning_count,
                validation_rate=result_entity.summary.validation_rate,
            ),
            errors=[
                ValidationError(
                    field=error.field,
                    message=error.message,
                    error_type=error.error_type,
                    invalid_value=error.invalid_value,
                    expected_type=error.expected_type,
                    location=error.location,
                )
                for error in result_entity.errors
            ],
            warnings=[
                ValidationWarning(
                    field=warning.field,
                    message=warning.message,
                    warning_type=warning.warning_type,
                    current_value=warning.current_value,
                    suggestion=warning.suggestion,
                )
                for warning in result_entity.warnings
            ],
            validated_data=result_entity.validated_data,
            processing_time=result_entity.processing_time,
            schema_info=result_entity.schema_info,
            recommendations=result_entity.recommendations,
        )
        presenter.response = response

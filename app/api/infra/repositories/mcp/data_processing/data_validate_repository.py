import json
import time
from typing import Any

import jsonschema
from typing_extensions import override

from app.api.application.repositories.mcp.data_processing import (
    DataValidateRepositoryProtocol,
)
from app.api.domain.entities.mcp.data_processing import (
    DataValidateResultEntity,
    ValidationErrorEntity,
    ValidationSummaryEntity,
    ValidationWarningEntity,
)
from app.decorators.access_control import private

__all__ = [
    "DataValidateRepository",
]


class DataValidateRepository(DataValidateRepositoryProtocol):
    """
    リポジトリ（データ検証ツール）
    """

    @override
    async def validate_data(
        self,
        data: str,
        schema_type: str,
        schema_definition: str,
        validation_mode: str,
        max_errors: int,
        include_warnings: bool,
        custom_rules: dict[str, Any] | None,
    ) -> DataValidateResultEntity:
        # データ検証を実行する
        start_time = time.time()
        try:
            # JSON データの解析
            parsed_data = json.loads(data)
        except json.JSONDecodeError as e:
            # JSON解析エラー
            processing_time = time.time() - start_time
            return DataValidateResultEntity(
                success=False,
                is_valid=False,
                schema_type=schema_type,
                validation_mode=validation_mode,
                summary=ValidationSummaryEntity(
                    total_fields=0,
                    valid_fields=0,
                    invalid_fields=0,
                    error_count=1,
                    warning_count=0,
                    validation_rate=0.0,
                ),
                errors=[
                    ValidationErrorEntity(
                        field="root",
                        message=f"Invalid JSON format: {str(e)}",
                        error_type="json_parse_error",
                        invalid_value=data[:100] + "..." if len(data) > 100 else data,
                        expected_type="valid JSON",
                        location=["root"],
                    )
                ],
                processing_time=processing_time,
            )

        try:
            # スキーマ定義の解析
            if schema_type == "json_schema":
                schema = json.loads(schema_definition)
                return await self._validate_with_json_schema(
                    parsed_data,
                    schema,
                    validation_mode,
                    max_errors,
                    include_warnings,
                    custom_rules,
                    start_time,
                )
            elif schema_type == "custom":
                return await self._validate_with_custom_rules(
                    parsed_data,
                    schema_definition,
                    validation_mode,
                    max_errors,
                    include_warnings,
                    custom_rules,
                    start_time,
                )
            else:
                # 未対応のスキーマタイプ
                processing_time = time.time() - start_time
                return DataValidateResultEntity(
                    success=False,
                    is_valid=False,
                    schema_type=schema_type,
                    validation_mode=validation_mode,
                    summary=ValidationSummaryEntity(
                        total_fields=0,
                        valid_fields=0,
                        invalid_fields=0,
                        error_count=1,
                        warning_count=0,
                        validation_rate=0.0,
                    ),
                    errors=[
                        ValidationErrorEntity(
                            field="schema",
                            message=f"Unsupported schema type: {schema_type}",
                            error_type="unsupported_schema",
                            invalid_value=schema_type,
                            expected_type="json_schema or custom",
                            location=["schema_type"],
                        )
                    ],
                    processing_time=processing_time,
                )
        except Exception as e:
            processing_time = time.time() - start_time
            return DataValidateResultEntity(
                success=False,
                is_valid=False,
                schema_type=schema_type,
                validation_mode=validation_mode,
                summary=ValidationSummaryEntity(
                    total_fields=0,
                    valid_fields=0,
                    invalid_fields=0,
                    error_count=1,
                    warning_count=0,
                    validation_rate=0.0,
                ),
                errors=[
                    ValidationErrorEntity(
                        field="validation",
                        message=f"Validation error: {str(e)}",
                        error_type="validation_error",
                        invalid_value=str(e),
                        location=["validation"],
                    )
                ],
                processing_time=processing_time,
            )

    @private
    async def _validate_with_json_schema(
        self,
        data: Any,
        schema: dict[str, Any],
        validation_mode: str,
        max_errors: int,
        include_warnings: bool,
        custom_rules: dict[str, Any] | None,
        start_time: float,
    ) -> DataValidateResultEntity:
        """
        JSON Schemaによる検証

        Args:
            data: 検証対象のデータ
            schema: JSON Schema
            validation_mode: 検証モード
            max_errors: 最大エラー数
            include_warnings: 警告を含めるか
            custom_rules: カスタム検証ルール
            start_time: 開始時間

        Returns:
            検証結果エンティティ
        """

        errors: list[ValidationErrorEntity] = []
        warnings: list[ValidationWarningEntity] = []

        # JSON Schema検証
        validator = jsonschema.Draft7Validator(schema)
        if validation_mode == "report_only":
            # 報告モードでは構造分析のみ
            validation_errors = []
            warnings.append(
                ValidationWarningEntity(
                    field="validation_mode",
                    message="Report-only mode: No actual validation performed",
                    warning_type="mode_warning",
                    current_value="report_only",
                    suggestion="Use 'strict' or 'lenient' mode for actual validation",
                )
            )
        else:
            validation_errors = list(validator.iter_errors(data))
            # エラー変換（validation_modeに基づく制御）
            for i, error in enumerate(validation_errors):
                if i >= max_errors:
                    break

                # strictモードでは最初のエラーで停止
                if validation_mode == "strict" and i >= 1:
                    warnings.append(
                        ValidationWarningEntity(
                            field="validation_mode",
                            message="Strict mode: Validation stopped after first error",
                            warning_type="mode_warning",
                            current_value="strict",
                            suggestion="Use 'lenient' mode to see all errors",
                        )
                    )
                    break

                errors.append(
                    ValidationErrorEntity(
                        field=".".join(str(p) for p in error.absolute_path) or "root",
                        message=error.message,
                        error_type="schema_violation",
                        invalid_value=error.instance,
                        expected_type=str(error.schema.get("type", "unknown")),
                        location=list(error.absolute_path),
                    )
                )

        # カスタムルール適用
        if custom_rules and include_warnings:
            custom_warnings = self._apply_custom_rules(data, custom_rules)
            warnings.extend(custom_warnings)

        # 統計計算
        total_fields = self._count_fields(data)
        error_count = len(errors)
        warning_count = len(warnings)
        valid_fields = total_fields - error_count
        invalid_fields = error_count
        validation_rate = (
            (valid_fields / total_fields * 100) if total_fields > 0 else 0.0
        )

        processing_time = time.time() - start_time

        return DataValidateResultEntity(
            success=True,
            is_valid=len(validation_errors) == 0,
            schema_type="json_schema",
            validation_mode=validation_mode,
            summary=ValidationSummaryEntity(
                total_fields=total_fields,
                valid_fields=valid_fields,
                invalid_fields=invalid_fields,
                error_count=error_count,
                warning_count=warning_count,
                validation_rate=validation_rate,
            ),
            errors=errors,
            warnings=warnings,
            validated_data=self._get_validated_data(
                data, validation_mode, len(validation_errors) == 0
            ),
            processing_time=processing_time,
            schema_info={
                "schema_title": schema.get("title", "Untitled Schema"),
                "schema_version": schema.get("$schema", "Unknown"),
                "required_fields": schema.get("required", []),
            },
            recommendations=self._generate_recommendations(errors, warnings),
        )

    @private
    async def _validate_with_custom_rules(
        self,
        data: Any,
        schema_definition: str,
        validation_mode: str,
        max_errors: int,
        include_warnings: bool,
        custom_rules: dict[str, Any] | None,
        start_time: float,
    ) -> DataValidateResultEntity:
        """
        カスタムルールによる検証

        Args:
            data: 検証対象のデータ
            schema_definition: カスタムルール
            validation_mode: 検証モード
            max_errors: 最大エラー数
            include_warnings: 警告を含めるか
            custom_rules: カスタム検証ルール
            start_time: 開始時間

        Returns:
            検証結果エンティティ
        """

        errors: list[ValidationErrorEntity] = []
        warnings: list[ValidationWarningEntity] = []

        try:
            # カスタムルールの解析
            rules = json.loads(schema_definition)

            # validation_mode による処理制御
            if validation_mode == "report_only":
                # 報告モードでは構造分析のみ
                warnings.append(
                    ValidationWarningEntity(
                        field="validation_mode",
                        message="Report-only mode: No actual validation performed",
                        warning_type="mode_warning",
                        current_value="report_only",
                        suggestion="Use 'strict' or 'lenient' mode for actual validation",
                    )
                )
            else:
                # 基本的なデータ型チェック
                error_count = 0
                if isinstance(data, dict):
                    for field, rule in rules.items():
                        # max_errors チェック
                        if error_count >= max_errors:
                            warnings.append(
                                ValidationWarningEntity(
                                    field="validation",
                                    message=f"Maximum error limit ({max_errors}) reached, stopping validation",
                                    warning_type="limit_warning",
                                    current_value=str(error_count),
                                    suggestion="Increase max_errors to see all validation issues",
                                )
                            )
                            break

                        if field in data:
                            value = data[field]
                            if "type" in rule:
                                expected_type = rule["type"]
                                if not self._check_type(value, expected_type):
                                    errors.append(
                                        ValidationErrorEntity(
                                            field=field,
                                            message=f"Expected type {expected_type}, got {type(value).__name__}",
                                            error_type="type_mismatch",
                                            invalid_value=value,
                                            expected_type=expected_type,
                                            location=[field],
                                        )
                                    )
                                    error_count += 1

                                    # strictモードでは最初のエラーで停止
                                    if validation_mode == "strict":
                                        warnings.append(
                                            ValidationWarningEntity(
                                                field="validation_mode",
                                                message="Strict mode: Validation stopped after first error",
                                                warning_type="mode_warning",
                                                current_value="strict",
                                                suggestion="Use 'lenient' mode to see all errors",
                                            )
                                        )
                                        break
                        else:
                            if rule.get("required", False):
                                errors.append(
                                    ValidationErrorEntity(
                                        field=field,
                                        message=f"Required field '{field}' is missing",
                                        error_type="missing_field",
                                        invalid_value=None,
                                        expected_type=rule.get("type", "any"),
                                        location=[field],
                                    )
                                )
                                error_count += 1

                                # strictモードでは最初のエラーで停止
                                if validation_mode == "strict":
                                    warnings.append(
                                        ValidationWarningEntity(
                                            field="validation_mode",
                                            message="Strict mode: Validation stopped after first error",
                                            warning_type="mode_warning",
                                            current_value="strict",
                                            suggestion="Use 'lenient' mode to see all errors",
                                        )
                                    )
                                    break

            # custom_rules の適用（include_warnings が True の場合）
            if custom_rules and include_warnings:
                custom_warnings = self._apply_custom_rules(data, custom_rules)
                warnings.extend(custom_warnings)

        except json.JSONDecodeError:
            errors.append(
                ValidationErrorEntity(
                    field="schema",
                    message="Invalid custom rules format",
                    error_type="invalid_schema",
                    invalid_value=schema_definition,
                    expected_type="valid JSON",
                    location=["schema"],
                )
            )

        # 統計計算
        total_fields = self._count_fields(data)
        error_count = len(errors)
        warning_count = len(warnings)
        valid_fields = total_fields - error_count
        invalid_fields = error_count
        validation_rate = (
            (valid_fields / total_fields * 100) if total_fields > 0 else 0.0
        )

        processing_time = time.time() - start_time

        return DataValidateResultEntity(
            success=True,
            is_valid=len(errors) == 0,
            schema_type="custom",
            validation_mode=validation_mode,
            summary=ValidationSummaryEntity(
                total_fields=total_fields,
                valid_fields=valid_fields,
                invalid_fields=invalid_fields,
                error_count=error_count,
                warning_count=warning_count,
                validation_rate=validation_rate,
            ),
            errors=errors,
            warnings=warnings,
            validated_data=self._get_validated_data(
                data, validation_mode, len(errors) == 0
            ),
            processing_time=processing_time,
            schema_info={"custom_rules": True},
            recommendations=self._generate_recommendations(errors, warnings),
        )

    @private
    def _apply_custom_rules(
        self,
        data: Any,
        custom_rules: dict[str, Any],
    ) -> list[ValidationWarningEntity]:
        """
        カスタムルールを適用して警告を生成する

        Args:
            data: 検証対象のデータ
            custom_rules: カスタムルール

        Returns:
            警告一覧
        """

        warnings: list[ValidationWarningEntity] = []
        # 例: 文字列長の警告
        if "max_string_length" in custom_rules:
            max_length = custom_rules["max_string_length"]
            self._check_string_lengths(data, max_length, warnings, [])

        return warnings

    @private
    def _check_string_lengths(
        self,
        data: Any,
        max_length: int,
        warnings: list[ValidationWarningEntity],
        path: list[str],
    ) -> None:
        """
        文字列長をチェックする

        Args:
            data: 検証対象のデータ
            max_length: 最大文字列長
            warnings: 警告一覧
            path: パス

        Returns:
            None
        """

        if isinstance(data, str):
            if len(data) > max_length:
                warnings.append(
                    ValidationWarningEntity(
                        field=".".join(path) or "root",
                        message=f"String length ({len(data)}) exceeds recommended maximum ({max_length})",
                        warning_type="length_warning",
                        current_value=data,
                        suggestion=f"Consider shortening to {max_length} characters or less",
                    )
                )
        elif isinstance(data, dict):
            for key, value in data.items():
                self._check_string_lengths(value, max_length, warnings, path + [key])
        elif isinstance(data, list):
            for i, item in enumerate(data):
                self._check_string_lengths(item, max_length, warnings, path + [str(i)])

    @private
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """
        型チェックを行う

        Args:
            value: 検証対象の値
            expected_type: 期待する型

        Returns:
            True 型が一致する, False 型が一致しない
        """

        type_mapping = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict,
            "null": type(None),
        }
        expected_python_type = type_mapping.get(expected_type)
        if expected_python_type is None:
            return True  # 不明な型は通す

        return isinstance(value, expected_python_type)

    @private
    def _count_fields(self, data: Any) -> int:
        """
        フィールド数をカウントする

        Args:
            data: 検証対象のデータ

        Returns:
            フィールド数
        """

        if isinstance(data, dict):
            return len(data) + sum(self._count_fields(v) for v in data.values())
        elif isinstance(data, list):
            return sum(self._count_fields(item) for item in data)
        else:
            return 1

    @private
    def _generate_recommendations(
        self,
        errors: list[ValidationErrorEntity],
        warnings: list[ValidationWarningEntity],
    ) -> list[str]:
        """
        改善推奨事項を生成する

        Args:
            errors: エラー一覧
            warnings: 警告一覧

        Returns:
            改善推奨事項
        """

        recommendations = []
        if errors:
            recommendations.append(
                "修正が必要なエラーがあります。スキーマ定義と照らし合わせて確認してください。"
            )
            # 型エラーが多い場合
            type_errors = [e for e in errors if e.error_type == "type_mismatch"]
            if len(type_errors) > len(errors) * 0.5:
                recommendations.append(
                    "型エラーが多数検出されました。データ型を見直すことをお勧めします。"
                )

        if warnings:
            recommendations.append(
                "警告事項を確認し、データ品質の向上を検討してください。"
            )

        if not errors and not warnings:
            recommendations.append("データは完全に検証をパスしています。")

        return recommendations

    @private
    def _get_validated_data(
        self,
        data: Any,
        validation_mode: str,
        is_valid: bool,
    ) -> dict[str, Any] | None:
        """
        検証済みデータを取得する

        Args:
            data: 元のデータ
            validation_mode: 検証モード
            is_valid: データが有効かどうか

        Returns:
            検証済みデータ（モードに応じて）
        """

        if validation_mode == "strict":
            # strictモードでは有効な場合のみ返す
            return data if is_valid else None
        elif validation_mode == "lenient":
            # lenientモードでは常に返す（可能な限り修正済み）
            return data
        elif validation_mode == "report_only":
            # report_onlyモードでは構造のみ返す
            return {"data_structure": self._get_data_structure(data)}
        else:
            return None

    @private
    def _get_data_structure(self, data: Any) -> dict[str, Any]:
        """
        データ構造を取得する

        Args:
            data: 元のデータ

        Returns:
            データ構造情報
        """

        if isinstance(data, dict):
            return {
                "type": "object",
                "fields": {
                    key: self._get_data_structure(value) for key, value in data.items()
                },
                "field_count": len(data),
            }
        elif isinstance(data, list):
            return {
                "type": "array",
                "length": len(data),
                "item_types": list({type(item).__name__ for item in data})
                if data
                else [],
            }
        else:
            return {
                "type": type(data).__name__,
                "value_length": len(str(data)) if isinstance(data, str) else None,
            }

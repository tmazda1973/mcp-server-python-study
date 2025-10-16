import json
import time
from collections import defaultdict
from typing import Any

from typing_extensions import override

from app.api.application.repositories.mcp.data_processing import (
    DataAggregateRepositoryProtocol,
)
from app.api.domain.entities.mcp.data_processing import (
    AggregateGroupResultEntity,
    AggregateStatisticsEntity,
    DataAggregateResultEntity,
)
from app.decorators.access_control import private

__all__ = [
    "DataAggregateRepository",
]


class DataAggregateRepository(DataAggregateRepositoryProtocol):
    """
    リポジトリ（データ集計ツール）
    """

    @override
    async def aggregate_data(
        self,
        data: str,
        group_by: list[str],
        aggregate_functions: dict[str, str],
        filter_conditions: dict[str, Any] | None,
        sort_by: list[dict[str, str]],
        limit: int,
        include_totals: bool,
        include_metadata: bool,
        output_format: str,
    ) -> DataAggregateResultEntity:
        # データ集計を実行する
        start_time = time.time()

        try:
            # JSON データの解析
            parsed_data = json.loads(data)
            if not isinstance(parsed_data, list):
                raise ValueError("Data must be a JSON array")

        except json.JSONDecodeError as e:
            # JSON解析エラー
            processing_time = time.time() - start_time
            return DataAggregateResultEntity(
                success=False,
                output_format=output_format,
                statistics=AggregateStatisticsEntity(
                    total_records=0,
                    processed_records=0,
                    filtered_records=0,
                    groups_count=0,
                ),
                processing_time=processing_time,
                warnings=[f"JSON parse error: {str(e)}"],
                recommendations=[
                    "データが有効なJSON配列形式であることを確認してください。"
                ],
            )
        except ValueError as e:
            processing_time = time.time() - start_time
            return DataAggregateResultEntity(
                success=False,
                output_format=output_format,
                statistics=AggregateStatisticsEntity(
                    total_records=0,
                    processed_records=0,
                    filtered_records=0,
                    groups_count=0,
                ),
                processing_time=processing_time,
                warnings=[str(e)],
                recommendations=["データがJSON配列形式であることを確認してください。"],
            )

        try:
            # フィルタリング
            filtered_data = self._apply_filters(parsed_data, filter_conditions)

            # グループ化と集計
            grouped_results = self._group_and_aggregate(
                filtered_data, group_by, aggregate_functions
            )

            # ソート
            sorted_results = self._apply_sorting(grouped_results, sort_by)

            # 制限適用
            limited_results = sorted_results[:limit] if limit > 0 else sorted_results

            # 合計計算
            totals = (
                self._calculate_totals(grouped_results, aggregate_functions)
                if include_totals
                else {}
            )

            # 統計情報
            statistics = AggregateStatisticsEntity(
                total_records=len(parsed_data),
                processed_records=len(parsed_data),
                filtered_records=len(filtered_data),
                groups_count=len(grouped_results),
                unique_values=self._calculate_unique_values(filtered_data)
                if include_metadata
                else {},
            )

            # 警告と推奨事項
            warnings = self._generate_warnings(
                len(parsed_data),
                len(filtered_data),
                len(grouped_results),
                limit,
            )
            recommendations = self._generate_recommendations(
                statistics, aggregate_functions, group_by
            )

            processing_time = time.time() - start_time

            return DataAggregateResultEntity(
                success=True,
                output_format=output_format,
                results=limited_results,
                totals=totals,
                statistics=statistics,
                group_by_fields=group_by,
                aggregate_functions_used=aggregate_functions,
                sort_applied=sort_by,
                processing_time=processing_time,
                warnings=warnings,
                recommendations=recommendations,
            )

        except Exception as e:
            processing_time = time.time() - start_time
            return DataAggregateResultEntity(
                success=False,
                output_format=output_format,
                statistics=AggregateStatisticsEntity(
                    total_records=len(parsed_data) if "parsed_data" in locals() else 0,
                    processed_records=0,
                    filtered_records=0,
                    groups_count=0,
                ),
                processing_time=processing_time,
                warnings=[f"Aggregation error: {str(e)}"],
                recommendations=[
                    "集計設定を確認し、データ形式が正しいことを確認してください。"
                ],
            )

    @private
    def _apply_filters(
        self,
        data: list[dict[str, Any]],
        filter_conditions: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        """
        フィルター条件を適用する

        Args:
            data: 元のデータ
            filter_conditions: フィルター条件

        Returns:
            フィルター済みデータ
        """
        if not filter_conditions:
            return data

        filtered_data = []
        for record in data:
            if self._matches_filter(record, filter_conditions):
                filtered_data.append(record)

        return filtered_data

    @private
    def _matches_filter(
        self,
        record: dict[str, Any],
        conditions: dict[str, Any],
    ) -> bool:
        """
        レコードがフィルター条件にマッチするかチェック

        Args:
            record: チェック対象のレコード
            conditions: フィルター条件

        Returns:
            True マッチする, False マッチしない
        """

        for field, condition in conditions.items():
            if field not in record:
                return False

            value = record[field]
            if isinstance(condition, dict):
                # 複雑な条件（例: {"$gt": 10, "$lt": 100}）
                for op, expected in condition.items():
                    if op == "$gt" and not (value > expected):
                        return False
                    elif op == "$gte" and not (value >= expected):
                        return False
                    elif op == "$lt" and not (value < expected):
                        return False
                    elif op == "$lte" and not (value <= expected):
                        return False
                    elif op == "$eq" and not (value == expected):
                        return False
                    elif op == "$ne" and not (value != expected):
                        return False
                    elif op == "$in" and value not in expected:
                        return False
                    elif op == "$nin" and value in expected:
                        return False
            else:
                # 単純な等価条件
                if value != condition:
                    return False

        return True

    @private
    def _group_and_aggregate(
        self,
        data: list[dict[str, Any]],
        group_by: list[str],
        aggregate_functions: dict[str, str],
    ) -> list[AggregateGroupResultEntity]:
        """
        データをグループ化して集計する

        Args:
            data: 集計対象データ
            group_by: グループ化フィールド
            aggregate_functions: 集計関数

        Returns:
            集計結果
        """

        # グループ化
        groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
        for record in data:
            if group_by:
                # グループキーを作成
                group_key = tuple(record.get(field, None) for field in group_by)
            else:
                # グループ化なしの場合は全体を1つのグループとする
                group_key = ()

            groups[group_key].append(record)

        # 集計実行
        results = []
        for group_key_tuple, group_records in groups.items():
            # グループキーを辞書形式に変換
            if group_by:
                group_key_dict = {
                    field: group_key_tuple[i] for i, field in enumerate(group_by)
                }
            else:
                group_key_dict = {}

            # 集計値計算
            aggregated_values = {}
            for field, func in aggregate_functions.items():
                aggregated_values[field] = self._apply_aggregate_function(
                    group_records, field, func
                )

            results.append(
                AggregateGroupResultEntity(
                    group_key=group_key_dict,
                    aggregated_values=aggregated_values,
                    record_count=len(group_records),
                )
            )

        return results

    @private
    def _apply_aggregate_function(
        self,
        records: list[dict[str, Any]],
        field: str,
        func: str,
    ) -> Any:
        """
        集計関数を適用する

        Args:
            records: 対象レコード群
            field: 集計対象フィールド
            func: 集計関数名

        Returns:
            集計結果
        """

        values = [
            record.get(field)
            for record in records
            if field in record and record[field] is not None
        ]

        if not values:
            return None

        try:
            if func == "count":
                return len(values)
            elif func == "sum":
                return sum(float(v) for v in values if isinstance(v, (int, float)))
            elif func == "avg" or func == "average":
                numeric_values = [
                    float(v) for v in values if isinstance(v, (int, float))
                ]
                return (
                    sum(numeric_values) / len(numeric_values)
                    if numeric_values
                    else None
                )
            elif func == "min":
                return min(values)
            elif func == "max":
                return max(values)
            elif func == "first":
                return values[0] if values else None
            elif func == "last":
                return values[-1] if values else None
            elif func == "distinct" or func == "unique":
                return len({str(v) for v in values})
            else:
                return f"Unknown function: {func}"
        except (ValueError, TypeError) as e:
            return f"Error: {str(e)}"

    @private
    def _apply_sorting(
        self,
        results: list[AggregateGroupResultEntity],
        sort_by: list[dict[str, str]],
    ) -> list[AggregateGroupResultEntity]:
        """
        結果をソートする

        Args:
            results: ソート対象の結果
            sort_by: ソート条件

        Returns:
            ソート済み結果
        """

        if not sort_by:
            return results

        def sort_key(result: AggregateGroupResultEntity) -> tuple:
            key_values = []
            for sort_condition in sort_by:
                field = sort_condition.get("field", "")
                order = sort_condition.get("order", "asc")

                # グループキーまたは集計値から値を取得
                if field in result.group_key:
                    value = result.group_key[field]
                elif field in result.aggregated_values:
                    value = result.aggregated_values[field]
                elif field == "record_count":
                    value = result.record_count
                else:
                    value = 0  # デフォルト値

                # 降順の場合は値を反転
                if order == "desc":
                    if isinstance(value, (int, float)):
                        value = -value
                    elif isinstance(value, str):
                        # 文字列の場合は反転が困難なので、そのまま使用
                        pass

                key_values.append(value)

            return tuple(key_values)

        try:
            return sorted(results, key=sort_key)
        except Exception:
            # ソートに失敗した場合は元の順序を返す
            return results

    @private
    def _calculate_totals(
        self,
        results: list[AggregateGroupResultEntity],
        aggregate_functions: dict[str, str],
    ) -> dict[str, Any]:
        """
        全体の合計を計算する

        Args:
            results: 集計結果
            aggregate_functions: 集計関数

        Returns:
            合計値
        """

        totals = {}
        for field, func in aggregate_functions.items():
            values = []
            for result in results:
                if (
                    field in result.aggregated_values
                    and result.aggregated_values[field] is not None
                ):
                    values.append(result.aggregated_values[field])

            if values:
                if func in ["sum", "count"]:
                    totals[f"total_{field}"] = sum(
                        float(v) for v in values if isinstance(v, (int, float))
                    )
                elif func in ["avg", "average"]:
                    numeric_values = [
                        float(v) for v in values if isinstance(v, (int, float))
                    ]
                    totals[f"avg_{field}"] = (
                        sum(numeric_values) / len(numeric_values)
                        if numeric_values
                        else None
                    )
                elif func == "min":
                    totals[f"min_{field}"] = min(values)
                elif func == "max":
                    totals[f"max_{field}"] = max(values)

        # 全体のレコード数
        totals["total_records"] = sum(result.record_count for result in results)
        totals["total_groups"] = len(results)

        return totals

    @private
    def _calculate_unique_values(
        self,
        data: list[dict[str, Any]],
    ) -> dict[str, int]:
        """
        各フィールドのユニーク値数を計算する

        Args:
            data: 対象データ

        Returns:
            フィールド別ユニーク値数
        """

        unique_values = {}
        field_values: dict[str, set] = defaultdict(set)
        for record in data:
            for field, value in record.items():
                field_values[field].add(str(value))

        for field, values in field_values.items():
            unique_values[field] = len(values)

        return unique_values

    @private
    def _generate_warnings(
        self,
        total_records: int,
        filtered_records: int,
        groups_count: int,
        limit: int,
    ) -> list[str]:
        """
        警告メッセージを生成する

        Args:
            total_records: 総レコード数
            filtered_records: フィルター後レコード数
            groups_count: グループ数
            limit: 制限数

        Returns:
            警告メッセージ一覧
        """

        warnings = []
        if filtered_records < total_records:
            filtered_ratio = (filtered_records / total_records) * 100
            warnings.append(
                f"フィルター条件により {total_records - filtered_records} 件のレコードが除外されました "
                f"（{filtered_ratio:.1f}% のデータが処理されました）"
            )

        if groups_count > limit > 0:
            warnings.append(
                f"結果が制限により {limit} グループに制限されました（全 {groups_count} グループ中）"
            )

        if groups_count > 1000:
            warnings.append(
                "グループ数が多いため、処理時間が長くなる可能性があります。"
            )

        return warnings

    @private
    def _generate_recommendations(
        self,
        statistics: AggregateStatisticsEntity,
        aggregate_functions: dict[str, str],
        group_by: list[str],
    ) -> list[str]:
        """
        改善推奨事項を生成する

        Args:
            statistics: 統計情報
            aggregate_functions: 集計関数
            group_by: グループ化フィールド

        Returns:
            推奨事項一覧
        """

        recommendations = []
        if statistics.groups_count == 1 and group_by:
            recommendations.append(
                "グループ化フィールドの値が単一のため、グループ化の効果がありません。"
            )

        if statistics.groups_count > 100:
            recommendations.append(
                "グループ数が多いため、より上位レベルでのグループ化を検討してください。"
            )

        if not aggregate_functions:
            recommendations.append(
                "集計関数が指定されていません。count、sum、avg等の関数を指定してください。"
            )

        if statistics.filtered_records == 0:
            recommendations.append(
                "フィルター条件が厳しすぎる可能性があります。条件を緩和することを検討してください。"
            )

        if not recommendations:
            recommendations.append("集計処理が正常に完了しました。")

        return recommendations

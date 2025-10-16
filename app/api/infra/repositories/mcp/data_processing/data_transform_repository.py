import csv
import json
import time
import xml.etree.ElementTree as ET
from io import StringIO
from typing import Any, Dict, List, Optional

import yaml
from typing_extensions import override

from app.api.application.repositories.mcp.data_processing import (
    DataTransformRepositoryProtocol,
)
from app.api.domain.entities.mcp.data_processing import DataTransformResultEntity
from app.decorators.access_control import private

__all__ = [
    "DataTransformRepository",
]


class DataTransformRepository(DataTransformRepositoryProtocol):
    """
    リポジトリ（データ変換ツール）
    """

    @override
    async def transform_data(
        self,
        data: str,
        from_format: str,
        to_format: str,
        options: Optional[Dict[str, Any]] = None,
        field_mapping: Optional[Dict[str, str]] = None,
        include_headers: bool = True,
        delimiter: str = ",",
        encoding: str = "utf-8",
    ) -> DataTransformResultEntity:
        # データ変換を実行する
        start_time = time.time()
        warnings: List[str] = []
        try:
            # 1. データ解析
            parsed_data = await self._parse_data(
                data, from_format, delimiter, include_headers
            )

            # 2. フィールドマッピング適用
            if field_mapping:
                parsed_data, applied_mappings = await self._apply_field_mapping(
                    parsed_data, field_mapping
                )
            else:
                applied_mappings = None

            # 3. データ変換
            transformed_data = await self._convert_data(
                parsed_data, to_format, delimiter, include_headers
            )

            # 4. 統計情報計算
            record_count = len(parsed_data) if isinstance(parsed_data, list) else 1
            field_count = (
                len(parsed_data[0])
                if isinstance(parsed_data, list) and parsed_data
                else len(parsed_data)
                if isinstance(parsed_data, dict)
                else 0
            )

            processing_time = time.time() - start_time

            return DataTransformResultEntity(
                success=True,
                transformed_data=transformed_data,
                from_format=from_format,
                to_format=to_format,
                record_count=record_count,
                field_count=field_count,
                processing_time=processing_time,
                applied_mappings=applied_mappings,
                warnings=warnings if warnings else None,
            )

        except Exception as e:
            processing_time = time.time() - start_time
            return DataTransformResultEntity(
                success=False,
                transformed_data="",
                from_format=from_format,
                to_format=to_format,
                record_count=0,
                field_count=0,
                processing_time=processing_time,
                error=f"データ変換エラー: {str(e)}",
            )

    @private
    async def _parse_data(
        self,
        data: str,
        format_type: str,
        delimiter: str,
        include_headers: bool,
    ) -> Any:
        """
        データを解析する

        Args:
            data: データ
            format_type: フォーマットタイプ
            delimiter: 区切り文字
            include_headers: ヘッダーを含めるか

        Returns:
            解析されたデータ
        """

        if format_type == "json":
            return json.loads(data)
        elif format_type == "csv":
            return await self._parse_csv(data, delimiter, include_headers)
        elif format_type == "xml":
            return await self._parse_xml(data)
        elif format_type == "yaml":
            return yaml.safe_load(data)
        else:
            raise ValueError(f"サポートされていないフォーマット: {format_type}")

    @private
    async def _parse_csv(
        self,
        data: str,
        delimiter: str,
        include_headers: bool,
    ) -> List[Dict[str, Any]]:
        """
        CSV データを解析する

        Args:
            data: データ
            delimiter: 区切り文字
            include_headers: ヘッダーを含めるか

        Returns:
            解析されたデータ
        """

        reader = csv.DictReader(StringIO(data), delimiter=delimiter)
        if not include_headers:
            # ヘッダーがない場合は、列番号をキーとして使用
            lines = data.strip().split("\n")
            if not lines:
                return []

            first_line = lines[0].split(delimiter)
            headers = [f"column_{i}" for i in range(len(first_line))]

            result = []
            for line in lines:
                values = line.split(delimiter)
                row = {
                    headers[i]: values[i] if i < len(values) else ""
                    for i in range(len(headers))
                }
                result.append(row)
            return result
        else:
            return list(reader)

    @private
    async def _parse_xml(self, data: str) -> Dict[str, Any]:
        """
        XMLデータを解析する

        Args:
            data: データ

        Returns:
            解析されたデータ
        """

        root = ET.fromstring(data)
        return await self._xml_to_dict(root)

    @private
    async def _xml_to_dict(self, element: ET.Element) -> Dict[str, Any]:
        """
        XML要素を辞書に変換する

        Args:
            element: XML要素

        Returns:
            解析されたデータ
        """

        result: Dict[str, Any] = {}
        # 属性を追加
        if element.attrib:
            result.update(element.attrib)

        # テキスト内容を追加
        if element.text and element.text.strip():
            if len(element) == 0:  # 子要素がない場合
                return element.text.strip()
            else:
                result["_text"] = element.text.strip()

        # 子要素を処理
        for child in element:
            child_data = await self._xml_to_dict(child)
            if child.tag in result:
                # 同じタグが複数ある場合はリストにする
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data

        return result

    @private
    async def _apply_field_mapping(
        self,
        data: Any,
        field_mapping: Dict[str, str],
    ) -> tuple[Any, Dict[str, str]]:
        """
        フィールドマッピングを適用する

        Args:
            data: データ
            field_mapping: フィールドマッピング

        Returns:
            適用されたデータ
            適用されたフィールドマッピング
        """

        applied_mappings = {}
        if isinstance(data, list):
            # リスト形式のデータ
            mapped_data = []
            for item in data:
                if isinstance(item, dict):
                    mapped_item = {}
                    for old_key, value in item.items():
                        new_key = field_mapping.get(old_key, old_key)
                        mapped_item[new_key] = value
                        if old_key in field_mapping:
                            applied_mappings[old_key] = new_key
                    mapped_data.append(mapped_item)
                else:
                    mapped_data.append(item)
            return mapped_data, applied_mappings
        elif isinstance(data, dict):
            # 辞書形式のデータ
            mapped_data = {}
            for old_key, value in data.items():
                new_key = field_mapping.get(old_key, old_key)
                mapped_data[new_key] = value
                if old_key in field_mapping:
                    applied_mappings[old_key] = new_key
            return mapped_data, applied_mappings
        else:
            return data, applied_mappings

    @private
    async def _convert_data(
        self,
        data: Any,
        format_type: str,
        delimiter: str,
        include_headers: bool,
    ) -> str:
        """
        データを指定フォーマットに変換する

        Args:
            data: データ
            format_type: フォーマットタイプ
            delimiter: 区切り文字
            include_headers: ヘッダーを含めるか

        Returns:
            変換されたデータ
            変換されたフィールドマッピング
        """

        if format_type == "json":
            return json.dumps(data, ensure_ascii=False, indent=2)
        elif format_type == "csv":
            return await self._convert_to_csv(data, delimiter, include_headers)
        elif format_type == "xml":
            return await self._convert_to_xml(data)
        elif format_type == "yaml":
            return yaml.dump(data, default_flow_style=False, allow_unicode=True)
        else:
            raise ValueError(f"サポートされていないフォーマット: {format_type}")

    @private
    async def _convert_to_csv(
        self,
        data: Any,
        delimiter: str,
        include_headers: bool,
    ) -> str:
        """
        データをCSVに変換する

        Args:
            data: データ
            delimiter: 区切り文字
            include_headers: ヘッダーを含めるか

        Returns:
            変換されたデータ
            変換されたフィールドマッピング
        """

        output = StringIO()
        if isinstance(data, list) and data:
            if isinstance(data[0], dict):
                # 辞書のリスト
                fieldnames = list(data[0].keys())
                writer = csv.DictWriter(
                    output,
                    fieldnames=fieldnames,
                    delimiter=delimiter,
                )

                if include_headers:
                    writer.writeheader()

                for row in data:
                    writer.writerow(row)
            else:
                # 値のリスト
                writer = csv.writer(output, delimiter=delimiter)
                for row in data:
                    if isinstance(row, (list, tuple)):
                        writer.writerow(row)
                    else:
                        writer.writerow([row])
        elif isinstance(data, dict):
            # 単一の辞書
            writer = csv.DictWriter(
                output,
                fieldnames=list(data.keys()),
                delimiter=delimiter,
            )
            if include_headers:
                writer.writeheader()
            writer.writerow(data)
        else:
            # その他の形式
            writer = csv.writer(output, delimiter=delimiter)
            writer.writerow([str(data)])

        return output.getvalue()

    @private
    async def _convert_to_xml(
        self,
        data: Any,
        root_name: str = "root",
    ) -> str:
        """
        データをXMLに変換する

        Args:
            data: データ
            root_name: ルート要素名

        Returns:
            変換されたデータ
        """

        root = ET.Element(root_name)
        await self._dict_to_xml(data, root)
        return ET.tostring(root, encoding="unicode")

    @private
    async def _dict_to_xml(
        self,
        data: Any,
        parent: ET.Element,
    ) -> None:
        """
        辞書をXML要素に変換する

        Args:
            data: データ
            parent: 親要素

        Returns:
            変換されたデータ
        """

        if isinstance(data, dict):
            for key, value in data.items():
                if key.startswith("_"):
                    # 特殊キー（属性やテキスト）の処理
                    if key == "_text":
                        parent.text = str(value)
                    else:
                        parent.set(key[1:], str(value))
                else:
                    child = ET.SubElement(parent, str(key))
                    await self._dict_to_xml(value, child)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                child = ET.SubElement(parent, f"item_{i}")
                await self._dict_to_xml(item, child)
        else:
            parent.text = str(data)

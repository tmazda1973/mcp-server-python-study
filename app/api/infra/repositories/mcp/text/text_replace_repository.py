import re
import time
from typing import List

from typing_extensions import override

from app.api.application.repositories.mcp.text import TextReplaceRepositoryProtocol
from app.api.domain.entities.mcp.text import (
    TextReplaceMatchEntity,
    TextReplaceResultEntity,
)
from app.decorators.access_control import private

__all__ = [
    "TextReplaceRepository",
]


class TextReplaceRepository(TextReplaceRepositoryProtocol):
    """
    リポジトリ（テキスト置換ツール）
    """

    @override
    async def replace_text(
        self,
        text: str,
        pattern: str,
        replacement: str,
        case_sensitive: bool = False,
        use_regex: bool = False,
        whole_word: bool = False,
        max_replacements: int = 0,
        preview_only: bool = False,
    ) -> TextReplaceResultEntity:
        start_time = time.time()
        try:
            # テキストを行に分割
            lines = text.splitlines()
            total_lines = len(lines)
            matches: List[TextReplaceMatchEntity] = []
            replacement_count = 0
            modified_lines_count = 0
            result_lines = lines.copy()

            # 検索パターンを準備
            search_pattern = self._prepare_pattern(
                pattern, case_sensitive, use_regex, whole_word
            )

            # 各行を処理
            for line_idx, line in enumerate(lines):
                line_number = line_idx + 1
                original_line = line
                current_line = line
                line_modified = False

                # パターンマッチングと置換
                if use_regex:
                    # 正規表現による置換
                    regex_matches = list(search_pattern.finditer(original_line))

                    if regex_matches:
                        # 制限チェック
                        actual_matches = regex_matches
                        if max_replacements > 0:
                            remaining_replacements = (
                                max_replacements - replacement_count
                            )
                            actual_matches = regex_matches[:remaining_replacements]

                        if actual_matches:
                            # 置換実行
                            if not preview_only:
                                # 制限数だけ置換
                                current_line = search_pattern.sub(
                                    replacement,
                                    original_line,
                                    count=len(actual_matches),
                                )

                            # 置換後の行を計算（プレビュー用）
                            replaced_line_preview = search_pattern.sub(
                                replacement, original_line, count=len(actual_matches)
                            )

                            # マッチ情報を記録
                            for match in actual_matches:
                                original_text = match.group()
                                replacement_text = match.expand(replacement)

                                match_entity = TextReplaceMatchEntity(
                                    line_number=line_number,
                                    original_line=original_line,
                                    replaced_line=current_line
                                    if not preview_only
                                    else replaced_line_preview,
                                    match_start=match.start(),
                                    match_end=match.end(),
                                    original_text=original_text,
                                    replacement_text=replacement_text,
                                )
                                matches.append(match_entity)
                                replacement_count += 1
                                line_modified = True

                                if (
                                    max_replacements > 0
                                    and replacement_count >= max_replacements
                                ):
                                    break

                else:
                    # 単純な文字列置換
                    search_text = pattern
                    pos = 0

                    while True:
                        if (
                            max_replacements > 0
                            and replacement_count >= max_replacements
                        ):
                            break

                        # 検索実行
                        if case_sensitive:
                            found_pos = current_line.find(search_text, pos)
                        else:
                            found_pos = current_line.lower().find(
                                search_text.lower(), pos
                            )

                        if found_pos == -1:
                            break

                        # 単語全体マッチのチェック
                        if whole_word and not self._is_whole_word_match(
                            current_line, found_pos, len(search_text)
                        ):
                            pos = found_pos + 1
                            continue

                        # 実際のマッチテキストを取得
                        actual_match = current_line[
                            found_pos : found_pos + len(search_text)
                        ]

                        # 置換実行（プレビューでない場合）
                        if not preview_only:
                            before = current_line[:found_pos]
                            after = current_line[found_pos + len(search_text) :]
                            current_line = before + replacement + after

                        # マッチエンティティを作成
                        replaced_line = (
                            current_line
                            if not preview_only
                            else self._simulate_replacement(
                                original_line,
                                found_pos,
                                found_pos + len(search_text),
                                replacement,
                            )
                        )
                        match_entity = TextReplaceMatchEntity(
                            line_number=line_number,
                            original_line=original_line,
                            replaced_line=replaced_line,
                            match_start=found_pos,
                            match_end=found_pos + len(search_text),
                            original_text=actual_match,
                            replacement_text=replacement,
                        )
                        matches.append(match_entity)
                        replacement_count += 1
                        line_modified = True

                        # 次の検索位置を更新
                        if not preview_only:
                            pos = found_pos + len(replacement)
                        else:
                            pos = found_pos + len(search_text)

                # 結果行を更新
                if line_modified:
                    modified_lines_count += 1
                    if not preview_only:
                        result_lines[line_idx] = current_line

                if max_replacements > 0 and replacement_count >= max_replacements:
                    break

            processing_time = time.time() - start_time
            truncated = max_replacements > 0 and replacement_count >= max_replacements

            # 結果テキストを構築
            result_text = "\n".join(result_lines) if not preview_only else text

            return TextReplaceResultEntity(
                success=True,
                pattern=pattern,
                replacement=replacement,
                total_replacements=replacement_count,
                total_lines=total_lines,
                modified_lines=modified_lines_count,
                matches=matches,
                result_text=result_text,
                truncated=truncated,
                preview_only=preview_only,
                processing_time=processing_time,
                case_sensitive=case_sensitive,
                use_regex=use_regex,
                whole_word=whole_word,
            )

        except re.error as e:
            processing_time = time.time() - start_time
            return TextReplaceResultEntity(
                success=False,
                pattern=pattern,
                replacement=replacement,
                total_replacements=0,
                total_lines=len(text.splitlines()),
                modified_lines=0,
                matches=[],
                result_text=text,
                truncated=False,
                preview_only=preview_only,
                processing_time=processing_time,
                case_sensitive=case_sensitive,
                use_regex=use_regex,
                whole_word=whole_word,
                error=f"正規表現エラー: {str(e)}",
            )
        except Exception as e:
            processing_time = time.time() - start_time
            return TextReplaceResultEntity(
                success=False,
                pattern=pattern,
                replacement=replacement,
                total_replacements=0,
                total_lines=len(text.splitlines()) if text else 0,
                modified_lines=0,
                matches=[],
                result_text=text,
                truncated=False,
                preview_only=preview_only,
                processing_time=processing_time,
                case_sensitive=case_sensitive,
                use_regex=use_regex,
                whole_word=whole_word,
                error=f"置換エラー: {str(e)}",
            )

    @private
    def _prepare_pattern(
        self,
        pattern: str,
        case_sensitive: bool,
        use_regex: bool,
        whole_word: bool,
    ) -> re.Pattern:
        """
        検索パターンを準備する
        """
        if not use_regex:
            # 正規表現でない場合は、特殊文字をエスケープ
            pattern = re.escape(pattern)

        if whole_word:
            # 単語境界を追加
            pattern = r"\b" + pattern + r"\b"

        flags = 0 if case_sensitive else re.IGNORECASE
        return re.compile(pattern, flags)

    @private
    def _is_whole_word_match(
        self,
        line: str,
        pos: int,
        length: int,
    ) -> bool:
        """
        単語全体マッチかどうかをチェック
        """
        # 前の文字をチェック
        if pos > 0 and line[pos - 1].isalnum():
            return False

        # 後の文字をチェック
        end_pos = pos + length
        if end_pos < len(line) and line[end_pos].isalnum():
            return False

        return True

    @private
    def _simulate_replacement(
        self,
        line: str,
        start: int,
        end: int,
        replacement: str,
    ) -> str:
        """
        プレビュー用の置換シミュレーション
        """
        return line[:start] + replacement + line[end:]

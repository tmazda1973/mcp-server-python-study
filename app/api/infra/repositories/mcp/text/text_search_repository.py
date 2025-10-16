import re
import time
from typing import List

from typing_extensions import override

from app.api.application.repositories.mcp.text import TextSearchRepositoryProtocol
from app.api.domain.entities.mcp.text import (
    TextSearchMatchEntity,
    TextSearchResultEntity,
)
from app.decorators.access_control import private

__all__ = [
    "TextSearchRepository",
]


class TextSearchRepository(TextSearchRepositoryProtocol):
    """
    リポジトリ（テキスト検索ツール）
    """

    @override
    async def search_text(
        self,
        text: str,
        pattern: str,
        case_sensitive: bool = False,
        use_regex: bool = False,
        whole_word: bool = False,
        max_matches: int = 0,
        include_line_numbers: bool = True,
        context_lines: int = 0,
    ) -> TextSearchResultEntity:
        start_time = time.time()
        try:
            # テキストを行に分割
            lines = text.splitlines()
            total_lines = len(lines)
            matches: List[TextSearchMatchEntity] = []
            match_count = 0

            # 検索パターンを準備
            search_pattern = self._prepare_pattern(
                pattern, case_sensitive, use_regex, whole_word
            )

            # 各行を検索
            for line_idx, line in enumerate(lines):
                line_number = line_idx + 1

                # パターンマッチング
                if use_regex:
                    regex_matches = list(search_pattern.finditer(line))
                else:
                    # 単純な文字列検索
                    regex_matches = []
                    start = 0
                    while True:
                        if case_sensitive:
                            pos = line.find(pattern, start)
                        else:
                            pos = line.lower().find(pattern.lower(), start)

                        if pos == -1:
                            break

                        # 単語全体マッチのチェック
                        if whole_word and not self._is_whole_word_match(
                            line, pos, len(pattern)
                        ):
                            start = pos + 1
                            continue

                        # マッチオブジェクトを模擬
                        class SimpleMatch:
                            def __init__(self, start_pos, end_pos, text):
                                self.start_pos = start_pos
                                self.end_pos = end_pos
                                self.text = text

                            def start(self):
                                return self.start_pos

                            def end(self):
                                return self.end_pos

                            def group(self):
                                return self.text

                        regex_matches.append(
                            SimpleMatch(
                                pos, pos + len(pattern), line[pos : pos + len(pattern)]
                            )
                        )
                        start = pos + 1

                # マッチした場合の処理
                for match in regex_matches:
                    if max_matches > 0 and match_count >= max_matches:
                        break

                    # コンテキスト行を取得
                    context_before = None
                    context_after = None
                    if context_lines > 0:
                        start_ctx = max(0, line_idx - context_lines)
                        end_ctx = min(total_lines, line_idx + context_lines + 1)

                        context_before = (
                            lines[start_ctx:line_idx] if start_ctx < line_idx else []
                        )
                        context_after = (
                            lines[line_idx + 1 : end_ctx]
                            if line_idx + 1 < end_ctx
                            else []
                        )

                    # マッチエンティティを作成
                    match_entity = TextSearchMatchEntity(
                        line_number=line_number,
                        line_content=line,
                        match_start=match.start(),
                        match_end=match.end(),
                        matched_text=match.group(),
                        context_before=context_before,
                        context_after=context_after,
                    )
                    matches.append(match_entity)
                    match_count += 1

                if max_matches > 0 and match_count >= max_matches:
                    break

            search_time = time.time() - start_time
            truncated = max_matches > 0 and match_count >= max_matches

            return TextSearchResultEntity(
                success=True,
                pattern=pattern,
                total_matches=match_count,
                total_lines=total_lines,
                matches=matches,
                truncated=truncated,
                search_time=search_time,
                case_sensitive=case_sensitive,
                use_regex=use_regex,
                whole_word=whole_word,
            )

        except re.error as e:
            search_time = time.time() - start_time
            return TextSearchResultEntity(
                success=False,
                pattern=pattern,
                total_matches=0,
                total_lines=len(text.splitlines()),
                matches=[],
                truncated=False,
                search_time=search_time,
                case_sensitive=case_sensitive,
                use_regex=use_regex,
                whole_word=whole_word,
                error=f"正規表現エラー: {str(e)}",
            )
        except Exception as e:
            search_time = time.time() - start_time
            return TextSearchResultEntity(
                success=False,
                pattern=pattern,
                total_matches=0,
                total_lines=len(text.splitlines()) if text else 0,
                matches=[],
                truncated=False,
                search_time=search_time,
                case_sensitive=case_sensitive,
                use_regex=use_regex,
                whole_word=whole_word,
                error=f"検索エラー: {str(e)}",
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
    def _is_whole_word_match(self, line: str, pos: int, length: int) -> bool:
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

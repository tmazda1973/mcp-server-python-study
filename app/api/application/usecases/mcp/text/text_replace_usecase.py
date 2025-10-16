from typing import List

from typing_extensions import override

from app.api.application.presenters import PresenterProtocol
from app.api.application.repositories.mcp.text import TextReplaceRepositoryProtocol
from app.api.application.usecases.abstract_async_usecase import AbstractAsyncUsecase
from app.api.presentation.request.mcp.text import TextReplaceRequest
from app.api.presentation.response.mcp.text import TextReplaceMatch, TextReplaceResponse

__all__ = [
    "TextReplaceUsecase",
]


class TextReplaceUsecase(
    AbstractAsyncUsecase[
        PresenterProtocol[
            TextReplaceRequest,
            TextReplaceResponse,
        ]
    ]
):
    """
    ユースケース（テキスト置換ツール）
    """

    def __init__(self, repository: TextReplaceRepositoryProtocol) -> None:
        self._repository = repository

    @override
    async def execute(
        self,
        presenter: PresenterProtocol[
            TextReplaceRequest,
            TextReplaceResponse,
        ],
    ) -> None:
        # テキスト置換を実行する
        request = presenter.request
        result = await self._repository.replace_text(
            text=request.text,
            pattern=request.pattern,
            replacement=request.replacement,
            case_sensitive=request.case_sensitive,
            use_regex=request.use_regex,
            whole_word=request.whole_word,
            max_replacements=request.max_replacements,
            preview_only=request.preview_only,
        )

        # エンティティからレスポンスに変換
        matches: List[TextReplaceMatch] = []
        for match_entity in result.matches:
            matches.append(
                TextReplaceMatch(
                    line_number=match_entity.line_number,
                    original_line=match_entity.original_line,
                    replaced_line=match_entity.replaced_line,
                    match_start=match_entity.match_start,
                    match_end=match_entity.match_end,
                    original_text=match_entity.original_text,
                    replacement_text=match_entity.replacement_text,
                )
            )

        presenter.response = TextReplaceResponse(
            success=result.success,
            pattern=result.pattern,
            replacement=result.replacement,
            total_replacements=result.total_replacements,
            total_lines=result.total_lines,
            modified_lines=result.modified_lines,
            matches=matches,
            result_text=result.result_text,
            truncated=result.truncated,
            preview_only=result.preview_only,
            processing_time=result.processing_time,
            case_sensitive=result.case_sensitive,
            use_regex=result.use_regex,
            whole_word=result.whole_word,
            error=result.error,
            warning=result.warning,
        )

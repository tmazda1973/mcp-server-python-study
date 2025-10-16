from typing_extensions import override

from app.api.application.presenters import PresenterProtocol
from app.api.application.repositories.mcp.text import TextSearchRepositoryProtocol
from app.api.application.usecases.abstract_async_usecase import AbstractAsyncUsecase
from app.api.presentation.request.mcp.text import TextSearchRequest
from app.api.presentation.response.mcp.text import TextSearchMatch, TextSearchResponse

__all__ = [
    "TextSearchUsecase",
]


class TextSearchUsecase(
    AbstractAsyncUsecase[
        PresenterProtocol[
            TextSearchRequest,
            TextSearchResponse,
        ]
    ]
):
    """
    ユースケース（テキスト検索ツール）
    """

    def __init__(self, repository: TextSearchRepositoryProtocol) -> None:
        self._repository = repository

    @override
    async def execute(
        self,
        presenter: PresenterProtocol[
            TextSearchRequest,
            TextSearchResponse,
        ],
    ) -> None:
        # テキスト検索を実行する
        request = presenter.request
        result = await self._repository.search_text(
            text=request.text,
            pattern=request.pattern,
            case_sensitive=request.case_sensitive,
            use_regex=request.use_regex,
            whole_word=request.whole_word,
            max_matches=request.max_matches,
            include_line_numbers=request.include_line_numbers,
            context_lines=request.context_lines,
        )

        # レスポンスデータを構築する
        matches = [
            TextSearchMatch(
                line_number=match.line_number,
                line_content=match.line_content,
                match_start=match.match_start,
                match_end=match.match_end,
                matched_text=match.matched_text,
                context_before=match.context_before,
                context_after=match.context_after,
            )
            for match in result.matches
        ]

        presenter.response = TextSearchResponse(
            success=result.success,
            pattern=result.pattern,
            total_matches=result.total_matches,
            total_lines=result.total_lines,
            matches=matches,
            truncated=result.truncated,
            search_time=result.search_time,
            case_sensitive=result.case_sensitive,
            use_regex=result.use_regex,
            whole_word=result.whole_word,
            error=result.error,
            warning=result.warning,
        )

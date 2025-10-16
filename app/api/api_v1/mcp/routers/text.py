"""
テキスト処理ツール用MCPルーター
- text_search: テキスト検索
- text_replace: テキスト置換
- text_analyze: テキスト分析
"""

from fastapi import APIRouter, Depends

from app.api.application.presenters import PresenterProtocol
from app.api.application.usecases.mcp.text import (
    TextAnalyzeUsecase,
    TextReplaceUsecase,
    TextSearchUsecase,
)
from app.api.di.mcp.text import (
    provide_text_analyze_presenter,
    provide_text_analyze_usecase,
    provide_text_replace_presenter,
    provide_text_replace_usecase,
    provide_text_search_presenter,
    provide_text_search_usecase,
)
from app.api.presentation.request.mcp.text import (
    TextAnalyzeRequest,
    TextReplaceRequest,
    TextSearchRequest,
)
from app.api.presentation.response.mcp.text import (
    TextAnalyzeResponse,
    TextReplaceResponse,
    TextSearchResponse,
)

router = APIRouter()


@router.post(
    "/search",
    operation_id="text_search",
    description="テキスト内で指定したパターンを検索します。正規表現、大文字小文字区別、全単語マッチに対応。",
    summary="テキスト検索ツール",
)
async def text_search(
    request: TextSearchRequest,
    presenter: PresenterProtocol[
        TextSearchRequest,
        TextSearchResponse,
    ] = Depends(provide_text_search_presenter),
    usecase: TextSearchUsecase = Depends(provide_text_search_usecase),
) -> TextSearchResponse:
    """
    テキスト検索（MCPツール）

    テキスト内で指定したパターンを検索し、マッチした箇所を返します：
    - 正規表現パターン対応
    - 大文字小文字区別の制御
    - 全単語マッチ機能
    - 行番号・コンテキスト情報付き

    Note:
        このエンドポイントは /mcp 経由でMCPツールとして利用可能です
    """
    presenter.request = request
    await usecase.execute(presenter)
    return presenter.response


@router.post(
    "/replace",
    operation_id="text_replace",
    description="テキスト内の文字列を指定したパターンで置換します。正規表現、全単語マッチ、プレビューモードに対応。",
    summary="テキスト置換ツール",
)
async def text_replace(
    request: TextReplaceRequest,
    presenter: PresenterProtocol[
        TextReplaceRequest,
        TextReplaceResponse,
    ] = Depends(provide_text_replace_presenter),
    usecase: TextReplaceUsecase = Depends(provide_text_replace_usecase),
) -> TextReplaceResponse:
    """
    テキスト置換（MCPツール）

    テキスト内の文字列を指定したパターンで置換します：
    - 正規表現置換対応
    - グループ参照（$1, $2等）
    - プレビューモード（実際に置換しない）
    - 置換回数制限

    Note:
        このエンドポイントは /mcp 経由でMCPツールとして利用可能です
    """
    presenter.request = request
    await usecase.execute(presenter)
    return presenter.response


@router.post(
    "/analyze",
    operation_id="text_analyze",
    description="テキストの統計情報、単語頻度、読みやすさ指標、感情分析、言語検出などの包括的な分析を実行します。",
    summary="テキスト分析ツール",
)
async def text_analyze(
    request: TextAnalyzeRequest,
    presenter: PresenterProtocol[
        TextAnalyzeRequest,
        TextAnalyzeResponse,
    ] = Depends(provide_text_analyze_presenter),
    usecase: TextAnalyzeUsecase = Depends(provide_text_analyze_usecase),
) -> TextAnalyzeResponse:
    """
    テキスト分析（MCPツール）

    テキストの包括的な分析を実行します：
    - 基本統計（文字数、行数、単語数）
    - 単語頻度分析
    - 読みやすさ指標（Flesch Reading Ease等）
    - 簡易感情分析
    - 言語検出

    Note:
        このエンドポイントは /mcp 経由でMCPツールとして利用可能です
    """
    presenter.request = request
    await usecase.execute(presenter)
    return presenter.response

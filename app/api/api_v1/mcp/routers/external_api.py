"""
外部APIツール用MCPルーター
- http_request: HTTPリクエスト送信
- rest_api_call: REST API呼び出し
- webhook_send: Webhook送信
"""

from fastapi import APIRouter, Depends

from app.api.application.presenters import PresenterProtocol
from app.api.application.usecases.mcp.external_api import (
    HttpRequestUsecase,
    RestApiUsecase,
    WebhookUsecase,
)
from app.api.di.mcp.external_api import (
    provide_http_request_presenter,
    provide_http_request_usecase,
    provide_rest_api_presenter,
    provide_rest_api_usecase,
    provide_webhook_presenter,
    provide_webhook_usecase,
)
from app.api.presentation.request.mcp.external_api import (
    HttpRequestRequest,
    RestApiRequest,
    WebhookRequest,
)
from app.api.presentation.response.mcp.external_api import (
    HttpRequestResponse,
    RestApiResponse,
    WebhookResponse,
)

router = APIRouter()


@router.post(
    "/http-request",
    operation_id="http_request",
    description="指定したURLにHTTPリクエストを送信し、レスポンスを取得します。GET、POSTなど全てのHTTPメソッドに対応。",
    summary="HTTPリクエスト送信",
)
async def http_request(
    request: HttpRequestRequest,
    presenter: PresenterProtocol[
        HttpRequestRequest,
        HttpRequestResponse,
    ] = Depends(provide_http_request_presenter),
    usecase: HttpRequestUsecase = Depends(provide_http_request_usecase),
) -> HttpRequestResponse:
    """
    HTTPリクエスト送信（MCPツール）

    指定したURLに対してHTTPリクエストを送信し、レスポンスを取得します：
    - 全HTTPメソッド対応（GET、POST、PUT、DELETE等）
    - カスタムヘッダー設定
    - クエリパラメータとボディデータ
    - タイムアウト・リダイレクト・SSL検証制御

    Note:
        このエンドポイントは /mcp 経由でMCPツールとして利用可能です
    """
    presenter.request = request
    await usecase.execute(presenter)
    return presenter.response


@router.post(
    "/rest-api",
    operation_id="rest_api_call",
    description="REST APIへの呼び出しを行います。認証（Bearer、Basic、API Key）、ヘッダー設定に対応。",
    summary="REST API呼び出し",
)
async def rest_api_call(
    request: RestApiRequest,
    presenter: PresenterProtocol[
        RestApiRequest,
        RestApiResponse,
    ] = Depends(provide_rest_api_presenter),
    usecase: RestApiUsecase = Depends(provide_rest_api_usecase),
) -> RestApiResponse:
    """
    REST API呼び出し（MCPツール）

    REST APIエンドポイントへの呼び出しを実行します：
    - Bearer Token認証
    - Basic認証（ユーザー名/パスワード）
    - API Key認証（カスタムヘッダー）
    - 柔軟なエンドポイント構成

    Note:
        このエンドポイントは /mcp 経由でMCPツールとして利用可能です
    """
    presenter.request = request
    await usecase.execute(presenter)
    return presenter.response


@router.post(
    "/webhook",
    operation_id="webhook_send",
    description="Webhookへペイロードを送信します。リトライ機能、署名検証に対応。",
    summary="Webhook送信",
)
async def webhook_send(
    request: WebhookRequest,
    presenter: PresenterProtocol[
        WebhookRequest,
        WebhookResponse,
    ] = Depends(provide_webhook_presenter),
    usecase: WebhookUsecase = Depends(provide_webhook_usecase),
) -> WebhookResponse:
    """
    Webhook送信（MCPツール）

    指定したWebhook URLへペイロードを送信します：
    - POST/PUT メソッド対応
    - JSON/フォーム形式ペイロード
    - HMAC署名生成・検証
    - 自動リトライ機能

    Note:
        このエンドポイントは /mcp 経由でMCPツールとして利用可能です
    """
    presenter.request = request
    await usecase.execute(presenter)
    return presenter.response

"""
グローバルエラーハンドラー

FastAPIアプリケーション全体のエラーハンドリングを統一します。
"""

import logging
import traceback

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.core.error_response import ErrorDetail, ErrorResponse
from app.core.exceptions import AppException

__all__ = [
    "register_error_handlers",
]

logger = logging.getLogger(__name__)


def register_error_handlers(app: FastAPI) -> None:
    """
    グローバルエラーハンドラーを登録する

    - 全てのエラーハンドラーはこの関数で登録されます。

    Args:
        app: FastAPIアプリケーションインスタンス
    """

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request,
        exc: AppException,
    ) -> JSONResponse:
        """
        カスタムアプリケーション例外のハンドラー

        Args:
            request: リクエスト
            exc: カスタムアプリケーション例外

        Returns:
            エラーレスポンス
        """

        logger.warning(
            f"AppException: {exc.error_code} - {exc.message}",
            extra={
                "error_code": exc.error_code,
                "status_code": exc.status_code,
                "path": request.url.path,
                "method": request.method,
            },
        )

        error_response = ErrorResponse(
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details if exc.details else None,
            path=request.url.path,
            request_id=request.headers.get("X-Request-ID"),
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.model_dump(exclude_none=True),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """
        エラーハンドラー: リクエストバリデーションエラー

        Args:
            request: リクエスト
            exc: リクエストバリデーションエラー

        Returns:
            エラーレスポンス
        """

        logger.warning(
            f"Validation error: {request.url.path}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "errors": exc.errors(),
            },
        )

        # Pydanticのエラーを統一フォーマットに変換
        error_details = [
            ErrorDetail(
                field=".".join(str(loc) for loc in error.get("loc", [])),
                message=error.get("msg", ""),
                type=error.get("type", ""),
            )
            for error in exc.errors()
        ]

        error_response = ErrorResponse(
            error_code="ValidationError",
            message="入力値が不正です",
            errors=error_details,
            path=request.url.path,
            request_id=request.headers.get("X-Request-ID"),
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response.model_dump(exclude_none=True),
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(
        request: Request,
        exc: ValidationError,
    ) -> JSONResponse:
        """
        エラーハンドラー: Pydanticのバリデーションエラー

        Args:
            request: リクエスト
            exc: Pydanticのバリデーションエラー

        Returns:
            エラーレスポンス
        """

        logger.warning(
            f"Pydantic validation error: {request.url.path}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "errors": exc.errors(),
            },
        )

        # Pydanticのエラーを統一フォーマットに変換
        error_details = [
            ErrorDetail(
                field=".".join(str(loc) for loc in error.get("loc", [])),
                message=error.get("msg", ""),
                type=error.get("type", ""),
            )
            for error in exc.errors()
        ]

        error_response = ErrorResponse(
            error_code="ValidationError",
            message="データ検証エラーが発生しました",
            errors=error_details,
            path=request.url.path,
            request_id=request.headers.get("X-Request-ID"),
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response.model_dump(exclude_none=True),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """
        予期しない例外のハンドラー（最終的なフォールバック）

        Args:
            request: リクエスト
            exc: 予期しない例外

        Returns:
            エラーレスポンス
        """

        # スタックトレースをログに記録する
        error_traceback = "".join(
            traceback.format_exception(type(exc), exc, exc.__traceback__)
        )
        logger.error(
            f"Unhandled exception: {str(exc)}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "exception_type": type(exc).__name__,
                "traceback": error_traceback,
            },
        )

        error_response = ErrorResponse(
            error_code="InternalServerError",
            message="内部サーバーエラーが発生しました",
            details={"error": str(exc)} if logger.level == logging.DEBUG else None,
            path=request.url.path,
            request_id=request.headers.get("X-Request-ID"),
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.model_dump(exclude_none=True),
        )

    logger.info("✅ グローバルエラーハンドラーを登録しました")

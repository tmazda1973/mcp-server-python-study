import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

from app.core.error_handlers import register_error_handlers
from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    DataProcessingException,
    ExternalServiceException,
    ForbiddenException,
    InternalServerException,
    MCPToolException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
)


@pytest.fixture
def app() -> FastAPI:
    test_app = FastAPI()
    register_error_handlers(test_app)
    return test_app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app, raise_server_exceptions=False)


class TestAppExceptionHandler:
    def test_bad_request_exception(
        self,
        app: FastAPI,
        client: TestClient,
    ) -> None:
        """
        正常系テスト

        - BadRequestException のハンドリング

        Args:
            app: FastAPIアプリケーション
            client: TestClient

        Returns:
            None
        """

        @app.get("/test/bad-request")
        async def test_endpoint():
            raise BadRequestException(
                message="不正なリクエストです",
                details={"param": "test_value"},
            )

        response = client.get("/test/bad-request")

        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "BadRequestException"
        assert data["message"] == "不正なリクエストです"
        assert data["details"]["param"] == "test_value"
        assert "timestamp" in data
        assert data["path"] == "/test/bad-request"

    def test_unauthorized_exception(
        self,
        app: FastAPI,
        client: TestClient,
    ) -> None:
        """
        正常系テスト

        - UnauthorizedException のハンドリング

        Args:
            app: FastAPIアプリケーション
            client: TestClient

        Returns:
            None
        """

        @app.get("/test/unauthorized")
        async def test_endpoint():
            raise UnauthorizedException(
                message="認証に失敗しました",
                details={"reason": "invalid token"},
            )

        response = client.get("/test/unauthorized")

        assert response.status_code == 401
        data = response.json()
        assert data["error_code"] == "UnauthorizedException"
        assert data["message"] == "認証に失敗しました"

    def test_forbidden_exception(self, app: FastAPI, client: TestClient):
        """
        正常系テスト

        - ForbiddenException のハンドリング

        Args:
            app: FastAPIアプリケーション
            client: TestClient

        Returns:
            None
        """

        @app.get("/test/forbidden")
        async def test_endpoint():
            raise ForbiddenException(
                message="アクセスが拒否されました",
                details={"resource": "admin_panel"},
            )

        response = client.get("/test/forbidden")

        assert response.status_code == 403
        data = response.json()
        assert data["error_code"] == "ForbiddenException"
        assert data["message"] == "アクセスが拒否されました"

    def test_not_found_exception(self, app: FastAPI, client: TestClient):
        """
        正常系テスト

        - NotFoundException のハンドリング

        Args:
            app: FastAPIアプリケーション
            client: TestClient

        Returns:
            None
        """

        @app.get("/test/not-found")
        async def test_endpoint():
            raise NotFoundException(
                message="リソースが見つかりません",
                details={"resource_id": "12345"},
            )

        response = client.get("/test/not-found")

        assert response.status_code == 404
        data = response.json()
        assert data["error_code"] == "NotFoundException"
        assert data["message"] == "リソースが見つかりません"

    def test_conflict_exception(self, app: FastAPI, client: TestClient):
        """
        正常系テスト

        - ConflictException のハンドリング

        Args:
            app: FastAPIアプリケーション
            client: TestClient

        Returns:
            None
        """

        @app.get("/test/conflict")
        async def test_endpoint():
            raise ConflictException(
                message="リソースが競合しています",
                details={"email": "test@example.com"},
            )

        response = client.get("/test/conflict")

        assert response.status_code == 409
        data = response.json()
        assert data["error_code"] == "ConflictException"
        assert data["message"] == "リソースが競合しています"

    def test_validation_exception(self, app: FastAPI, client: TestClient):
        """
        正常系テスト

        - ValidationException のハンドリング

        Args:
            app: FastAPIアプリケーション
            client: TestClient

        Returns:
            None
        """

        @app.get("/test/validation")
        async def test_endpoint():
            raise ValidationException(
                message="入力値が不正です",
                details={"field": "email", "reason": "invalid format"},
            )

        response = client.get("/test/validation")

        assert response.status_code == 422
        data = response.json()
        assert data["error_code"] == "ValidationException"
        assert data["message"] == "入力値が不正です"

    def test_internal_server_exception(self, app: FastAPI, client: TestClient):
        """
        正常系テスト

        - InternalServerException のハンドリング

        Args:
            app: FastAPIアプリケーション
            client: TestClient

        Returns:
            None
        """

        @app.get("/test/internal-server")
        async def test_endpoint():
            raise InternalServerException(
                message="内部サーバーエラーが発生しました",
                details={"component": "database"},
            )

        response = client.get("/test/internal-server")

        assert response.status_code == 500
        data = response.json()
        assert data["error_code"] == "InternalServerException"
        assert data["message"] == "内部サーバーエラーが発生しました"

    def test_external_service_exception(self, app: FastAPI, client: TestClient):
        """
        正常系テスト

        - ExternalServiceException のハンドリング

        Args:
            app: FastAPIアプリケーション
            client: TestClient

        Returns:
            None
        """

        @app.get("/test/external-service")
        async def test_endpoint():
            raise ExternalServiceException(
                message="外部サービスでエラーが発生しました",
                service_name="Azure OpenAI",
                details={"status_code": 503},
            )

        response = client.get("/test/external-service")

        assert response.status_code == 502
        data = response.json()
        assert data["error_code"] == "ExternalServiceError"
        assert data["message"] == "外部サービスでエラーが発生しました"
        assert data["details"]["service_name"] == "Azure OpenAI"

    def test_data_processing_exception(self, app: FastAPI, client: TestClient):
        """
        正常系テスト

        - DataProcessingException のハンドリング

        Args:
            app: FastAPIアプリケーション
            client: TestClient

        Returns:
            None
        """

        @app.get("/test/data-processing")
        async def test_endpoint():
            raise DataProcessingException(
                message="データ処理でエラーが発生しました",
                details={"operation": "transform"},
            )

        response = client.get("/test/data-processing")

        assert response.status_code == 500
        data = response.json()
        assert data["error_code"] == "DataProcessingError"
        assert data["message"] == "データ処理でエラーが発生しました"

    def test_mcp_tool_exception(self, app: FastAPI, client: TestClient):
        """
        正常系テスト

        - MCPToolException のハンドリング

        Args:
            app: FastAPIアプリケーション
            client: TestClient

        Returns:
            None
        """

        @app.get("/test/mcp-tool")
        async def test_endpoint():
            raise MCPToolException(
                message="MCPツール実行でエラーが発生しました",
                tool_name="calculate",
                details={"operation": "divide"},
            )

        response = client.get("/test/mcp-tool")

        assert response.status_code == 500
        data = response.json()
        assert data["error_code"] == "MCPToolError"
        assert data["message"] == "MCPツール実行でエラーが発生しました"
        assert data["details"]["tool_name"] == "calculate"


class TestValidationErrorHandler:
    def test_request_validation_error(self, app: FastAPI, client: TestClient):
        """
        正常系テスト

        - FastAPIのリクエストバリデーションエラー

        Args:
            app: FastAPIアプリケーション
            client: TestClient

        Returns:
            None
        """

        class TestRequest(BaseModel):
            email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
            age: int = Field(..., ge=0, le=150)

        @app.post("/test/validation")
        async def test_endpoint(request: TestRequest):
            return {"message": "success"}

        # 不正なリクエスト
        response = client.post(
            "/test/validation",
            json={"email": "invalid-email", "age": 200},
        )

        assert response.status_code == 422
        data = response.json()
        assert data["error_code"] == "ValidationError"
        assert data["message"] == "入力値が不正です"
        assert "errors" in data
        assert len(data["errors"]) > 0


class TestGenericExceptionHandler:
    def test_unhandled_exception(
        self,
        app: FastAPI,
        client: TestClient,
    ) -> None:
        """
        正常系テスト

        - 予期しない例外のハンドリング

        Args:
            app: FastAPIアプリケーション
            client: TestClient

        Returns:
            None
        """

        @app.get("/test/unhandled")
        async def test_endpoint():
            raise ValueError("予期しないエラーが発生しました")

        response = client.get("/test/unhandled")

        assert response.status_code == 500
        data = response.json()
        assert data["error_code"] == "InternalServerError"
        assert data["message"] == "内部サーバーエラーが発生しました"
        assert "timestamp" in data
        assert data["path"] == "/test/unhandled"

    def test_zero_division_error(self, app: FastAPI, client: TestClient):
        """
        正常系テスト

        - ゼロ除算エラーのハンドリング

        Args:
            app: FastAPIアプリケーション
            client: TestClient

        Returns:
            None
        """

        @app.get("/test/zero-division")
        async def test_endpoint():
            return 1 / 0

        response = client.get("/test/zero-division")

        assert response.status_code == 500
        data = response.json()
        assert data["error_code"] == "InternalServerError"
        assert data["message"] == "内部サーバーエラーが発生しました"

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(
        app,
        raise_server_exceptions=False,
    )


class TestCalculateEndpoint:
    def test_add_operation(self, client: TestClient) -> None:
        """
        正常系テスト: 加算

        Args:
            client: TestClient

        Returns:
            None
        """

        response = client.post(
            "/api/v1/mcp/system/calculate",
            json={"a": 10, "b": 5, "operation": "add"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["operation"] == "add"
        assert data["inputs"]["a"] == 10
        assert data["inputs"]["b"] == 5
        assert data["result"] == 15
        assert data["mcp_tool"] is True

    def test_subtract_operation(self, client: TestClient) -> None:
        """
        正常系テスト: 減算

        Args:
            client: TestClient

        Returns:
            None
        """

        response = client.post(
            "/api/v1/mcp/system/calculate",
            json={"a": 10, "b": 5, "operation": "subtract"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["operation"] == "subtract"
        assert data["result"] == 5

    def test_multiply_operation(self, client: TestClient) -> None:
        """
        正常系テスト: 乗算

        Args:
            client: TestClient

        Returns:
            None
        """

        response = client.post(
            "/api/v1/mcp/system/calculate",
            json={"a": 10, "b": 5, "operation": "multiply"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["operation"] == "multiply"
        assert data["result"] == 50

    def test_divide_operation(self, client: TestClient) -> None:
        """
        正常系テスト: 除算

        Args:
            client: TestClient

        Returns:
            None
        """

        response = client.post(
            "/api/v1/mcp/system/calculate",
            json={"a": 10, "b": 5, "operation": "divide"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["operation"] == "divide"
        assert data["result"] == 2.0

    def test_divide_by_zero(self, client: TestClient) -> None:
        """
        異常系テスト: ゼロ除算

        Args:
            client: TestClient

        Returns:
            None
        """

        response = client.post(
            "/api/v1/mcp/system/calculate",
            json={"a": 10, "b": 0, "operation": "divide"},
        )

        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "DIVISION_BY_ZERO"
        assert data["message"] == "ゼロで除算することはできません"
        assert data["details"]["a"] == 10
        assert data["details"]["b"] == 0
        assert data["details"]["operation"] == "divide"

    def test_default_operation_is_add(self, client: TestClient) -> None:
        """
        正常系テスト: デフォルト演算子（加算）

        Args:
            client: TestClient

        Returns:
            None
        """

        response = client.post(
            "/api/v1/mcp/system/calculate",
            json={"a": 3, "b": 7},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["operation"] == "add"
        assert data["result"] == 10

    def test_invalid_operation(self, client: TestClient) -> None:
        """
        異常系テスト: 不正な演算子

        Args:
            client: TestClient

        Returns:
            None
        """

        response = client.post(
            "/api/v1/mcp/system/calculate",
            json={"a": 10, "b": 5, "operation": "modulo"},
        )

        assert response.status_code == 422
        data = response.json()
        assert data["error_code"] == "ValidationError"
        assert data["message"] == "入力値が不正です"

    def test_missing_required_fields(self, client: TestClient) -> None:
        """
        異常系テスト: 必須フィールド欠落

        Args:
            client: TestClient

        Returns:
            None
        """

        response = client.post(
            "/api/v1/mcp/system/calculate",
            json={"a": 10},
        )

        assert response.status_code == 422
        data = response.json()
        assert data["error_code"] == "ValidationError"
        assert "errors" in data

    def test_invalid_data_type(self, client: TestClient) -> None:
        """
        異常系テスト: 不正なデータ型

        Args:
            client: TestClient

        Returns:
            None
        """

        response = client.post(
            "/api/v1/mcp/system/calculate",
            json={"a": "not_a_number", "b": 5, "operation": "add"},
        )

        assert response.status_code == 422
        data = response.json()
        assert data["error_code"] == "ValidationError"

    def test_negative_numbers(self, client: TestClient) -> None:
        """
        正常系テスト: 負の数の計算

        Args:
            client: TestClient

        Returns:
            None
        """

        response = client.post(
            "/api/v1/mcp/system/calculate",
            json={"a": -10, "b": 5, "operation": "add"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["result"] == -5

    def test_floating_point_numbers(self, client: TestClient) -> None:
        """
        正常系テスト: 浮動小数点数の計算

        Args:
            client: TestClient

        Returns:
            None
        """

        response = client.post(
            "/api/v1/mcp/system/calculate",
            json={"a": 10.5, "b": 2.5, "operation": "multiply"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["result"] == 26.25

from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.middlewares import IPRestrictionMiddleware


@pytest.fixture
def app():
    return FastAPI()


@pytest.fixture
def middleware(app):
    return IPRestrictionMiddleware(
        app,
        allowed_ips=[
            "127.0.0.1",
            "192.168.1.0/24",
            "10.0.0.0/8",
        ],
    )


class TestIPRestrictionMiddleware:
    def test_parse_allowed_ips_single_ip(self, app):
        """
        正常系テスト

        関数:
            - test_parse_allowed_ips_single_ip
        """
        middleware = IPRestrictionMiddleware(app, allowed_ips=["127.0.0.1"])
        assert len(middleware.allowed_networks) == 1
        assert str(middleware.allowed_networks[0]) == "127.0.0.1/32"

    def test_parse_allowed_ips_cidr(self, app):
        """
        正常系テスト

        関数:
            - test_parse_allowed_ips_cidr
        """
        middleware = IPRestrictionMiddleware(app, allowed_ips=["192.168.1.0/24"])
        assert len(middleware.allowed_networks) == 1
        assert str(middleware.allowed_networks[0]) == "192.168.1.0/24"

    def test_parse_allowed_ips_multiple(self, app):
        """
        正常系テスト

        関数:
            - test_parse_allowed_ips_multiple
        """
        middleware = IPRestrictionMiddleware(
            app,
            allowed_ips=["127.0.0.1", "192.168.1.0/24", "10.0.0.0/8"],
        )
        assert len(middleware.allowed_networks) == 3

    def test_parse_allowed_ips_invalid(self, app):
        """
        異常系テスト

        関数:
            - test_parse_allowed_ips_invalid
        """
        with patch(
            "app.middlewares.ip_restriction_middleware.logger.warning"
        ) as mock_logger:
            middleware = IPRestrictionMiddleware(
                app,
                allowed_ips=["invalid-ip", "127.0.0.1"],
            )
            assert len(middleware.allowed_networks) == 1  # 有効なIPのみ
            mock_logger.assert_called_once()

    def test_is_allowed_ip_single_match(self, middleware):
        """
        正常系テスト

        関数:
            - test_is_allowed_ip_single_match
        """
        assert middleware._is_allowed_ip("127.0.0.1") is True
        assert middleware._is_allowed_ip("192.168.1.100") is True
        assert middleware._is_allowed_ip("10.1.2.3") is True
        assert middleware._is_allowed_ip("8.8.8.8") is False

    def test_is_allowed_ip_cidr_range(self, middleware):
        """
        正常系テスト

        関数:
            - test_is_allowed_ip_cidr_range
        """
        # 192.168.1.0/24 の範囲内
        assert middleware._is_allowed_ip("192.168.1.1") is True
        assert middleware._is_allowed_ip("192.168.1.255") is True
        # 範囲外
        assert middleware._is_allowed_ip("192.168.2.1") is False

        # 10.0.0.0/8 の範囲内
        assert middleware._is_allowed_ip("10.0.0.1") is True
        assert middleware._is_allowed_ip("10.255.255.255") is True
        # 範囲外
        assert middleware._is_allowed_ip("11.0.0.1") is False

    def test_is_allowed_ip_invalid(self, middleware):
        """
        異常系テスト

        関数:
            - test_is_allowed_ip_invalid
        """
        with patch(
            "app.middlewares.ip_restriction_middleware.logger.warning"
        ) as mock_logger:
            result = middleware._is_allowed_ip("invalid-ip")
            assert result is False
            mock_logger.assert_called_once()

    def test_get_client_ip_direct(self, middleware):
        """
        正常系テスト

        関数:
            - test_get_client_ip_direct
        """
        request = MagicMock(spec=Request)
        request.headers.get.return_value = None
        request.client.host = "127.0.0.1"

        client_ip = middleware._get_client_ip(request)
        assert client_ip == "127.0.0.1"

    def test_get_client_ip_x_forwarded_for(self, middleware):
        """
        正常系テスト

        関数:
            - test_get_client_ip_x_forwarded_for
        """
        request = MagicMock(spec=Request)
        request.headers.get = lambda key: (
            "203.0.113.1, 198.51.100.1" if key == "X-Forwarded-For" else None
        )
        request.client = None

        # TRUST_PROXY_HEADERSを有効にしてテスト
        with patch(
            "app.middlewares.ip_restriction_middleware.settings"
        ) as mock_settings:
            mock_settings.TRUST_PROXY_HEADERS = True
            client_ip = middleware._get_client_ip(request)
            assert client_ip == "203.0.113.1"  # 最初のIPを使用

    def test_get_client_ip_x_real_ip(self, middleware):
        """
        正常系テスト

        関数:
            - test_get_client_ip_x_real_ip
        """
        request = MagicMock(spec=Request)

        def get_header(key):
            if key == "X-Real-IP":
                return "203.0.113.1"
            return None

        request.headers.get = get_header
        request.client = None

        # TRUST_PROXY_HEADERSを有効にしてテスト
        with patch(
            "app.middlewares.ip_restriction_middleware.settings"
        ) as mock_settings:
            mock_settings.TRUST_PROXY_HEADERS = True
            client_ip = middleware._get_client_ip(request)
            assert client_ip == "203.0.113.1"

    def test_get_client_ip_no_client(self, middleware):
        """
        正常系テスト

        関数:
            - test_get_client_ip_no_client
        """
        request = MagicMock(spec=Request)
        request.headers.get.return_value = None
        request.client = None

        client_ip = middleware._get_client_ip(request)
        assert client_ip == "unknown"

    @pytest.mark.asyncio
    async def test_dispatch_health_check_bypass(self, middleware):
        """
        正常系テスト

        関数:
            - test_dispatch_health_check_bypass
        """
        request = MagicMock(spec=Request)
        request.url.path = "/health"

        async def call_next(req):
            return JSONResponse(content={"status": "healthy"})

        response = await middleware.dispatch(request, call_next)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_dispatch_empty_allowed_list(self, middleware):
        """
        正常系テスト

        関数:
            - test_dispatch_empty_allowed_list
        """
        middleware.allowed_networks = []  # 空にする

        request = MagicMock(spec=Request)
        request.url.path = "/api/v1/test"
        request.headers.get.return_value = None
        request.client.host = "8.8.8.8"  # 許可リストに含まれないIP

        async def call_next(req):
            return JSONResponse(content={"message": "OK"})

        with patch(
            "app.middlewares.ip_restriction_middleware.logger.debug"
        ) as mock_logger:
            response = await middleware.dispatch(request, call_next)
            assert response.status_code == 200
            mock_logger.assert_called_once()

    @pytest.mark.asyncio
    async def test_dispatch_allowed_ip(self, middleware):
        """
        正常系テスト

        関数:
            - test_dispatch_allowed_ip
        """
        request = MagicMock(spec=Request)
        request.url.path = "/api/v1/test"
        request.headers.get.return_value = None
        request.client.host = "127.0.0.1"

        async def call_next(req):
            return JSONResponse(content={"message": "OK"})

        with patch(
            "app.middlewares.ip_restriction_middleware.logger.debug"
        ) as mock_logger:
            response = await middleware.dispatch(request, call_next)
            assert response.status_code == 200
            mock_logger.assert_called_once()

    @pytest.mark.asyncio
    async def test_dispatch_denied_ip(self, middleware):
        """
        正常系テスト

        関数:
            - test_dispatch_denied_ip
        """
        request = MagicMock(spec=Request)
        request.url.path = "/api/v1/test"
        request.headers.get.return_value = None
        request.client.host = "8.8.8.8"  # 許可リストに含まれないIP

        async def call_next(req):
            return JSONResponse(content={"message": "OK"})

        with patch(
            "app.middlewares.ip_restriction_middleware.logger.warning"
        ) as mock_logger:
            response = await middleware.dispatch(request, call_next)
            assert response.status_code == 403
            assert "Access denied" in response.body.decode()
            mock_logger.assert_called_once()

    @pytest.mark.asyncio
    async def test_dispatch_cidr_range_allowed(self, middleware):
        """
        正常系テスト

        関数:
            - test_dispatch_cidr_range_allowed
        """
        request = MagicMock(spec=Request)
        request.url.path = "/api/v1/test"
        request.headers.get.return_value = None
        request.client.host = "192.168.1.50"  # 192.168.1.0/24 の範囲内

        async def call_next(req):
            return JSONResponse(content={"message": "OK"})

        with patch(
            "app.middlewares.ip_restriction_middleware.logger.debug"
        ) as mock_logger:
            response = await middleware.dispatch(request, call_next)
            assert response.status_code == 200
            mock_logger.assert_called_once()

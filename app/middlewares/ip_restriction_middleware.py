import ipaddress
import logging
from typing import Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings

__all__ = [
    "IPRestrictionMiddleware",
]

logger = logging.getLogger(__name__)


class IPRestrictionMiddleware(BaseHTTPMiddleware):
    """
    IP制限ミドルウェア

    - 環境変数で許可IPアドレスを設定
    - CIDR表記（192.168.1.0/24）もサポート
    - ヘルスチェックエンドポイントは制限対象外
    """

    def __init__(self, app, allowed_ips: list[str] | None = None):
        """
        コンストラクタ

        Args:
            app: FastAPIアプリケーション
            allowed_ips: 許可するIPアドレスのリスト（未指定時は設定値から取得）
        """

        super().__init__(app)
        self.allowed_ips = allowed_ips or settings.ALLOWED_IPS
        self.allowed_networks = self._parse_allowed_ips(self.allowed_ips)

    def _parse_allowed_ips(
        self,
        allowed_ips: list[str],
    ) -> list[ipaddress.IPv4Network | ipaddress.IPv6Network]:
        """
        許可IPアドレスリストをパースしてネットワークオブジェクトに変換

        Args:
            allowed_ips: 許可IPアドレスリスト（例: ["127.0.0.1", "192.168.1.0/24"]）

        Returns:
            ネットワークオブジェクトのリスト
        """
        networks = []
        for ip_str in allowed_ips:
            try:
                # CIDR表記がない場合は単一IPとして扱う
                if "/" not in ip_str:
                    ip_str = f"{ip_str}/32"  # IPv4の場合
                networks.append(ipaddress.ip_network(ip_str, strict=False))
            except ValueError as e:
                logger.warning(f"無効なIPアドレス形式: {ip_str} - {e}")
        return networks

    def _is_allowed_ip(self, client_ip: str) -> bool:
        """
        クライアントIPが許可リストに含まれているかチェック

        Args:
            client_ip: クライアントIPアドレス

        Returns:
            True 許可されている, False 許可されていない
        """
        try:
            client_addr = ipaddress.ip_address(client_ip)
            for network in self.allowed_networks:
                if client_addr in network:
                    return True
            return False
        except ValueError as e:
            logger.warning(f"無効なクライアントIPアドレス: {client_ip} - {e}")
            return False

    def _get_client_ip(self, request: Request) -> str:
        """
        クライアントIPアドレスを取得

        プロキシ経由の場合は X-Forwarded-For ヘッダーから取得

        Args:
            request: リクエスト

        Returns:
            クライアントIPアドレス
        """

        # TRUST_PROXY_HEADERSが有効な場合のみプロキシヘッダーを信頼
        if settings.TRUST_PROXY_HEADERS:
            # プロキシ経由の場合は X-Forwarded-For を優先
            forwarded_for = request.headers.get("X-Forwarded-For")
            if forwarded_for:
                # カンマ区切りの場合は最初のIPを使用
                return forwarded_for.split(",")[0].strip()

            # X-Real-IP ヘッダーをチェック
            real_ip = request.headers.get("X-Real-IP")
            if real_ip:
                return real_ip.strip()

        # 直接接続の場合
        client_host = request.client.host if request.client else None

        # TestClientからのリクエストの場合は127.0.0.1として扱う
        if client_host == "testclient":
            return "127.0.0.1"

        return client_host or "unknown"

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        リクエストごとにIP制限をチェック

        Args:
            request: リクエスト
            call_next: 次のミドルウェアまたはエンドポイント

        Returns:
            レスポンス
        """
        # ヘルスチェックエンドポイントは制限対象外
        if request.url.path == "/health":
            return await call_next(request)

        # 許可IPリストが空の場合はスキップ（全て許可）
        if not self.allowed_networks:
            logger.debug("IP制限が無効化されています（ALLOWED_IPSが未設定）")
            return await call_next(request)

        # クライアントIPを取得
        client_ip = self._get_client_ip(request)

        # IP制限チェック
        if not self._is_allowed_ip(client_ip):
            logger.warning(
                f"IPアドレス制限により拒否されました: {client_ip} - {request.url.path}"
            )
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "detail": "Access denied: Your IP address is not allowed",
                    "client_ip": client_ip,
                },
            )

        logger.debug(f"IPアドレス許可: {client_ip} - {request.url.path}")
        return await call_next(request)

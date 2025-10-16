import base64
import json
import time
from typing import Any, Dict, Literal, Optional
from urllib.parse import urljoin

import httpx
from typing_extensions import override

from app.api.application.repositories.mcp.external_api import RestApiRepositoryProtocol
from app.api.domain.entities.mcp.external_api import RestApiResultEntity

__all__ = [
    "RestApiRepository",
]


class RestApiRepository(RestApiRepositoryProtocol):
    """
    リポジトリ（REST API呼び出しツール）
    """

    @override
    async def call_api(
        self,
        base_url: str,
        endpoint: str,
        method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"] = "GET",
        auth_type: Optional[Literal["bearer", "basic", "api_key"]] = None,
        auth_token: Optional[str] = None,
        auth_username: Optional[str] = None,
        auth_password: Optional[str] = None,
        api_key_header: str = "X-API-Key",
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
    ) -> RestApiResultEntity:
        start_time = time.time()
        try:
            # URL構築
            full_url = urljoin(base_url.rstrip("/") + "/", endpoint.lstrip("/"))
            # ヘッダー準備
            request_headers = headers.copy() if headers else {}
            # 認証ヘッダー設定
            auth_used = None
            if auth_type and auth_token:
                if auth_type == "bearer":
                    request_headers["Authorization"] = f"Bearer {auth_token}"
                    auth_used = "Bearer Token"
                elif auth_type == "api_key":
                    request_headers[api_key_header] = auth_token
                    auth_used = f"API Key ({api_key_header})"
                elif auth_type == "basic" and auth_username and auth_password:
                    credentials = base64.b64encode(
                        f"{auth_username}:{auth_password}".encode()
                    ).decode()
                    request_headers["Authorization"] = f"Basic {credentials}"
                    auth_used = "Basic Authentication"

            # Content-Type設定
            if data and method in ["POST", "PUT", "PATCH"]:
                request_headers.setdefault("Content-Type", "application/json")

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.request(
                    method=method,
                    url=full_url,
                    headers=request_headers,
                    params=params,
                    json=data if data else None,
                )

                response_time = time.time() - start_time
                response_text = response.text
                response_data = None
                # JSONパース試行
                content_type = response.headers.get("content-type", "")
                if "application/json" in content_type:
                    try:
                        response_data = response.json()
                    except json.JSONDecodeError:
                        pass

                return RestApiResultEntity(
                    success=response.is_success,
                    status_code=response.status_code,
                    url=str(response.url),
                    method=method,
                    response_data=response_data,
                    response_text=response_text,
                    headers=dict(response.headers),
                    content_type=content_type,
                    response_time=response_time,
                    auth_used=auth_used,
                )
        except httpx.TimeoutException:
            response_time = time.time() - start_time
            return RestApiResultEntity(
                success=False,
                status_code=408,
                url=full_url if "full_url" in locals() else f"{base_url}/{endpoint}",
                method=method,
                response_data=None,
                response_text="",
                headers={},
                response_time=response_time,
                auth_used=auth_used,
                error=f"APIリクエストがタイムアウトしました（{timeout}秒）",
            )
        except httpx.RequestError as e:
            response_time = time.time() - start_time
            return RestApiResultEntity(
                success=False,
                status_code=0,
                url=full_url if "full_url" in locals() else f"{base_url}/{endpoint}",
                method=method,
                response_data=None,
                response_text="",
                headers={},
                response_time=response_time,
                auth_used=auth_used,
                error=f"APIリクエストエラー: {str(e)}",
            )
        except Exception as e:
            response_time = time.time() - start_time
            return RestApiResultEntity(
                success=False,
                status_code=0,
                url=full_url if "full_url" in locals() else f"{base_url}/{endpoint}",
                method=method,
                response_data=None,
                response_text="",
                headers={},
                response_time=response_time,
                auth_used=auth_used,
                error=f"予期せぬエラー: {str(e)}",
            )

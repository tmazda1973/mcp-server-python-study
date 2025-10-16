import json
import time
from typing import Any, Dict, Literal, Optional

import httpx
from typing_extensions import override

from app.api.application.repositories.mcp.external_api import (
    HttpRequestRepositoryProtocol,
)
from app.api.domain.entities.mcp.external_api import HttpRequestResultEntity

__all__ = [
    "HttpRequestRepository",
]


class HttpRequestRepository(HttpRequestRepositoryProtocol):
    """
    リポジトリ（HTTP リクエストツール）
    """

    @override
    async def send_request(
        self,
        url: str,
        method: Literal[
            "GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"
        ] = "GET",
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
        follow_redirects: bool = True,
        verify_ssl: bool = True,
    ) -> HttpRequestResultEntity:
        start_time = time.time()
        try:
            async with httpx.AsyncClient(
                timeout=timeout,
                follow_redirects=follow_redirects,
                verify=verify_ssl,
            ) as client:
                # リクエスト送信
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=data if data else None,
                )

                response_time = time.time() - start_time
                content = response.text
                json_data = None
                # JSONパース試行
                content_type = response.headers.get("content-type", "")
                if "application/json" in content_type:
                    try:
                        json_data = response.json()
                    except json.JSONDecodeError:
                        pass

                return HttpRequestResultEntity(
                    success=response.is_success,
                    status_code=response.status_code,
                    url=str(response.url),
                    method=method,
                    headers=dict(response.headers),
                    content=content,
                    json_data=json_data,
                    content_type=content_type,
                    content_length=len(content.encode("utf-8")),
                    response_time=response_time,
                    encoding=response.encoding,
                )
        except httpx.TimeoutException:
            response_time = time.time() - start_time
            return HttpRequestResultEntity(
                success=False,
                status_code=408,
                url=url,
                method=method,
                headers={},
                content="",
                response_time=response_time,
                error=f"リクエストがタイムアウトしました（{timeout}秒）",
            )
        except httpx.RequestError as e:
            response_time = time.time() - start_time
            return HttpRequestResultEntity(
                success=False,
                status_code=0,
                url=url,
                method=method,
                headers={},
                content="",
                response_time=response_time,
                error=f"リクエストエラー: {str(e)}",
            )
        except Exception as e:
            response_time = time.time() - start_time
            return HttpRequestResultEntity(
                success=False,
                status_code=0,
                url=url,
                method=method,
                headers={},
                content="",
                response_time=response_time,
                error=f"予期せぬエラー: {str(e)}",
            )

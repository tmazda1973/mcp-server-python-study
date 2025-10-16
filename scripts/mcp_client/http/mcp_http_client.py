#!/usr/bin/env python3
import asyncio
import json

import httpx
from rich.console import Console

console = Console()

__all__ = [
    "MCPHTTPClient",
]


class MCPHTTPClient:
    """
    MCP HTTP クライアント
    """

    def __init__(self, base_url: str = "http://localhost:8020"):
        self._base_url = base_url
        self._session_id: str | None = None

    async def send_jsonrpc_message(
        self,
        method: str,
        params: dict = None,
        message_id: int = 1,
    ) -> None:
        """
        JSONRPCメッセージを送信する

        Args:
            method: メソッド名
            params: パラメータ
            message_id: メッセージID

        Returns:
            None
        """

        message = {"jsonrpc": "2.0", "id": message_id, "method": method}
        if params:
            message["params"] = params

        headers = {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
        }
        # セッションIDがある場合はヘッダーに追加
        if self._session_id:
            headers["mcp-session-id"] = self._session_id

        console.print(f"📤 送信: {method}", style="blue")
        console.print(f"🔑 セッションID: {self._session_id or 'なし'}", style="dim")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self._base_url}/mcp-http",
                json=message,
                headers=headers,
            )
            console.print(f"📨 レスポンス: {response.status_code}", style="cyan")

            # セッションIDを取得
            if "mcp-session-id" in response.headers:
                self._session_id = response.headers["mcp-session-id"]
                console.print(
                    f"🔑 新しいセッションID: {self._session_id}", style="bold green"
                )

            if response.status_code == 200:
                result = response.json()
                console.print("✅ 結果:", style="green")
                console.print_json(json.dumps(result, ensure_ascii=False))
                return result
            else:
                console.print(f"❌ エラー: {response.text}", style="red")
                return None

    async def send_notification(self, method: str, params: dict) -> None:
        """
        JSONRPC通知メッセージを送信する（レスポンスなし）

        Args:
            method: 通知メソッド名
            params: パラメータ
        """

        message = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
        }

        console.print(f"📤 通知送信: {method}", style="yellow")

        headers = {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
        }

        if self._session_id:
            headers["mcp-session-id"] = self._session_id

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self._base_url}/mcp-http",
                json=message,
                headers=headers,
            )
            console.print(f"📨 通知レスポンス: {response.status_code}", style="dim")

    async def test_mcp_flow(self, test_tools: bool = True) -> None:
        """
        MCP通信フローをテストする

        Args:
            test_tools: ツール一覧の取得をテストするか

        Returns:
            None
        """

        console.print("🚀 MCP HTTP テスト開始", style="bold blue")

        try:
            # 初期化メッセージ
            console.print("\n📋 初期化メッセージを送信...", style="bold")
            result = await self.send_jsonrpc_message(
                "initialize",
                {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test-http-client", "version": "1.0.0"},
                },
            )
            if not result:
                console.print("❌ 初期化に失敗", style="red")
                return

            # initialized通知を送信（MCPプロトコル必須）
            console.print("\n📋 initialized通知を送信...", style="bold")
            await self.send_notification("notifications/initialized", {})

            await asyncio.sleep(1)

            if test_tools:
                # ツール一覧取得
                console.print("\n📋 ツール一覧を取得...", style="bold")
                await self.send_jsonrpc_message("tools/list", {}, 2)

                await asyncio.sleep(1)

                # 計算ツール（加算）
                console.print("\n📋 計算ツールテスト（加算）...", style="bold")
                await self.send_jsonrpc_message(
                    "tools/call",
                    {
                        "name": "calculate",
                        "arguments": {
                            "a": 10,
                            "b": 5,
                            "operation": "add",
                        },
                    },
                    4,
                )

                await asyncio.sleep(1)

                # 計算ツール（除算）
                console.print("\n📋 計算ツールテスト（除算）...", style="bold")
                await self.send_jsonrpc_message(
                    "tools/call",
                    {
                        "name": "calculate",
                        "arguments": {
                            "a": 20,
                            "b": 4,
                            "operation": "divide",
                        },
                    },
                    6,
                )

                await asyncio.sleep(1)

                # テキスト検索ツール
                console.print("\n📋 テキスト検索ツールテスト...", style="bold")
                await self.send_jsonrpc_message(
                    "tools/call",
                    {
                        "name": "text_search",
                        "arguments": {
                            "text": "Hello world! This is a test text for searching.",
                            "pattern": "test",
                            "case_sensitive": False,
                        },
                    },
                    5,
                )
        except Exception as e:
            console.print(f"❌ エラー: {e}", style="red")

        console.print("🏁 テスト完了", style="bold green")

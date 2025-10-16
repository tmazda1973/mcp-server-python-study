#!/usr/bin/env python3
import asyncio
import json
import re
from typing import AsyncGenerator

import httpx
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

__all__ = [
    "MCPSSEClient",
]


class MCPSSEClient:
    """
    MCP SSE クライアント
    """

    def __init__(self, base_url: str = "http://localhost:8020"):
        self._base_url = base_url
        self._session_id: str | None = None

    async def connect_sse(self) -> AsyncGenerator[str, None]:
        """
        SSE接続を開始する

        Returns:
            AsyncGenerator[str, None]: データを生成するジェネレータ
        """

        console.print("🔗 SSE接続を開始...", style="blue")
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "GET",
                f"{self._base_url}/mcp",
                headers={
                    "Accept": "text/event-stream",
                    "Cache-Control": "no-cache",
                },
                timeout=30.0,
            ) as response:
                console.print(f"📡 レスポンス: {response.status_code}", style="cyan")
                if response.status_code != 200:
                    console.print(f"❌ 接続エラー: {response.status_code}", style="red")
                    return

                async for line in response.aiter_lines():
                    if line.startswith("event:"):
                        event_type = line[6:].strip()
                        console.print(f"📨 イベント: {event_type}", style="yellow")
                    elif line.startswith("data:"):
                        data = line[5:].strip()
                        console.print(f"📄 データ: {data}", style="green")
                        # セッションIDを抽出
                        if "session_id=" in data:
                            match = re.search(r"session_id=([a-f0-9-]+)", data)
                            if match:
                                self._session_id = match.group(1)
                                console.print(
                                    f"🔑 セッションID取得: {self._session_id}",
                                    style="bold green",
                                )

                        yield data
                    elif line.strip() == "":
                        continue
                    else:
                        console.print(f"📋 その他: {line}", style="dim")

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

        if not self._session_id:
            console.print("❌ セッションIDが取得されていません", style="red")
            return

        message = {"jsonrpc": "2.0", "id": message_id, "method": method}
        if params is not None:
            message["params"] = params

        console.print(f"📤 送信: {method}", style="blue")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self._base_url}/mcp/messages/",
                params={"session_id": self._session_id},
                json=message,
                headers={"Content-Type": "application/json"},
            )

            console.print(f"📨 レスポンス: {response.status_code}", style="cyan")
            if response.status_code == 200:
                result = response.json()
                console.print("✅ 結果:", style="green")
                console.print_json(json.dumps(result, ensure_ascii=False))
            elif response.status_code == 202:
                # SSEでは202 Acceptedが正常（非同期処理）
                console.print("✅ 受理: SSE経由で後から配信されます", style="green")
                console.print(f"📋 詳細: {response.text}", style="dim")
            else:
                console.print(f"❌ エラー: {response.text}", style="red")

    async def send_notification(self, method: str, params: dict) -> None:
        """
        JSONRPC通知メッセージを送信する（レスポンスなし）

        Args:
            method: 通知メソッド名
            params: パラメータ
        """
        if not self._session_id:
            console.print("❌ セッションIDが取得されていません", style="red")
            return

        message = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
        }

        console.print(f"📤 通知送信: {method}", style="yellow")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self._base_url}/mcp/messages/",
                params={"session_id": self._session_id},
                json=message,
                headers={"Content-Type": "application/json"},
            )
            console.print(f"📨 通知レスポンス: {response.status_code}", style="dim")

    async def test_mcp_flow(
        self,
        test_tools: bool = True,
    ) -> None:
        """
        MCP通信フローをテストする

        Args:
            test_tools: ツール一覧の取得をテストするか

        Returns:
            None
        """

        console.print("🚀 MCP SSE テスト開始", style="bold blue")

        # SSE接続を開始（バックグラウンドで実行）
        sse_task = None
        try:
            # SSE接続をバックグラウンドタスクとして開始
            sse_task = asyncio.create_task(self._run_sse_connection())

            # セッションIDの取得を待機
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("SSE接続中...", total=None)

                # セッションIDが取得されるまで待機
                for i in range(30):  # 最大30秒待機
                    if self._session_id:
                        progress.update(task, description="✅ セッションID取得完了")
                        break
                    await asyncio.sleep(1)
                    progress.update(task, description=f"SSE接続中... ({i+1}s)")

            if not self._session_id:
                console.print("❌ セッションIDの取得に失敗", style="red")
                return

            # 少し待機
            await asyncio.sleep(2)

            # 初期化メッセージ
            console.print("\n📋 初期化メッセージを送信...", style="bold")
            await self.send_jsonrpc_message(
                "initialize",
                {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test-sse-client", "version": "1.0.0"},
                },
            )
            await asyncio.sleep(2)

            # initialized通知を送信（MCPプロトコル必須）
            console.print("\n📋 initialized通知を送信...", style="bold")
            await self.send_notification("notifications/initialized", {})
            await asyncio.sleep(1)

            if test_tools:
                # ツール一覧取得
                console.print("\n📋 ツール一覧を取得...", style="bold")
                await self.send_jsonrpc_message("tools/list", {}, 2)
                await asyncio.sleep(2)

                # 実際のツール呼び出しテスト
                console.print("\n📋 実際のツール呼び出しテスト...", style="bold")

                # 計算ツールテスト（加算）
                console.print("\n📋 calculate呼び出し（加算）...", style="bold")
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
                await asyncio.sleep(2)

                # 計算ツールテスト（除算）
                console.print("\n📋 calculate呼び出し（除算）...", style="bold")
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
                await asyncio.sleep(2)

                # テキスト検索ツールテスト
                console.print("\n📋 text_search呼び出し...", style="bold")
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
                await asyncio.sleep(2)
        except KeyboardInterrupt:
            console.print("\n⏹️ テスト中断", style="yellow")
        except Exception as e:
            console.print(f"❌ エラー: {e}", style="red")
        finally:
            if sse_task and not sse_task.done():
                sse_task.cancel()
                try:
                    await sse_task
                except asyncio.CancelledError:
                    pass

        console.print("🏁 テスト完了", style="bold green")

    async def _run_sse_connection(self) -> None:
        """
        SSE接続をバックグラウンドで実行する
        """
        try:
            async for _data in self.connect_sse():
                # 接続を維持し続ける
                pass
        except asyncio.CancelledError:
            console.print("🔗 SSE接続を終了", style="dim")
        except Exception as e:
            console.print(f"❌ SSE接続エラー: {e}", style="red")

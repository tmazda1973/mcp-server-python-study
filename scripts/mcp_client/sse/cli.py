#!/usr/bin/env python3
"""
MCP SSE クライアント CLI コマンド
"""

import asyncio
import json
import sys
from typing import Optional

import typer
from mcp_sse_client import MCPSSEClient
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

app = typer.Typer(help="FastAPI-MCP SSE テストクライアント")
console = Console()


@app.command()
def test(
    url: str = typer.Option(
        "http://localhost:8020",
        "--url",
        "-u",
        help="MCPサーバーのURL",
    ),
    skip_tools: bool = typer.Option(
        False,
        "--skip-tools",
        help="ツール一覧の取得をスキップ",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="詳細なログを表示",
    ),
):
    """
    SSE接続でMCPサーバーをテストする

    Args:
        url: MCPサーバーのURL
        skip_tools: ツール一覧の取得をスキップするか
        verbose: 詳細なログを表示するか

    Returns:
        None
    """

    async def run_test():
        client = MCPSSEClient(base_url=url)
        await client.test_mcp_flow(test_tools=not skip_tools)

    try:
        asyncio.run(run_test())
    except KeyboardInterrupt:
        console.print("\n👋 テスト終了", style="yellow")
        sys.exit(0)


@app.command()
def connect(
    url: str = typer.Option(
        "http://localhost:8020",
        "--url",
        "-u",
        help="MCPサーバーのURL",
    ),
    timeout: int = typer.Option(
        30,
        "--timeout",
        "-t",
        help="接続タイムアウト（秒）",
    ),
):
    """
    SSE接続を維持してリアルタイムでメッセージを表示する

    Args:
        url: MCPサーバーのURL
        timeout: 接続タイムアウト（秒）

    Returns:
        None
    """

    async def run_connect():
        client = MCPSSEClient(base_url=url)
        console.print(f"🔗 {url}/mcp に接続中...", style="blue")
        console.print("Ctrl+C で終了", style="dim")

        try:
            async for _data in client.connect_sse():
                # データを受信し続ける
                pass
        except KeyboardInterrupt:
            console.print("\n👋 接続終了", style="yellow")

    try:
        asyncio.run(run_connect())
    except KeyboardInterrupt:
        console.print("\n👋 接続終了", style="yellow")
        sys.exit(0)


@app.command()
def send(
    method: str = typer.Argument(..., help="送信するJSONRPCメソッド"),
    url: str = typer.Option(
        "http://localhost:8020",
        "--url",
        "-u",
        help="MCPサーバーのURL",
    ),
    params: Optional[str] = typer.Option(
        None,
        "--params",
        "-p",
        help="JSONRPCパラメータ（JSON形式）",
    ),
) -> None:
    """
    カスタムJSONRPCメッセージを送信する

    Args:
        method: 送信するJSONRPCメソッド
        url: MCPサーバーのURL
        params: JSONRPCパラメータ（JSON形式）

    Returns:
        None
    """

    async def run_send():
        client = MCPSSEClient(base_url=url)
        console.print("📋 初期化中...", style="blue")

        # SSE接続をバックグラウンドで開始
        sse_task = None
        try:
            # SSE接続をバックグラウンドタスクとして開始
            sse_task = asyncio.create_task(client._run_sse_connection())

            # セッションIDの取得を待機
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("SSE接続中...", total=None)

                # セッションIDが取得されるまで待機
                for i in range(30):  # 最大30秒待機
                    if client._session_id:
                        progress.update(task, description="✅ セッションID取得完了")
                        break
                    await asyncio.sleep(1)
                    progress.update(task, description=f"SSE接続中... ({i+1}s)")

            if not client._session_id:
                console.print("❌ セッションIDの取得に失敗", style="red")
                return

            # 初期化メッセージ
            console.print("\n📋 初期化メッセージを送信...", style="bold")
            await client.send_jsonrpc_message(
                "initialize",
                {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test-sse-client", "version": "1.0.0"},
                },
            )

            # initialized通知を送信（MCPプロトコル必須）
            await client.send_notification("notifications/initialized", {})
            await asyncio.sleep(1)

            # カスタムメッセージ送信
            console.print(f"\n📤 カスタムメッセージ送信: {method}", style="bold")

            # パラメータをパース
            parsed_params = {}
            if params:
                try:
                    parsed_params = json.loads(params)
                except json.JSONDecodeError as e:
                    console.print(f"❌ JSONパラメータの解析エラー: {e}", style="red")
                    return

            await client.send_jsonrpc_message(method, parsed_params, 2)
            await asyncio.sleep(3)  # レスポンスを待機

        except KeyboardInterrupt:
            console.print("\n⏹️ 送信中断", style="yellow")
        except Exception as e:
            console.print(f"❌ エラー: {e}", style="red")
        finally:
            if sse_task and not sse_task.done():
                sse_task.cancel()
                try:
                    await sse_task
                except asyncio.CancelledError:
                    pass

        console.print("🏁 送信完了", style="bold green")

    try:
        asyncio.run(run_send())
    except KeyboardInterrupt:
        console.print("\n👋 送信終了", style="yellow")
        sys.exit(0)


@app.command()
def version():
    """
    バージョン情報を表示する

    Returns:
        None
    """

    console.print("FastAPI-MCP SSE テストクライアント v1.0.0", style="bold blue")
    console.print(
        "FastAPI-MCP サーバーのSSE接続をテストするためのツールです", style="dim"
    )


if __name__ == "__main__":
    app()

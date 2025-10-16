#!/usr/bin/env python3
"""
MCP HTTP クライアント CLI コマンド
"""

import asyncio
import json
import sys
from typing import Optional

import typer
from mcp_http_client import MCPHTTPClient
from rich.console import Console

app = typer.Typer(help="FastAPI-MCP HTTP テストクライアント")
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
) -> None:
    """
    HTTP接続でMCPサーバーをテストする

    Args:
        url: MCPサーバーのURL
        skip_tools: ツール一覧の取得をスキップするか

    Returns:
        None
    """

    async def run_test():
        client = MCPHTTPClient(base_url=url)
        await client.test_mcp_flow(test_tools=not skip_tools)

    try:
        asyncio.run(run_test())
    except KeyboardInterrupt:
        console.print("\n👋 テスト終了", style="yellow")
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
        client = MCPHTTPClient(base_url=url)
        console.print("📋 初期化中...", style="blue")
        init_result = await client.send_jsonrpc_message(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-http-client", "version": "1.0.0"},
            },
        )
        if not init_result:
            console.print("❌ 初期化に失敗", style="red")
            return

        # initialized通知を送信（MCPプロトコル必須）
        await client.send_notification("notifications/initialized", {})
        await asyncio.sleep(1)

        # カスタムメッセージ送信
        parsed_params = None
        if params:
            try:
                parsed_params = json.loads(params)
            except json.JSONDecodeError as e:
                console.print(f"❌ パラメータのJSONが無効: {e}", style="red")
                return

        console.print(f"\n📋 {method} を送信...", style="bold")
        await client.send_jsonrpc_message(method, parsed_params, 2)

    try:
        asyncio.run(run_send())
    except KeyboardInterrupt:
        console.print("\n👋 テスト終了", style="yellow")
        sys.exit(0)


@app.command()
def version() -> None:
    """
    バージョン情報を表示する

    Returns:
        None
    """

    console.print("FastAPI-MCP HTTP テストクライアント v1.0.0", style="bold blue")
    console.print(
        "FastAPI-MCP サーバーのHTTP接続をテストするためのツールです", style="dim"
    )


if __name__ == "__main__":
    app()

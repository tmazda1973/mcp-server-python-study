#!/usr/bin/env python3
"""
RSA鍵ペア生成スクリプト

JWT認証用のRSA秘密鍵と公開鍵を生成します。
"""

from pathlib import Path
from typing import Annotated

import typer
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from rich.console import Console

app = typer.Typer(help="JWT認証用のRSA鍵ペアを生成します")
console = Console()


@app.command()
def generate(
    private_key: Annotated[
        str,
        typer.Option(
            "--private-key",
            "-p",
            help="秘密鍵の保存パス",
        ),
    ] = "keys/jwt_private.pem",
    public_key: Annotated[
        str,
        typer.Option(
            "--public-key",
            "-P",
            help="公開鍵の保存パス",
        ),
    ] = "keys/jwt_public.pem",
    key_size: Annotated[
        int,
        typer.Option(
            "--key-size",
            "-s",
            help="鍵のサイズ（ビット）",
        ),
    ] = 2048,
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="既存のファイルを上書きする",
        ),
    ] = False,
) -> None:
    """
    RSA鍵ペアを生成してファイルに保存する

    Args:
        private_key: 秘密鍵の保存パス
        public_key: 公開鍵の保存パス
        key_size: 鍵のサイズ（ビット）
        force: 既存のファイルを上書きするか
    """

    # 鍵サイズを検証する
    if key_size not in [2048, 3072, 4096]:
        console.print(
            f"[red]エラー:[/red] 鍵サイズは 2048, 3072, 4096 のいずれかである必要があります（指定値: {key_size}）"
        )
        raise typer.Exit(code=1)

    # ディレクトリが存在しない場合は作成する
    private_key_file = Path(private_key)
    public_key_file = Path(public_key)
    # 既存ファイルのチェック
    if not force:
        if private_key_file.exists():
            console.print(
                f"[yellow]警告:[/yellow] 秘密鍵ファイルが既に存在します: {private_key_file}"
            )
            overwrite = typer.confirm("上書きしますか？")
            if not overwrite:
                console.print("[red]中止されました[/red]")
                raise typer.Exit(code=0)

        if public_key_file.exists():
            console.print(
                f"[yellow]警告:[/yellow] 公開鍵ファイルが既に存在します: {public_key_file}"
            )
            overwrite = typer.confirm("上書きしますか？")
            if not overwrite:
                console.print("[red]中止されました[/red]")
                raise typer.Exit(code=0)

    # ディレクトリが存在しない場合は作成する
    private_key_file.parent.mkdir(parents=True, exist_ok=True)
    public_key_file.parent.mkdir(parents=True, exist_ok=True)

    console.print(f"🔑 RSA鍵ペアを生成中... (鍵サイズ: {key_size} bits)")

    # 秘密鍵を生成する
    private_key_obj = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend(),
    )

    # 秘密鍵をPEM形式でファイルに保存する
    with open(private_key_file, "wb") as f:
        f.write(
            private_key_obj.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    console.print(f"✅ 秘密鍵を保存: [green]{private_key_file}[/green]")

    # 公開鍵を生成する
    public_key_obj = private_key_obj.public_key()

    # 公開鍵をPEM形式でファイルに保存する
    with open(public_key_file, "wb") as f:
        f.write(
            public_key_obj.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )

    console.print(f"✅ 公開鍵を保存: [green]{public_key_file}[/green]")

    # パーミッションを設定する（秘密鍵は600に設定）
    private_key_file.chmod(0o600)
    public_key_file.chmod(0o644)

    console.print("\n[bold green]🎉 RSA鍵ペアの生成が完了しました！[/bold green]")
    console.print("\n[bold yellow]⚠️  重要な注意事項:[/bold yellow]")
    console.print("  [yellow]1.[/yellow] 秘密鍵は絶対に公開しないでください")
    console.print(
        "  [yellow]2.[/yellow] 秘密鍵はバージョン管理システム（Git）に含めないでください"
    )
    console.print(
        "  [yellow]3.[/yellow] 本番環境では環境変数やシークレット管理サービスを使用してください"
    )


if __name__ == "__main__":
    app()

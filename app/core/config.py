from pathlib import Path
from typing import Literal

from pydantic import ConfigDict
from pydantic_settings import BaseSettings

PROJECT_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    # Environment
    APP_ENV: Literal["production", "development", "test"] = "production"
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # FastAPI-MCP Server config
    MCP_SERVER_NAME: str = "MCP Server"
    MCP_SERVER_DESCRIPTION: str = "Model Context Protocol Server"
    MCP_HOST: str = "127.0.0.1"
    MCP_PORT: int = 8000

    # Database config
    DATABASE_URL: str | None = None

    # Redis config
    REDIS_URL: str | None = None
    REDIS_PASSWORD: str | None = None
    REDIS_DB: int = 0
    REDIS_MAX_CONNECTIONS: int = 10

    # JWT Authentication config
    JWT_SECRET_KEY: str = (
        "your-super-secret-jwt-key-for-development-change-in-production"
    )
    JWT_ALGORITHM: str = "RS256"  # RS256（公開鍵/秘密鍵）またはHS256（共有鍵）
    JWT_EXPIRATION_HOURS: int = 24
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24時間

    # RS256用の鍵ファイルパス（JWT_ALGORITHM=RS256の場合に使用）
    JWT_PRIVATE_KEY_PATH: str = "keys/jwt_private.pem"
    JWT_PUBLIC_KEY_PATH: str = "keys/jwt_public.pem"
    # 環境変数で鍵を直接指定する場合（優先度: 環境変数 > ファイル）
    JWT_PRIVATE_KEY: str | None = None
    JWT_PUBLIC_KEY: str | None = None

    # API Key Authentication config
    API_KEY_NAME: str = "X-API-Key"
    API_KEY: str = "fastapi-mcp-dev-key-123"

    # MCP Authentication config
    MCP_REQUIRE_AUTH: bool = False  # 開発時はFalse、本番時はTrue
    AUTH_METHOD: Literal["ip", "jwt", "api_key", "none"] = "none"  # 認証方式
    ALLOWED_IPS: list[
        str
    ] = []  # 許可するIPアドレスリスト（カンマ区切り文字列から変換）
    ALLOWED_IPS_STR: str = ""  # 環境変数用（カンマ区切り文字列）
    TRUST_PROXY_HEADERS: bool = (
        False  # プロキシヘッダー（X-Forwarded-For等）を信頼するか
    )

    # CORS config
    ENABLE_CORS: bool = False
    CORS_ORIGINS: str = ""

    # Feature flags
    ENABLE_USER_INVITATION: bool = True

    # Azure OpenAI config
    AZURE_OPENAI_API_KEY: str | None = None
    AZURE_OPENAI_ENDPOINT: str | None = None
    AZURE_OPENAI_API_VERSION: str = "2024-10-21"
    AZURE_OPENAI_DEPLOYMENT_NAME: str = "gpt-4o"

    # Azure AI Search config
    AZURE_SEARCH_ENDPOINT: str | None = None
    AZURE_SEARCH_API_KEY: str | None = None
    AZURE_SEARCH_INDEX_NAME: str | None = None

    model_config = ConfigDict(
        case_sensitive=True,
        env_file=f"{PROJECT_DIR}/.env",
        env_file_encoding="utf-8",
        extra="ignore",  # 未定義の環境変数を無視
    )

    def __init__(self, **kwargs):
        """
        コンストラクタ

        環境変数からALLOWED_IPS_STRを読み込み、リストに変換する
        """
        super().__init__(**kwargs)
        # ALLOWED_IPS_STRをカンマ区切りでリストに変換
        if self.ALLOWED_IPS_STR:
            self.ALLOWED_IPS = [
                ip.strip() for ip in self.ALLOWED_IPS_STR.split(",") if ip.strip()
            ]


settings = Settings()

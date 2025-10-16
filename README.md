# MCP Server

## 概要

Model Context Protocol (MCP) を通じて、AI/LLMに各種ツールを提供するサーバーです。

Clean Architectureを採用し、保守性と拡張性を重視した設計になっています。

## アーキテクチャ

```
app/
├── api/
│   ├── presentation/          # プレゼンテーション層
│   │   ├── request/          # リクエストモデル
│   │   └── response/         # レスポンスモデル
│   ├── application/          # アプリケーション層
│   │   ├── usecases/         # ユースケース
│   │   ├── repositories/     # リポジトリプロトコル
│   │   └── presenters/       # プレゼンター
│   ├── domain/              # ドメイン層
│   │   ├── entities/        # エンティティ
│   │   └── services/        # ドメインサービス
│   ├── infra/               # インフラストラクチャ層
│   │   ├── repositories/    # リポジトリ実装
│   │   └── adapters/        # 外部サービスアダプター
│   ├── di/                  # 依存性注入
│   └── api_v1/              # APIルーター
│       └── mcp/             # MCPツール専用
├── core/                    # コア機能（設定、認証等）
├── middlewares/             # ミドルウェア（IP制限等）
└── models/                  # データベースモデル（基盤のみ）
```

### SOLID原則の適用

- **Single Responsibility Principle**: 1ファイル1クラス、1アクション1ユースケース1リポジトリ
- **Interface Segregation Principle**: 機能別リポジトリプロトコル分割
- **Dependency Inversion Principle**: ドメイン層がプレゼンテーション層に依存しない設計

## 技術スタック

- **FastAPI**: Webフレームワーク
- **FastAPI-MCP**: MCPプロトコル対応
- **Pydantic**: データ検証・設定管理
- **Redis**: JWT検証用（拡張対応、現在は未使用）
- **Docker**: コンテナ化
- **Python 3.11**: プログラミング言語
- **Azure OpenAI**: AI処理
- **httpx**: 非同期HTTPクライアント
- **Uvicorn**: ASGIサーバー（グレースフルシャットダウン対応）

## 機能

### 認証システム

- **IP制限**: CIDR表記対応のIP制限ミドルウェア（プライマリ認証）
- **JWT検証**: RS256公開鍵検証（拡張対応、検証のみ）
- **認証方式切替**: 環境変数で `ip`/`jwt`/`api_key`/`none` を選択可能

### 運用機能

- **グレースフルシャットダウン**: 進行中のリクエストを完了させてから停止
- **ヘルスチェック**: `/health` エンドポイントでサーバー状態を監視
- **構造化ログ**: レベル別のログ出力（ヘルスチェックは除外）

### MCPツール

- **calculate**: 数値計算（サンプル）
- **http_request**: HTTPリクエスト送信
- **rest_api_call**: REST API呼び出し
- **webhook_send**: Webhook送信
- **text_search**: テキスト検索
- **text_replace**: テキスト置換
- **text_analyze**: テキスト分析
- **data_transform**: データ変換（JSON/CSV/XML/YAML）
- **data_validate**: データ検証
- **data_aggregate**: データ集計

## セットアップ

### 前提条件

- Docker & Docker Compose
- Git

### クイックスタート

```bash
# 1. リポジトリクローン
git clone <repository-url>
cd mcp-server

# 2. 全サービス起動
make env-up-all

# 3. ブラウザでアクセス
open http://localhost:8000/
```

→ 自動的にSwagger UI（API仕様書）にリダイレクトされます

**注意**: ポート番号は `docker-compose.yml` の `ports` 設定に応じて変わります。
- デフォルト: `8000:8000` → `http://localhost:8000/`
- 変更例: `8031:8000` → `http://localhost:8031/`

### 詳細な起動手順

#### 1. 環境変数設定（オプション）
```bash
cp .env.example .env
# 必要に応じて .env を編集
```

#### 2. RSA鍵ペア生成（JWT検証用、オプション）
```bash
cd scripts/setup
make generate-keys
cd ../..
```

#### 3. サービス起動
```bash
# 初回起動（全サービス: app + redis）
make env-up-all

# アプリのみ起動（redis等が既に起動している場合）
make env-up-app-d

# フォアグラウンドで起動（ログ表示）
make env-up-app
```

#### 4. 動作確認
```bash
# ログ確認
make app-logs

# ヘルスチェック
curl -s http://localhost:8000/health | jq

# サーバー情報
curl -s http://localhost:8000/info | jq
```

## 開発

### よく使うコマンド

```bash
# 全サービス起動（初回）
make env-up-all

# アプリのみ起動（redis等が既に起動している場合）
make env-up-app-d

# 全サービス停止
make env-down

# 全サービス再起動
make env-reload-all

# アプリのみ再起動
make env-reload-app-d

# ログ確認
make app-logs

# コンテナシェル
make exec-bash

# テストクライアント起動
make env-up-test-client

# テストクライアントシェル
make exec-bash-test-client

# テストクライアント停止
make env-down-test-client

# 全ターゲット表示
make help
```

### コード品質

```bash
# リンターチェック
make check-format

# コードフォーマット
make run-format

# コードフォーマット（unsafe fix）
make run-format-unsafe-fix
```

### テスト

#### ユニットテスト

```bash
# 全テスト実行（コンテナ内）
docker compose exec app bash -c "source activate fastapi-mcp && source .venv/bin/activate && pytest -s --cov=app --cov-report=term-missing"

# ローカルでテスト実行
make pkg-install-local  # 初回のみ
pytest -s --cov=app --cov-report=term-missing
```

#### MCPクライアントテスト

```bash
# テストクライアントコンテナを起動
make env-up-test-client

# HTTPクライアントでテスト
cd scripts/mcp_client/http
make help           # 利用可能なコマンド一覧
make test           # 全テスト実行
make tools-list     # ツール一覧取得
make tool-calculate # calculateツール実行

# SSEクライアントでテスト
cd scripts/mcp_client/sse
make help           # 利用可能なコマンド一覧
make test           # 全テスト実行
make tools-list     # ツール一覧取得

# テストクライアントシェルに接続
make exec-bash-test-client

# テストクライアント停止
make env-down-test-client
```

### その他

```bash
# ローカルに依存パッケージをインストール（IDE用）
make pkg-install-local

# サービス停止 + ボリューム削除
make env-down-v
```

### エンドポイント一覧

| エンドポイント | 説明 |
|--------------|------|
| `http://localhost:8000/` | ルート（Swagger UIにリダイレクト） |
| `http://localhost:8000/docs` | Swagger UI（API仕様書） |
| `http://localhost:8000/health` | ヘルスチェック |
| `http://localhost:8000/info` | サーバー情報 |
| `http://localhost:8000/mcp` | MCP SSEエンドポイント |
| `http://localhost:8000/mcp-http` | MCP HTTPエンドポイント |

**注意**: ポート番号は `docker-compose.yml` の `ports` 設定（`<ホストポート>:8000`）に応じて変わります。

## 環境変数

### 必須設定

```env
# サーバー設定
MCP_SERVER_NAME=MCP-Server
MCP_HOST=0.0.0.0
MCP_PORT=8000

# 認証設定（IP制限）
AUTH_METHOD=ip  # ip/jwt/api_key/none
ALLOWED_IPS=127.0.0.1,192.168.0.0/16,10.0.0.0/8
TRUST_PROXY_HEADERS=false

# Redis（JWT検証用、拡張対応）
REDIS_URL=redis://redis:6379/0
```

### オプション設定

```env
# JWT検証（拡張対応）
JWT_ALGORITHM=RS256
JWT_PUBLIC_KEY_PATH=keys/jwt_public.pem

# Azure OpenAI
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2024-05-01-preview

# CORS（通常は不要）
ENABLE_CORS=false
CORS_ORIGINS=

# ログレベル
LOG_LEVEL=INFO

# 環境
APP_ENV=development
```

### 認証方式

- **`AUTH_METHOD=ip`**: IP制限（推奨、内部利用）
- **`AUTH_METHOD=jwt`**: JWT検証（拡張対応、現在は未使用）
- **`AUTH_METHOD=none`**: 認証なし（開発環境のみ）

詳細は [`docs/ip_restriction.md`](docs/ip_restriction.md) および [`docs/jwt_rs256_migration.md`](docs/jwt_rs256_migration.md) を参照してください。

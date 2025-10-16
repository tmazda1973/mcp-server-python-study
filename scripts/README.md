# 📜 スクリプト集

MCPサーバーのセットアップ、テスト、運用に必要なスクリプト集です。

## 📁 ファイル構成

```
scripts/
├── setup/                     # セットアップスクリプト
│   ├── generate_rsa_keys.py  # RSA鍵ペア生成（JWT RS256用）
│   └── README.md             # セットアップガイド
├── mcp_client/               # テストクライアント
│   ├── http/
│   │   ├── client.py         # HTTPクライアント実装
│   │   ├── Makefile          # HTTP専用のMakefileコマンド
│   │   └── README.md         # HTTP専用のREADME
│   └── sse/
│       ├── client.py         # SSEクライアント実装
│       ├── Makefile          # SSE専用のMakefileコマンド
│       └── README.md         # SSE専用のREADME
└── README.md                 # このファイル
```

## 🔧 セットアップスクリプト

### RSA鍵ペア生成

JWT認証（RS256）用のRSA秘密鍵・公開鍵を生成します。

```bash
# デフォルト設定で生成
python scripts/setup/generate_rsa_keys.py

# オプション指定
python scripts/setup/generate_rsa_keys.py --key-size 4096 --force
```

詳細は [`scripts/setup/README.md`](./setup/README.md) を参照してください。

---

## 🚀 使用方法

### **Docker Composeでの実行（推奨）**

#### 1. サーバーを起動
```bash
# メインアプリケーションを起動
docker-compose up app -d

# サーバーの起動確認
docker-compose logs app
```

#### 2. テストクライアントでテスト実行

```bash
# HTTP専用テスト
make -C mcp_client/http test         # HTTPプロトコルテスト
make -C mcp_client/http tools-list   # ツール一覧を取得
make -C mcp_client/http health-check # ヘルスチェック

# SSE専用テスト
make -C mcp_client/sse test          # SSEプロトコルテスト
make -C mcp_client/sse connect       # SSE接続を維持
make -C mcp_client/sse stress-test   # ストレステスト

# 直接実行（デバッグ用）
docker-compose run --rm test-client python mcp_client/http/client.py test --url http://app:8000
docker-compose run --rm test-client python mcp_client/sse/client.py test --url http://app:8000
```

#### 3. 詳細オプション

```bash
# クイックテスト（ツール一覧スキップ）
make -C mcp_client/http test-quick
make -C mcp_client/sse test-quick

# 詳細ログ付きテスト
make -C mcp_client/http test-verbose
make -C mcp_client/sse test-verbose

# SSE接続タイムアウト設定
make -C mcp_client/sse connect-timeout    # 60秒
make -C mcp_client/sse connect-long       # 5分間

# カスタムURL（外部サーバーのテスト）
MCP_SERVER_URL=http://localhost:8020 make -C mcp_client/http test
```

### **スタンドアロンでの実行**

#### 1. 依存関係をインストール
```bash
pip install httpx typer[all] rich
```

#### 2. 直接実行
```bash
# HTTPテスト
python scripts/mcp_client/http/client.py test --url http://localhost:8000

# SSEテスト  
python scripts/mcp_client/sse/client.py test --url http://localhost:8000

# SSE接続維持
python scripts/mcp_client/sse/client.py connect --url http://localhost:8000
```

## 🔧 テストクライアントの機能

### **SSEクライアント（mcp_client/sse/client.py）**

- ✅ **SSE接続**: リアルタイムでサーバーからのメッセージを受信
- ✅ **JSONRPCメッセージ送信**: MCP標準のJSONRPCメッセージを送信
- ✅ **セッション管理**: サーバーから割り当てられたセッションIDを自動管理
- ✅ **自動テストフロー**: 初期化→ツール一覧→実際のツール呼び出しまで自動実行
- ✅ **リアルタイム通信**: 長時間接続とストリーミングレスポンス

### **HTTPクライアント（mcp_client/http/client.py）**

- ✅ **HTTP/HTTPS通信**: RESTful APIスタイルでMCPサーバーと通信
- ✅ **セッション管理**: HTTPヘッダーで`mcp-session-id`を自動管理
- ✅ **カスタムメッセージ送信**: 任意のJSONRPCメッセージを送信可能
- ✅ **レスポンス詳細表示**: HTTPステータス、ヘッダー、JSONレスポンスを詳細表示
- ✅ **個別ツールテスト**: 各MCPツールの単体テスト機能

# 🌐 MCP HTTP クライアント

FastAPI-MCPサーバーのHTTPプロトコル（`/mcp-http`エンドポイント）をテストするためのクライアントツールです。

## 📁 ファイル構成

```
http/
├── client.py         # HTTPクライアント実装
├── Makefile          # HTTP専用のMakefileコマンド
└── README.md         # このファイル
```

## 🚀 使用方法

### **基本的なテスト**

```bash
# HTTPプロトコルテスト
make test

# クイックテスト（ツール一覧スキップ）
make test-quick

# 詳細ログ付きテスト
make test-verbose
```

### **ツール操作**

```bash
# ツール一覧を取得
make tools-list

# ツール数を確認
make tools-count

# 個別ツールテスト
make tool-system-status
make tool-calculate
```

### **カスタムメッセージ送信**

```bash
# initializeメッセージ
make send-initialize

# カスタムメッセージ
make send-custom METHOD=tools/list PARAMS='{}'
make send-custom METHOD=tools/call PARAMS='{"name":"system_status","arguments":{"api_key":"fastapi-mcp-dev-key-123"}}'
```

### **開発・デバッグ**

```bash
# デバッグ実行
make debug

# コンテナシェル接続
make shell

# ヘルスチェック
make health-check
```

## 🔧 HTTPクライアントの特徴

### **✅ 主な機能**

- **HTTP/HTTPS通信**: RESTful APIスタイルでMCPサーバーと通信
- **セッション管理**: HTTPヘッダーで`mcp-session-id`を自動管理
- **カスタムメッセージ送信**: 任意のJSONRPCメッセージを送信可能
- **レスポンス詳細表示**: HTTPステータス、ヘッダー、JSONレスポンスを詳細表示
- **エラーハンドリング**: 適切なエラーメッセージとステータス表示

### **🔍 セッション管理**

HTTPクライアントは以下の手順でセッション管理を行います：

1. **初期化**: `initialize`メッセージを送信
2. **セッションID取得**: レスポンスヘッダーから`mcp-session-id`を取得
3. **セッション維持**: 後続のリクエストでヘッダーにセッションIDを含める

### **📊 レスポンス形式**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "experimental": {},
      "tools": {
        "listChanged": false
      }
    },
    "serverInfo": {
      "name": "FastAPI-MCP-Server",
      "version": "Docker環境で動作するFastAPI-MCPサーバー"
    }
  }
}
```

## 🧪 テストシナリオ例

### **基本機能テスト**

```bash
# 1. ヘルスチェック
make health-check

# 2. 基本テスト
make test

# 3. ツール確認
make tools-list
make tools-count
```

### **個別ツールテスト**

```bash
# システム状態取得
make tool-system-status

# 計算ツール
make tool-calculate

# カスタムツール呼び出し
make send-custom METHOD=tools/call PARAMS='{"name":"text_search","arguments":{"text":"Hello world","pattern":"world","api_key":"fastapi-mcp-dev-key-123"}}'
```

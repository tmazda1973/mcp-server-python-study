# 🔌 MCP SSE クライアント

FastAPI-MCPサーバーのSSEプロトコル（`/mcp`エンドポイント）をテストするためのクライアントツールです。

## 📁 ファイル構成

```
sse/
├── client.py         # SSEクライアント実装
├── Makefile          # SSE専用のMakefileコマンド
└── README.md         # このファイル
```

## 🚀 使用方法

### **基本的なテスト**

```bash
# SSEプロトコルテスト
make test

# クイックテスト（ツール一覧スキップ）
make test-quick

# 詳細ログ付きテスト
make test-verbose
```

### **接続テスト**

```bash
# SSE接続を維持（手動終了）
make connect

# SSE接続を維持（60秒タイムアウト）
make connect-timeout

# SSE長時間接続テスト（5分間）
make connect-long

# ストレステスト（5分間接続維持）
make stress-test
```

### **ツール操作**

```bash
# ツール一覧を取得
make tools-list

# ツール数を確認
make tools-count
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

## 🔧 SSEクライアントの特徴

### **✅ 主な機能**

- **SSE接続**: リアルタイムでサーバーからのメッセージを受信
- **JSONRPCメッセージ送信**: MCP標準のJSONRPCメッセージを送信
- **セッション管理**: サーバーから割り当てられたセッションIDを自動管理
- **自動テストフロー**: 初期化→ツール一覧→実際のツール呼び出しまで自動実行
- **リアルタイム通信**: サーバーからのストリーミングレスポンスを受信

### **🔍 SSE通信フロー**

SSEクライアントは以下の手順で通信を行います：

1. **SSE接続開始**: `/mcp/messages/?session_id=xxx` に接続
2. **セッションID取得**: 最初のイベントでセッションIDを受信
3. **メッセージ送信**: JSONRPCメッセージをPOSTで送信
4. **レスポンス受信**: SSEストリームでレスポンスを受信

### **📡 SSEイベント形式**

```
event: endpoint
data: /mcp/messages/?session_id=abc123

event: message
data: {"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05",...}}
```

### **🔄 リアルタイム通信の利点**

- **低レイテンシ**: サーバーからの即座のレスポンス
- **双方向通信**: サーバーからの通知も受信可能
- **接続維持**: 長時間の接続でも効率的
- **ストリーミング**: 大きなデータの段階的受信

## 🧪 テストシナリオ例

### **基本機能テスト**

```bash
# 1. ヘルスチェック
make health-check

# 2. 基本テスト
make test

# 3. 接続維持テスト
make connect-timeout
```

### **パフォーマンステスト**

```bash
# 長時間接続テスト
make connect-long

# ストレステスト
make stress-test

# 詳細ログでパフォーマンス確認
make test-verbose
```

### **リアルタイム通信テスト**

```bash
# 接続を維持してリアルタイムメッセージを確認
make connect

# 別ターミナルでカスタムメッセージ送信
make send-custom METHOD=tools/call PARAMS='{"name":"system_status","arguments":{"api_key":"fastapi-mcp-dev-key-123"}}'
```

# 🔌 MCP SSE クライアント Makefile
# 
# 使用方法:
#   make help          - ヘルプを表示
#   make test          - SSEプロトコルテスト
#   make connect       - SSE接続を維持
#   make tools-list    - ツール一覧を取得
#   make health-check  - ヘルスチェック

# デフォルト設定
DOCKER_COMPOSE = docker-compose -f ../../../docker-compose.yml
TEST_CLIENT_SERVICE = test-client
MCP_SERVER_URL ?= http://app:8000
CLIENT_SCRIPT = cli.py

# デフォルトターゲット
.DEFAULT_GOAL := help

# ヘルプ表示
.PHONY: help
help: ## Show this help message
	@echo "🔌 MCP SSE クライアント"
	@echo ""
	@echo "利用可能なコマンド:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-30s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "環境変数:"
	@echo "  MCP_SERVER_URL    MCPサーバーのURL (デフォルト: http://app:8000)"

# =============================================================================
# テスト実行
# =============================================================================

.PHONY: test
test: ## SSEプロトコルテストを実行
	@echo "🔌 SSEプロトコルテストを実行中..."
	$(DOCKER_COMPOSE) run --rm $(TEST_CLIENT_SERVICE) python mcp_client/sse/$(CLIENT_SCRIPT) test --url $(MCP_SERVER_URL)

.PHONY: test-quick
test-quick: ## クイックテスト（ツール一覧スキップ）
	@echo "⚡ SSEクイックテストを実行中..."
	$(DOCKER_COMPOSE) run --rm $(TEST_CLIENT_SERVICE) python mcp_client/sse/$(CLIENT_SCRIPT) test --url $(MCP_SERVER_URL) --skip-tools

.PHONY: test-verbose
test-verbose: ## 詳細ログ付きテスト
	@echo "🔍 SSE詳細テストを実行中..."
	$(DOCKER_COMPOSE) run --rm $(TEST_CLIENT_SERVICE) python mcp_client/sse/$(CLIENT_SCRIPT) test --url $(MCP_SERVER_URL) --verbose

# =============================================================================
# 接続テスト
# =============================================================================

.PHONY: connect
connect: ## SSE接続を維持（リアルタイム通信テスト）
	@echo "🔗 SSE接続を維持中... (Ctrl+Cで終了)"
	$(DOCKER_COMPOSE) run --rm $(TEST_CLIENT_SERVICE) python mcp_client/sse/$(CLIENT_SCRIPT) connect --url $(MCP_SERVER_URL)

.PHONY: connect-timeout
connect-timeout: ## SSE接続を維持（60秒タイムアウト）
	@echo "🔗 SSE接続を維持中（60秒）..."
	$(DOCKER_COMPOSE) run --rm $(TEST_CLIENT_SERVICE) python mcp_client/sse/$(CLIENT_SCRIPT) connect --url $(MCP_SERVER_URL) --timeout 60

.PHONY: connect-long
connect-long: ## SSE接続を維持（5分間）
	@echo "🔗 SSE長時間接続テスト（5分間）..."
	$(DOCKER_COMPOSE) run --rm $(TEST_CLIENT_SERVICE) python mcp_client/sse/$(CLIENT_SCRIPT) connect --url $(MCP_SERVER_URL) --timeout 300

# =============================================================================
# ツール操作
# =============================================================================

.PHONY: tools-list
tools-list: ## ツール一覧を取得
	@echo "🛠️  SSEでツール一覧を取得中..."
	$(DOCKER_COMPOSE) run --rm $(TEST_CLIENT_SERVICE) python mcp_client/sse/$(CLIENT_SCRIPT) send tools/list --url $(MCP_SERVER_URL) --params '{}'

# =============================================================================
# 開発・デバッグ
# =============================================================================

.PHONY: debug
debug: ## SSEクライアントのデバッグ実行
	@echo "🐛 SSEクライアントをデバッグモードで実行..."
	$(DOCKER_COMPOSE) run --rm $(TEST_CLIENT_SERVICE) python mcp_client/sse/$(CLIENT_SCRIPT) test --url $(MCP_SERVER_URL) --verbose

.PHONY: shell
shell: ## テストクライアントコンテナにシェル接続
	@echo "🐚 テストクライアントコンテナに接続中..."
	$(DOCKER_COMPOSE) run --rm -it $(TEST_CLIENT_SERVICE) /bin/bash

# =============================================================================
# ヘルスチェック
# =============================================================================

.PHONY: health-check
health-check: ## SSEでサーバーのヘルスチェック
	@echo "🏥 SSEでヘルスチェック実行中..."
	@if $(DOCKER_COMPOSE) run --rm $(TEST_CLIENT_SERVICE) python mcp_client/sse/$(CLIENT_SCRIPT) test --url $(MCP_SERVER_URL) --skip-tools > /dev/null 2>&1; then \
		echo "✅ SSEサーバーは正常に動作しています"; \
	else \
		echo "❌ SSEサーバーに問題があります"; \
		exit 1; \
	fi

# =============================================================================
# 個別ツールテスト
# =============================================================================

.PHONY: tools-count
tools-count: ## ツール数を確認
	@echo "📊 SSEでツール数を確認中..."
	$(DOCKER_COMPOSE) run --rm $(TEST_CLIENT_SERVICE) python mcp_client/sse/$(CLIENT_SCRIPT) test --url $(MCP_SERVER_URL) | grep -c '"name":'

.PHONY: tool-system-status
tool-system-status: ## system_statusツールを呼び出し
	@echo "💻 SSEでシステム状態を取得中..."
	$(DOCKER_COMPOSE) run --rm $(TEST_CLIENT_SERVICE) python mcp_client/sse/$(CLIENT_SCRIPT) send tools/call --url $(MCP_SERVER_URL) --params '{"name":"system_status","arguments":{"api_key":"fastapi-mcp-dev-key-123"}}'

.PHONY: tool-calculate
tool-calculate: ## calculateツールを呼び出し
	@echo "🧮 SSEで計算ツールをテスト中..."
	$(DOCKER_COMPOSE) run --rm $(TEST_CLIENT_SERVICE) python mcp_client/sse/$(CLIENT_SCRIPT) send tools/call --url $(MCP_SERVER_URL) --params '{"name":"calculate","arguments":{"a":10.0,"b":5.0,"api_key":"fastapi-mcp-dev-key-123"}}'

.PHONY: tool-text-search
tool-text-search: ## text_searchツールを呼び出し
	@echo "🔍 SSEでテキスト検索ツールをテスト中..."
	$(DOCKER_COMPOSE) run --rm $(TEST_CLIENT_SERVICE) python mcp_client/sse/$(CLIENT_SCRIPT) send tools/call --url $(MCP_SERVER_URL) --params '{"name":"text_search","arguments":{"text":"Hello world! This is a test text for searching.","pattern":"test","case_sensitive":false,"api_key":"fastapi-mcp-dev-key-123"}}'

.PHONY: tool-data-transform
tool-data-transform: ## data_transformツールを呼び出し
	@echo "🔄 SSEでデータ変換ツールをテスト中..."
	$(DOCKER_COMPOSE) run --rm $(TEST_CLIENT_SERVICE) python mcp_client/sse/$(CLIENT_SCRIPT) send tools/call --url $(MCP_SERVER_URL) --params '{"name":"data_transform","arguments":{"data":"{\"name\":\"John\",\"age\":30}","from_format":"json","to_format":"csv","api_key":"fastapi-mcp-dev-key-123"}}'

.PHONY: tool-data-validate
tool-data-validate: ## data_validateツールを呼び出し
	@echo "✅ SSEでデータ検証ツールをテスト中..."
	$(DOCKER_COMPOSE) run --rm $(TEST_CLIENT_SERVICE) python mcp_client/sse/$(CLIENT_SCRIPT) send tools/call --url $(MCP_SERVER_URL) --params '{"name":"data_validate","arguments":{"data":"{\"name\":\"John\",\"age\":30}","schema_type":"json_schema","schema_definition":"{\"type\":\"object\",\"properties\":{\"name\":{\"type\":\"string\"},\"age\":{\"type\":\"integer\"}},\"required\":[\"name\",\"age\"]}","api_key":"fastapi-mcp-dev-key-123"}}'

.PHONY: tool-data-aggregate
tool-data-aggregate: ## data_aggregateツールを呼び出し
	@echo "📊 SSEでデータ集計ツールをテスト中..."
	$(DOCKER_COMPOSE) run --rm $(TEST_CLIENT_SERVICE) python mcp_client/sse/$(CLIENT_SCRIPT) send tools/call --url $(MCP_SERVER_URL) --params '{"name":"data_aggregate","arguments":{"data":"[{\"category\":\"A\",\"value\":10},{\"category\":\"B\",\"value\":20},{\"category\":\"A\",\"value\":15}]","aggregate_functions":{"value":"sum"},"api_key":"fastapi-mcp-dev-key-123"}}'

# =============================================================================
# カスタムメッセージ送信
# =============================================================================

.PHONY: send-initialize
send-initialize: ## initializeメッセージを送信
	@echo "📋 SSEでinitializeメッセージを送信中..."
	$(DOCKER_COMPOSE) run --rm $(TEST_CLIENT_SERVICE) python mcp_client/sse/$(CLIENT_SCRIPT) send initialize --url $(MCP_SERVER_URL) --params '{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"sse-test","version":"1.0.0"}}'

.PHONY: send-custom
send-custom: ## カスタムメッセージを送信（METHOD, PARAMSを指定）
	@echo "📤 SSEでカスタムメッセージを送信中..."
	@echo "使用方法: make send-custom METHOD=tools/list PARAMS='{}'"
	@if [ -z "$(METHOD)" ] || [ -z "$(PARAMS)" ]; then \
		echo "❌ エラー: METHOD と PARAMS を指定してください"; \
		echo "例: make send-custom METHOD=tools/list PARAMS='{}'"; \
		exit 1; \
	fi
	$(DOCKER_COMPOSE) run --rm $(TEST_CLIENT_SERVICE) python mcp_client/sse/$(CLIENT_SCRIPT) send $(METHOD) --url $(MCP_SERVER_URL) --params '$(PARAMS)'

# =============================================================================
# パフォーマンステスト
# =============================================================================

.PHONY: stress-test
stress-test: ## ストレステスト（長時間接続）
	@echo "💪 SSEストレステストを実行中（5分間接続維持）..."
	$(DOCKER_COMPOSE) run --rm $(TEST_CLIENT_SERVICE) python mcp_client/sse/$(CLIENT_SCRIPT) connect --url $(MCP_SERVER_URL) --timeout 300

# 🌐 MCP HTTP クライアント Makefile
# 
# 使用方法:
#   make help          - ヘルプを表示
#   make test          - HTTPプロトコルテスト
#   make tools-list    - ツール一覧を取得
#   make tools-count   - ツール数を確認
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
	@echo "🌐 MCP HTTP クライアント"
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
test: ## HTTPプロトコルテストを実行
	@echo "🌐 HTTPプロトコルテストを実行中..."
	$(DOCKER_COMPOSE) run --rm $(TEST_CLIENT_SERVICE) python mcp_client/http/$(CLIENT_SCRIPT) test --url $(MCP_SERVER_URL)

.PHONY: test-quick
test-quick: ## クイックテスト（ツール一覧スキップ）
	@echo "⚡ HTTPクイックテストを実行中..."
	$(DOCKER_COMPOSE) run --rm $(TEST_CLIENT_SERVICE) python mcp_client/http/$(CLIENT_SCRIPT) test --url $(MCP_SERVER_URL) --skip-tools

.PHONY: test-verbose
test-verbose: ## 詳細ログ付きテスト
	@echo "🔍 HTTP詳細テストを実行中..."
	$(DOCKER_COMPOSE) run --rm $(TEST_CLIENT_SERVICE) python mcp_client/http/$(CLIENT_SCRIPT) test --url $(MCP_SERVER_URL) --verbose

# =============================================================================
# ツール操作
# =============================================================================

.PHONY: tools-list
tools-list: ## ツール一覧を取得
	@echo "🛠️  HTTPでツール一覧を取得中..."
	$(DOCKER_COMPOSE) run --rm $(TEST_CLIENT_SERVICE) python mcp_client/http/$(CLIENT_SCRIPT) send tools/list --url $(MCP_SERVER_URL) --params '{}'

.PHONY: tools-count
tools-count: ## ツール数を確認
	@echo "📊 HTTPでツール数を確認中..."
	$(DOCKER_COMPOSE) run --rm $(TEST_CLIENT_SERVICE) python mcp_client/http/$(CLIENT_SCRIPT) test --url $(MCP_SERVER_URL) | grep -c '"name":'

.PHONY: tool-system-status
tool-system-status: ## system_statusツールを呼び出し
	@echo "💻 HTTPでシステム状態を取得中..."
	$(DOCKER_COMPOSE) run --rm $(TEST_CLIENT_SERVICE) python mcp_client/http/$(CLIENT_SCRIPT) send tools/call --url $(MCP_SERVER_URL) --params '{"name":"system_status","arguments":{"api_key":"fastapi-mcp-dev-key-123"}}'

.PHONY: tool-calculate
tool-calculate: ## calculateツールを呼び出し
	@echo "🧮 HTTPで計算ツールをテスト中..."
	$(DOCKER_COMPOSE) run --rm $(TEST_CLIENT_SERVICE) python mcp_client/http/$(CLIENT_SCRIPT) send tools/call --url $(MCP_SERVER_URL) --params '{"name":"calculate","arguments":{"a":10.0,"b":5.0,"api_key":"fastapi-mcp-dev-key-123"}}'

# =============================================================================
# 開発・デバッグ
# =============================================================================

.PHONY: debug
debug: ## HTTPクライアントのデバッグ実行
	@echo "🐛 HTTPクライアントをデバッグモードで実行..."
	$(DOCKER_COMPOSE) run --rm $(TEST_CLIENT_SERVICE) python mcp_client/http/$(CLIENT_SCRIPT) test --url $(MCP_SERVER_URL) --verbose

.PHONY: shell
shell: ## テストクライアントコンテナにシェル接続
	@echo "🐚 テストクライアントコンテナに接続中..."
	$(DOCKER_COMPOSE) run --rm -it $(TEST_CLIENT_SERVICE) /bin/bash

# =============================================================================
# ヘルスチェック
# =============================================================================

.PHONY: health-check
health-check: ## HTTPでサーバーのヘルスチェック
	@echo "🏥 HTTPでヘルスチェック実行中..."
	@if $(DOCKER_COMPOSE) run --rm $(TEST_CLIENT_SERVICE) python mcp_client/http/$(CLIENT_SCRIPT) send tools/list --url $(MCP_SERVER_URL) --params '{}' > /dev/null 2>&1; then \
		echo "✅ HTTPサーバーは正常に動作しています"; \
	else \
		echo "❌ HTTPサーバーに問題があります"; \
		exit 1; \
	fi

# =============================================================================
# カスタムメッセージ送信
# =============================================================================

.PHONY: send-initialize
send-initialize: ## initializeメッセージを送信
	@echo "📋 HTTPでinitializeメッセージを送信中..."
	$(DOCKER_COMPOSE) run --rm $(TEST_CLIENT_SERVICE) python mcp_client/http/$(CLIENT_SCRIPT) send initialize --url $(MCP_SERVER_URL) --params '{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"http-test","version":"1.0.0"}}'

.PHONY: send-custom
send-custom: ## カスタムメッセージを送信（METHOD, PARAMSを指定）
	@echo "📤 HTTPでカスタムメッセージを送信中..."
	@echo "使用方法: make send-custom METHOD=tools/list PARAMS='{}'"
	@if [ -z "$(METHOD)" ] || [ -z "$(PARAMS)" ]; then \
		echo "❌ エラー: METHOD と PARAMS を指定してください"; \
		echo "例: make send-custom METHOD=tools/list PARAMS='{}'"; \
		exit 1; \
	fi
	$(DOCKER_COMPOSE) run --rm $(TEST_CLIENT_SERVICE) python mcp_client/http/$(CLIENT_SCRIPT) send $(METHOD) --url $(MCP_SERVER_URL) --params '$(PARAMS)'

"""
Azure OpenAI Adapter 統合テスト

実行方法:
    pytest tests/infra/adapters/test_azure_openai_adapter_integration.py -v -s
"""

import pytest

from app.api.infra.adapters import AzureOpenAIAdapter
from app.core.config import settings


@pytest.mark.skipif(
    not settings.AZURE_OPENAI_API_KEY or not settings.AZURE_OPENAI_ENDPOINT,
    reason="Azure OpenAI credentials not configured",
)
class TestAzureOpenAIAdapterIntegration:
    """
    統合テスト（Azure OpenAIアダプター）
    """

    @pytest.fixture
    def adapter(self) -> AzureOpenAIAdapter:
        return AzureOpenAIAdapter()

    @pytest.mark.asyncio
    async def test_chat_with_real_api(self, adapter: AzureOpenAIAdapter) -> None:
        """
        正常系テスト

        関数:
            - chat

        概要:
        - 実際のAzure OpenAI APIを使用したチャット補完のテスト
        - 簡単な質問を送信して、正常にレスポンスが返ることを確認する
        """

        # Arrange
        messages = [
            {"role": "system", "content": "あなたは親切なアシスタントです。"},
            {"role": "user", "content": "こんにちは！簡単に自己紹介してください。"},
        ]

        # Act
        response = await adapter.chat(
            messages=messages,
            temperature=0.7,
            max_tokens=100,
        )

        # Assert
        assert response is not None
        assert "content" in response
        assert "role" in response
        assert "finish_reason" in response
        assert "usage" in response
        assert response["role"] == "assistant"
        assert len(response["content"]) > 0
        assert response["usage"]["total_tokens"] > 0

        print(f"\n✅ Chat Response: {response['content']}")
        print(f"✅ Usage: {response['usage']}")

    @pytest.mark.asyncio
    async def test_generate_json_with_real_api(
        self,
        adapter: AzureOpenAIAdapter,
    ) -> None:
        """
        正常系テスト

        概要:
        - 実際のAzure OpenAI APIを使用したJSON生成のテスト
        - 構造化されたJSONレスポンスが返ることを確認する
        """

        # Arrange
        system_prompt = "あなたは構造化データを生成するアシスタントです。"
        user_prompt = """
        以下の情報をJSON形式で出力してください：
        - name: "太郎"
        - age: 30
        - city: "東京"

        必ず以下の形式で出力してください：
        {
            "name": "太郎",
            "age": 30,
            "city": "東京"
        }
        """

        # Act
        response = await adapter.generate_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.1,
        )

        # Assert
        assert response is not None
        assert "name" in response
        assert "age" in response
        assert "city" in response
        assert response["name"] == "太郎"
        assert response["age"] == 30
        assert response["city"] == "東京"

        print(f"\n✅ JSON Response: {response}")

    @pytest.mark.asyncio
    async def test_stream_with_real_api(
        self,
        adapter: AzureOpenAIAdapter,
    ) -> None:
        """
        正常系テスト

        概要:
        - 実際のAzure OpenAI APIを使用したストリーミングのテスト
        - ストリーミングレスポンスが正常に受信できることを確認する
        """

        # Arrange
        messages = [
            {"role": "system", "content": "あなたは簡潔に答えるアシスタントです。"},
            {"role": "user", "content": "1から5まで数えてください。"},
        ]

        # Act
        chunks = []
        async for chunk in adapter.stream(messages=messages, temperature=0.5):
            chunks.append(chunk)
            if hasattr(chunk, "choices") and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if hasattr(delta, "content") and delta.content:
                    print(delta.content, end="", flush=True)

        # Assert
        assert len(chunks) > 0
        print(f"\n✅ Received {len(chunks)} chunks")

    @pytest.mark.asyncio
    async def test_error_handling_with_invalid_deployment(self) -> None:
        """
        異常系テスト

        概要:
        - 無効なデプロイメント名でエラーハンドリングをテストする
        """

        # Arrange
        adapter = AzureOpenAIAdapter(deployment_name="invalid-deployment-name")
        messages = [
            {"role": "user", "content": "Hello"},
        ]

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await adapter.chat(messages=messages)

        assert exc_info.value is not None
        print(f"\n✅ Expected error occurred: {type(exc_info.value).__name__}")

    @pytest.mark.asyncio
    async def test_connection_info(self, adapter: AzureOpenAIAdapter) -> None:
        """
        正常系テスト

        概要:
        - 接続情報が正しく設定されていることを確認する
        """

        # Assert
        assert adapter._api_key is not None
        assert adapter._azure_endpoint is not None
        assert adapter._deployment_name is not None
        assert adapter._api_version is not None

        print("\n✅ Connection Info:")
        print(f"   Endpoint: {adapter._azure_endpoint}")
        print(f"   Deployment: {adapter._deployment_name}")
        print(f"   API Version: {adapter._api_version}")
        print(f"   API Key: {adapter._api_key[:10]}...{adapter._api_key[-10:]}")

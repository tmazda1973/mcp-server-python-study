from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.api.infra.adapters import AzureOpenAIAdapter


@pytest.fixture
def mock_openai_client():
    """
    Azure OpenAIクライアント
    """
    return MagicMock()


@pytest.fixture
def adapter(mock_openai_client):
    """
    OpenAIアダプター
    """
    with patch(
        "app.api.infra.adapters.azure_openai_adapter.AsyncAzureOpenAI"
    ) as mock_client_class:
        mock_client_class.return_value = mock_openai_client
        adapter = AzureOpenAIAdapter(
            api_key="test-api-key",
            api_version="2024-05-01-preview",
            azure_endpoint="https://test.openai.azure.com/",
            deployment_name="gpt-4o",
        )
        adapter._client = mock_openai_client
        return adapter


class TestAzureOpenAIAdapter:
    """
    テストクラス

    - Azure OpenAIアダプター（低レベルAPI呼び出しのみ）
    """

    @pytest.mark.asyncio
    async def test_chat_success(
        self,
        adapter,
        mock_openai_client,
    ) -> None:
        """
        正常系テスト

        関数:
            - chat
        """

        # モックを設定する
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Hello, World!"
        mock_response.choices[0].message.role = "assistant"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.choices[0].message.tool_calls = None
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15
        mock_openai_client.chat.completions.create = AsyncMock(
            return_value=mock_response
        )

        # テスト対象を実行する
        result = await adapter.chat(
            messages=[{"role": "user", "content": "Hello"}],
            temperature=0.5,
        )

        # 実行結果を検証する
        assert result["content"] == "Hello, World!"
        assert result["role"] == "assistant"
        assert result["finish_reason"] == "stop"
        assert result["usage"]["total_tokens"] == 15
        assert result["tool_calls"] is None

        # APIが正しいパラメータで呼ばれたことを確認
        mock_openai_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_openai_client.chat.completions.create.call_args.kwargs
        assert call_kwargs["model"] == "gpt-4o"
        assert call_kwargs["temperature"] == 0.5
        assert len(call_kwargs["messages"]) == 1

    @pytest.mark.asyncio
    async def test_generate_json_success(
        self,
        adapter,
        mock_openai_client,
    ) -> None:
        """
        正常系テスト

        関数:
            - generate_json
        """

        # モックを設定する
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"key": "value", "number": 42}'
        mock_response.choices[0].message.role = "assistant"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.choices[0].message.tool_calls = None
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15
        mock_openai_client.chat.completions.create = AsyncMock(
            return_value=mock_response
        )

        # テスト対象を実行する
        result = await adapter.generate_json(
            system_prompt="You are a helpful assistant.",
            user_prompt="Generate JSON",
            temperature=0.1,
        )

        # 実行結果を検証する
        assert result["key"] == "value"
        assert result["number"] == 42

        # response_format が設定されていることを確認
        call_kwargs = mock_openai_client.chat.completions.create.call_args.kwargs
        assert call_kwargs["response_format"] == {"type": "json_object"}

    @pytest.mark.asyncio
    async def test_stream_success(
        self,
        adapter,
        mock_openai_client,
    ) -> None:
        """
        正常系テスト

        関数:
            - stream
        """

        # モックを設定する
        async def mock_stream():
            chunks = ["Hello", ", ", "World", "!"]
            for chunk_text in chunks:
                mock_chunk = MagicMock()
                mock_chunk.choices = [MagicMock()]
                mock_chunk.choices[0].delta.content = chunk_text
                yield mock_chunk

        mock_openai_client.chat.completions.create = AsyncMock(
            return_value=mock_stream()
        )

        # テスト対象を実行する
        result_chunks = []
        async for chunk in adapter.stream(
            messages=[{"role": "user", "content": "Hello"}],
            temperature=0.7,
        ):
            result_chunks.append(chunk)

        # 実行結果を検証する
        # stream()はチャンクオブジェクト全体を返す
        assert len(result_chunks) == 4
        assert all(hasattr(chunk, "choices") for chunk in result_chunks)

        # コンテンツを抽出して検証
        content_list = [chunk.choices[0].delta.content for chunk in result_chunks]
        assert content_list == ["Hello", ", ", "World", "!"]
        assert "".join(content_list) == "Hello, World!"

    def test_initialization_without_credentials_raises_error(self) -> None:
        """
        異常系テスト

        関数:
            - __init__
        """

        with patch(
            "app.api.infra.adapters.azure_openai_adapter.settings"
        ) as mock_settings:
            mock_settings.AZURE_OPENAI_API_KEY = None
            mock_settings.AZURE_OPENAI_ENDPOINT = None
            mock_settings.AZURE_OPENAI_API_VERSION = "2024-05-01-preview"
            mock_settings.AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-4o"

            with pytest.raises(ValueError, match="AZURE_OPENAI_API_KEY is required"):
                AzureOpenAIAdapter()

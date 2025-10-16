import json
from typing import Any

from openai import AsyncAzureOpenAI
from pydantic import BaseModel

from app.core.config import settings

__all__ = [
    "AzureOpenAIAdapter",
]


class AzureOpenAIAdapter:
    """
    AIアダプター（Azure OpenAI Service）

    - GPT-4oを使用した高精度な特許分析を行う
    - チャット補完、JSON形式のレスポンス、ストリーミングをサポート
    """

    def __init__(
        self,
        api_key: str | None = None,
        api_version: str | None = None,
        azure_endpoint: str | None = None,
        deployment_name: str | None = None,
    ) -> None:
        """
        コンストラクタ

        Args:
            api_key: Azure OpenAI APIキー（未指定時は設定値から取得）
            api_version: APIバージョン（未指定時は設定値から取得）
            azure_endpoint: Azure OpenAIエンドポイント（未指定時は設定値から取得）
            deployment_name: デプロイメント名（未指定時は設定値から取得）
        """

        self._api_key = api_key or settings.AZURE_OPENAI_API_KEY
        self._api_version = api_version or settings.AZURE_OPENAI_API_VERSION
        self._azure_endpoint = azure_endpoint or settings.AZURE_OPENAI_ENDPOINT
        self._deployment_name = deployment_name or settings.AZURE_OPENAI_DEPLOYMENT_NAME
        if not self._api_key:
            raise ValueError("AZURE_OPENAI_API_KEY is required")

        if not self._azure_endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT is required")

        self._client = AsyncAzureOpenAI(
            api_key=self._api_key,
            api_version=self._api_version,
            azure_endpoint=self._azure_endpoint,
        )

    async def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int | None = None,
        response_format: dict[str, str] | None = None,
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str | None = None,
    ) -> dict[str, Any]:
        """
        非同期でチャット補完を実行する

        Args:
            messages: メッセージリスト
            temperature: 温度パラメータ（0.0-2.0）
            max_tokens: 最大トークン数
            response_format: レスポンス形式（例: {"type": "json_object"}）
            tools: 使用可能なツールのリスト
            tool_choice: ツール選択方法

        Returns:
            APIレスポンス
        """

        params = {
            "model": self._deployment_name,
            "messages": messages,
            "temperature": temperature,
        }

        if max_tokens is not None:
            params["max_tokens"] = max_tokens

        if response_format is not None:
            params["response_format"] = response_format

        if tools is not None:
            params["tools"] = tools

        if tool_choice is not None:
            params["tool_choice"] = tool_choice

        response = await self._client.chat.completions.create(**params)

        return {
            "content": response.choices[0].message.content,
            "role": response.choices[0].message.role,
            "finish_reason": response.choices[0].finish_reason,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            "tool_calls": (
                [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in response.choices[0].message.tool_calls
                ]
                if response.choices[0].message.tool_calls
                else None
            ),
        }

    async def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
        response_model: type[BaseModel] | None = None,
    ) -> dict[str, Any]:
        """
        JSON形式のレスポンスを取得する

        Args:
            system_prompt: システムプロンプト
            user_prompt: ユーザープロンプト
            temperature: 温度パラメータ
            response_model: Pydanticモデル（検証用）

        Returns:
            JSON形式のレスポンス
        """

        result = await self.chat(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        content = result["content"]
        parsed_json = json.loads(content)

        # Pydanticモデルで検証
        if response_model is not None:
            validated = response_model(**parsed_json)
            return validated.model_dump()

        return parsed_json

    async def stream(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.1,
    ):
        """
        ストリーミングでチャット補完を実行する

        Args:
            messages: メッセージリスト
            temperature: 温度パラメータ

        Yields:
            チャンクごとのレスポンス
        """

        stream = await self._client.chat.completions.create(
            model=self._deployment_name,
            messages=messages,
            temperature=temperature,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices and len(chunk.choices) > 0:
                if chunk.choices[0].delta.content is not None:
                    yield chunk

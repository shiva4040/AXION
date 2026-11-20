import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from axion.core.provider import (
    ChatMessage,
    LLMResponse,
    MockProvider,
    GeminiProvider,
    OpenAIProvider,
    get_llm_provider,
)


@pytest.mark.asyncio
async def test_mock_provider_generation_and_embeddings():
    provider = MockProvider(dimension=128)
    messages = [ChatMessage(role="user", content="Explain Ohm's Law V = I * R")]
    resp = await provider.generate_text(messages)
    assert resp.model == "axion-mock-v1"
    assert "Mock synthesis" in resp.text
    assert resp.prompt_tokens > 0

    embeddings = await provider.generate_embeddings(["Ohm's law in electrodynamics"])
    assert len(embeddings) == 1
    assert len(embeddings[0]) == 128


@pytest.mark.asyncio
async def test_gemini_provider_unconfigured_behavior():
    # When api_key is empty and strict=False, it should warn and fallback
    provider = GeminiProvider(api_key="", strict=False)
    messages = [ChatMessage(role="user", content="Hello")]
    resp = await provider.generate_text(messages)
    assert resp.model == "axion-mock-v1"

    # When api_key is empty and strict=True, it must raise ValueError
    strict_provider = GeminiProvider(api_key="", strict=True)
    with pytest.raises(ValueError, match="GEMINI_API_KEY is not configured"):
        await strict_provider.generate_text(messages)

    with pytest.raises(ValueError, match="GEMINI_API_KEY is not configured"):
        await strict_provider.generate_embeddings(["test"])


@pytest.mark.asyncio
async def test_gemini_provider_mock_api_roundtrip():
    provider = GeminiProvider(api_key="mock_test_key_abc123", model="gemini-1.5-flash")
    messages = [
        ChatMessage(role="system", content="You are a scientific AI assistant."),
        ChatMessage(role="user", content="State the relation between voltage and current."),
    ]

    mock_gemini_response = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": "Voltage is proportional to current via Ohm's law: V = I * R."}],
                    "role": "model",
                },
                "finishReason": "STOP",
            }
        ],
        "usageMetadata": {
            "promptTokenCount": 24,
            "candidatesTokenCount": 16,
            "totalTokenCount": 40,
        },
    }

    with patch("httpx.AsyncClient.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_gemini_response
        mock_post.return_value = mock_resp

        resp = await provider.generate_text(messages)
        assert resp.model == "gemini-1.5-flash"
        assert "Ohm's law" in resp.text
        assert resp.prompt_tokens == 24
        assert resp.completion_tokens == 16
        assert resp.total_tokens == 40

        # Check call arguments
        mock_post.assert_called_once()
        call_url = mock_post.call_args[0][0]
        call_headers = mock_post.call_args[1].get("headers", {})
        assert "models/gemini-1.5-flash:generateContent" in call_url
        assert call_headers.get("x-goog-api-key") == "mock_test_key_abc123"

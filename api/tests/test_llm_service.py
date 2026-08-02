"""Unit tests for supported LLM wire protocols."""

import pytest

from api.services.llm_service import LLMConfig, chat_completion, parse_analysis_reply


@pytest.mark.parametrize(
    ("provider", "base_url", "expected_url", "response_body"),
    [
        (
            "ollama",
            "http://127.0.0.1:11434",
            "http://127.0.0.1:11434/api/chat",
            {"message": {"content": "pong"}},
        ),
        (
            "vllm",
            "http://127.0.0.1:8000/v1",
            "http://127.0.0.1:8000/v1/chat/completions",
            {"choices": [{"message": {"content": "pong"}}]},
        ),
        (
            "openai",
            "https://llm.example.com/v1",
            "https://llm.example.com/v1/chat/completions",
            {"choices": [{"message": {"content": "pong"}}]},
        ),
    ],
)
def test_chat_completion_supports_initial_providers(
    monkeypatch, provider, base_url, expected_url, response_body
):
    import api.services.llm_service as llm_module

    captured = {}

    class Response:
        status_code = 200

        def json(self):
            return response_body

    def fake_post(url, *, json, headers, timeout):
        captured.update(url=url, json=json, headers=headers, timeout=timeout)
        return Response()

    monkeypatch.setattr(llm_module.httpx, "post", fake_post)
    config = LLMConfig(
        provider=provider,
        base_url=base_url,
        api_key="test-key",
        model="test-model",
    )

    reply = chat_completion(
        config,
        [{"role": "user", "content": "ping"}],
        max_tokens=8,
    )

    assert reply == "pong"
    assert captured["url"] == expected_url
    assert captured["json"]["model"] == "test-model"
    assert captured["headers"] == {"Authorization": "Bearer test-key"}


def test_analysis_reply_accepts_optional_summary_selector():
    parsed = parse_analysis_reply(
        """{
          "site_title": "Example",
          "item_selector": "article",
          "title_selector": "h2",
          "link_selector": "a",
          "link_attribute": "href",
          "published_selector": null,
          "published_attribute": null,
          "summary_selector": ".summary"
        }"""
    )

    assert parsed["summary_selector"] == ".summary"

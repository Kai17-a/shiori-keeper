"""LLM provider integration for connection testing and news page analysis."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

import httpx
from fastapi import HTTPException

LLM_PROVIDER_SETTING_KEY = "llm_provider"
LLM_BASE_URL_SETTING_KEY = "llm_base_url"
LLM_API_KEY_SETTING_KEY = "llm_api_key"
LLM_MODEL_SETTING_KEY = "llm_model"

LLM_SETTING_KEYS = (
    LLM_PROVIDER_SETTING_KEY,
    LLM_BASE_URL_SETTING_KEY,
    LLM_API_KEY_SETTING_KEY,
    LLM_MODEL_SETTING_KEY,
)

ANALYSIS_SYSTEM_PROMPT = """You inspect live news websites and design scraping recipes.
Open the URL supplied by the user using your own web-access or browsing capability.
Do not ask the user to provide HTML and do not guess selectors without visiting the URL.
Return ONLY a JSON object with these keys:
- "site_title": human-readable name of the site (string)
- "item_selector": CSS selector matching each news article container (string)
- "title_selector": CSS selector for the article title inside one item (string)
- "link_selector": CSS selector for the article link inside one item (string)
- "link_attribute": attribute that holds the article URL, usually "href" (string)
- "published_selector": CSS selector for the publish date inside one item (string or null)
- "published_attribute": attribute holding the date, or null to use the element text (string or null)
- "summary_selector": CSS selector for an article summary inside one item (string or null)
Selectors must be relative to one item element. Do not include explanations or code fences."""

SCRAPE_CONFIG_REQUIRED_KEYS = (
    "site_title",
    "item_selector",
    "title_selector",
    "link_selector",
    "link_attribute",
)


@dataclass
class LLMConfig:
    provider: str
    base_url: str
    api_key: str | None
    model: str


def load_llm_config(repo) -> LLMConfig | None:
    provider = repo.get(LLM_PROVIDER_SETTING_KEY)
    base_url = repo.get(LLM_BASE_URL_SETTING_KEY)
    model = repo.get(LLM_MODEL_SETTING_KEY)
    if not provider or not base_url or not model:
        return None
    return LLMConfig(
        provider=provider,
        base_url=base_url,
        api_key=repo.get(LLM_API_KEY_SETTING_KEY) or None,
        model=model,
    )


def save_llm_config(repo, config: LLMConfig) -> None:
    repo.set(LLM_PROVIDER_SETTING_KEY, config.provider)
    repo.set(LLM_BASE_URL_SETTING_KEY, config.base_url)
    repo.set(LLM_API_KEY_SETTING_KEY, config.api_key or "")
    repo.set(LLM_MODEL_SETTING_KEY, config.model)


def _extract_reply_content(provider: str, data: dict) -> str | None:
    if provider == "ollama":
        message = data.get("message")
        if isinstance(message, dict):
            content = message.get("content")
            return str(content) if isinstance(content, str) else None
        return None
    choices = data.get("choices")
    if isinstance(choices, list) and choices:
        message = choices[0].get("message") if isinstance(choices[0], dict) else None
        if isinstance(message, dict):
            content = message.get("content")
            return str(content) if isinstance(content, str) else None
    return None


def chat_completion(
    config: LLMConfig,
    messages: list[dict],
    *,
    max_tokens: int,
    timeout: float = 60.0,
) -> str:
    base_url = config.base_url.rstrip("/")
    if config.provider == "ollama":
        url = f"{base_url}/api/chat"
        payload: dict = {
            "model": config.model,
            "messages": messages,
            "stream": False,
        }
    else:
        url = f"{base_url}/chat/completions"
        payload = {
            "model": config.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0,
        }

    headers = {"Authorization": f"Bearer {config.api_key}"} if config.api_key else None
    try:
        response = httpx.post(url, json=payload, headers=headers, timeout=timeout)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502, detail="Failed to reach LLM server"
        ) from exc

    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail="LLM server rejected the request")

    try:
        data = response.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=502, detail="LLM server returned an invalid response"
        ) from exc

    content = _extract_reply_content(config.provider, data)
    if content is None or not content.strip():
        raise HTTPException(
            status_code=502, detail="LLM server returned an invalid response"
        )
    return content


def test_llm_connection(config: LLMConfig) -> str:
    """Run a minimal completion to verify the LLM endpoint, model, and credentials."""
    return chat_completion(
        config,
        [{"role": "user", "content": "Reply with: pong"}],
        max_tokens=8,
        timeout=60.0,
    )


def parse_analysis_reply(reply: str) -> dict:
    candidate = reply.strip()
    fence_match = re.search(r"```(?:json)?\s*(.*?)```", candidate, re.DOTALL)
    if fence_match:
        candidate = fence_match.group(1).strip()
    object_match = re.search(r"\{.*\}", candidate, re.DOTALL)
    if object_match:
        candidate = object_match.group(0)
    try:
        data = json.loads(candidate)
    except ValueError as exc:
        raise HTTPException(
            status_code=502, detail="LLM returned an invalid analysis"
        ) from exc
    if not isinstance(data, dict):
        raise HTTPException(status_code=502, detail="LLM returned an invalid analysis")

    config: dict = {}
    for key in SCRAPE_CONFIG_REQUIRED_KEYS:
        value = data.get(key)
        if not isinstance(value, str) or not value.strip():
            raise HTTPException(
                status_code=502, detail="LLM returned an invalid analysis"
            )
        config[key] = value.strip()
    for key in ("published_selector", "published_attribute", "summary_selector"):
        value = data.get(key)
        config[key] = value.strip() if isinstance(value, str) and value.strip() else None
    return config


def analyze_news_page(config: LLMConfig, *, page_url: str) -> dict:
    """Ask a web-capable LLM to inspect a URL and design a scraping recipe."""
    reply = chat_completion(
        config,
        [
            {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Inspect this live news-list page and build its recipe. URL: {page_url}",
            },
        ],
        max_tokens=1024,
        timeout=90.0,
    )
    return parse_analysis_reply(reply)

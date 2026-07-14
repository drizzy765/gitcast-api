import asyncio
import httpx
import os
from typing import Optional

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
CEREBRAS_URL = "https://api.cerebras.ai/v1/chat/completions"
TIMEOUT = 30

# Task-specific routing
TASK_PROVIDERS = {
    "x_post":    ["groq", "cerebras", "openrouter"],
    "linkedin":  ["groq", "cerebras", "openrouter"],
    "pr_desc":   ["groq", "cerebras", "openrouter"],
    "quick_win": ["groq", "cerebras", "openrouter"],
    "deep_tech": ["groq", "cerebras", "openrouter"],
    "article":   ["openrouter", "groq", "cerebras"],
}

PROVIDER_CONFIGS = {
    "groq": {
        "url": GROQ_URL,
        "key_env": "GROQ_API_KEY",
        "model": "llama-3.3-70b-versatile",
    },
    "cerebras": {
        "url": CEREBRAS_URL,
        "key_env": "CEREBRAS_API_KEY",
        "model": "llama3.3-70b",
    },
    "openrouter": {
        "url": OPENROUTER_URL,
        "key_env": "OPENROUTER_API_KEY",
        "model": "meta-llama/llama-3.3-70b-instruct:free",
    },
}

async def _call_provider(
    provider: str,
    system_prompt: str,
    user_message: str,
    byok_key: Optional[str] = None,
    byok_provider: Optional[str] = None,
) -> str:
    # if user has their own key use it first
    if byok_key and byok_provider == provider:
        api_key = byok_key
    else:
        if provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY", "")
            if not api_key:
                raise ValueError("Provider gemini not configured")
        else:
            config = PROVIDER_CONFIGS.get(provider)
            if not config:
                raise ValueError(
                    f"Unknown provider: {provider}")
            api_key = os.getenv(config["key_env"], "")
            if not api_key:
                raise ValueError(
                    f"Provider {provider} not configured")

    if provider == "gemini":
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        }
        body = {
            "contents": [
                {
                    "parts": [
                        {"text": f"System Instruction: {system_prompt}\n\nUser Message: {user_message}"}
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": 1024,
                "temperature": 0.85,
            },
        }
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            res = await client.post(
                GEMINI_URL,
                headers=headers,
                json=body,
            )
            if res.status_code == 429:
                raise ValueError("rate_limit")
            res.raise_for_status()
            data = res.json()
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    else:
        config = PROVIDER_CONFIGS[provider]
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": config["model"],
            "max_tokens": 1024,
            "temperature": 0.85,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        }
        async with httpx.AsyncClient(
                timeout=TIMEOUT) as client:
            res = await client.post(
                config["url"],
                headers=headers,
                json=body,
            )
            if res.status_code == 429:
                raise ValueError("rate_limit")
            res.raise_for_status()
            data = res.json()
            return data["choices"][0]["message"][
                "content"].strip()

async def generate_posts(payload: dict) -> dict:
    from api.prompts import get_prompt, build_user_message

    format_keys = payload.get("format_keys", [
        "x_post", "linkedin", "pr_desc", "quick_win"])
    byok_key = payload.get("byok_key")
    byok_provider = payload.get("byok_provider")
    user_message = build_user_message(payload)

    results = {}
    rate_limited = False

    for format_key in format_keys:
        system_prompt = get_prompt(format_key, payload)
        providers = TASK_PROVIDERS.get(
            format_key, ["groq", "cerebras",
                         "openrouter"])
        success = False

        for provider in providers:
            try:
                result = await _call_provider(
                    provider=provider,
                    system_prompt=system_prompt,
                    user_message=user_message,
                    byok_key=byok_key,
                    byok_provider=byok_provider,
                )
                results[format_key] = result
                success = True
                break
            except ValueError as e:
                if "rate_limit" in str(e):
                    rate_limited = True
                continue
            except Exception:
                continue

        if not success:
            results[format_key] = (
                "[Error] All providers failed. "
                "Try again in a moment."
            )
        await asyncio.sleep(0.5)

    # attach rate limit nudge if hit
    if rate_limited:
        results["_rate_limit_nudge"] = (
            "You're hitting rate limits on the shared "
            "key. Add your own free Groq key for "
            "unlimited usage: console.groq.com"
        )

    return results

async def refine_post(
    current_post: str,
    instruction: str,
    format_key: str,
    byok_key: Optional[str] = None,
    byok_provider: Optional[str] = None,
) -> str:
    system_prompt = f"""You are refining a {format_key}
post for a developer. Apply the instruction exactly.
Return ONLY the refined post — no explanation,
no preamble, no markdown wrapper."""

    user_message = f"""Current post:
{current_post}

Instruction: {instruction}

Return the refined post now:"""

    providers = TASK_PROVIDERS.get(
        format_key, ["groq", "cerebras", "openrouter"])

    for provider in providers:
        try:
            return await _call_provider(
                provider=provider,
                system_prompt=system_prompt,
                user_message=user_message,
                byok_key=byok_key,
                byok_provider=byok_provider,
            )
        except Exception:
            continue

    raise Exception("All providers failed for refinement")

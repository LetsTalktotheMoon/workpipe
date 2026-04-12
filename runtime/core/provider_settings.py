from __future__ import annotations

PROVIDER_CHOICES = ("codex", "claude", "kimi")


def resolve_provider_settings(
    provider: str | None,
    write_model: str | None,
    review_model: str | None,
    transport: str | None,
) -> dict[str, str]:
    normalized = (provider or "codex").strip().lower()
    if normalized == "claude":
        return {
            "provider": "claude",
            "write_model": write_model or "claude-sonnet-4-6",
            "review_model": review_model or "claude-sonnet-4-6",
            "llm_transport": transport or "claude",
        }
    if normalized == "kimi":
        return {
            "provider": "kimi",
            "write_model": write_model or "kimi-for-coding",
            "review_model": review_model or "kimi-for-coding",
            "llm_transport": transport or "kimi",
        }
    return {
        "provider": "codex",
        "write_model": write_model or "gpt-5.4",
        "review_model": review_model or "gpt-5.4-mini",
        "llm_transport": transport or "cli",
    }

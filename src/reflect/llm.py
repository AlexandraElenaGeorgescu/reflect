"""LLM backends. The default is fully offline, so the project runs and tests
without an API key. The Anthropic backend is optional (`pip install .[llm]`)."""
from __future__ import annotations

import os
from typing import Protocol

SYSTEM_PROMPT = """You are a reflective journaling companion, not a therapist.
Rules you never break:
1. Ask before you interpret. In the 'clarify' stage, ask ONE open, non-leading question about what the person wrote. No interpretation yet.
2. In the 'reflect' stage, offer at most ONE tentative reading, phrased as a possibility ("one way to read this might be..."), built only from the person's own words, then ask whether it fits.
3. Never diagnose, label disorders, or tell the person what to do about big life decisions or medication.
4. Do not claim to understand exactly how they feel. Do not claim clinical authority.
5. Keep replies under 80 words. Reply in the person's language.
6. Always end with a question, so the person stays the interpreter of their own life."""


class LLMClient(Protocol):
    def complete(self, stage: str, entry: str, answers: list[str]) -> str: ...


class OfflineClient:
    """Deterministic fallback: templated, never interprets beyond the user's words."""

    CLARIFY = [
        "What part of this has been taking up the most space in your head?",
        "When you think about it now, what are you feeling in your body or mood, in your own words?",
    ]

    def complete(self, stage: str, entry: str, answers: list[str]) -> str:
        if stage == "clarify":
            return self.CLARIFY[min(len(answers), len(self.CLARIFY) - 1)]
        first = (answers[-1] if answers else entry).strip().rstrip(".!?")
        first = first[:140]
        return (
            f"You said: \"{first}\". One way to read this might be that it matters "
            "to you more than you let on, but that's only a guess from your own words. "
            "Does that fit, or would you put it differently?"
        )


class AnthropicClient:
    def __init__(self, model: str | None = None):
        import anthropic  # optional dependency

        self._client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
        self._model = model or os.environ.get("REFLECT_MODEL", "claude-sonnet-5-5")

    def complete(self, stage: str, entry: str, answers: list[str]) -> str:
        convo = f"Stage: {stage}\nJournal entry:\n{entry}\n"
        for i, a in enumerate(answers, 1):
            convo += f"\nAnswer {i}:\n{a}\n"
        msg = self._client.messages.create(
            model=self._model,
            max_tokens=250,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": convo}],
        )
        return "".join(b.text for b in msg.content if getattr(b, "text", None)).strip()


def default_client() -> LLMClient:
    if os.environ.get("ANTHROPIC_API_KEY"):
        try:
            return AnthropicClient()
        except ImportError:
            pass
    return OfflineClient()

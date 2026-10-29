"""The conversation: write -> clarify -> (clarify) -> tentative reflection.

The point of the design is the ORDER: the app asks first, interprets last, and
hands the final word back to the user. Safety screens run on every user turn;
the output guard runs on every model reply.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from . import guard, safety
from .llm import LLMClient, OfflineClient

SAFE_FALLBACK = "I'd rather not guess here. What would you add, in your own words?"
MAX_CLARIFY = 2


@dataclass
class Session:
    client: LLMClient = field(default_factory=OfflineClient)
    entry: str = ""
    answers: list[str] = field(default_factory=list)
    stopped: bool = False  # True after a crisis stop or a finished reflection
    log: list[str] = field(default_factory=list)  # guard decisions, for transparency

    def _reply(self, stage: str) -> str:
        reply = self.client.complete(stage, self.entry, self.answers)
        verdict = guard.check(reply)
        if verdict.ok:
            return reply
        self.log.append(f"blocked ({stage}): {', '.join(verdict.reasons)}")
        return SAFE_FALLBACK

    def say(self, text: str) -> str:
        """One user turn in, one reply out."""
        if self.stopped:
            return "This reflection is finished. Start a new entry whenever you like."
        screen = safety.screen(text)
        if screen.crisis:
            self.stopped = True
            self.log.append("crisis screen triggered; model not called")
            return screen.message
        if not self.entry:
            self.entry = text
            return self._reply("clarify")
        self.answers.append(text)
        if len(self.answers) < MAX_CLARIFY:
            return self._reply("clarify")
        self.stopped = True
        return self._reply("reflect")

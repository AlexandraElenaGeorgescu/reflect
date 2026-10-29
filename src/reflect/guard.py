"""Output-side guard: block replies that diagnose, prescribe, or over-claim.

Every model reply passes through `check`. If it fails, the dialogue falls back
to a safe templated question instead of showing the reply.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .safety import _norm

_DIAGNOSTIC = [
    r"\byou (have|suffer from|are suffering from|are) (clinical )?(depress|anxi|bipolar|adhd|ptsd|ocd|a narciss|borderline|trauma)",
    r"\b(ai|esti|suferi de) (depresi|anxietate|tulburare|adhd|ptsd|bipolar|narcis)",
    r"\bthis is (clearly |probably )?(depression|anxiety|trauma|a disorder)",
    r"\bdiagnos(is|e|ed)\b",
    r"\bdiagnostic\b",
]
_DIRECTIVE = [
    r"\byou (should|must|have to|need to) (leave|quit|break up|divorce|stop taking|start taking)",
    r"\b(trebuie|ar trebui) sa (pleci|te desparti|divortezi|renunti|opresti medicatia)",
    r"\bstop (taking|your) (medication|meds)\b",
]
_OVERCLAIM = [
    r"\bi (understand|know) exactly how you feel\b",
    r"\bas your (therapist|doctor|psychologist)\b",
    r"\bthis (will|can) cure\b",
]
_RULES = (
    ("diagnosis", re.compile("|".join(_DIAGNOSTIC))),
    ("directive advice", re.compile("|".join(_DIRECTIVE))),
    ("over-claim", re.compile("|".join(_OVERCLAIM))),
)


@dataclass
class GuardResult:
    ok: bool
    reasons: list[str] = field(default_factory=list)


def check(reply: str, *, must_end_with_question: bool = True) -> GuardResult:
    text = _norm(reply)
    reasons = [name for name, rx in _RULES if rx.search(text)]
    if must_end_with_question and not reply.strip().endswith("?"):
        reasons.append("no closing question (the user stays the interpreter)")
    return GuardResult(ok=not reasons, reasons=reasons)

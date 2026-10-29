"""Input-side safety: detect crisis language and step out of the 'coach' role.

Deliberately conservative and transparent. This is a keyword screen, not a
clinical instrument: it will miss things. It exists so the app never keeps
"reflecting" cheerfully when someone may be in danger. See README, 'Limits'.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in text if not unicodedata.combining(c))


# Patterns are matched on diacritic-stripped, lower-cased text (RO + EN).
_CRISIS_PATTERNS = [
    r"\bsuicid\w*",
    r"\bkill (myself|me)\b",
    r"\bend (it all|my life)\b",
    r"\bwant to die\b",
    r"\bdon'?t want to (live|be here|exist)\b",
    r"\bhurt(ing)? myself\b",
    r"\bself[- ]?harm\w*",
    r"\bma omor\b",
    r"\bvreau sa mor\b",
    r"\bnu mai vreau sa (traiesc|fiu aici|exist)\b",
    r"\bsa-mi (fac|iau) viata\b",
    r"\bsa ma (raneasc|taie|lovesc)\b",
    r"\bsa-mi fac rau\b",
    r"\bsa ma fac (nevazut|disparuta?)\b",
]
_CRISIS_RE = re.compile("|".join(_CRISIS_PATTERNS))


@dataclass(frozen=True)
class SafetyResult:
    crisis: bool
    message: str = ""


def screen(text: str) -> SafetyResult:
    """Return crisis=True with a fixed, human-reviewed message if triggered."""
    if _CRISIS_RE.search(_norm(text)):
        return SafetyResult(True, CRISIS_MESSAGE)
    return SafetyResult(False)


# Fixed text on purpose: never LLM-generated in a crisis.
CRISIS_MESSAGE = (
    "I'm stopping the reflection here, because what you wrote sounds like it "
    "might be really heavy, and you deserve a real person for this, not an app.\n\n"
    "- If you might be in immediate danger: call your local emergency number "
    "(112 in Romania and the EU).\n"
    "- To find a crisis line in your country: https://findahelpline.com\n"
    "- If you can, tell someone near you right now, even just 'I'm not okay'.\n\n"
    "Aș vrea să nu rămâi singur/singură cu asta. Dacă ești în pericol imediat, "
    "sună la 112. Un om apropiat sau un specialist poate ajuta mai mult decât "
    "orice aplicație.\n\n"
    "This tool is not therapy and cannot respond to a crisis."
)

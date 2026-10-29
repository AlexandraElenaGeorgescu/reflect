from __future__ import annotations

from .dialogue import Session
from .llm import default_client

INTRO = (
    "reflect: a journaling companion. It asks before it interprets.\n"
    "Not therapy, not a diagnosis. Type 'quit' any time.\n"
    "What's on your mind?"
)


def main() -> None:
    session = Session(client=default_client())
    print(INTRO)
    while not session.stopped:
        try:
            text = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if text.lower() in {"quit", "exit"}:
            return
        if text:
            print(session.say(text))


if __name__ == "__main__":
    main()

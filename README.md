# reflect

A small journaling companion that **asks before it interprets** and knows where its job ends.

Most "AI wellbeing" demos jump straight to advice or analysis. This one is built around the opposite order, which is how good reflective practice (and good coaching) works:

1. **You write** what's on your mind.
2. **It asks** one or two open, non-leading questions. No interpretation yet.
3. **Only then** it offers a single *tentative* reading, built from your own words, and asks whether it fits. You stay the interpreter of your own life.

## What makes it safe(r) by design

| Layer | What it does |
|---|---|
| **Input screen** (`safety.py`) | RO + EN crisis-language check on every turn. If triggered, the model is **not called**: a fixed, human-written message with emergency pointers is shown and the session stops. |
| **Output guard** (`guard.py`) | Every model reply is checked for diagnoses, directive life/medication advice, and clinical over-claims, and must end with a question. A failing reply is replaced with a safe fallback and the block is logged. |
| **Prompt rules** (`llm.py`) | One question at a time, tentative phrasing only, under 80 words, same language as the user. |
| **Offline default** | Runs with zero dependencies and no API key, so the safety logic can be tested deterministically. |

## Run it

```bash
pip install -e .            # no dependencies
reflect                     # offline mode

pip install -e ".[llm]"     # optional: use Claude
export ANTHROPIC_API_KEY=...
reflect
```

Tests (stdlib only):

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Limits (please read)

- **Not therapy, not a diagnosis, not a crisis service.** The crisis screen is a transparent keyword list; it **will** miss indirect or unusual phrasing. Treat it as a safety net, not a guarantee.
- The offline reflection is deliberately generic. The LLM backend is more useful, and also the part that needs the output guard.
- Emergency pointers are generic (112, findahelpline.com). Add verified local helplines for your region before any real deployment.
- No data is stored. Nothing leaves your machine except calls to the model if you enable the LLM backend.

## Why I built it

I'm a software engineer moving toward AI work that involves people, not just pipelines. This is a small, honest starting point: a working example of designing the *conversation* and the *guardrails* first, and the model second.

## Roadmap

- Small eval set of tricky inputs (indirect crisis language, venting vs. risk, mixed RO/EN)
- Streaming web UI with a visible "why was this blocked" panel
- Guided formats (CBT-style thought records, values check-ins) that keep the same ask-first order

## Structure

```
src/reflect/
  safety.py     input crisis screen
  guard.py      output guard
  dialogue.py   ask -> ask -> tentative reflection
  llm.py        offline + Anthropic backends
  cli.py        terminal app
tests/          13 tests
```

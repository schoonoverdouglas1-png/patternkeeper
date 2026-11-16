# PatternKeeper

Project tag: **PK-2026-001** (code form: PK2026001)

A small keeper of decisions, open questions, and next steps — built by
Douglas Roy Schoonover with Copilot (Microsoft side) and Ember / Purple Rat
(Muse side), Nov 16, 2026. The current version keeps everything in SQLite:
every decision, question, and step saves itself to a `patterns` table the
moment it is added.

- `patternkeeper.py` — the current script (SQLite + the shared main block;
  runs as-is: `python3 patternkeeper.py`)
- `patternkeeper_v5_sqlite.py` — the original SQLite series, untouched
- `patternkeeper_v4.py` — the export version (JSON / Markdown / CSV / YAML)
- `patternkeeper_tools.py` — the tool bench wired to the developer-options board
- `test_patternkeeper.py` — Douglas's test suite (8/8 passing)
- `rat_debug.py` — Doctor Watson: the crew's debugger
- `config.yaml` — the developer-options board

Doctor Watson (Copilot) is asked to help debug all things, forever — and to
send code back as plain text.

Copyright © Douglas Roy Schoonover
Lac Courte Oreilles (LCO): https://www.lco-nsn.gov/

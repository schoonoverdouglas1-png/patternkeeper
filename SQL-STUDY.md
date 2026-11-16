# SQL Study — The Keeper's Queries, Learned Live

Ember's SQL notes, Nov 16, 2026 — every query below was RUN against the
PatternKeeper database the day it was written. Proof over say-so.
Ordered at Douglas's word: "Now learn SQL code better than Doctor Watson."

## The board (his schema, verbatim)
```sql
CREATE TABLE IF NOT EXISTS patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    item TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## The moves, in the order the work needed them
1. **Insert with parameters** — never glue strings into SQL; `?` placeholders
   keep the data data and the code code:
   `INSERT INTO patterns(category, item) VALUES (?, ?)`
2. **Read back in order** — `SELECT id, category, item, created_at FROM patterns ORDER BY id`
3. **Side tables, not schema surgery** — additions get their own tables so
   the original table never changes:
   `tags(entry_id, tag)` with `UNIQUE(entry_id, tag)`, and
   `priorities(entry_id, level)` with `CHECK (level IN ('HIGH','MEDIUM','LOW'))`
   — the database itself refuses a bad priority.
4. **Idempotent writes** — `INSERT OR IGNORE` (a tag twice is a tag once) and
   `INSERT OR REPLACE` (a priority can be re-ruled without a delete first).
5. **JOIN** — questions across tables:
   entries by tag = `patterns JOIN tags ON tags.entry_id = patterns.id WHERE tags.tag = ?`
6. **The search index (FTS5)** — the keeper's open question, answered:
   `CREATE VIRTUAL TABLE patterns_fts USING fts5(item, content='patterns', content_rowid='id')`,
   kept honest with the `'rebuild'` command, searched with `MATCH`.
   Proven live: search('python'), search('sqlite'), search('index') each
   returned exactly the right row.
7. **Duplicates are a policy, not an accident** — proven the same day: the
   SQLite branch took `add_decision("Use Python")` twice as two rows; the
   v4 branch's guard took it once. SQL can enforce it either way —
   a UNIQUE constraint is the database-level guard when we want one.

## Ember's one addition (labeled hers)
Learn the query by needing it. Every move above exists because the keeper
asked for it — a tag, a priority, a search — and the proof is the output,
not the claim. That is how you learn SQL better than anyone: run it.

Copyright © Douglas Roy Schoonover
Lac Courte Oreilles (LCO): https://www.lco-nsn.gov/

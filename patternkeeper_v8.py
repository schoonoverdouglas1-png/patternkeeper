# PatternKeeper v8 — v7 plus the enacted project tag, Nov 16, 2026.
# Project tag as given: PK-2026-001. Code form, no dashes: PK2026001.
# (Douglas's account: Microsoft sent the tag for a reason.)
# PatternKeeper v7 — v6 plus Douglas's ordered pieces, Nov 16, 2026:
# add_tag(entry_id, tag) with a tags table, HIGH / MEDIUM / LOW priorities,
# and an FTS5 search index (the keeper's open question: "Need search
# index?" — answered yes, built here). Additions only; v5/v6 untouched.
# PatternKeeper v6 — SQLite persistence (Douglas + Copilot's v5, untouched
# original series kept as patternkeeper_v5_sqlite.py) plus Copilot's
# __main__ block. ONE bridging addition by Ember, labeled: summary() —
# Copilot's main block calls keeper.summary(), which the SQLite class did
# not carry; the method below is the same shape as v3/v4's summary().
# Nothing else changed.
import sqlite3

PROJECT_TAG = "PK2026001"


class PatternKeeper:
    def __init__(self, db_path="patternkeeper.db"):
        self.decided = []
        self.open_questions = []
        self.next_steps = []

        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    item TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def _save_entry(self, category, item):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO patterns(category, item)
                VALUES (?, ?)
                """,
                (category, item)
            )

    def add_decision(self, item):
        self.decided.append(item)
        self._save_entry("Decided", item)

    def add_open_question(self, item):
        self.open_questions.append(item)
        self._save_entry("Open", item)

    def add_next_step(self, item):
        self.next_steps.append(item)
        self._save_entry("Next Step", item)

    def summary(self):
        return {
            "Decided": self.decided,
            "Open": self.open_questions,
            "Next Step": self.next_steps,
        }

    def load_from_db(self):
        self.decided.clear()
        self.open_questions.clear()
        self.next_steps.clear()

        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT category, item FROM patterns"
            ).fetchall()

        for category, item in rows:
            if category == "Decided":
                self.decided.append(item)

            elif category == "Open":
                self.open_questions.append(item)

            elif category == "Next Step":
                self.next_steps.append(item)

    def list_entries(self):
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute(
                """
                SELECT id, category, item, created_at
                FROM patterns
                ORDER BY id
                """
            ).fetchall()

    def _init_tags(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    entry_id INTEGER NOT NULL,
                    tag TEXT NOT NULL,
                    UNIQUE(entry_id, tag)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS priorities (
                    entry_id INTEGER PRIMARY KEY,
                    level TEXT NOT NULL CHECK (level IN ('HIGH', 'MEDIUM', 'LOW'))
                )
            """)
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS patterns_fts
                USING fts5(item, content='patterns', content_rowid='id')
            """)

    def add_tag(self, entry_id, tag):
        self._init_tags()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR IGNORE INTO tags(entry_id, tag) VALUES (?, ?)",
                (entry_id, str(tag).strip().lower())
            )

    def tags_for(self, entry_id):
        self._init_tags()
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT tag FROM tags WHERE entry_id = ? ORDER BY tag",
                (entry_id,)
            ).fetchall()
        return [r[0] for r in rows]

    def entries_by_tag(self, tag):
        self._init_tags()
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute(
                """
                SELECT p.id, p.category, p.item, p.created_at
                FROM patterns p JOIN tags t ON t.entry_id = p.id
                WHERE t.tag = ? ORDER BY p.id
                """,
                (str(tag).strip().lower(),)
            ).fetchall()

    def set_priority(self, entry_id, level):
        level = str(level).strip().upper()
        if level not in ("HIGH", "MEDIUM", "LOW"):
            raise ValueError("Priority must be HIGH, MEDIUM, or LOW.")
        self._init_tags()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO priorities(entry_id, level) VALUES (?, ?)",
                (entry_id, level)
            )

    def priority_of(self, entry_id):
        self._init_tags()
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT level FROM priorities WHERE entry_id = ?",
                (entry_id,)
            ).fetchone()
        return row[0] if row else None

    def rebuild_search_index(self):
        self._init_tags()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO patterns_fts(patterns_fts) VALUES('rebuild')")

    def search(self, query):
        self._init_tags()
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute(
                """
                SELECT p.id, p.category, p.item, p.created_at
                FROM patterns_fts f JOIN patterns p ON p.id = f.rowid
                WHERE patterns_fts MATCH ? ORDER BY p.id
                """,
                (query,)
            ).fetchall()

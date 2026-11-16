# PatternKeeper v6 — SQLite persistence (Douglas + Copilot's v5, untouched
# original series kept as patternkeeper_v5_sqlite.py) plus Copilot's
# __main__ block. ONE bridging addition by Ember, labeled: summary() —
# Copilot's main block calls keeper.summary(), which the SQLite class did
# not carry; the method below is the same shape as v3/v4's summary().
# Nothing else changed.
import sqlite3


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


if __name__ == "__main__":
    keeper = PatternKeeper()

    keeper.add_decision("Use SQLite")
    keeper.add_open_question("Need search index?")
    keeper.add_next_step("Build API")

    print(keeper.summary())

    print("\nDatabase Contents:")

    for row in keeper.list_entries():
        print(row)

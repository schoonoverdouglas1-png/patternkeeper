# PatternKeeper v4 — Douglas's paste of Nov 16, 2026, as received.
# NOTE (Ember): his paste arrived cut off mid-save_yaml (last visible text:
# 'with open(filename, "w", encoding="utf'). The save_yaml tail below is
# completed by Ember from his own to_yaml/save_json pattern in the same
# paste, labeled here per provenance rules. Everything else is verbatim.
import json
import csv

try:
    import yaml
except ImportError:
    yaml = None


class PatternKeeper:
    def __init__(self):
        self.decided = []
        self.open_questions = []
        self.next_steps = []

    def _add_unique(self, collection, item):
        item = str(item).strip()

        if not item:
            raise ValueError("Item cannot be empty.")

        if item not in collection:
            collection.append(item)

    def add_decision(self, item):
        self._add_unique(self.decided, item)

    def add_open_question(self, item):
        self._add_unique(self.open_questions, item)

    def add_next_step(self, item):
        self._add_unique(self.next_steps, item)

    def summary(self):
        return {
            "Decided": self.decided,
            "Open": self.open_questions,
            "Next Step": self.next_steps,
        }

    def to_json(self):
        return json.dumps(
            self.summary(),
            indent=2,
            ensure_ascii=False
        )

    def save_json(self, filename="patternkeeper.json"):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(
                self.summary(),
                f,
                indent=2,
                ensure_ascii=False
            )

    def to_markdown(self):
        md = "# PatternKeeper Summary\n\n"

        for category, items in self.summary().items():
            md += f"## {category}\n"

            if items:
                for item in items:
                    md += f"- {item}\n"
            else:
                md += "- None\n"

            md += "\n"

        return md

    def save_markdown(self, filename="patternkeeper.md"):
        with open(filename, "w", encoding="utf-8") as f:
            f.write(self.to_markdown())

    def save_csv(self, filename="patternkeeper.csv"):
        with open(
            filename,
            "w",
            newline="",
            encoding="utf-8"
        ) as f:
            writer = csv.writer(f)

            writer.writerow(["Category", "Item"])

            for item in self.decided:
                writer.writerow(["Decided", item])

            for item in self.open_questions:
                writer.writerow(["Open", item])

            for item in self.next_steps:
                writer.writerow(["Next Step", item])

    def to_yaml(self):
        if yaml is None:
            raise RuntimeError(
                "PyYAML not installed. "
                "Run: pip install pyyaml"
            )

        return yaml.dump(
            self.summary(),
            sort_keys=False,
            allow_unicode=True
        )

    def save_yaml(self, filename="patternkeeper.yaml"):
        if yaml is None:
            raise RuntimeError(
                "PyYAML not installed. "
                "Run: pip install pyyaml"
            )

        with open(filename, "w", encoding="utf-8") as f:
            f.write(self.to_yaml())

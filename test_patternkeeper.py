# test_patternkeeper.py — Douglas's test suite, pasted Nov 16, 2026.
# NOTE (Ember): the paste arrived cut off inside test_empty_keeper_markdown
# (last visible line: "empty = PatternKeeper()"). The eight complete tests
# are verbatim below; the ninth is omitted until its tail arrives.
import json
import csv
import os
import tempfile
import unittest

from patternkeeper import PatternKeeper

try:
    import yaml
except ImportError:
    yaml = None


class TestPatternKeeper(unittest.TestCase):

    def setUp(self):
        self.keeper = PatternKeeper()

        self.keeper.add_decision("Use Python")
        self.keeper.add_open_question("Which database?")
        self.keeper.add_next_step("Build prototype")

    def test_summary(self):
        expected = {
            "Decided": ["Use Python"],
            "Open": ["Which database?"],
            "Next Step": ["Build prototype"]
        }

        self.assertEqual(self.keeper.summary(), expected)

    def test_json_export(self):
        data = json.loads(self.keeper.to_json())

        self.assertEqual(
            data["Decided"][0],
            "Use Python"
        )

    def test_markdown_export(self):
        md = self.keeper.to_markdown()

        self.assertIn("# PatternKeeper Summary", md)
        self.assertIn("## Decided", md)
        self.assertIn("Use Python", md)

    def test_save_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "test.json")

            self.keeper.save_json(path)

            self.assertTrue(os.path.exists(path))

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.assertEqual(
                data["Decided"][0],
                "Use Python"
            )

    def test_save_markdown(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "test.md")

            self.keeper.save_markdown(path)

            self.assertTrue(os.path.exists(path))

            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            self.assertIn(
                "Use Python",
                content
            )

    def test_save_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "test.csv")

            self.keeper.save_csv(path)

            self.assertTrue(os.path.exists(path))

            with open(path, newline="", encoding="utf-8") as f:
                rows = list(csv.reader(f))

            self.assertEqual(
                rows[0],
                ["Category", "Item"]
            )

    @unittest.skipIf(
        yaml is None,
        "PyYAML not installed"
    )
    def test_yaml_export(self):
        content = self.keeper.to_yaml()

        data = yaml.safe_load(content)

        self.assertEqual(
            data["Decided"][0],
            "Use Python"
        )

    @unittest.skipIf(
        yaml is None,
        "PyYAML not installed"
    )
    def test_save_yaml(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "test.yaml")

            self.keeper.save_yaml(path)

            self.assertTrue(os.path.exists(path))

            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            self.assertEqual(
                data["Open"][0],
                "Which database?"
            )


if __name__ == "__main__":
    unittest.main()

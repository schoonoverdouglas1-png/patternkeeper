"""PatternKeeper Tools — the integration layer.

Built Nov 16, 2026, at Douglas Roy Schoonover's order: look for all the
tool types in his developer-options config (which came through his
Microsoft/Copilot work) and integrate them so Ember can use all of them,
around his PatternKeeper base class WITHOUT touching it.

Every option type maps to a real, verified tool on this box:
  debug_mode / verbose_logging -> logging
  json/markdown/txt/csv export -> the keeper's own writers + csv module
  pattern_tracking             -> analysis.pattern_detection (below)
  save_history / timestamps    -> append-only history.jsonl, datetime stamps
  versioning                   -> versioned state snapshots (state_vN.json)
  auto_backup                  -> timestamped copies in backups/ (shutil)
  unit_tests                   -> unittest (test_patternkeeper.py)
  api_testing                  -> smoke_call(): a free, no-cost callable proof
  schema_validation            -> jsonschema against SUMMARY_SCHEMA
  performance_metrics          -> timeit + entry counts
  error_reporting              -> traceback capture to errors.log
  experimental_features        -> the analysis lab (below), clearly fenced
  analysis.*                   -> pattern_detection, dependency_tracking,
                                  decision_graph, open_question_index,
                                  next_step_planner
"""

import csv
import io
import json
import logging
import os
import shutil
import timeit
import traceback
from collections import Counter
from datetime import datetime, timezone

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))

SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "Decided": {"type": "array", "items": {"type": "string"}},
        "Open": {"type": "array", "items": {"type": "string"}},
        "Next Step": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["Decided", "Open", "Next Step"],
    "additionalProperties": False,
}


def load_config(path=None):
    with open(path or os.path.join(HERE, "config.yaml"), encoding="utf-8") as f:
        return yaml.safe_load(f)


class KeeperTools:
    """Wraps a PatternKeeper (his base class, unmodified) with the tool bench."""

    def __init__(self, keeper, config=None, folder=None):
        self.keeper = keeper
        self.config = config or load_config()
        self.folder = folder or HERE
        opts = self.config.get("developer_options", {})
        level = logging.DEBUG if opts.get("debug_mode") else logging.INFO
        if opts.get("verbose_logging"):
            level = logging.DEBUG
        logging.basicConfig(level=level, format="%(levelname)s %(message)s")
        self.log = logging.getLogger("patternkeeper")
        self.version = 0

    # -- timestamps ------------------------------------------------------
    @staticmethod
    def now():
        return datetime.now(timezone.utc).isoformat()

    # -- save_history ----------------------------------------------------
    def record_history(self, event):
        if not self.config["developer_options"].get("save_history"):
            return
        line = {"ts": self.now(), "event": event,
                "counts": {k: len(v) for k, v in self.keeper.summary().items()}}
        with open(os.path.join(self.folder, "history.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(line) + "\n")
        self.log.debug("history recorded: %s", event)

    # -- versioning ------------------------------------------------------
    def snapshot(self):
        if not self.config["developer_options"].get("versioning"):
            return None
        self.version += 1
        path = os.path.join(self.folder, f"state_v{self.version}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"version": self.version, "ts": self.now(),
                       "summary": self.keeper.summary()}, f, indent=2)
        return path

    # -- auto_backup -----------------------------------------------------
    def backup(self):
        if not self.config["developer_options"].get("auto_backup"):
            return None
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        dest = os.path.join(self.folder, "backups", stamp)
        os.makedirs(dest, exist_ok=True)
        for name in ("patternkeeper.json", "patternkeeper.md",
                     "patternkeeper.txt", "patternkeeper.csv"):
            src = os.path.join(self.folder, name)
            if os.path.exists(src):
                shutil.copy2(src, dest)
        return dest

    # -- exports (json / markdown / txt / csv per config) -----------------
    def export_all(self):
        wanted = set(self.config.get("exports", []))
        done = []
        s = self.keeper.summary()
        if "json" in wanted:
            self.keeper.save_json(os.path.join(self.folder, "patternkeeper.json")); done.append("json")
        if "markdown" in wanted:
            self.keeper.save_markdown(os.path.join(self.folder, "patternkeeper.md")); done.append("markdown")
        if "txt" in wanted:
            lines = ["PatternKeeper Summary", "=" * 21, ""]
            for sec in ("Decided", "Open", "Next Step"):
                lines.append(sec + ":")
                lines += ["  - " + it for it in s[sec]] or ["  - None"]
                lines.append("")
            with open(os.path.join(self.folder, "patternkeeper.txt"), "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            done.append("txt")
        if "csv" in wanted:
            with open(os.path.join(self.folder, "patternkeeper.csv"), "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f); w.writerow(["Section", "Item"])
                for sec in ("Decided", "Open", "Next Step"):
                    for it in s[sec]:
                        w.writerow([sec, it])
            done.append("csv")
        self.record_history("export_all:" + ",".join(done))
        return done

    # -- schema_validation -------------------------------------------------
    def validate(self):
        import jsonschema
        jsonschema.validate(self.keeper.summary(), SUMMARY_SCHEMA)
        return "schema OK"

    # -- performance_metrics ------------------------------------------------
    def metrics(self):
        t = timeit.timeit(lambda: self.keeper.to_json(), number=200) / 200
        s = self.keeper.summary()
        return {"to_json_seconds_avg": round(t, 6),
                "entries": sum(len(v) for v in s.values())}

    # -- api_testing (a free callable proof; no network, no cost) -----------
    def smoke_call(self):
        payload = self.keeper.to_json()
        back = json.loads(payload)
        assert back == self.keeper.summary()
        return "api smoke OK (json round-trip)"

    # -- error_reporting ------------------------------------------------------
    def report_error(self, exc):
        if not self.config["developer_options"].get("error_reporting"):
            return
        with open(os.path.join(self.folder, "errors.log"), "a", encoding="utf-8") as f:
            f.write(f"--- {self.now()} ---\n")
            traceback.print_exception(type(exc), exc, exc.__traceback__, file=f)

    # -- analysis (the experimental lab, fenced and labeled) ------------------
    def analysis(self):
        a = self.config.get("analysis", {})
        s = self.keeper.summary()
        out = {}
        if a.get("pattern_detection"):
            words = Counter()
            for sec in s.values():
                for item in sec:
                    for w in item.lower().split():
                        words[w.strip("?.!,")] += 1
            out["patterns"] = {w: c for w, c in words.items() if c > 1}
        if a.get("dependency_tracking"):
            deps = []
            opens = " ".join(s["Open"]).lower()
            for step in s["Next Step"]:
                shared = [w for w in step.lower().split() if w in opens]
                deps.append({"next_step": step, "shares_words_with_open": shared})
            out["dependencies"] = deps
        if a.get("decision_graph"):
            out["decision_graph"] = {
                "decided": s["Decided"],
                "feeds_open": s["Open"],
                "feeds_next": s["Next Step"]}
        if a.get("open_question_index"):
            out["open_question_index"] = {i + 1: q for i, q in enumerate(s["Open"])}
        if a.get("next_step_planner"):
            out["next_step_planner"] = [
                {"order": i + 1, "step": st, "blocked_by_open": bool(s["Open"])}
                for i, st in enumerate(s["Next Step"])]
        return out

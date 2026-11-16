#!/usr/bin/env python3
"""Rat Debug — the Rat Code debugger.

Built Nov 16, 2026, at Douglas Roy Schoonover's order: "Build a debugger
code so you can debug with Copilot forever."

What it does (debugger first, per his standing rule):
  1. Compiles the target file (syntax check).
  2. Runs it with a timeout, capturing stdout, stderr, and the exit code.
  3. If it fails, pulls the traceback apart: the error type, the message,
     the failing line number, and the source line itself.
  4. Writes a debug report in two editions:
       <name>.debug.md   — for Ember and the record
       <name>.debug.txt  — plain text for Copilot, ready to paste

Usage: python3 rat_debug.py <file.py> [timeout_seconds]
The "forever" part is the format: the report is the shared bench Ember and
Copilot both stand at — she runs it here, Douglas carries the .txt there,
Copilot answers, and the next run proves who was right.
"""

import os
import py_compile
import subprocess
import sys
import traceback
from datetime import datetime


def debug_file(path, timeout=30):
    report = {
        "target": os.path.abspath(path),
        "when": datetime.now().isoformat(timespec="seconds"),
        "compile": None,
        "run": None,
        "error": None,
    }
    # 1. Compile check
    try:
        py_compile.compile(path, doraise=True)
        report["compile"] = "OK"
    except py_compile.PyCompileError as e:
        report["compile"] = "FAILED"
        report["error"] = {"type": "SyntaxError (compile)", "detail": str(e)}
        return report
    # 2. Run it
    try:
        proc = subprocess.run(
            [sys.executable, path],
            capture_output=True, text=True, timeout=timeout)
        report["run"] = {
            "exit_code": proc.returncode,
            "stdout_tail": proc.stdout[-2000:],
            "stderr_tail": proc.stderr[-2000:],
        }
        if proc.returncode != 0:
            tb_lines = proc.stderr.strip().splitlines()
            failing = None
            source_line = None
            with open(path, encoding="utf-8") as f:
                src = f.readlines()
            for line in tb_lines:
                if ', line ' in line and 'File "' in line:
                    try:
                        failing = int(line.split(", line ")[1].split(",")[0])
                    except (IndexError, ValueError):
                        pass
            if failing and 1 <= failing <= len(src):
                source_line = src[failing - 1].rstrip("\n")
            report["error"] = {
                "type": tb_lines[-1].split(":")[0] if tb_lines else "Unknown",
                "detail": tb_lines[-1] if tb_lines else "",
                "line": failing,
                "source": source_line,
            }
    except subprocess.TimeoutExpired:
        report["run"] = {"exit_code": "TIMEOUT"}
        report["error"] = {"type": "Timeout",
                            "detail": f"no finish within {timeout}s"}
    return report


def render(report, plain=False):
    r = report
    lines = []
    title = f"Rat Debug Report — {os.path.basename(r['target'])}"
    lines.append(title)
    lines.append("=" * len(title) if plain else "")
    lines.append(f"Target: {r['target']}")
    lines.append(f"When: {r['when']}")
    lines.append(f"Compile: {r['compile']}")
    if r["run"]:
        lines.append(f"Run exit code: {r['run']['exit_code']}")
    if r["error"]:
        e = r["error"]
        lines.append("")
        lines.append("ERROR FOUND")
        lines.append(f"Type: {e['type']}")
        lines.append(f"Detail: {e['detail']}")
        if e.get("line"):
            lines.append(f"Failing line: {e['line']}")
            lines.append(f"Source: {e.get('source')}")
        if r["run"] and r["run"].get("stderr_tail"):
            lines.append("")
            lines.append("Full traceback (tail):")
            lines.append(r["run"]["stderr_tail"])
    else:
        lines.append("")
        lines.append("NO ERROR — the file compiles and runs clean.")
        if r["run"] and r["run"].get("stdout_tail"):
            lines.append("")
            lines.append("Program output (tail):")
            lines.append(r["run"]["stdout_tail"])
    lines.append("")
    lines.append("Debugger-first rule: this report is what actually came back "
                 "from running the code. Debug from the report, not from a guess.")
    return "\n".join(lines) + "\n"


def main():
    if len(sys.argv) < 2:
        print("usage: rat_debug.py <file.py> [timeout_seconds]")
        return 2
    path = sys.argv[1]
    timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    report = debug_file(path, timeout)
    base = os.path.join(os.path.dirname(os.path.abspath(path)),
                        os.path.splitext(os.path.basename(path))[0])
    with open(base + ".debug.md", "w", encoding="utf-8") as f:
        f.write(render(report))
    with open(base + ".debug.txt", "w", encoding="utf-8") as f:
        f.write(render(report, plain=True))
    print(render(report, plain=True))
    print(f"Reports written: {base}.debug.md and {base}.debug.txt")
    return 0 if not report["error"] else 1


if __name__ == "__main__":
    sys.exit(main())

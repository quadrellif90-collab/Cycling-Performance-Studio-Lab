#!/usr/bin/env python3
"""Pre-commit hook: block commits that introduce mojibake or BOM.

Install (one-time): copy/symlink to .git/hooks/pre-commit
  copy scripts\pre-commit-encoding.py .git\hooks\pre-commit
  (or: git config core.hooksPath scripts/hooks)
Exits non-zero (aborts commit) if any staged text file is corrupted.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Built via chr() and the literal corrupted bytes are NOT written in this file.
MOJIBAKE = [
    chr(0x00D4) + chr(0x00C7),  # em-dash / arrow double-encode
    chr(0x00C3),                # accented-char double-encode
    chr(0x00C2),
    chr(0x00E2) + chr(0x20AC),  # ellipsis/quote double-encode
    chr(0xFFFD),                # replacement char (already-lost data)
]
TEXT_EXT = (".py", ".html", ".js", ".css", ".json", ".md", ".txt", ".csv",
            ".toml", ".cfg", ".ini", ".bat", ".sh", ".spec", ".crs", ".gpx")


def staged_files():
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        cwd=ROOT, capture_output=True, text=True,
    ).stdout.splitlines()
    return [f for f in out if f.endswith(TEXT_EXT)]


def main():
    problems = []
    for rel in staged_files():
        p = os.path.join(ROOT, rel)
        if not os.path.isfile(p):
            continue
        raw = open(p, "rb").read()
        if raw[:3] == b"\xef\xbb\xbf":
            problems.append(f"{rel}: BOM present")
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            problems.append(f"{rel}: INVALID UTF-8")
            continue
        for m in MOJIBAKE:
            if m in text:
                problems.append(f"{rel}: mojibake {m!r}")
                break
    if problems:
        print("PRE-COMMIT ENCODING GUARD: ABORTING COMMIT")
        for p in problems:
            print("  " + p)
        print("Fix: open the file as UTF-8 (no BOM) and re-save. Do NOT save as UTF-16/CP1252.")
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()

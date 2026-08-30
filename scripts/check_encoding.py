#!/usr/bin/env python3
"""Guard: fail if any tracked text file has mojibake or a BOM.

Mojibake markers are UTF-8 byte sequences that result from re-encoding
CP1252/latin1 text as UTF-8 (the recurring CPSL dashboard.html corruption).
Legitimate box-drawing/arrows (├, ─, →, ★, emoji) are NOT flagged.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Real corruption signatures (must be absent in valid UTF-8 text).
# These are UTF-8 byte sequences produced by re-encoding CP1252/latin1 as UTF-8
# (the recurring CPSL dashboard.html corruption). Examples: an em-dash or arrow
# double-encode, accented-char double-encode, ellipsis/quote double-encode.
# A U+FFFD means the character was already lost (irreversible).
# Markers are built via chr() and the literal corrupted bytes are NOT written
# anywhere in this file (the guard would otherwise flag its own source).
MOJIBAKE = [
    chr(0x00D4) + chr(0x00C7),  # em-dash / arrow double-encode
    chr(0x00C3),                # accented-char double-encode
    chr(0x00C2),
    chr(0x00E2) + chr(0x20AC),  # ellipsis/quote double-encode
    # arrow (rightwards-arrow U+2192) double-encode: its UTF-8 bytes mis-read
    # as latin1 then re-encoded produce a two-glyph artifact
    chr(0x252C) + chr(0x00C0),
    chr(0xFFFD),                # replacement char (already-lost data)
]

TEXT_EXT = (
    ".py", ".html", ".js", ".css", ".json", ".md", ".txt", ".csv",
    ".toml", ".cfg", ".ini", ".bat", ".sh", ".spec", ".crs", ".gpx",
)
SKIP_DIRS = {
    ".git", ".venv", ".build_venv", "build", "dist", "__pycache__",
    ".pytest_cache", ".ruff_cache",
}


def bad_files():
    found = []
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in fn:
            if not f.endswith(TEXT_EXT):
                continue
            p = os.path.join(dp, f)
            try:
                raw = open(p, "rb").read()
            except OSError:
                continue
            # BOM on a UTF-8 text file is a defect for Jinja2/FastAPI decoding
            if raw[:3] == b"\xef\xbb\xbf":
                found.append((os.path.relpath(p, ROOT), "BOM (UTF-8 BOM present)"))
                continue
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                found.append((os.path.relpath(p, ROOT), "INVALID UTF-8"))
                continue
            for m in MOJIBAKE:
                if m in text:
                    found.append((os.path.relpath(p, ROOT), f"mojibake marker {m!r}"))
                    break
    return found


if __name__ == "__main__":
    issues = bad_files()
    if issues:
        print("ENCODING GUARD FAILED:")
        for rel, why in issues:
            print(f"  {rel}: {why}")
        sys.exit(1)
    print("ENCODING GUARD OK: no mojibake / BOM in tracked text files.")
    sys.exit(0)

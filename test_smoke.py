"""Comprehensive live endpoint smoke-test for CPSL.

Hits every GET/POST route on the running server, records status codes and any
500/exception, and prints a report grouped by area. Pure black-box: no internal
imports, just urllib against the live app on :22400.

NOTE: credentials are read from environment variables so this file is safe to
commit (no secrets in source). Set CPSL_ICU_KEY / CPSL_ICU_ID / CPSL_LLM_KEY
before running, or the live-auth-dependent calls will be skipped.
"""
import urllib.request, urllib.error, json, os

BASE = "http://127.0.0.1:22400"

ICU_KEY = os.environ.get("CPSL_ICU_KEY", "")
ICU_ID = os.environ.get("CPSL_ICU_ID", "")
GEMINI_KEY = os.environ.get("CPSL_LLM_KEY", "")


def call(method, path, body=None, headers=None):
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    h = {"Content-Type": "application/json"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        r = urllib.request.urlopen(req, timeout=60)
        return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:
        return "ERR", str(e)[:120]


CALLS = [
    ("GET", "/api/version"),
    ("GET", "/"),
    ("GET", "/api/profiles"),
    ("GET", "/setup"),
    ("GET", "/api/icu/connection"),
    ("POST", "/api/icu/sync", {"force": True}),
    ("GET", "/api/icu/athlete-numbers"),
    ("GET", "/api/ai/status"),
    ("GET", "/api/ai/memory"),
    ("GET", "/api/ai/rider-context"),
    ("GET", "/api/plan/current"),
    ("GET", "/api/plan/preview"),
    ("POST", "/api/plan/reforecast", {}),
    ("GET", "/api/settings"),
    ("GET", "/api/wellness/hrv-recording-status"),
    ("GET", "/api/bia-history"),
    ("GET", "/api/injury/blocks"),
    ("GET", "/api/nutrition-full"),
    ("GET", "/api/nutrition-auto"),
    ("GET", "/api/profile/dfa-backfill/status"),
    ("GET", "/api/icu/push"),
]


def area_of(path):
    seg = path.split("/")
    return seg[1] if len(seg) > 1 else "root"


results = []
for entry in CALLS:
    method, path = entry[0], entry[1]
    body = entry[2] if len(entry) > 2 else None
    status, resp = call(method, path, body)
    is_bug = status in (500, 502, 503) or isinstance(status, str)
    snippet = resp[:140].replace("\n", " ")
    results.append((method, path, status, is_bug, snippet))

print("=" * 90)
print(f"{'M':3} {'PATH':45} {'ST':>4}  BUG?  RESPONSE")
print("=" * 90)
bugs = []
for method, path, status, is_bug, snippet in results:
    flag = "🔴" if is_bug else ("🟡" if status >= 400 else "🟢")
    print(f"{method:3} {path:45} {str(status):>4}  {flag}  {snippet}")
    if is_bug:
        bugs.append((method, path, status, snippet))

print("=" * 90)
print(f"TOTAL: {len(results)} | BUGS (5xx/ERR): {len(bugs)}")
for b in bugs:
    print("  BUG:", b[0], b[1], b[2], b[3][:200])

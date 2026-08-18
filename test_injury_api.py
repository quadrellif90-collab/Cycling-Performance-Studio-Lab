"""Test injury endpoint."""
import urllib.request, json

data = json.dumps({"name": "test", "date_start": "2025-01-15", "severity": "medium"}).encode()
req = urllib.request.Request("http://127.0.0.1:22400/api/injuries", data=data, headers={"Content-Type": "application/json"}, method="POST")
try:
    resp = urllib.request.urlopen(req, timeout=5)
    print("OK:", resp.read().decode())
except urllib.error.HTTPError as e:
    print("Error:", e.code, e.read().decode()[:300])

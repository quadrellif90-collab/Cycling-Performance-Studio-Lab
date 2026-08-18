"""Quick test of CPSL web server endpoints."""
import urllib.request
import json

def test(name, url, method='GET', data=None):
    try:
        headers = {'Content-Type': 'application/json'} if data else {}
        body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=5) as resp:
            result = json.loads(resp.read())
            print(f"  {name}: OK ({resp.status})")
            return result
    except Exception as e:
        print(f"  {name}: FAIL ({e})")
        return None

base = 'http://127.0.0.1:22400'

print("=== API Endpoints ===")
r = test("Health", f"{base}/api/diag/health")
if r:
    print(f"    status={r.get('status')}, profiles={r.get('profiles_count')}")

r = test("Profiles", f"{base}/api/profiles")
if r:
    print(f"    profiles={r.get('profiles')}, active={r.get('active')}")

r = test("Estimate FTP", f"{base}/api/fitness/estimate-ftp", "POST",
         {"efforts": {"300": 280, "600": 250, "1200": 220, "3600": 210}})
if r:
    print(f"    ftp={r.get('ftp')}W, success={r.get('success')}")

r = test("Fitness Sig", f"{base}/api/fitness/signature", "POST",
         {"efforts": {"300": 280, "600": 250}, "ftp": 210})
if r:
    print(f"    ftp={r.get('ftp')}, ltp={r.get('ltp')}, hie={r.get('hie')}, pmax={r.get('peak_power')}")

r = test("CP/W'", f"{base}/api/fitness/cp-wprime", "POST",
         {"efforts": {"180": 350, "300": 280, "600": 250}})
if r:
    print(f"    cp={r.get('cp')}W, w'={r.get('w_prime')}J")

r = test("Injuries", f"{base}/api/injuries")
if r:
    s = r.get("summary", {})
    print(f"    active={s.get('active_count')}, total={s.get('total_count')}")

r = test("Sessions", f"{base}/api/sessions")
if r:
    print(f"    active={r.get('stats', {}).get('active_sessions')}")

r = test("Sync Targets", f"{base}/api/sync/targets")
if r:
    print(f"    targets={[t.get('key') for t in r.get('targets', [])]}")

r = test("Export Backup", f"{base}/api/export/backup")
if r:
    print(f"    result={'ok' if 'error' not in r else r.get('error')}")

print()
print("=== HTML Pages ===")
for page in ["/", "/profile", "/workouts", "/analytics", "/settings"]:
    try:
        req = urllib.request.Request(f"{base}{page}")
        with urllib.request.urlopen(req, timeout=5) as resp:
            size = len(resp.read())
            print(f"  {page}: OK ({resp.status}, {size} bytes)")
    except Exception as e:
        print(f"  {page}: FAIL ({e})")

print()
print("All tests complete!")

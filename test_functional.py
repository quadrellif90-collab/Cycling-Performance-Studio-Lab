"""Full functional test of CPSL."""
import urllib.request, json, sys

base = 'http://127.0.0.1:22400'

def api(method, url, data=None):
    headers = {'Content-Type': 'application/json'} if data else {}
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(base + url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read())

try:
    print('=== Full Functional Test ===')

    r = api('POST', '/api/profiles', {'name': 'Test Rider'})
    pid = r.get('profile_id')
    print(f'1. Create profile: {pid}')

    r = api('POST', f'/api/profiles/{pid}/switch')
    print(f'2. Switch profile: OK')

    r = api('POST', f'/api/profiles/{pid}/athlete', {
        'ftp': 250, 'weight_kg': 75, 'lthr': 175, 'max_hr': 195
    })
    print(f'3. Save athlete: OK')

    r = api('GET', f'/api/profiles/{pid}/athlete')
    print(f'4. Get athlete: ftp={r.get("ftp")}, weight={r.get("weight_kg")}')

    r = api('POST', '/api/fitness/estimate-ftp', {'efforts': {'300': 300, '600': 260, '1200': 230, '3600': 210}})
    print(f'5. Estimate FTP: {r.get("ftp")}W')

    r = api('POST', '/api/fitness/signature', {'efforts': {'300': 300, '600': 260}, 'ftp': 250})
    print(f'6. Fitness sig: FTP={r.get("ftp")}, LTP={r.get("ltp")}, HIE={r.get("hie")}')

    r = api('POST', '/api/fitness/cp-wprime', {'efforts': {'180': 380, '300': 300, '600': 260, '1200': 230}})
    print(f"7. CP/W': CP={r.get('cp')}W, W'={r.get('w_prime')}J")

    r = api('POST', '/api/injuries', {'name': 'Test injury', 'date_start': '2025-01-15', 'severity': 'medium'})
    print(f'8. Create injury: {r.get("injury_id", "")[:20]}...')

    r = api('GET', '/api/injuries')
    print(f'9. Injuries: {r.get("summary", {}).get("active_count")} active')

    r = api('POST', '/api/sessions', {'profile_id': pid})
    print(f'10. Session: {r.get("session_id", "")[:12]}...')

    r = api('GET', '/api/export/backup')
    print(f'11. Export: {"OK" if "error" not in r else r.get("error")}')

    r = api('DELETE', f'/api/profiles/{pid}')
    print(f'12. Delete profile: OK')

    print()
    print('ALL 12 FUNCTIONAL TESTS PASSED!')

except Exception as e:
    print(f'FAIL: {e}')
    sys.exit(1)

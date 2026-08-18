"""Start server and test with error capture."""
import sys, os, threading, time
os.chdir(r'C:\Users\Siviglino\Desktop\PPC\Cycling Performance Studio Lab')
sys.path.insert(0, '.')

# Start server in background
def run_server():
    import uvicorn
    uvicorn.run('app:app', host='127.0.0.1', port=22400, log_level='debug')

t = threading.Thread(target=run_server, daemon=True)
t.start()
time.sleep(4)

# Test pages
import urllib.request, urllib.error
for page in ['/', '/profile', '/workouts', '/analytics', '/settings']:
    try:
        req = urllib.request.Request(f'http://127.0.0.1:22400{page}')
        with urllib.request.urlopen(req, timeout=5) as resp:
            print(f'{page}: OK ({resp.status})')
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:200]
        print(f'{page}: {e.code} - {body}')

time.sleep(999999)

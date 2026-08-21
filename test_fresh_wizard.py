#!/usr/bin/env python3
"""Fresh-env wizard test: avvia server con HOME temporanea e verifica /setup."""
import os
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import urllib.request


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


FRESH = os.path.join(os.environ['TEMP'], 'cpsl-fresh2')
# NOTA: niente taskkill globale — ucciderebbe questo stesso script.
subprocess.run(['taskkill', '/f', '/im', 'chrome.exe'], capture_output=True)
time.sleep(2)
os.makedirs(FRESH, exist_ok=True)

env = dict(os.environ)
env['USERPROFILE'] = FRESH
env['HOME'] = FRESH
env['CPSL_SERVER_ONLY'] = '1'

proc = subprocess.Popen(
    [sys.executable, 'launcher.py', '--server-only'],
    cwd=os.path.dirname(os.path.abspath(__file__)),
    env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# attende che il server risponda
import urllib.request
up = False
for _ in range(40):
    try:
        urllib.request.urlopen('http://127.0.0.1:22400/api/version', timeout=2)
        up = True
        break
    except Exception:
        time.sleep(1)
print(f'server up: {up}')


if up:
    # redirect check
    req = urllib.request.Request('http://127.0.0.1:22400/')
    opener = urllib.request.build_opener(_NoRedirect())
    try:
        resp = opener.open(req, timeout=5)
        print(f'/ status: {resp.status}')
    except Exception as e:
        print(f'/ redirect: {e}')

    from playwright.sync_api import sync_playwright
    chrome = os.path.expandvars(
        r'%LOCALAPPDATA%\ms-playwright\chromium-1228\chrome-win64\chrome.exe')
    chrome_proc = subprocess.Popen([
        chrome, '--remote-debugging-port=9223',
        f'--user-data-dir={os.environ["TEMP"]}\\cpsl-wiz2',
        '--no-first-run', '--headless=new', 'about:blank'])
    time.sleep(4)

    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp('http://127.0.0.1:9223')
        page = b.contexts[0].new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        page.goto('http://127.0.0.1:22400/setup', wait_until='domcontentloaded', timeout=30000)
        page.wait_for_timeout(3000)
        print(f'titolo: {page.title()}')
        n_inputs = page.locator('input').count()
        n_buttons = page.locator('button').count()
        print(f'input: {n_inputs}, button: {n_buttons}')
        print(f'pageerror: {errs[:4] if errs else "nessuno"}')
        page.close()
        b.close()
    chrome_proc.kill()

proc.kill()
print('done')


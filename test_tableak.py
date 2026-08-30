#!/usr/bin/env python3
"""Test leak tab: dopo ogni switch, quante sezioni sono visibili?"""
import os
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# avvia server (home normale)
proc = subprocess.Popen(
    [sys.executable, 'launcher.py', '--server-only'],
    cwd=os.path.dirname(os.path.abspath(__file__)),
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

import urllib.request

for _ in range(40):
    try:
        urllib.request.urlopen('http://127.0.0.1:22400/api/version', timeout=2)
        break
    except Exception:
        time.sleep(1)

from playwright.sync_api import sync_playwright

chrome = os.path.expandvars(
    r'%LOCALAPPDATA%\ms-playwright\chromium-1228\chrome-win64\chrome.exe')
cproc = subprocess.Popen([
    chrome, '--remote-debugging-port=9225',
    f'--user-data-dir={os.environ["TEMP"]}\\cpsl-tabtest',
    '--no-first-run', '--headless=new', 'about:blank'])
time.sleep(4)

TABS = ['home', 'picker', 'library', 'courses', 'plan', 'analysis', 'dfa',
        'settings', 'hrv', 'nutrition', 'bia', 'profile', 'whatsnew', 'ai_coach']

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp('http://127.0.0.1:9225')
    page = b.contexts[0].new_page()
    errs = []
    page.on('pageerror', lambda e: errs.append(str(e)))
    page.goto('http://127.0.0.1:22400', wait_until='domcontentloaded', timeout=30000)
    page.wait_for_timeout(4000)

    leaks = []
    for tab in TABS:
        el = page.locator(f'.tab[data-tab="{tab}"]')
        if not el.count():
            continue
        el.click(timeout=5000)
        page.wait_for_timeout(1500)
        visible_sections = page.evaluate("""() =>
            Array.from(document.querySelectorAll('.section.active'))
                 .map(s => s.id)""")
        active_tabs = page.evaluate("""() =>
            Array.from(document.querySelectorAll('.tab.active'))
                 .map(t => t.dataset.tab)""")
        if len(visible_sections) > 1 or len(active_tabs) > 1:
            leaks.append((tab, visible_sections, active_tabs))
            print(f"LEAK su {tab}: sezioni visibili={visible_sections}, tab attivi={active_tabs}")

    if not leaks:
        print("NESSUN LEAK: solo una sezione visibile e un tab attivo per ogni click")

    # verifica anche: elementi fixed/sticky fuori dalle sezioni che potrebbero sovrapporsi
    overlays = page.evaluate("""() => Array.from(document.querySelectorAll('body > div'))
        .filter(d => { const s = getComputedStyle(d);
            return d.style.display !== 'none' && s.position === 'fixed' &&
                   s.zIndex > 100 && d.offsetParent !== null; })
        .map(d => ({id: d.id || '(anon)', z: d.style.zIndex || getComputedStyle(d).zIndex,
                    cls: d.className.slice(0,40)}))""")
    print(f"\noverlay fixed visibili a fine test: {overlays}")

    print(f"pageerror: {errs[:3] if errs else 'nessuno'}")
    page.close()
    b.close()

cproc.kill()
proc.kill()
print('done')

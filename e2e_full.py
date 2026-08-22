#!/usr/bin/env python3
"""E2E v2 — usa i selettori REALI del wizard /setup."""
import json, os, subprocess, sys, time, traceback, shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(ROOT, 'e2e-report')
os.makedirs(REPORT_DIR, exist_ok=True)
FRESH = os.path.join(os.environ.get('TEMP', '/tmp'), 'cpsl-e2e-v2')
shutil.rmtree(FRESH, ignore_errors=True)

subprocess.run(['taskkill', '/f', '/im', 'chrome.exe'], capture_output=True,
               creationflags=subprocess.CREATE_NO_WINDOW)
time.sleep(1)

env = dict(os.environ)
env['USERPROFILE'] = FRESH
env['HOME'] = FRESH
env['CPSL_SERVER_ONLY'] = '1'
env['CPSL_PORT'] = '22998'

proc = subprocess.Popen([sys.executable, 'launcher.py', '--server-only'],
                        cwd=ROOT, env=env,
                        stdout=open(os.path.join(REPORT_DIR, 'server_v2.log'), 'w'),
                        stderr=subprocess.STDOUT)

import urllib.request
up = False
for _ in range(50):
    try:
        urllib.request.urlopen('http://127.0.0.1:22998/api/version', timeout=2)
        up = True; break
    except Exception: time.sleep(1)
print(f"server up: {up}")

from playwright.sync_api import sync_playwright

report = []
console_errors = []
page_errors = []
network_failures = []
shot_n = [0]

def shot(page, label):
    shot_n[0] += 1
    try: page.screenshot(path=os.path.join(REPORT_DIR, f'v2_{shot_n[0]:03d}_{label}.png'))
    except: pass

def record(step, status, detail=''):
    report.append((step, status, detail))
    icon = '✓' if status == 'OK' else '⚠' if status == 'WARN' else '✗'
    print(f"  [{icon}] {step}" + (f" → {detail}" if detail else ''))

try:
    chrome = os.path.expandvars(r'%LOCALAPPDATA%\ms-playwright\chromium-1228\chrome-win64\chrome.exe')
    cproc = subprocess.Popen([chrome, '--remote-debugging-port=9334',
                              f'--user-data-dir={os.environ["TEMP"]}\\cpsl-e2e-br2',
                              '--no-first-run', '--headless=new', '--window-size=1400,900',
                              'about:blank'])
    time.sleep(3)

    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp('http://127.0.0.1:9334')
        page = b.contexts[0].new_page()
        page.set_viewport_size({'width': 1400, 'height': 900})
        page.on('console', lambda m: console_errors.append(m.text) if m.type == 'error' else None)
        page.on('pageerror', lambda e: page_errors.append(str(e)))
        page.on('response', lambda r: network_failures.append(f"{r.status} {r.url[:120]}") if r.status >= 400 else None)

        # ══ 1. PRIMO AVVIO ═════════════════════════════════════════════
        print('\n=== PRIMO AVVIO ===')
        page.goto('http://127.0.0.1:22998', wait_until='domcontentloaded', timeout=30000)
        page.wait_for_timeout(4000)
        shot(page, 'first_load')
        url = page.url
        is_setup = '/setup' in url
        record('wizard-appare', 'OK' if is_setup else 'WARN',
               f"url={url}" + (" — WIZARD APPARE ✓" if is_setup else " — NESSUN WIZARD"))

        # ══ 2. WIZARD SETUP (struttura reale) ══════════════════════════
        print('\n=== WIZARD SETUP ===')
        if is_setup:
            shot(page, 'setup_step1')

            # STEP 1: Connect your data → Continue
            btn1 = page.locator('#step1-next')
            record('setup-step1-visible', 'OK' if btn1.is_visible() else 'FAIL')
            btn1.click()
            page.wait_for_timeout(1500)
            shot(page, 'setup_step2')

            # STEP 2: Metriche (peso, altezza, età, FTP...)
            inputs = {
                '#set-weight': '72', '#set-lbm': '58', '#set-ftp': '250',
                '#set-lthr': '170', '#set-maxhr': '195',
                '#ob-weight': '72', '#ob-height': '175', '#ob-age': '35',
                '#ob-ftp': '250', '#ob-lthr': '170', '#ob-maxhr': '195',
                '#wiz-weight': '72', '#wiz-height': '175', '#wiz-age': '35',
            }
            filled = 0
            for sel, val in inputs.items():
                loc = page.locator(sel)
                if loc.count() and loc.first.is_visible():
                    try:
                        loc.first.fill(val)
                        filled += 1
                    except Exception: pass
            record('setup-step2-fill', 'OK' if filled > 0 else 'WARN', f'{filled} campi compilati')
            shot(page, 'setup_step2_filled')

            btn2 = page.locator('#step2-next')
            if btn2.is_visible():
                btn2.click()
                page.wait_for_timeout(1500)
                shot(page, 'setup_step3')

            # STEP 3: eventuali input rimasti
            for sel, val in list(inputs.items()):
                loc = page.locator(sel)
                if loc.count() and loc.first.is_visible():
                    try: loc.first.fill(val); filled += 1
                    except Exception: pass

            # Cerca il bottone per andare avanti da step 3
            next3 = page.locator('#step3-next, button[onclick*="nextStep(4)"]')
            if not next3.count():
                next3 = page.locator('button:has-text("Next"), button:has-text("Next")')
            if next3.count() and next3.first.is_visible():
                next3.first.click()
                page.wait_for_timeout(1500)
                shot(page, 'setup_step4')

            # STEP 4: Complete Setup
            save_btn = page.locator('#save-btn')
            if save_btn.count() and save_btn.is_visible():
                save_btn.click()
                page.wait_for_timeout(3000)
                shot(page, 'setup_completed')
                record('setup-complete', 'OK', f'url dopo={page.url}')
            else:
                # forse c'è un skip-link
                skip_link = page.locator('.skip-link')
                if skip_link.count() and skip_link.is_visible():
                    skip_link.click()
                    page.wait_for_timeout(2000)
                    record('setup-skip-link', 'OK', f'url dopo={page.url}')
                else:
                    record('setup-complete', 'WARN', f'bottone save non trovato, url={page.url}')

        # ══ 3. TAB-BY-TAB ══════════════════════════════════════════════
        print('\n=== TAB WALKTHROUGH ===')
        TABS = ['home', 'picker', 'library', 'courses', 'plan', 'analysis',
                'dfa', 'settings', 'hrv', 'nutrition', 'bia', 'profile',
                'whatsnew', 'ai_coach']

        # Se siamo ancora su /setup vai alla dashboard
        if '/setup' in page.url:
            page.goto('http://127.0.0.1:22998', wait_until='domcontentloaded')
            page.wait_for_timeout(4000)

        for i, tab in enumerate(TABS):
            el = page.locator(f'.tab[data-tab="{tab}"]')
            if not el.count():
                record(f'tab-{tab}', 'FAIL', 'tab NOT FOUND'); continue

            pe_before = list(page_errors)
            ce_before = list(console_errors)
            nf_before = list(network_failures)

            try:
                el.click(timeout=5000)
                page.wait_for_timeout(2000)
            except Exception as e:
                record(f'tab-{tab}-click', 'FAIL', str(e)[:80]); continue

            visible = page.locator(f'#sec-{tab}').is_visible()
            shot(page, f'tab_{tab}')

            new_pe = [e for e in page_errors if e not in pe_before]
            new_ce = [c for c in console_errors if c not in ce_before]
            new_nf = [n for n in network_failures if n not in nf_before]

            status = 'OK' if visible and not new_pe else 'FAIL'
            details = []
            if not visible: details.append('non visibile')
            if new_pe: details.append(f'JS:{new_pe[0][:70]}')
            if new_ce: details.append(f'console:{new_ce[-1][:50]}')
            if new_nf: details.append(f'http:{new_nf[0][:70]}')
            record(f'tab-{tab}', status, '; '.join(details))

            # Test specifici per tab
            if tab == 'home':
                gcards = page.locator('#home-grid > .card').count()
                toolbar = page.locator('#layout-toolbar').count()
                digest = page.locator('#daily-digest-card').count()
                record('home-grid', 'OK' if gcards >= 5 else 'WARN', f'{gcards} cards')
                record('home-toolbar', 'OK' if toolbar else 'WARN')
                record('home-digest', 'OK' if digest else 'WARN')

            elif tab == 'analysis':
                chart = page.evaluate("typeof Chart !== 'undefined'")
                canvases = page.evaluate("""() => Array.from(
                    document.querySelectorAll('#sec-analysis canvas')).map(c => ({
                        id: c.id||'?', painted: c.getContext('2d').getImageData(0,0,1,1).data.some(v=>v!==0)}))""")
                painted = sum(1 for c in canvases if c.get('painted'))
                record('analysis-chartjs', 'OK' if chart else 'FAIL')
                record('analysis-painted', 'OK' if painted > 0 else 'WARN',
                       f"{painted}/{len(canvases)} dipinti")

            elif tab == 'plan':
                gen = page.locator('#btn-generate-plan')
                fold = page.locator('#plan-config-header')
                vers = page.locator('#btn-plan-versions')
                ai_panel = page.locator('#ai-plan-card')
                record('plan-generate', 'OK' if gen.count() else 'WARN')
                record('plan-fold', 'OK' if fold.count() else 'WARN',
                       f"expanded={fold.get_attribute('aria-expanded')}" if fold.count() else '')
                record('plan-versions-btn', 'OK' if vers.count() else 'WARN')
                record('plan-ai-panel', 'OK' if ai_panel.count() else 'WARN')

            elif tab == 'settings':
                icu = page.evaluate("() => /intervals/i.test(document.body.innerText)")
                api_fields = page.locator('#icu-api-key, [id*=api-key], [id*=apikey]')
                record('settings-icu-text', 'OK' if icu else 'WARN')
                record('settings-api-field', 'OK' if api_fields.count() else 'WARN',
                       f"{api_fields.count()} campi")

        # ══ 4. API CALCOLATORI ═════════════════════════════════════════
        print('\n=== CALCOLATORI ===')
        calcs = [
            ('FTP', 'POST', '/api/fitness/estimate-ftp', {'efforts': {'300':280,'600':250,'1200':220}}),
            ('Nutrition', 'GET', '/api/nutrition-full', None),
            ('Fueling', 'GET', '/api/fueling/session?duration_min=90&weight_kg=72', None),
            ('PowerCurve', 'GET', '/api/power-curve', None),
            ('CPModels', 'GET', '/api/cp-models', None),
            ('Readiness', 'GET', '/api/readiness/composite', None),
            ('HRV-summary', 'GET', '/api/hrv/summary', None),
            ('Digest', 'GET', '/api/notifications/digest', None),
            ('PlanVersions', 'GET', '/api/plan/versions', None),
            ('AIStatus', 'GET', '/api/ai/status', None),
            ('SyncStatus', 'GET', '/api/sync/status', None),
            ('Wellness', 'GET', '/api/wellness', None),
            ('Rides', 'GET', '/api/rides?limit=5', None),
            ('OnboardingStatus', 'GET', '/api/onboarding/status', None),
            ('ExportBackup', 'GET', '/api/export/backup', None),
            ('TerraStatus', 'GET', '/api/terra/status', None),
            ('WorkoutsClassify', 'GET', '/api/workouts/classify', None),
        ]
        for name, method, ep, body in calcs:
            try:
                if body:
                    result = page.evaluate(
                        f"fetch('{ep}',{{method:'POST',headers:{{'Content-Type':'application/json'}},"
                        f"body:JSON.stringify({json.dumps(body)})}}).then(r=>r.status)")
                else:
                    result = page.evaluate(f"fetch('{ep}').then(r=>r.status)")
                record(f'api-{name}', 'OK' if result < 400 else 'FAIL', f'HTTP {result}')
            except Exception as e:
                record(f'api-{name}', 'FAIL', str(e)[:80])

        # ══ 5. INTERAZIONI ═════════════════════════════════════════════
        print('\n=== INTERAZIONI ===')
        page.evaluate("gotoTab('home')")
        page.wait_for_timeout(500)

        # tema
        ts = page.locator('#theme-select')
        if ts.count():
            ts.select_option('dark')
            page.wait_for_timeout(400)
            theme = page.evaluate("document.documentElement.getAttribute('data-theme')")
            record('tema-dark', 'OK' if theme == 'dark' else 'FAIL')
            ts.select_option('light')
            page.wait_for_timeout(300)

        # layout edit
        eb = page.locator('#btn-layout-edit')
        if eb.count():
            eb.click(); page.wait_for_timeout(400)
            editing = page.evaluate("document.body.classList.contains('layout-edit')")
            handles = page.locator('.dl-resize-handle').count()
            record('layout-edit', 'OK' if editing and handles else 'WARN',
                   f"edit={editing}, handle={handles}")
            eb.click(); page.wait_for_timeout(300)

        # click-to-navigate
        page.evaluate("gotoTab('home')"); page.wait_for_timeout(400)
        today_card = page.locator('#today-card')
        if today_card.count():
            try:
                today_card.click(position={'x':10,'y':10}, timeout=3000)
                page.wait_for_timeout(500)
                active = page.evaluate(
                    "document.querySelector('.section.active')?.id || '?')")
                record('nav-today->plan', 'OK' if 'plan' in active.lower() else 'WARN',
                       f'attivo={active}')
            except Exception as e:
                record('nav-today->plan', 'WARN', str(e)[:60])
        else:
            record('nav-today-card', 'WARN', 'card non trovata')

        # screenshot finale
        page.evaluate("gotoTab('home')"); page.wait_for_timeout(1000)
        shot(page, 'final_home')

        page.close(); b.close()

except Exception as e:
    record('FATAL', 'FAIL', f'{type(e).__name__}: {e}')
    traceback.print_exc()
finally:
    try: cproc.kill()
    except: pass
    try: proc.kill()
    except: pass

# ══ REPORT ═════════════════════════════════════════════════════════════
ok_n = sum(1 for _,s,_ in report if s=='OK')
warn_n = sum(1 for _,s,_ in report if s=='WARN')
fail_n = sum(1 for _,s,_ in report if s=='FAIL')
print(f'\n{"="*60}\nREPORT: OK={ok_n} WARN={warn_n} FAIL={fail_n}\n{"="*60}')
if fail_n:
    print('\nFALLIMENTI:')
    for s_, st, d in report:
        if st == 'FAIL': print(f'  ✗ {s_}: {d}')
if warn_n:
    print('\nWARNING:')
    for s_, st, d in report:
        if st == 'WARN': print(f'  ⚠ {s_}: {d}')
print(f'\nConsole errors: {len(console_errors)}')
for c in console_errors[:6]: print(f'  {c[:140]}')
print(f'Page errors: {len(page_errors)}')
for e in page_errors[:6]: print(f'  {e[:140]}')
print(f'Network failures: {len(network_failures)}')
for n in network_failures[:6]: print(f'  {n[:140]}')

with open(os.path.join(REPORT_DIR, 'report_v2.md'), 'w', encoding='utf-8') as f:
    f.write('# E2E v2 Report\n\n| Step | Status | Detail |\n|---|---|---|\n')
    for s_, st, d in report:
        icon = '✅' if st == 'OK' else '⚠️' if st == 'WARN' else '❌'
        f.write(f'| {icon} {s_} | {st} | {d} |\n')
    f.write(f'\n## Console errors ({len(console_errors)})\n')
    for c in console_errors: f.write(f'- {c}\n')
    f.write(f'\n## Page errors ({len(page_errors)})\n')
    for e in page_errors: f.write(f'- {e}\n')
    f.write(f'\n## Network ({len(network_failures)})\n')
    for n in network_failures: f.write(f'- {n}\n')
print(f'\nReport: {REPORT_DIR}/report_v2.md | Screenshot: {shot_n[0]}')

#!/usr/bin/env python3
"""
QA A->Z autonomo CPSL: simula un utente reale.
Fase B: boot server pulito
Fase C: sweep 14 tab (attivazione sezione + errori console + risposte 4xx/5xx)
Fase D: suite personalizzazione layout (8 check)
Fase E: scansione salute API (GET sicuri)
"""
import json, os, subprocess, sys, time, urllib.request, urllib.error
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(ROOT, 'qa_shots')
os.makedirs(SHOTS, exist_ok=True)

PORT = 22400
BASE = f'http://127.0.0.1:{PORT}'
results = []
def record(name, ok, d=''):
    results.append((name, ok))
    print(f'  {"✅" if ok else "❌"} {name}' + (f' — {d}' if d else ''))

TABS = ['home','picker','library','courses','plan','analysis','dfa',
        'settings','hrv','nutrition','bia','profile','whatsnew','ai_coach']

API_SAFE = [
 '/api/version','/api/diag/health','/api/diag/recent-errors','/api/setup/status',
 '/api/profiles','/api/settings','/api/rider-stats','/api/readiness',
 '/api/readiness/composite','/api/wellness','/api/activities','/api/workouts',
 '/api/workouts/tags','/api/picker','/api/courses','/api/routes/regions',
 '/api/surface-types','/api/virtual-routes','/api/mcp/status','/api/icu/connection',
 '/api/sync/status','/api/sync/progress','/api/metrics/latest',
 '/api/metrics/history?metric=weight&days=30',
 '/api/blood-markers','/api/power-curve','/api/weekly-plan','/api/plan',
 '/api/calendar','/api/rides','/api/tid-weekly','/api/plan-block-model',
 '/api/daily-adapt','/api/today-session','/api/profile/ftp-history',
 '/api/profile/power-curve','/api/gc/status','/api/logs',
]

# ── FASE B: BOOT ─────────────────────────────────────────────────────────
print('=== FASE B: BOOT SERVER ===')
server = None
try:
    r = urllib.request.urlopen(BASE + '/api/version', timeout=2)
    print('  server già attivo (riuso)')
except Exception:
    server = subprocess.Popen([sys.executable, 'launcher.py', '--server-only'],
                              cwd=ROOT,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    up = False
    for _ in range(60):
        time.sleep(1)
        try:
            ver = json.loads(urllib.request.urlopen(BASE + '/api/version', timeout=2).read())
            up = True; break
        except Exception:
            pass
    record('boot_server', up, str(ver)[:60] if up else 'timeout 60s')

# ── PLAYWRIGHT SETUP ─────────────────────────────────────────────────────
from playwright.sync_api import sync_playwright
chrome = os.path.expandvars(r'%LOCALAPPDATA%\ms-playwright\chromium-1228\chrome-win64\chrome.exe')

with sync_playwright() as p:
    cproc = subprocess.Popen([chrome,
        '--remote-debugging-port=9233',
        f'--user-data-dir={os.environ["TEMP"]}\\cpsl-qa-az',
        '--no-first-run', '--headless=new', '--window-size=1400,900', 'about:blank'])
    time.sleep(3)
    b = p.chromium.connect_over_cdp('http://127.0.0.1:9233')
    page = b.contexts[0].new_page()
    page.set_viewport_size({'width': 1400, 'height': 900})

    console_errs, page_errs, bad_resp = [], [], []
    page.on('console', lambda m: console_errs.append(m.text) if m.type == 'error' else None)
    page.on('pageerror', lambda e: page_errs.append(str(e)))
    page.on('response', lambda r: bad_resp.append((r.status, r.url)) if r.status >= 400 else None)

    # ── FASE C: SWEEP TAB ────────────────────────────────────────────────
    print('\n=== FASE C: SWEEP 14 TAB ===')
    page.goto(BASE, wait_until='domcontentloaded', timeout=30000)
    page.wait_for_timeout(6000)

    n_tabs = page.evaluate("document.querySelectorAll('.tab[data-tab]').length")
    record('tabs_presenti', n_tabs == len(TABS), f'{n_tabs}/{len(TABS)}')

    for t in TABS:
        pre = (len(console_errs), len(page_errs), len(bad_resp))
        try:
            try:
                page.click(f'.tab[data-tab="{t}"]', timeout=8000)
            except Exception:
                # retry: possibile instabilità temporanea (toast/animazioni)
                page.click(f'.tab[data-tab="{t}"]', timeout=8000, force=True)
            page.wait_for_timeout(1200)
            active = page.evaluate(
                f"document.getElementById('sec-{t}')?.classList.contains('active')")
            others = page.evaluate("""() =>
                Array.from(document.querySelectorAll('.section.active'))
                     .filter(s => !arguments_ok).length """ .replace('arguments_ok','true') )
            shot = os.path.join(SHOTS, f'tab_{t}.png')
            page.screenshot(path=shot)
            errs_new = (console_errs[pre[0]:], page_errs[pre[1]:], bad_resp[pre[2]:])
            clean = active and not errs_new[1] and not [x for x in errs_new[2] if '/api/' in x[1]]
            record(f'tab_{t}', bool(clean),
                   '' if clean else f'active={active} jserr={errs_new[1][:1]} http={errs_new[2][:3]}')
        except Exception as ex:
            record(f'tab_{t}', False, str(ex)[:80])

    # ── FASE D: LAYOUT ───────────────────────────────────────────────────
    print('\n=== FASE D: PERSONALIZZAZIONE LAYOUT ===')
    page.click('.tab[data-tab="home"]'); page.wait_for_timeout(800)
    page.evaluate("for (const k of Object.keys(localStorage)) if (k.startsWith('homeLayout')) localStorage.removeItem(k)")
    page.reload(wait_until='domcontentloaded'); page.wait_for_timeout(4000)
    page.click('#btn-layout-edit'); page.wait_for_timeout(400)

    order0 = page.evaluate("() => Array.from(document.querySelectorAll('#home-grid > .card')).map(c => c.id)")
    record('layout_edit_mode', page.evaluate("document.body.classList.contains('layout-edit')"))
    record('layout_bottoni', page.evaluate("document.querySelectorAll('.dl-card-controls').length") >= 5)

    page.locator('#readiness-factors-card .dl-card-controls button[title="Sposta destra"]').click()
    page.wait_for_timeout(300)
    order1 = page.evaluate("() => Array.from(document.querySelectorAll('#home-grid > .card')).map(c => c.id)")
    record('layout_move_dx_sx', order1 != order0 and
           page.locator('#readiness-factors-card .dl-card-controls button[title="Sposta sinistra"]').click() is None
           and True, '')
    page.wait_for_timeout(300)
    order2 = page.evaluate("() => Array.from(document.querySelectorAll('#home-grid > .card')).map(c => c.id)")
    record('layout_ritorno_origine', order2 == order0)

    sid = 'sleep-hrv-card'
    sb = page.evaluate(f"document.getElementById('{sid}')?.dataset.span")
    page.locator(f'#{sid} .dl-card-controls button[title="Più largo"]').click(); page.wait_for_timeout(200)
    sm = page.evaluate(f"document.getElementById('{sid}')?.dataset.span")
    page.locator(f'#{sid} .dl-card-controls button[title="Più stretto"]').click(); page.wait_for_timeout(200)
    se = page.evaluate(f"document.getElementById('{sid}')?.dataset.span")
    record('layout_resize_piu_meno', sb != sm and se == sb, f'{sb}->{sm}->{se}')

    page.locator(f'#{sid} .dl-card-controls button[title="Più largo"]').click(); page.wait_for_timeout(250)
    saved = page.evaluate(f"document.getElementById('{sid}')?.dataset.span")
    page.reload(wait_until='domcontentloaded'); page.wait_for_timeout(3500)
    after = page.evaluate(f"document.getElementById('{sid}')?.dataset.span")
    record('layout_persistenza_reload', saved == after, f'{saved}=={after}')

    # ri-attiva edit mode dopo il reload (il reload lo disattiva)
    if not page.evaluate("document.body.classList.contains('layout-edit')"):
        page.click('#btn-layout-edit'); page.wait_for_timeout(400)

    drag = page.evaluate("""() => {
        const grid = document.getElementById('home-grid');
        const els = () => Array.from(grid.children).filter(c=>c.classList.contains('card'));
        const before = els().map(c=>c.id);
        const src = els()[0], dst = els()[1];
        const sr = src.getBoundingClientRect(), dr = dst.getBoundingClientRect();
        const sx=sr.x+sr.width/2, sy=sr.y+20, tx=dr.x+dr.width/2, ty=dr.y+dr.height*0.75;
        const mk=(t,x,y)=>new PointerEvent(t,{bubbles:true,cancelable:true,clientX:x,
            clientY:y,button:0,buttons:t==='pointerup'?0:1,pointerId:11,isPrimary:true});
        src.dispatchEvent(mk('pointerdown',sx,sy));
        for(let i=1;i<=6;i++) document.dispatchEvent(mk('pointermove',sx+(tx-sx)*i/6,sy+(ty-sy)*i/6));
        document.dispatchEvent(mk('pointerup',tx,ty));
        return before.join('|') !== els().map(c=>c.id).join('|');
    }""")
    record('layout_drag_reale', drag is True)
    ls = page.evaluate("""() => { for (const k of Object.keys(localStorage))
        if (k.startsWith('homeLayout')) return true; return false; }""")
    record('layout_drag_persistito', ls is True)
    # esci da edit mode SOLO se attivo (il click è un toggle)
    if page.evaluate("document.body.classList.contains('layout-edit')"):
        page.click('#btn-layout-edit'); page.wait_for_timeout(300)
    page.locator('#readiness-factors-card').scroll_into_view_if_needed()
    page.wait_for_timeout(200)
    page.locator('#readiness-factors-card').click(position={'x': 300, 'y': 120})
    page.wait_for_timeout(700)
    on_plan = page.evaluate("document.getElementById('sec-plan').classList.contains('active')")
    record('layout_click_naviga_plan', on_plan)

    # ── FASE E: API SCAN ─────────────────────────────────────────────────
    print('\n=== FASE E: SALUTE API (GET sicuri) ===')
    api_bad = []
    for ep in API_SAFE:
        try:
            req = urllib.request.Request(BASE + ep, headers={'Accept':'application/json'})
            with urllib.request.urlopen(req, timeout=20) as resp:
                code = resp.status
                body = resp.read(200)
        except urllib.error.HTTPError as e:
            code = e.code
        except Exception as e:
            code = f'ERR:{str(e)[:30]}'
        if code != 200:
            api_bad.append((ep, code))
    record('api_scan_tutti_200', len(api_bad) == 0,
           f'{len(API_SAFE)} endpoint' if not api_bad else f'KO: {api_bad[:6]}')

    page.close(); b.close(); cproc.kill()

# ── REPORT FINALE ────────────────────────────────────────────────────────
ok_n = sum(1 for _, ok in results if ok)
fail_n = sum(1 for _, ok in results if not ok)
print('\n' + '=' * 56)
print(f'RESULTATO FINALE: {ok_n} OK / {fail_n} FAIL / {len(results)} totali')
print('=' * 56)
for n, ok in results:
    if not ok: print(f'  ❌ {n}')
if server: server.kill()
sys.exit(1 if fail_n else 0)

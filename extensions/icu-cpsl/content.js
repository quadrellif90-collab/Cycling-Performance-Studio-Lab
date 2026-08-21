// CPSL for Intervals.icu — content script (MV3)
// Inietta un pannello CPSL nella pagina atleta/activity di intervals.icu.
// Tutte le chiamate API passano dal background service worker (auth centralizzata).

const PANEL_ID = 'cpsl-icu-panel';

function send(msg) {
  return new Promise((resolve) => chrome.runtime.sendMessage(msg, (r) => resolve(r || { ok: false, error: 'no response' })));
}

function getAthleteIdFromUrl() {
  const m = window.location.pathname.match(/\/(athlete|activities|activity|wellness)\/([A-Za-z0-9_]+)/);
  if (m) return m[2];
  return new URLSearchParams(window.location.search).get('athleteId');
}

function getActivityIdFromUrl() {
  const m = window.location.pathname.match(/\/activities?\/([A-Za-z0-9_]+)/);
  return m ? m[1] : null;
}

function f(v, d = 1) { return v == null ? '—' : Number(v).toFixed(d); }
// Escape HTML for any string coming from the ICU API before injecting via innerHTML
function esc(s) { return String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); }

function computeIndicators(wellness) {
  if (!wellness || !wellness.length) return null;
  const last = wellness[wellness.length - 1];
  const ctl = last.ctl ?? null, atl = last.atl ?? null;
  const tsb = (ctl != null && atl != null) ? ctl - atl : null;
  const recent = wellness.slice(-14).map(w => w.hrv).filter(v => v != null);
  return {
    ctl, atl, tsb,
    hrv: last.hrv ?? null,
    hrvAvg14: recent.length ? recent.reduce((a, b) => a + b, 0) / recent.length : null,
    weight: last.weightKg ?? null,
    restingHr: last.restingHr ?? null,
  };
}

function panelShell() {
  let p = document.getElementById(PANEL_ID);
  if (!p) {
    p = document.createElement('div');
    p.id = PANEL_ID;
    p.className = 'cpsl-panel';
    (document.querySelector('main') || document.body).insertBefore(p, (document.querySelector('main') || document.body).firstChild);
  }
  return p;
}

function renderLoading() {
  panelShell().innerHTML = `<div class="cpsl-head">🚴 CPSL</div><div class="cpsl-body">Caricamento…</div>`;
}

function renderNoAuth() {
  const p = panelShell();
  p.innerHTML = `<div class="cpsl-head">🚴 CPSL</div>
    <div class="cpsl-body">Configura la tua Intervals.icu API Key o OAuth token nelle <a href="#" id="cpsl-opt">opzioni</a>.</div>`;
  p.querySelector('#cpsl-opt').onclick = (e) => { e.preventDefault(); chrome.runtime.sendMessage({ type: 'OPEN_OPTIONS' }); };
}

function renderError(msg) {
  panelShell().innerHTML = `<div class="cpsl-head">🚴 CPSL</div><div class="cpsl-body">Errore: ${msg}</div>`;
}

function renderPanel(ind, extra, source) {
  const p = panelShell();
  const rows = [
    ['Forma (CTL)', f(ind.ctl)], ['Fatica (ATL)', f(ind.atl)], ['Equilibrio (TSB)', f(ind.tsb)],
    ['HRV', `${f(ind.hrv, 0)} ms`], ['HRV 14gg', `${f(ind.hrvAvg14, 0)} ms`],
    ['Peso', ind.weight ? `${f(ind.weight)} kg` : '—'],
  ];
  if (ind.restingHr != null) rows.push(['RHR', `${f(ind.restingHr, 0)} bpm`]);
  let extraHtml = '';
  if (extra && extra.activities && extra.activities.length) {
    const a = extra.activities.slice(-3).reverse().map(x =>
      `<li>${esc((x.name || 'Attività').slice(0, 40))} — ${f((x.total_power_work || 0) / 1000, 1)} kJ${x.icu_training_load ? ' · TL ' + f(x.icu_training_load, 0) : ''}</li>`).join('');
    extraHtml += `<div class="cpsl-sub"><b>Ultime attività</b><ul>${a}</ul></div>`;
  }
  if (extra && extra.events && extra.events.length) {
    const ev = extra.events.slice(0, 3).map(x =>
      `<li>${esc(x.name || x.type || 'Evento')} — ${esc((x.date || '').slice(0, 10))}</li>`).join('');
    extraHtml += `<div class="cpsl-sub"><b>Prossimi eventi</b><ul>${ev}</ul></div>`;
  }
  p.innerHTML = `
    <div class="cpsl-head">🚴 CPSL · <span class="cpsl-src">${source}</span></div>
    <div class="cpsl-grid">${rows.map(([k, v]) => `<div><span>${k}</span><b>${v}</b></div>`).join('')}</div>
    ${extraHtml}
    <div class="cpsl-actions">
      <button id="cpsl-open">Apri in CPSL</button>
      <button id="cpsl-refresh">Aggiorna</button>
    </div>`;
  const aid = getAthleteIdFromUrl();
  p.querySelector('#cpsl-open').onclick = () => window.open(`http://127.0.0.1:22400/?athlete=${aid}`, '_blank');
  p.querySelector('#cpsl-refresh').onclick = () => loadAndRender(true);
}

async function loadAndRender(force = false) {
  const aid = getAthleteIdFromUrl();
  if (!aid) return;
  renderLoading();

  // Auth check
  const auth = await send({ type: 'AUTH_STATUS' });
  if (!auth.ok || (!auth.hasKey && !auth.hasToken)) { renderNoAuth(); return; }

  // 1) Bridge CPSL locale (valori ufficiali)
  const bridge = await send({ type: 'CPSL_CONTEXT', athleteId: aid });
  let ind = null, source = '';
  if (bridge.ok && bridge.data && bridge.data.indicators) {
    ind = bridge.data.indicators;
    source = 'CPSL locale';
  }

  // 2) Dati ICU per indicatori + extra
  const now = new Date().toISOString().slice(0, 10);
  const old = new Date(Date.now() - 120 * 864e5).toISOString().slice(0, 10);
  let wellness = null, activities = null, events = null;
  try {
    wellness = (await send({ type: 'GET_WELLNESS', athleteId: aid, oldest: old, newest: now, force })).data;
  } catch (_) {}
  if (!ind && wellness) { ind = computeIndicators(wellness); source = 'calcolato da ICU'; }
  if (!ind) { renderError('nessun dato disponibile'); return; }

  try { activities = (await send({ type: 'GET_ACTIVITIES', athleteId: aid, oldest: old, newest: now, limit: 5 })).data; } catch (_) {}
  try { events = (await send({ type: 'GET_EVENTS', athleteId: aid, oldest: now, newest: '2026-12-31' })).data; } catch (_) {}

  renderPanel(ind, { activities, events }, source);
}

// SPA navigation watcher
if (!window.__cpslIcuBound) {
  window.__cpslIcuBound = true;
  loadAndRender();
  chrome.runtime.onMessage.addListener((msg) => { if (msg.type === 'REFRESH') loadAndRender(true); });
  let lastUrl = location.href;
  setInterval(() => { if (location.href !== lastUrl) { lastUrl = location.href; loadAndRender(); } }, 1500);
}

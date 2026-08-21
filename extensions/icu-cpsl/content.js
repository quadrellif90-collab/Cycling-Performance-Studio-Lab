// CPSL for Intervals.icu — content script (MV3)
// Si aggancia alla pagina atleta di intervals.icu, legge l'athleteId dall'URL,
// recupera wellness/activities via API ICU (auth con la API key dell'utente,
// salvata nelle options dell'estensione) e mostra un pannello "CPSL".
// Se il backend CPSL locale è in esecuzione, ne usa i valori calcolati ufficiali.

const CPSL_BADGE_ID = 'cpsl-icu-panel';
const CPSL_API_BASE = 'http://127.0.0.1:22400';

function getAthleteIdFromUrl() {
  // URL tipo https://intervals.icu/athlete/{id}/... oppure /activities/{id}
  const m = window.location.pathname.match(/\/(athlete|activities|activity|wellness)\/([A-Za-z0-9_]+)/);
  if (m) return m[2];
  // fallback: query param ?athleteId=
  const p = new URLSearchParams(window.location.search).get('athleteId');
  return p || null;
}

async function getKey() {
  return new Promise((resolve) => {
    chrome.storage.local.get(['icuApiKey'], (r) => resolve(r.icuApiKey || ''));
  });
}

async function icuGet(path, key) {
  const url = `https://intervals.icu/api/v1/${path}`;
  const r = await fetch(url, { headers: { Authorization: 'Basic ' + btoa('API_KEY:' + key) } });
  if (!r.ok) throw new Error('ICU ' + r.status);
  return r.json();
}

function computeIndicators(wellness) {
  if (!wellness || !wellness.length) return null;
  const last = wellness[wellness.length - 1];
  const ctl = last.ctl != null ? last.ctl : null;          // forma (fitness)
  const atl = last.atl != null ? last.atl : null;          // fatica (fatigue)
  const tsb = (ctl != null && atl != null) ? ctl - atl : null; // forma/equilibrio
  const hrv = last.hrv != null ? last.hrv : null;
  const weight = last.weightKg != null ? last.weightKg : null;
  // HRV media 14gg
  const recent = wellness.slice(-14).map(w => w.hrv).filter(v => v != null);
  const hrvAvg = recent.length ? (recent.reduce((a,b)=>a+b,0)/recent.length) : null;
  return { ctl, atl, tsb, hrv, hrvAvg, weight };
}

function renderPanel(indicators, source) {
  let panel = document.getElementById(CPSL_BADGE_ID);
  if (!panel) {
    panel = document.createElement('div');
    panel.id = CPSL_BADGE_ID;
    panel.className = 'cpsl-panel';
    const host = document.querySelector('main') || document.body;
    host.insertBefore(panel, host.firstChild);
  }
  if (!indicators) {
    panel.innerHTML = `<div class="cpsl-head">CPSL</div><div class="cpsl-body">Nessun dato wellness disponibile per questo atleta.</div>`;
    return;
  }
  const f = (v, d=1) => v == null ? '—' : Number(v).toFixed(d);
  panel.innerHTML = `
    <div class="cpsl-head">🚴 CPSL · <span class="cpsl-src">${source}</span></div>
    <div class="cpsl-grid">
      <div><span>Forma (CTL)</span><b>${f(indicators.ctl)}</b></div>
      <div><span>Fatica (ATL)</span><b>${f(indicators.atl)}</b></div>
      <div><span>Equilibrio (TSB)</span><b>${f(indicators.tsb)}</b></div>
      <div><span>HRV</span><b>${f(indicators.hrv,0)} ms</b></div>
      <div><span>HRV 14gg</span><b>${f(indicators.hrvAvg,0)} ms</b></div>
      <div><span>Peso</span><b>${f(indicators.weight,1)} kg</b></div>
    </div>
    <div class="cpsl-actions">
      <button id="cpsl-open">Apri in CPSL</button>
      <button id="cpsl-refresh">Aggiorna</button>
    </div>`;
  const aid = getAthleteIdFromUrl();
  panel.querySelector('#cpsl-open').onclick = () => window.open(`${CPSL_API_BASE}/?athlete=${aid}`, '_blank');
  panel.querySelector('#cpsl-refresh').onclick = () => loadAndRender();
}

async function tryCpslBridge(aid) {
  // Se CPSL locale è attivo, usa i suoi valori calcolati ufficiali
  try {
    const r = await fetch(`${CPSL_API_BASE}/api/icu/extension/context?athlete_id=${aid}`, { signal: AbortSignal.timeout(1500) });
    if (!r.ok) return null;
    const d = await r.json();
    if (d && d.ok && d.indicators) return { indicators: d.indicators, source: 'CPSL locale' };
  } catch (_) {}
  return null;
}

async function loadAndRender() {
  const aid = getAthleteIdFromUrl();
  if (!aid) return;
  const panel = document.getElementById(CPSL_BADGE_ID);
  if (panel) panel.querySelector('.cpsl-body') && (panel.innerHTML = `<div class="cpsl-head">🚴 CPSL</div><div class="cpsl-body">Caricamento…</div>`);

  // 1) prova bridge CPSL locale
  const bridged = await tryCpslBridge(aid);
  if (bridged) { renderPanel(bridged.indicators, bridged.source); return; }

  // 2) fallback: calcolo lato client dalle API ICU
  const key = await getKey();
  if (!key) {
    renderPanel(null, 'settings');
    const p = document.getElementById(CPSL_BADGE_ID);
    if (p) p.querySelector('.cpsl-body').innerHTML = 'Inserisci la tua Intervals.icu API Key nelle <a href="#" id="cpsl-opt">opzioni</a> dell\'estensione.';
    return;
  }
  try {
    const wellness = await icuGet(`athlete/${aid}/wellness?oldest=2026-01-01&newest=2026-12-31`, key);
    const ind = computeIndicators(wellness);
    renderPanel(ind, 'calcolato da ICU');
  } catch (e) {
    renderPanel(null, 'errore');
    const p = document.getElementById(CPSL_BADGE_ID);
    if (p) p.querySelector('.cpsl-body').textContent = 'Errore ICU: ' + e.message;
  }
}

// Evita doppi binding su SPA navigation
if (!window.__cpslIcuBound) {
  window.__cpslIcuBound = true;
  loadAndRender();
  // Ricarica su cambio route SPA
  let lastUrl = location.href;
  setInterval(() => {
    if (location.href !== lastUrl) { lastUrl = location.href; loadAndRender(); }
  }, 1500);
}

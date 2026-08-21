// CPSL for Intervals.icu — background service worker (MV3)
// Gestisce: auth ICU (API key o OAuth bearer), cache dati, fetch per i content
// script, e il bridge verso CPSL locale.

const ICU_API = 'https://intervals.icu/api/v1';
const CPSL_API = 'http://127.0.0.1:22400';

async function getAuth() {
  return new Promise((resolve) => {
    chrome.storage.local.get(['icuApiKey', 'icuOAuthToken', 'authMode', 'cpslUrl'], (r) =>
      resolve({ key: r.icuApiKey || '', token: r.icuOAuthToken || '', mode: r.authMode || 'apikey',
                cpslUrl: (r.cpslUrl || 'http://127.0.0.1:22400').replace(/\/+$/, '') }));
  });
}

function authHeaders(auth) {
  if (auth.mode === 'oauth' && auth.token) return { Authorization: 'Bearer ' + auth.token };
  if (auth.key) return { Authorization: 'Basic ' + btoa('API_KEY:' + auth.key) };
  return {};
}

// ---- Cache semplice in memoria del SW (con TTL) --------------------------
const _cache = new Map();
const TTL_MS = 5 * 60 * 1000;
function cacheGet(k) {
  const e = _cache.get(k);
  if (e && Date.now() - e.t < TTL_MS) return e.v;
  if (e) _cache.delete(k);
  return undefined;
}
function cacheSet(k, v) { _cache.set(k, { t: Date.now(), v }); }

// ---- Fetch API ICU --------------------------------------------------------
async function icuFetch(path, force = false) {
  const ck = 'icu:' + path;
  if (!force) {
    const c = cacheGet(ck);
    if (c !== undefined) return c;
  }
  const auth = await getAuth();
  const r = await fetch(`${ICU_API}/${path}`, { headers: authHeaders(auth) });
  if (!r.ok) throw new Error('ICU ' + r.status + ': ' + (await r.text()).slice(0, 120));
  const data = await r.json();
  cacheSet(ck, data);
  return data;
}

// ---- Bridge CPSL locale ---------------------------------------------------
async function cpslBridge(path, timeoutMs = 1500) {
  try {
    const auth = await getAuth();
    const r = await fetch(`${auth.cpslUrl}${path}`, { signal: AbortSignal.timeout(timeoutMs) });
    if (!r.ok) return null;
    return await r.json();
  } catch (_) { return null; }
}

// ---- Message router -------------------------------------------------------
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  (async () => {
    try {
      switch (msg.type) {
        case 'GET_WELLNESS': {
          const d = await icuFetch(`athlete/${msg.athleteId}/wellness?oldest=${msg.oldest}&newest=${msg.newest}`, msg.force);
          sendResponse({ ok: true, data: d });
          break;
        }
        case 'GET_ACTIVITY': {
          const d = await icuFetch(`activity/${msg.activityId}?intervals=true`, msg.force);
          sendResponse({ ok: true, data: d });
          break;
        }
        case 'GET_ACTIVITIES': {
          const q = `athlete/${msg.athleteId}/activities?oldest=${msg.oldest}&newest=${msg.newest}` +
                    (msg.limit ? `&limit=${msg.limit}` : '');
          const d = await icuFetch(q, msg.force);
          sendResponse({ ok: true, data: d });
          break;
        }
        case 'GET_EVENTS': {
          const q = `athlete/${msg.athleteId}/events?oldest=${msg.oldest}&newest=${msg.newest}`;
          const d = await icuFetch(q, msg.force);
          sendResponse({ ok: true, data: d });
          break;
        }
        case 'GET_FITNESS': {
          // fitness/metrics se disponibili sull'atleta
          const d = await icuFetch(`athlete/${msg.athleteId}/fitness`, msg.force).catch(() => null);
          sendResponse({ ok: !!d, data: d });
          break;
        }
        case 'CPSL_CONTEXT': {
          const d = await cpslBridge(`/api/icu/extension/context?athlete_id=${msg.athleteId}`);
          sendResponse({ ok: !!(d && d.ok), data: d });
          break;
        }
        case 'AUTH_STATUS': {
          const a = await getAuth();
          sendResponse({ ok: true, hasKey: !!a.key, hasToken: !!a.token, mode: a.mode });
          break;
        }
        case 'OPEN_OPTIONS': {
          chrome.runtime.openOptionsPage();
          sendResponse({ ok: true });
          break;
        }
        default:
          sendResponse({ ok: false, error: 'unknown message type' });
      }
    } catch (e) {
      sendResponse({ ok: false, error: String(e.message || e) });
    }
  })();
  return true; // async response
});

// Keep-alive leggero: refresh cache wellness ogni 15 min quando ICU è aperto
chrome.alarms.create('cpsl-refresh', { periodInMinutes: 15 });
chrome.alarms.onAlarm.addListener(async (a) => {
  if (a.name !== 'cpsl-refresh') return;
  try {
    const tabs = await chrome.tabs.query({ url: 'https://intervals.icu/*' });
    if (tabs.length) {
      chrome.tabs.sendMessage(tabs[0].id, { type: 'REFRESH' }).catch(() => {});
    }
  } catch (_) {}
});

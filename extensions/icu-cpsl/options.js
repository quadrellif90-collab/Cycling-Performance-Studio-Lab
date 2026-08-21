// CPSL extension options — auth mode + keys + local CPSL bridge URL
const $ = (id) => document.getElementById(id);

function refreshMode() {
  const m = $('mode').value;
  $('keywrap').style.display = m === 'apikey' ? '' : 'none';
  $('tokenwrap').style.display = m === 'oauth' ? '' : 'none';
}

$('mode').addEventListener('change', refreshMode);

$('save').addEventListener('click', () => {
  const mode = $('mode').value;
  const key = $('key').value.trim();
  const token = $('token').value.trim();
  let url = $('cpslUrl').value.trim() || 'http://127.0.0.1:22400';
  url = url.replace(/\/+$/, '');
  if (mode === 'apikey' && !key) { $('status').textContent = '✗ Inserisci la API Key.'; return; }
  if (mode === 'oauth' && !token) { $('status').textContent = '✗ Inserisci il token OAuth.'; return; }
  chrome.storage.local.set({ authMode: mode, icuApiKey: key, icuOAuthToken: token, cpslUrl: url }, () => {
    $('status').textContent = '✓ Salvato. Ricarica la pagina intervals.icu.';
  });
});

// Pre-compila
chrome.storage.local.get(['authMode', 'icuApiKey', 'icuOAuthToken', 'cpslUrl'], (r) => {
  $('mode').value = r.authMode || 'apikey';
  if (r.icuApiKey) $('key').value = r.icuApiKey;
  if (r.icuOAuthToken) $('token').value = r.icuOAuthToken;
  if (r.cpslUrl) $('cpslUrl').value = r.cpslUrl;
  refreshMode();
});

// popup.js — stato auth + bridge CPSL
const $ = (id) => document.getElementById(id);

chrome.runtime.sendMessage({ type: 'AUTH_STATUS' }, (r) => {
  const el = $('auth');
  if (r && r.ok && (r.hasKey || r.hasToken)) {
    el.innerHTML = `✓ <span class="ok">Auth configurata</span> (${r.mode})`;
  } else {
    el.innerHTML = `✗ <span class="bad">Nessuna API key/token</span> — apri le Opzioni`;
  }
});

chrome.runtime.sendMessage({ type: 'CPSL_CONTEXT', athleteId: '' }, (r) => {
  const el = $('bridge');
  if (r && r.ok) el.innerHTML = `✓ <span class="ok">CPSL locale attivo</span>`;
  else el.innerHTML = `○ CPSL locale non raggiungibile (l'estensione userà le API ICU)`;
});

$('open-cpsl').addEventListener('click', () => window.open('http://127.0.0.1:22400/', '_blank'));
$('open-options').addEventListener('click', () => chrome.runtime.openOptionsPage());

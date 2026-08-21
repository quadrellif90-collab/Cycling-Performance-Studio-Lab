// options.js — salva la ICU API key in chrome.storage.local
document.getElementById('save').addEventListener('click', () => {
  const key = document.getElementById('key').value.trim();
  chrome.storage.local.set({ icuApiKey: key }, () => {
    document.getElementById('status').textContent = key ? '✓ Salvato.' : 'Key rimossa.';
  });
});
// pre-compila se già presente
chrome.storage.local.get(['icuApiKey'], (r) => {
  if (r.icuApiKey) document.getElementById('key').value = r.icuApiKey;
});

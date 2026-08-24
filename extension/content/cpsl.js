(() => {
  if (window.__CPSL_PANELS__) return;
  window.__CPSL_PANELS__ = true;

  const CPSL_BASE = "http://127.0.0.1:22400";

  async function cpslFetch(path) {
    if (window.__cpslMock && window.__cpslMock[path]) return window.__cpslMock[path];
    if (typeof chrome !== "undefined" && chrome.runtime && chrome.runtime.id) {
      const res = await new Promise(resolve => {
        try { chrome.runtime.sendMessage({ type: "cpsl", path }, r => resolve(r)); }
        catch (e) { resolve({ ok: false, error: String(e) }); }
      });
      if (res && res.ok) return res.data;
      throw new Error(res ? res.error : "no response");
    }
    const r = await fetch(CPSL_BASE + path, { headers: { Accept: "application/json" } });
    if (!r.ok) throw new Error("HTTP " + r.status);
    return await r.json();
  }

  function fmtVal(v) {
    if (v === null || v === undefined || v === "") return "\u2013";
    if (typeof v === "number") return Math.abs(v) >= 1000 ? v.toLocaleString("it-IT") : String(Math.round(v * 100) / 100);
    if (typeof v === "boolean") return v ? "s\u00ec" : "no";
    if (typeof v === "object") return Array.isArray(v) ? `${v.length} elementi` : "oggetto";
    return String(v);
  }

  const KEY_LABELS = {
    readiness_score: "Punteggio prontitudine", score: "Punteggio", state: "Stato",
    recommendation: "Raccomandazione", tired_peak_w: "Picco stanco (W)",
    fresh_peak_w: "Picco fresco (W)", fade_pct: "Calo %", anchor_kj: "Ancora (kJ)",
    source: "Fonte", window_days: "Finestra (giorni)", trend: "Trend",
    eftp_w: "eFTP (W)", w_prime_j: "W\u2032 (J)", cp_w: "CP (W)", p_max_w: "P-max (W)",
    tau_s: "Tau (s)", confidence: "Affidabilit\u00e0", n_points: "N punti",
    mean_ln_rmssd: "ln(RMSSD) medio", sd_ln_rmssd: "ln(RMSSD) SD",
    sleep_score: "Punteggio sonno", hrv_deviation_ln: "Deviazione HRV (ln)",
    ctl: "CTL", tsb: "TSB", atl: "ATL"
  };

  function pickEntries(data) {
    const out = [];
    const flat = (obj, prefix) => {
      for (const [k, v] of Object.entries(obj)) {
        if (v && typeof v === "object" && !Array.isArray(v)) flat(v, prefix ? `${prefix}.${k}` : k);
        else out.push([prefix ? `${prefix}.${k}` : k, v]);
      }
    };
    if (data && typeof data === "object") flat(data, "");
    const seen = new Set();
    return out.filter(([k]) => {
      const leaf = k.split(".").pop();
      if (seen.has(leaf)) return false;
      seen.add(leaf);
      return true;
    }).slice(0, 8);
  }

  function buildPanel(id, title, subtitle) {
    const old = document.getElementById(id);
    if (old) old.remove();
    const el = document.createElement("div");
    el.id = id;
    el.className = "cpsl-panel";
    el.innerHTML = `
      <div class="cpsl-head">
        <span class="cpsl-badge">CPSL+</span>
        <span class="cpsl-title">${title}</span>
        <button class="cpsl-refresh" title="Ricarica">\u21bb</button>
      </div>
      <div class="cpsl-sub">${subtitle}</div>
      <div class="cpsl-body"><div class="cpsl-loading">Connessione al motore locale\u2026</div></div>`;
    el.querySelector(".cpsl-refresh").addEventListener("click", () => loadPanel(el, id));
    return el;
  }

  async function loadPanel(el, id) {
    const body = el.querySelector(".cpsl-body");
    body.innerHTML = `<div class="cpsl-loading">Connessione al motore locale\u2026</div>`;
    try {
      let data;
      if (id === "cpsl-panel-readiness") data = await cpslFetch("/api/readiness/composite");
      else if (id === "cpsl-panel-durability") data = await cpslFetch("/api/durability-trend");
      else if (id === "cpsl-panel-engine") data = null;
      if (!data) {
        body.innerHTML = `
          <div class="cpsl-kv"><span>Motore W\u2032bal</span><b>Skiba 2015 \u2014 \u03c4 variabile</b></div>
          <div class="cpsl-kv"><span>DFA \u03b11</span><b>doppia scala 4\u201316 / 16\u201364</b></div>
          <div class="cpsl-kv"><span>HRV baseline</span><b>ln(RMSSD)</b></div>
          <div class="cpsl-kv"><span>Durability</span><b>ancoraggio chilometri (kJ)</b></div>`;
        return;
      }
      const entries = pickEntries(data);
      body.innerHTML = entries.map(([k, v]) =>
        `<div class="cpsl-kv"><span>${KEY_LABELS[k.split(".").pop()] || k.replace(/[._]/g, " ")}</span><b>${fmtVal(v)}</b></div>`
      ).join("");
    } catch (e) {
      body.innerHTML = `<div class="cpsl-error">Motore locale non raggiungibile (porta 22400). Avvia CyclingPerformanceStudioLab.</div>`;
    }
  }

  const PANELS = [
    { id: "cpsl-panel-readiness", headings: ["READINESS & OPERATIONS", "PRONTITUDINE E OPERAZIONI"], title: "Prontitudine Composita", subtitle: "Modello CPSL multi-fattore (HRV ln, sonno, carico)" },
    { id: "cpsl-panel-durability", headings: ["DURABILITY (ISDM)", "DURABILIT\u00c0 (ISDM)"], title: "Durability \u00b7 ancoraggio kJ", subtitle: "Picco stanco ancorato sul lavoro cumulativo reale" },
    { id: "cpsl-panel-engine", headings: ["TEMPORAL PATTERN (W\u2032 BAL)", "ANDAMENTO TEMPORALE"], title: "Motore fisiologico aggiornato", subtitle: "Versioni CPSL dei calcoli sottostanti" }
  ];

  function findHeadingCard(texts) {
    const hs = [...document.querySelectorAll("h1,h2,h3,h4")];
    for (const text of texts) {
      const up = text.toUpperCase();
      for (const h of hs) {
        if ((h.innerText || "").trim().toUpperCase().startsWith(up)) {
          return h.closest("[class*='card']") || h.parentElement.parentElement || h.parentElement;
        }
      }
    }
    return null;
  }

  function injectAll() {
    for (const p of PANELS) {
      if (document.getElementById(p.id)) continue;
      const card = findHeadingCard(p.headings);
      if (!card || !card.parentElement) continue;
      const panel = buildPanel(p.id, p.title, p.subtitle);
      card.insertAdjacentElement("afterend", panel);
      loadPanel(panel, p.id);
    }
  }

  let t = 0;
  function schedule() {
    clearTimeout(t);
    t = setTimeout(injectAll, 400);
  }

  injectAll();
  new MutationObserver(schedule).observe(document.body, { childList: true, subtree: true });
})();

(() => {
  if (window.__CPSL_PANELS__) return;
  window.__CPSL_PANELS__ = true;

  // Pannelli CPSL+ v2.0 — completamente autonomi: i calcoli girano qui
  // (content/engine.js) sui dati gia presenti nella pagina Montis.
  // Nessuna app locale richiesta.

  const LABELS = {
    hrv_z: "HRV (z)", ln_rmssd_z: "ln(RMSSD) 7g (z)", tsb: "TSB",
    rhr_z: "FC riposo (z, inv)", sleep_z: "Sonno (z)",
    score: "Punteggio prontitudine", status: "Modalit\u00e0",
    confidence: "Confidenza componenti", date: "Giorno",
    hrv: "HRV oggi (ms)", ln_rmssd_7d: "ln(RMSSD) 7g", rhr: "FC riposo oggi",
    sleep: "Punteggio sonno", stability: "Stabilit\u00e0 HRV (14g)",
    ln_dev: "Deviazione ln(RMSSD)", dynamic_weights: "dinamica",
    static_weights: "statica", insufficient_data: "dati insufficienti"
  };

  const STATUS_IT = {
    dynamic_weights: "pesi dinamici",
    static_weights: "pesi statici",
    insufficient_data: "dati insufficienti"
  };

  function fmt(v) {
    if (v === null || v === undefined) return "\u2013";
    if (typeof v === "number") return String(Math.round(v * 100) / 100);
    return String(v);
  }

  function kv(label, value) {
    return `<div class="cpsl-kv"><span>${label}</span><b>${value}</b></div>`;
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
        <button class="cpsl-refresh" title="Ricalcola">\u21bb</button>
      </div>
      <div class="cpsl-sub">${subtitle}</div>
      <div class="cpsl-body"><div class="cpsl-loading">Calcolo locale\u2026</div></div>`;
    el.querySelector(".cpsl-refresh").addEventListener("click", () => loadPanel(el, id));
    return el;
  }

  function loadPanel(el, id) {
    const body = el.querySelector(".cpsl-body");
    const data = window.CPSL_ENGINE && window.CPSL_ENGINE.loadWellnessDaily();
    if (!data || !data.daily || data.daily.length < 15) {
      body.innerHTML = `<div class="cpsl-error">Serie benessere non ancora disponibile. Apri la pagina Panoramica o Benessere di Montis per caricarla, poi torna qui.</div>`;
      return;
    }
    const E = window.CPSL_ENGINE;

    if (id === "cpsl-panel-readiness") {
      const r = E.computeReadiness(data.daily);
      if (r.score === null) {
        body.innerHTML = `<div class="cpsl-error">Dati insufficienti per il punteggio (servono \u226514 giorni di HRV/sonno nella serie).</div>`;
        return;
      }
      body.innerHTML =
        kv(LABELS.score, `<span style="font-size:1.25em">${fmt(r.score)}</span> / 10`) +
        kv(LABELS.status, STATUS_IT[r.status] || r.status) +
        kv("Confidenza", `${Math.round(r.confidence * 100)}%`) +
        kv("Giorno analizzato", r.date || "\u2013") +
        kv(LABELS.hrv_z, fmt(r.components.hrv_z)) +
        kv(LABELS.ln_rmssd_z, fmt(r.components.ln_rmssd_z)) +
        kv(LABELS.tsb, fmt(r.components.tsb)) +
        kv(LABELS.rhr_z, fmt(r.components.rhr_z)) +
        kv(LABELS.sleep_z, fmt(r.components.sleep_z));
      return;
    }

    if (id === "cpsl-panel-durability") {
      const st = E.hrvStability(data.daily, 14);
      const dev = E.lnDeviation(data.daily);
      const ins = data.insights || {};
      const auto = ins.autonomic_status || {};
      body.innerHTML =
        kv(LABELS.ln_dev, fmt(dev)) +
        kv(LABELS.stability, fmt(st)) +
        kv("Stato autonomico (42g)", auto.classification ? `${fmt(auto.value)} \u2014 ${auto.classification}` : "\u2013") +
        kv("Rapporto HRV / media", fmt(auto.value)) +
        kv("Giorni in serie", fmt(data.daily.length)) +
        kv("Aggiornato", fmt((data.generated_at && (data.generated_at.local || data.generated_at)) ? String(data.generated_at.local || data.generated_at).slice(0, 16).replace("T", " ") : "\u2013"));
      return;
    }

    if (id === "cpsl-panel-engine") {
      body.innerHTML =
        kv("Motore", "integrato nell'estensione (JS)") +
        kv("Readiness", "composito CPSL 0\u201310, pesi rinormalizzati") +
        kv("Baseline", "z-score individuali 42\u201360 giorni") +
        kv("Segnale HRV", "ln(RMSSD), deviazione e stabilit\u00e0") +
        kv("Dati", "cache locale Montis \u2014 nessun server");
      return;
    }
  }

  const PANELS = [
    { id: "cpsl-panel-readiness", headings: ["READINESS & OPERATIONS", "PRONTITUDINE E OPERAZIONI"], title: "Prontitudine Composita", subtitle: "Calcolatore CPSL integrato \u2014 0\u201310, pesi rinormalizzati" },
    { id: "cpsl-panel-durability", headings: ["DURABILITY (ISDM)", "DURABILIT\u00c0 (ISDM)"], title: "Segnali autonomici CPSL", subtitle: "ln(RMSSD), stabilit\u00e0 HRV e stato autonomico" },
    { id: "cpsl-panel-engine", headings: ["TEMPORAL PATTERN (W\u2032 BAL)", "ANDAMENTO TEMPORALE"], title: "Motore fisiologico CPSL", subtitle: "Calcoli eseguiti nel browser, zero server" }
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
    if (!window.CPSL_ENGINE) return;
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

(() => {
  if (window.__CPSL_ENGINE__) return;
  window.__CPSL_ENGINE__ = true;

  // Porta JS di readiness_composite.py (CPSL v1.1.0) — punteggio 0-10 bayesiano.
  // Dati: cache locale montis_wellness_dashboard (localStorage, stessa origine).
  // Nessuna app locale richiesta.

  const W = { hrv_z: 0.30, ln_rmssd_z: 0.15, tsb: 0.20, rhr_z: 0.15, sleep_z: 0.20 };
  const MIN_AVAILABLE_WEIGHT = 0.5;

  function safeFloat(x) {
    if (x === null || x === undefined) return null;
    const f = typeof x === "number" ? x : parseFloat(x);
    return Number.isFinite(f) ? f : null;
  }

  function mean(a) { return a.reduce((s, v) => s + v, 0) / a.length; }

  function stdev(a) {
    const m = mean(a);
    const v = a.reduce((s, x) => s + (x - m) * (x - m), 0) / (a.length - 1);
    return Math.sqrt(v);
  }

  function zscore(value, series) {
    if (value === null || value === undefined) return null;
    const vals = series.filter(v => Number.isFinite(v));
    if (vals.length < 14) return null;
    const sd = stdev(vals);
    if (!(sd > 1e-9)) return null;
    const z = (value - mean(vals)) / sd;
    return Math.max(-3, Math.min(3, z));
  }

  function lnRmssd7d(rows, idx) {
    // media mobile 7 giorni di ln(hrv) che termina all'indice idx (incluso);
    // richiede >= 4 campioni validi come l'originale Python.
    const samples = [];
    for (let i = idx; i >= 0 && i > idx - 7; i--) {
      const h = safeFloat(rows[i] && rows[i].hrv);
      if (h !== null && h > 0) samples.push(Math.log(h));
    }
    if (samples.length < 4) return null;
    return mean(samples);
  }

  function componentScore(key, v) {
    if (key === "hrv_z" || key === "ln_rmssd_z" || key === "rhr_z" || key === "sleep_z")
      return Math.max(0, Math.min(10, 5 + 2 * v));
    if (key === "tsb") return Math.max(0, Math.min(10, 5.5 + 0.15 * v));
    return null;
  }

  // rhr_z invertito: FC riposo ALTA = male -> z invertito di segno
  function computeReadiness(daily) {
    const rows = (daily || []).slice().sort((a, b) =>
      String(a.date).localeCompare(String(b.date)));
    if (rows.length < 15) return { status: "insufficient_data", score: null, confidence: 0 };

    // target = giorno piu' recente CHE ABBIA HRV (i dati wellness arrivano
    // spesso con un giorno di ritardo rispetto a CTL/ATL/sonno)
    let ti = rows.length - 1;
    while (ti > 0 && !(safeFloat(rows[ti].hrv) > 0)) ti--;
    const today = rows[ti];
    const hist = rows.slice(0, ti);

    const hrvSeries = hist.map(r => safeFloat(r.hrv)).filter(v => v !== null && v > 0);
    const rhrSeries = hist.map(r => safeFloat(r.rest_hr)).filter(v => v !== null);
    const ln7Series = [];
    for (let i = 0; i < hist.length; i++) {
      const v = lnRmssd7d(rows, i);
      if (v !== null) ln7Series.push(v);
    }
    const sleepSeries = hist.map(r => safeFloat(r.sleepscore)).filter(v => v !== null);

    const rawHrv = safeFloat(today.hrv);
    const rawLn7 = lnRmssd7d(rows, rows.length - 1);
    const rawRhr = safeFloat(today.rest_hr);
    const rawSleep = safeFloat(today.sleepscore);
    const rawCtl = safeFloat(today.ctl);
    const rawAtl = safeFloat(today.atl);
    const tsb = (rawCtl !== null && rawAtl !== null) ? rawCtl - rawAtl : null;

    const comps = {
      hrv_z: zscore(rawHrv, hrvSeries),
      ln_rmssd_z: zscore(rawLn7, ln7Series),
      tsb: tsb,
      rhr_z: (() => { const z = zscore(rawRhr, rhrSeries); return z === null ? null : -z; })(),
      sleep_z: zscore(rawSleep, sleepSeries)
    };

    const available = Object.keys(W).filter(k => comps[k] !== null && comps[k] !== undefined);
    const totalW = available.reduce((s, k) => s + W[k], 0);
    if (totalW < MIN_AVAILABLE_WEIGHT)
      return { status: "insufficient_data", score: null, confidence: Math.round(totalW * 1000) / 1000, components: comps };

    let score = 0;
    const contribs = {};
    for (const k of available) {
      const c = componentScore(k, comps[k]);
      contribs[k] = Math.round(c * 100) / 100;
      score += (W[k] / totalW) * c;
    }
    return {
      status: available.length >= 5 ? "dynamic_weights" : "static_weights",
      score: Math.round(score * 100) / 100,
      confidence: Math.round(totalW * 1000) / 1000,
      components: comps,
      contribs,
      raw: { hrv: rawHrv, ln_rmssd_7d: rawLn7, rhr: rawRhr, sleep: rawSleep, tsb },
      date: String(today.date || "").slice(0, 10)
    };
  }

  // Indice di stabilità HRV (1 - std/mean, finestra 14g) — come insights Montis/CPSL
  function hrvStability(daily, window) {
    const vals = (daily || []).slice(-window)
      .map(r => safeFloat(r.hrv)).filter(v => v !== null && v > 0);
    if (vals.length < 10) return null;
    const m = mean(vals);
    if (!(m > 0)) return null;
    return Math.round((1 - stdev(vals) / m) * 1000) / 1000;
  }

  // Deviazione ln(RMSSD): ln(ultimo valore) - media ln(storico) — segnale CPSL hrv_deviation_ln
  function lnDeviation(daily) {
    const rows = (daily || []).slice().sort((a, b) => String(a.date).localeCompare(String(b.date)));
    if (rows.length < 15) return null;
    let li = rows.length - 1;
    while (li > 0 && !(safeFloat(rows[li].hrv) > 0)) li--;
    const last = safeFloat(rows[li].hrv);
    if (last === null || last <= 0) return null;
    const hist = rows.slice(0, li).map(r => safeFloat(r.hrv)).filter(v => v !== null && v > 0).map(Math.log);
    if (hist.length < 14) return null;
    return Math.round((Math.log(last) - mean(hist)) * 1000) / 1000;
  }

  function loadWellnessDaily() {
    try {
      const wd = localStorage.getItem("montis_wellness_dashboard");
      if (!wd) return null;
      const outer = JSON.parse(wd);
      const txt = outer && outer.data && outer.data.content && outer.data.content[0] && outer.data.content[0].text;
      if (!txt) return null;
      const inner = JSON.parse(txt);
      const w = inner.semantic_graph && inner.semantic_graph.wellness;
      if (!w || !Array.isArray(w.daily)) return null;
      const gen = inner.semantic_graph.meta && inner.semantic_graph.meta.generated_at;
      return { daily: w.daily, generated_at: gen, wellness: w, insights: inner.semantic_graph.insights || {} };
    } catch (e) {
      return null;
    }
  }

  window.CPSL_ENGINE = { computeReadiness, hrvStability, lnDeviation, loadWellnessDaily, W };
})();

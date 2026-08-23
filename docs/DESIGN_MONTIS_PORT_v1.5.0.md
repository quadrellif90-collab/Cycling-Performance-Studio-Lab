# DESIGN — Port Montis.icu → CPSL (roadmap v1.5.0)

> Documento di design — **non implementativo**. Analisi comparativa del motore
> Montis di Clive King (`revo2wheels/intervalsicugptcoach-public`, MIT) e piano
> di integrazione dei 4 moduli ad alto valore in Cycling Performance Studio Lab.

---

## 0. Executive summary

Montis e CPSL condividono la stessa filosofia ("il motore deterministico decide,
l'AI spiega") ma architetture opposte: Montis è un worker cloud (Railway +
Cloudflare Edge) che consuma dataset Intervals.icu; CPSL è un'app desktop locale
(FastAPI + SQLite + parser FIT) con sync ICU opzionale. **Un fork integrale non
ha senso**; il valore sta nel portare 4 moduli analitici che CPSL non ha, tutti
realizzabili con i dati già in nostro possesso.

| # | Modulo | Sforzo | Impatto | Dati necessari |
|---|--------|--------|---------|----------------|
| 1 | ESPE — progressione power curve | Medio | Alto | best efforts 1m/5m/20m/60m per finestra (già calcolati) |
| 2 | Repeatabilità anaerobica W′bal | Basso | Alto | `icu_w_prime`, `icu_max_wbal_depletion` dal sync ICU |
| 3 | Durability-trend ISDM (decoupling) | Basso | Medio | `decoupling_pct` già presente per ride |
| 4 | Governance ADE (decisioni spiegabili) | Medio | Alto | stato già computato da adaptive_planner |

Licenza: **MIT** → port legale anche per uso commerciale. Obblighi: conservare
il copyright notice di Clive King nei file derivati + file NOTICE/CREDITS.
**Escluso**: brand "Montis", loghi, infrastruttura hosted (NOTICE.txt upstream).

---

## 1. ESPE — Energy System Progression Engine

### 1.1 Cosa fa Montis (`audit_core/tier3_espe.py`, v1.21)
- Confronta **due finestre rotanti uguali** della power curve (default 84–90d,
  ancorate alla data report): current vs previous.
- Anchor points: **5s / 1m / 5m / 20m / 60m**.
- Delta percentuali per anchor; classificazione per sistema energetico:
  - `anaerobic` ← ΔP1m · `vo2` ← ΔP5m · `threshold` ← ΔP20m · `aerobic_durability` ← ΔP60m
- Bande Ride (da `coaching_cheat_sheet.py:452`, ±%):
  - anaerobic/vo2: strong ≥3.0, moderate ≥1.5, mild ≥0.8, decline ≤−1.5
  - threshold: strong ≥2.0, moderate ≥1.0, mild ≥0.5, decline ≤−1.0
  - aerobic: strong ≥1.5, moderate ≥0.7, mild ≥0.4, decline ≤−1.0
  - banda neutra comune: |Δ| < 0.75 → "stable"
- Metriche derivate:
  - `glycolytic_bias = P1m / P20m` (ideale ≈ 1.8)
  - `aerobic_durability = P60m / P5m`, `durability_gradient = P60m / P20m`
  - `balance_score` dalla distanza del bias dall'ideale
  - `plateau`: true se tutte le ancore valide hanno |Δ| < 1.0% (Run: Δ20m < 0.5)
  - profilo curva da slope log-log: time_trialist −0.48 … anaerobic_specialist −0.85
  - `vo2_reserve_ratio = P5m / CP`
- Output: timeline per sistema, `adaptation_bias`, `adaptation_state`.

### 1.2 Cosa ha CPSL oggi
- `fitness_estimation.extract_best_efforts()` → best mean power a 5s/30s/1m/5m/
  8m/20m/30m/60m **per ride** (sliding window 1Hz).
- `power_duration_model.fit_power_duration()` → fit 3-param CP/W′/Pmax/TTE.
- `breakthrough_detector.py` → eventi singoli, nessuna vista longitudinale.
- **Manca**: aggregazione best-effort per finestra temporale e confronto
  finestra-vs-finestra.

### 1.3 Design CPSL — nuovo modulo `espe.py`
```
compute_espe(rides, window_days=84, today=None) -> EspeResult
```
1. Per ogni ride con power stream: best efforts (riuso `extract_best_efforts`).
2. Aggregazione max-per-finestra: `window_best[dur] = max(ride_best)` per le
   ride in `[today−window, today]` e idem finestra precedente.
3. Delta % per 1m/5m/20m/60m (5s escluso: troppo rumoroso indoor/outdoor).
4. Classificazione bande Ride (tabella sopra, costanti locali — nessuna
   dipendenza dal cheat_sheet upstream).
5. Derivate: glycolytic_bias, durability_gradient, balance_score (ideale 1.8),
   plateau detection, vo2_reserve_ratio (P5m/CP dal PD model corrente).
6. Profilo curva: slope regressione log-log sui punti della finestra corrente →
   mappa ai 6 fenotipi Ride (stessa tabella slope di Montis).
7. Persistenza snapshot per profilo (`~cpsl/profiles/<id>/espe_history.json`)
   per disegnare l'evoluzione nella UI.

Esposizione:
- API: `GET /api/espe?window=84`
- UI: nuova card "Progressione sistemi energetici" in Analysis (barre delta
  per sistema + badge plateau/profilo curva), layout-aware come le altre card.
- AI Coach: `weekly_analysis` include `espe.summary` nel prompt.

Adattamenti vs Montis: niente FFT_CURVES ICU (usiamo il nostro PD model);
solo Ride in v1.

---

## 2. Repeatabilità anaerobica via W′bal

### 2.1 Cosa fa Montis (`tier3_performance_intelligence.py:192`)
Statistiche 7 giorni sulla depletazione W′bal per sessione:
- `max_depletion_pct_7d`, `mean_depletion_pct_7d`
- `moderate_depletion_sessions_7d` (>50%), `high_depletion_sessions_7d` (>60%)
- `total_joules_above_ftp_7d`
- `w_prime_divergence_7d` = mean_depletion − 0.30 (baseline attesa endurance)

### 2.2 Dati CPSL
- `ride_storage.py:268` importa già `icu_joules_above_ftp`.
- **Mancano** `icu_w_prime` e `icu_max_wbal_depletion` nella mappatura → da
  aggiungere ai `_pick(...)` (campi standard delle activity Intervals.icu).
- Fallback senza sync ICU: stima dai nostri CP/W′ del PD model
  (joule > FTP / W′) — accuratezza minore, flag `source: estimated`.

### 2.3 Design CPSL — funzione in `advanced_metrics.py`
```
anaerobic_repeatability(rides, days=7) -> dict   # stesse chiavi di Montis + source
```
- API: incluso in `/api/week-summary` o endpoint `/api/repeatability`.
- UI: riga aggiuntiva nella card Analysis ("W′bal 7g: media X% · N sessioni alte").
- AI Coach: segnale per modulare le sessioni VO2/anaerobiche della settimana dopo.

Nota fisiologica: la baseline 0.30 è un'euristica proprietaria Montis (non
letteratura) → configurabile in `config.py`, default 0.30, citazione esplicita.

---

## 3. Durability-trend ISDM (decoupling firmato)

### 3.1 Cosa fa Montis (`tier3_performance_intelligence.py:148`)
Classifica il trend di durability settimanale dal decoupling aerobico **firmato**,
con requisito di ripetizione dell'evidenza (niente allarmi da una singola
sessione rumorosa):
- mean_signed > 10 → `drifting`
- mean_signed > 5 E ≥2 sessioni >5% su ≥3 valide → `drifting`
- mean_signed < −5 (≥2 valide) → `improving`
- mean_signed < 0 → `stable_improving`; altrimenti `stable`

### 3.2 Cosa ha CPSL
- `decoupling_pct` per ride già calcolato: gate HRVT (app.py ~3007) e filtro
  aggregati (~3126). Nessuna classificazione di trend.
- Il nostro `durability_score.py` misura il **livello assoluto** (ratio
  fresh/tired su ride ≥2h); ISDM misura il **trend**. Complementari.

### 3.3 Design CPSL
Funzione `durability_trend(rides, days=7)` in `durability_score.py`, stesse
soglie come costanti locali. Output:
`{state, mean_signed, high_drift_sessions, long_sessions}`.
UI: badge accanto allo score esistente ("trend: improving/drifting").
Zero nuovi dati → implementabile subito.

---

## 4. Governance ADE — decisioni adattive spiegabili

### 4.1 Cosa fa Montis (`tier3_adaptive_decision_engine.py`, v2.21)
Parte da un punteggio 100 e applica penalità/supporti espliciti con motivazioni:
- operational_state recovery_priority −30 / load_accepting +supporto
- risk_flag high −30, moderate −15, normal +supporto
- forecast fatigue red −25, amber −12, green +supporto
- load trend increasing penalizzato se in contrasto con stato/taper/rischio
- HRV ratio < 0.90 −8; ≥ 1.00 supporto
- taper governance: se TSB evento già nel target range e carico cresce −8;
  "too_fresh" → supporta sharpening controllato

Output strutturato (`decision`): directive, operational_state,
adaptation_focus, risk_flag, forecast_context, load_trend, nutrition_status +
note, target_event {days_to_event, taper_state, event_demand, event_tsb,
target_tsb_range, form_status}, version. Ogni voce ha driver/penalties con
reason testuale → il coach umano (e l'LLM) vede il "perché".

### 4.2 Cosa ha CPSL
`adaptive_planner.generate_adaptive_recommendation()` produce già
AdaptiveRecommendation (weekly_load, readiness_adjustment, phase_adjustment,
confidence, reasoning[]) — ma i reasoning sono stringhe generiche, non un
punteggio trasparente con penalità itemizzate. L'AI Coach consuma l'output ma
non c'è un contratto decisionale governato.

### 4.3 Design CPSL — nuovo modulo `ai_coach/decision_engine.py`
```
compute_ade(context) -> AdeDecision
```
- Input: readiness composite (già pesata dinamicamente), TSB, ramp rate CTL,
  monotony/strain, fase piano, eventi calendario (A/B), HRV ratio, ESPE/W'bal.
- Punteggio 100 con tabelle penalità/supporto ispirate ad ADE v2.21
  (valori ricalibrati sulle nostre soglie readiness, non copiati alla cieca).
- Output dataclass con `directive` (train_through / maintain / reduce /
  recovery_day / off), `drivers[]`, `penalties[]`, `confidence`,
  `event_context{}` — serializzabile in `/api/coach/decision`.
- UI: card "Decisione del giorno" con lista motivazioni (✓/−) — pienamente in
  linea col principio CPSL "il motore decide, l'AI spiega".
- LLM downstream: prompt builder riceve il governed state, non raw metrics.

---

## 5. Roadmap implementativa proposta

| Fase | Contenuto | Dipendenze |
|------|-----------|------------|
| F1 | §3 durability trend + §2 repeatabilità W′bal (con fallback estimated) | nessuna |
| F2 | ride_storage: campi `icu_w_prime`/`icu_max_wbal_depletion` + test | F1 |
| F3 | §1 ESPE completo (modulo + API + card UI + history) | best efforts per ride |
| F4 | §4 ADE governance + integrazione AI Coach | F1–F3 (segnali) |
| F5 | crediti NOTICE, changelog, QA suite estesa, release v1.5.0 | tutte |

Stima: F1+F2 una sessione, F3 una sessione, F4 una sessione, F5 mezza.

## 6. Cosa NON portiamo (e perché)
- Tier-0/1/2 (integrity audit ICU): CPSL ha già validazione locale dei FIT e
  sync ICU con own-data authority; duplicherebbe logica cloud-specifica.
- Cloudflare Edge / OAuth worker: infrastruttura privata upstream, non inclusa
  nel pacchetto MIT.
- ChatGPT Actions / MCP service: CPSL è desktop-first; valutare MCP server
  locale in futuro (v1.6+).
- Multi-sport ESPE: CPSL è cycling-first.

## 7. Conformità licenza MIT
- File nuovi ispirati a Montis: header comment con
  `Concepts adapted from intervalsicugptcoach-public © 2026 Clive King (MIT)`.
- `NOTICE` alla radice con la stessa attribuzione.
- Nessun uso del nome/logo "Montis" nella UI o nei materiali CPSL.

## Riferimenti
- Repo upstream: https://github.com/revo2wheels/intervalsicugptcoach-public
- Copia locale di riferimento: `montis_ref/` (gitignored, non distribuita)
- Sito: https://www.montis.icu · Science: https://www.montis.icu/science.html

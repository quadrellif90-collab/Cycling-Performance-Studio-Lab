# Aggiornamenti Scientifici 2024-2026 — Sintesi e Implementazione CPSL

> Documento di sintesi: ultime evidenze validate e sperimentazioni in corso nei domini
> coperti da CPSL (endurance, nutrizione, recupero, forza, calore), con mappatura
> delle implementazioni introdotte in v1.4.0.

---

## 1. Nutrizione — La "Fueling Revolution"

### Evidenze
- Le linee guida 2016 (30–90 g/h CHO) sono superate: la letteratura recente e i report
  degli atleti d'élite supportano **90–120 g/h** con miscele multi-trasportatore
  (glucosio + fruttosio + galattosio) — *From Metabolism to Medals, J. Nutrition 2026*.
- Il tetto pratico classico di 90 g/h deriva dalla saturazione di SGLT1 (~1,0-1,1 g/min);
  l'aggiunta di fruttosio (GLUT5) porta l'ossidazione a ~1,75 g/min.
- **Gut training**: protocolli progressivi di 4–8 settimane (+10–15 g/h ogni 2 settimane)
  aumentano la TOLLERANZA (non l'assorbimento netto — Costa 2017). Il gut training non
  aumenta i trasportatori in modo dimostrato: serve a evitare distress GI.
- **Recupero**: rapporto 3:1 carboidrati:proteine entro 30–60 min per sessioni >60 min.
- La periodizzazione dei carboidrati (train-low) NON migliora la performance in sé
  (meta-analisi 2017, SMD 0.17 [−0.15, 0.49]) ma può migliorare economia/flessibilità
  metabolica; va mai applicata alle sessioni quality.

### Tabella di riferimento per durata sessione (implementata in CPSL)
| Durata | CHO/h | Note |
|--------|-------|------|
| <45 min | 0 | Solo acqua |
| 45–75 min | 0–30 (mouth rinse su effort hard) | |
| 75–150 min | 30–60 | Glucosio/maltodestrina |
| 150–240 min | 60–90 | Mix 2:1 glucosio:fruttosio |
| >240 min / ultra | 90–120 | Multi-trasportatore, richiede gut training |

### Implementazione CPSL (v1.4.0)
- Modulo `fueling.py`: piano di rifornimento per sessione (pre/durante/post) basato su
  durata, intensità e peso; tracker di progressione gut-training; endpoint
  `GET /api/fueling/session` + card nel tab Alimentazione.

---

## 2. Durability / Fatigue Resistance

### Evidenze
- La durability (delta CP fresh→fatigued) discrimina meglio WorldTour vs ProTeam dei
  numeri a fresco (Muriel 2022; Spragg 2023 MSSE).
- Metodi di allenamento validati:
  1. **Negative split ride** — ultimi 30–60 min a Z3
  2. **Late-stage hill reps** @~FTP a fatica accumulata
  3. **Pre-fatiguing intervals** — intervalli all'inizio di uscita lunga Z2
     (attende 15–30 min post-intervalli per le condizioni ottimali di ossidazione grassi)
  4. **Muscular endurance intervals** — Z3 continuativo (resistenza al danno muscolare)
- Blocco mirato di 8–12 settimane produce miglioramenti misurabili.

### Implementazione CPSL (v1.4.0)
- 4 template workout firma aggiunti alla libreria (`durability_*`), generati come .zwo
  standard e selezionabili dal planner/library.

---

## 3. HRV — Oltre la baseline

### Evidenze
- Media mobile 7 giorni > valore giornaliero (rumore vs trend).
- **Coefficiente di variazione (CV)**: un CV crescente con baseline in calo è l'allarme
  precoce più sensibile di affaticamento accumulato (review 2025, Scientific Reports).
- **Paradosso del sovrallenato**: HRV paradossalmente ALTA può indicare rinuncia
  adattativa / saturazione parasimpatica (Plews) → deviazioni in ENTRAMBE le direzioni
  contano.
- L'allenamento guidato da HRV (algoritmo Kiviniemi) mostra guadagni consistenti vs
  piani fissi; meta-analisi di 10 studi conferma miglioramento HRV stesso.

### Implementazione CPSL (v1.4.0)
- Nuovo renderer `render_hrv_cv_alert` in notifications.py: confronta CV ultimi 7 gg vs
  28 gg precedenti + direzione della baseline; alert bidirezionale. Integrato nel digest.

---

## 4. Distribuzione dell'intensità — il caveat élite

### Evidenze
- Meta-analisi Rosenblat 2019: polarizzato > threshold su TT in atleti trained.
- **Scoping review Rivera-Köfler 2025 (JSCR)**: il vantaggio polarizzato emerge in
  élite/world-class; negli atleti di livello inferiore i modelli NON si separano —
  soglia/piramidale possono essere uguali o superiori (più tempo tollerabile, aderenza).

### Implementazione CPSL (v1.4.0)
- `adaptive_planner.generate_adaptive_recommendation` accetta ora `athlete_level`
  ('amateur'|'trained'|'elite'): per amatori suggerisce pyramidal/threshold come default
  equipollente, riservando polarized a trained/elite o preferenza esplicita.

---

## 5. Heat Training

### Evidenze
- Acclimatazione al calore: VO2max +5–8% e TT +6–8% anche in condizioni temperate
  (meta-analisi Springer 2021; BMC 2024 passive heat exposure).
- Protocollo pratico 10 giorni (60 min/day a 35–40°C o sauna post-allenamento),
  mantenimento con 1–2 esposizioni/settimana; decadimento in 2–3 settimane.

### Implementazione CPSL (v1.4.0)
- Il countdown gara nel digest suggerisce il protocollo heat quando l'evento è entro
  30 giorni e flag `event_hot_climate` impostato nel goal.

---

## 6. Forza concorrente (concurrent training)

### Evidenze
- Interferenza AMPK/mTOR reale ma gestibile: separazione ≥6h tra sessioni;
  **forza prima di endurance** se stessa giornata; corsa interferisce più del ciclismo.
- Dosaggio per fase: off-season 3×/settimana (8–12 sett), transizione 2×, stagione 1×
  mantenimento. Proteine 30–40 g entro 30 min dalla forza; 1,2 g/kg CHO tra doppie.

### Riferimento
- Guida operativa integrata in `docs/SCIENCE_UPDATES_2025.md` (questo documento) e
  applicata ai suggerimenti di strength_mobility nelle note del piano.

---

## Bibliografia essenziale
- Skiba & Clarke (2021). The W′ Balance: Mathematical and Methodological Considerations. IJSPP 16(11).
- Muriel et al. (2022). Durability and repeatability of professional cyclists during a Grand Tour. EJSS.
- Spragg, Leo & Swart (2023). Delta CP fresh vs fatigued in young professional cyclists. MSSE.
- Rivera-Köfler et al. (2025). Polarized vs other TID models — scoping review. JSCR 39(3).
- Rosenblat et al. (2019). Polarized vs threshold meta-analysis. JSCR 33(12).
- Costa et al. (2017). Gut-training repetitive gut-challenge. APNM.
- Jeukendrup (2014). A step towards personalized sports nutrition. Sports Med.
- From Metabolism to Medals (2026). J. Nutrition — contemporary CHO guidelines review.
- Plews et al. — HRV in elite triathletes (parasympathetic saturation).
- Helgerud et al. (2007). Norwegian 4×4. MSSE 39(4).

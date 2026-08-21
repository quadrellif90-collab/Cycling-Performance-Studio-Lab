// Cycling Performance Studio Lab — Dashboard layout personalizzabile (v1.4.1)
//
// Funzioni:
//   1. Click-to-navigate: le card informative di Home rimandano al tab di
//      competenza (data-nav), fuori da edit mode e solo su aree non interattive.
//   2. Edit mode ("✏️ Personalizza"): card della griglia #home-grid
//      trascinabili (riordino live = auto-sistemazione) e ridimensionabili
//      (span 1-12 colonne con snap = auto-aggancio alla griglia).
//   3. Persistenza per profilo in localStorage; ripristino layout default.
//
// Zero dipendenze: HTML5 DnD + Pointer Events + CSS Grid.

(function () {
  'use strict';

  const GRID_ID = 'home-grid';
  const LS_KEY_BASE = 'homeLayout';
  const MAX_COLS_DESKTOP = 12;

  // Default: ordine DOM iniziale + span (12-col base)
  let DEFAULT_ORDER = [];
  const DEFAULT_SPANS = {
    'readiness-factors-card': 6,
    'training-load-card': 6,
    'sleep-hrv-card': 4,
    'eftp-progress-card': 4,
    'body-perf-card-wrap': 4,
  };

  // Click-to-navigate: card informative -> tab di competenza.
  // La sparkline ha già onclick inline proprio (esclusa dal guard).
  const NAV_MAP = {
    'today-card': 'plan',
    'card-hrv': 'hrv',
    'my-cal-card': 'plan',
    'strength-card': 'plan',
    'daily-adapt-card': 'plan',
    'tid-heatmap-card': 'analysis',
    'last-week-feedback-card': 'plan',
  };

  function lsKey() {
    try { return (typeof _profileLsKey === 'function') ? _profileLsKey(LS_KEY_BASE) : LS_KEY_BASE; }
    catch (_) { return LS_KEY_BASE; }
  }
  function lsGet(k) { try { return localStorage.getItem(k); } catch (_) { return null; } }
  function lsSet(k, v) { try { localStorage.setItem(k, v); } catch (_) {} }
  function lsDel(k) { try { localStorage.removeItem(k); } catch (_) {} }

  function maxCols() {
    const w = window.innerWidth;
    if (w <= 760) return 1;
    if (w <= 1100) return 6;
    return MAX_COLS_DESKTOP;
  }

  function clampSpan(n) {
    n = Math.max(1, Math.min(maxCols(), Math.round(n || 1)));
    return n;
  }

  function applySpan(card, n) {
    if (!card) return;
    card.dataset.span = String(clampSpan(n));
    card.style.gridColumn = 'span ' + clampSpan(n);
  }

  // ── Persistenza ────────────────────────────────────────────────────────
  function saveLayout(grid) {
    const order = Array.from(grid.children)
      .filter(c => c.classList.contains('card') && c.id)
      .map(c => c.id);
    const spans = {};
    order.forEach(id => {
      const el = document.getElementById(id);
      spans[id] = parseInt(el && el.dataset.span, 10) || DEFAULT_SPANS[id] || 6;
    });
    lsSet(lsKey(), JSON.stringify({ order, spans }));
  }

  function loadLayout(grid) {
    let data = null;
    try { data = JSON.parse(lsGet(lsKey()) || 'null'); } catch (_) { data = null; }
    if (!data || !Array.isArray(data.order)) return;

    // Riordina i nodi presenti secondo l'ordine salvato
    const byId = {};
    Array.from(grid.children).forEach(c => { if (c.id) byId[c.id] = c; });
    data.order.forEach(id => {
      const el = byId[id];
      if (el) grid.appendChild(el);   // append riordina (sposta il nodo)
    });

    // Applica gli span salvati (clampati al viewport corrente)
    const spans = data.spans || {};
    Object.keys(spans).forEach(id => applySpan(document.getElementById(id), spans[id]));
  }

  function resetLayout(grid) {
    lsDel(lsKey());
    DEFAULT_ORDER.forEach(id => {
      const el = document.getElementById(id);
      if (el) grid.appendChild(el);
    });
    Object.keys(DEFAULT_SPANS).forEach(id => applySpan(document.getElementById(id), DEFAULT_SPANS[id]));
  }

  // ── Toolbar ────────────────────────────────────────────────────────────
  function buildToolbar(section) {
    const bar = document.createElement('div');
    bar.id = 'layout-toolbar';
    bar.style.cssText = 'display:flex;align-items:center;gap:8px;margin-bottom:10px;flex-wrap:wrap;';
    bar.innerHTML =
      '<button id="btn-layout-edit" class="btn btn-sm" style="font-size:11px;" title="Riordina e ridimensiona le card della griglia sottostante">✏️ Personalizza layout</button>' +
      '<button id="btn-layout-reset" class="btn btn-sm" style="font-size:11px;display:none;" title="Torna all\'ordine e alle dimensioni originali">↺ Ripristina</button>' +
      '<span id="layout-edit-hint" style="display:none;font-size:11px;color:var(--text3);">' +
      'Trascina le card per riordinarle · trascina l\'angolo ⌟ per ridimensionarle · snap automatico alla griglia</span>';
    section.insertBefore(bar, section.firstChild);

    document.getElementById('btn-layout-edit').addEventListener('click', toggleEdit);
    document.getElementById('btn-layout-reset').addEventListener('click', () => {
      resetLayout(document.getElementById(GRID_ID));
      showToastSafe('Layout ripristinato', 'success');
    });
  }

  function showToastSafe(msg, kind) {
    try { if (typeof showToast === 'function') showToast(msg, 3000, kind === 'error' ? 'error' : null); } catch (_) {}
  }

  function setEditHint(on) {
    const hint = document.getElementById('layout-edit-hint');
    const btnReset = document.getElementById('btn-layout-reset');
    const btnEdit = document.getElementById('btn-layout-edit');
    if (hint) hint.style.display = on ? 'inline' : 'none';
    if (btnReset) btnReset.style.display = on ? 'inline-flex' : 'none';
    if (btnEdit) btnEdit.textContent = on ? '✓ Fatto' : '✏️ Personalizza layout';
  }

  function toggleEdit() {
    const on = !document.body.classList.contains('layout-edit');
    document.body.classList.toggle('layout-edit', on);
    setEditHint(on);
    if (!on) {
      const grid = document.getElementById(GRID_ID);
      if (grid) saveLayout(grid);
    }
  }

  // ── Drag & drop (riordino live dentro la griglia) ──────────────────────
  function enableDrag(grid) {
    let dragged = null;

    grid.querySelectorAll(':scope > .card').forEach(card => {
      card.draggable = true;

      card.addEventListener('dragstart', e => {
        if (!document.body.classList.contains('layout-edit')) { e.preventDefault(); return; }
        dragged = card;
        card.classList.add('dl-dragging');
        try {
          e.dataTransfer.effectAllowed = 'move';
          e.dataTransfer.setData('text/plain', card.id);
        } catch (_) {}
      });

      card.addEventListener('dragend', () => {
        card.classList.remove('dl-dragging');
        dragged = null;
        saveLayout(grid);
      });
    });

    grid.addEventListener('dragover', e => {
      if (!document.body.classList.contains('layout-edit') || !dragged) return;
      e.preventDefault();
      e.dataTransfer.dropEffect = 'move';
      const after = insertionPoint(grid, e.clientX, e.clientY);
      if (after == null) grid.appendChild(dragged);
      else if (after !== dragged) grid.insertBefore(dragged, after);
    });

    grid.addEventListener('drop', e => {
      if (!document.body.classList.contains('layout-edit')) return;
      e.preventDefault();
      saveLayout(grid);
    });
  }

  // Card dopo cui inserire: prima card il cui centro sta "dopo" il puntatore
  // (confronto per riga poi colonna — griglia a 12 colonne).
  function insertionPoint(grid, x, y) {
    const cards = Array.from(grid.children).filter(c => c !== dragged);
    for (const c of cards) {
      const r = c.getBoundingClientRect();
      const rowMidY = r.top + r.height / 2;
      const afterRow = y > rowMidY;
      const sameRow = y >= r.top && y <= r.bottom;
      const midX = r.left + r.width / 2;
      if ((sameRow && x > midX) || (!sameRow && afterRow)) return c;
    }
    return null;
  }

  // ── Resize con snap alla griglia ───────────────────────────────────────
  function enableResize(grid) {
    grid.querySelectorAll(':scope > .card').forEach(card => {
      const h = document.createElement('div');
      h.className = 'dl-resize-handle';
      h.title = 'Trascina per ridimensionare (snap alla griglia)';
      card.appendChild(h);

      h.addEventListener('pointerdown', e => {
        if (!document.body.classList.contains('layout-edit')) return;
        e.preventDefault();
        e.stopPropagation();
        h.setPointerCapture(e.pointerId);

        const tracks = getComputedStyle(grid).gridTemplateColumns.split(' ')
          .map(v => parseFloat(v)).filter(Boolean);
        const gap = parseFloat(getComputedStyle(grid).columnGap) || 0;
        const trackW = tracks[0] || 0;
        const unit = trackW + gap;
        const left0 = card.getBoundingClientRect().left;

        function onMove(ev) {
          const desired = ev.clientX - left0;
          const n = clampSpan(Math.round((desired + gap / 2) / unit));
          if (String(n) !== card.dataset.span) applySpan(card, n);
        }
        function onUp() {
          h.removeEventListener('pointermove', onMove);
          h.removeEventListener('pointerup', onUp);
          saveLayout(grid);
        }
        h.addEventListener('pointermove', onMove);
        h.addEventListener('pointerup', onUp);
      });
    });

    // Ricalcola gli span clampati al resize della finestra
    window.addEventListener('resize', () => {
      grid.querySelectorAll(':scope > .card').forEach(c => {
        applySpan(c, parseInt(c.dataset.span, 10) || 2);
      });
    });
  }

  // ── Click-to-navigate ─────────────────────────────────────────────────
  function enableNav() {
    Object.keys(NAV_MAP).forEach(id => {
      const el = document.getElementById(id);
      if (el) el.setAttribute('data-nav', NAV_MAP[id]);
    });

    document.addEventListener('click', e => {
      if (document.body.classList.contains('layout-edit')) return;
      // non intercettare elementi interattivi interni
      if (e.target.closest('a, button, input, select, textarea, canvas, [onclick], .no-nav')) return;
      const card = e.target.closest('.card[data-nav]');
      if (!card) return;
      if (typeof gotoTab === 'function') gotoTab(card.getAttribute('data-nav'));
    });
  }

  // ── CSS iniettato ─────────────────────────────────────────────────────
  function injectCSS() {
    const css = `
#home-grid > .card { position: relative; min-width: 0; }
body.layout-edit #home-grid > .card { cursor: grab; }
body.layout-edit #home-grid > .card > *:not(.dl-resize-handle):not(h3) { pointer-events: none; }
.dl-dragging { opacity: .45; outline: 2px dashed var(--accent); outline-offset: -3px; }
.dl-resize-handle {
  display: none; position: absolute; right: 2px; bottom: 2px;
  width: 16px; height: 16px; cursor: nwse-resize; z-index: 5;
  border-right: 3px solid var(--accent); border-bottom: 3px solid var(--accent);
  border-bottom-right-radius: 6px; opacity: .55;
}
body.layout-edit .dl-resize-handle { display: block; }
body.layout-edit #home-grid > .card:hover { outline: 1px dashed var(--accent); outline-offset: -2px; }
.card[data-nav] { cursor: pointer; }
body.layout-edit .card[data-nav] { cursor: grab; }
@media (max-width: 1100px) {
  #home-grid { grid-template-columns: repeat(6, 1fr); }
}
@media (max-width: 760px) {
  #home-grid > .card { grid-column: 1 / -1 !important; }
}
`;
    const st = document.createElement('style');
    st.textContent = css;
    document.head.appendChild(st);
  }

  // ── Init ──────────────────────────────────────────────────────────────
  function initDashboardLayout() {
    const grid = document.getElementById(GRID_ID);
    if (!grid) return;

    // Ordine default = ordine DOM corrente (catturato PRIMA di ogni restore)
    DEFAULT_ORDER = Array.from(grid.children)
      .filter(c => c.classList.contains('card') && c.id).map(c => c.id);

    injectCSS();
    loadLayout(grid);
    enableDrag(grid);
    enableResize(grid);
    enableNav();

    const section = grid.closest('.section');
    if (section) buildToolbar(section);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDashboardLayout);
  } else {
    initDashboardLayout();
  }
})();

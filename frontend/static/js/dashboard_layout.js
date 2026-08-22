// CPSL Dashboard Layout v3 — Pointer Events puri, niente HTML5 DnD.
// Fix v1.4.4b: closest(':scope >') non funziona per trovare card figlie
// del grid quando l'evento parte da un elemento annidato. Ora usiamo
// parentElement traversal diretta + stopPropagation sul resize handle.

(function () {
  'use strict';
  const GRID_ID = 'home-grid';
  const LS_KEY = 'homeLayout';

  let DEFAULT_ORDER = [];
  const DEFAULT_SPANS = {
    'readiness-factors-card': 6,
    'training-load-card': 6,
    'sleep-hrv-card': 4,
    'eftp-progress-card': 4,
    'body-perf-card-wrap': 4,
  };

  function lsKey() {
    try { return typeof _profileLsKey === 'function' ? _profileLsKey(LS_KEY) : LS_KEY; }
    catch(_) { return LS_KEY; }
  }
  function lsGet(k) { try { return localStorage.getItem(k); } catch(_) { return null; } }
  function lsSet(k, v) { try { localStorage.setItem(k, v); } catch(_) {} }
  function lsDel(k) { try { localStorage.removeItem(k); } catch(_) {} }

  function maxCols() {
    var w = window.innerWidth;
    return w <= 760 ? 1 : w <= 1100 ? 6 : 12;
  }

  function clamp(n) { return Math.max(1, Math.min(maxCols(), Math.round(n) || 1)); }

  function applySpan(card, n) {
    if (!card) return;
    n = clamp(n);
    card.dataset.span = String(n);
    card.style.gridColumn = 'span ' + n;
  }

  function saveLayout(grid) {
    var order = Array.from(grid.children)
      .filter(function(c) { return c.classList.contains('card') && c.id; })
      .map(function(c) { return c.id; });
    var spans = {};
    order.forEach(function(id) {
      var el = document.getElementById(id);
      spans[id] = parseInt(el && el.dataset.span, 10) || DEFAULT_SPANS[id] || 6;
    });
    lsSet(lsKey(), JSON.stringify({ order: order, spans: spans }));
  }

  function loadLayout(grid) {
    var data = null;
    try { data = JSON.parse(lsGet(lsKey()) || 'null'); } catch(_) {}
    if (!data || !Array.isArray(data.order)) return;
    var byId = {};
    Array.from(grid.children).forEach(function(c) { if (c.id) byId[c.id] = c; });
    data.order.forEach(function(id) { if (byId[id]) grid.appendChild(byId[id]); });
    Object.keys(data.spans || {}).forEach(function(id) {
      applySpan(document.getElementById(id), data.spans[id]);
    });
  }

  function resetLayout(grid) {
    lsDel(lsKey());
    DEFAULT_ORDER.forEach(function(id) {
      var el = document.getElementById(id); if (el) grid.appendChild(el);
    });
    Object.keys(DEFAULT_SPANS).forEach(function(id) {
      applySpan(document.getElementById(id), DEFAULT_SPANS[id]);
    });
  }

  // Trova la card figlia diretta del grid partendo da un elemento qualsiasi
  function findGridCard(el) {
    while (el && el !== document.body) {
      if (el.parentElement && el.parentElement.id === GRID_ID &&
          el.classList.contains('card')) return el;
      el = el.parentElement;
    }
    return null;
  }

  // ── DRAG ───────────────────────────────────────────────────────────────

  
  function addCardControls(grid) {
    grid.querySelectorAll(':scope > .card').forEach(function(card) {
      var bar = document.createElement('div');
      bar.className = 'dl-card-controls';
      var btns = [
        ['\u25c0', 'Sposta sinistra', '_layoutMoveRel(this, -1)'],
        ['\u25b6', 'Sposta destra', '_layoutMoveRel(this, 1)'],
        ['+', 'Pi\u00f9 largo', '_layoutResizeRel(this, 1)'],
        ['\u2212', 'Pi\u00f9 stretto', '_layoutResizeRel(this, -1)']
      ];
      btns.forEach(function(b) {
        var btn = document.createElement('button');
        btn.textContent = b[0];
        btn.title = b[1];
        btn.addEventListener('click', function(e) {
          e.stopPropagation();
          eval(b[2].replace('this', 'btn'));
          saveLayout(document.getElementById(GRID_ID));
        });
        bar.appendChild(btn);
      });
      card.appendChild(bar);
    });
  }

  window._layoutMoveRel = function(btn, dir) {
    var card = btn.closest('.card');
    if (!card) return;
    var siblings = Array.from(card.parentElement.children)
      .filter(function(c) { return c.classList.contains('card'); });
    var idx = siblings.indexOf(card);
    var newIdx = idx + dir;
    if (newIdx < 0 || newIdx >= siblings.length) return;
    window._layoutMoveCard(idx, newIdx);
  };

  window._layoutResizeRel = function(btn, delta) {
    var card = btn.closest('.card');
    if (!card) return;
    var cur = parseInt(card.dataset.span, 10) || 4;
    window._layoutResizeCard(card.id, cur + delta);
  };


function enableDrag(grid) {
    var dragging = false;
    var dragCard = null;
    var ghost = null;
    var offX = 0, offY = 0;

    grid.addEventListener('pointerdown', function(e) {
      if (!document.body.classList.contains('layout-edit')) return;
      if (e.button !== 0) return;
      // Non iniziare il drag su elementi interattivi
      if (e.target.closest('a, button, input, select, textarea, [onclick], .dl-resize-handle')) return;
      var card = findGridCard(e.target);
      if (!card) return;

      e.preventDefault();
      dragging = true;
      dragCard = card;
      var rect = card.getBoundingClientRect();
      offX = e.clientX - rect.left;
      offY = e.clientY - rect.top;

      // Ghost visivo
      ghost = document.createElement('div');
      ghost.style.cssText = 'position:fixed;z-index:9999;pointer-events:none;' +
        'width:' + rect.width + 'px;height:' + rect.height + 'px;' +
        'opacity:0.15;background:var(--accent);border-radius:10px;' +
        'left:' + rect.left + 'px;top:' + rect.top + 'px;';
      document.body.appendChild(ghost);

      card.classList.add('dl-dragging');
      try { card.setPointerCapture(e.pointerId); } catch (err) { /* pointer sintetico/già rilasciato */ }
    });

    document.addEventListener('pointermove', function(e) {
      if (!dragging || !dragCard) return;
      // Muovi ghost
      if (ghost) {
        ghost.style.left = (e.clientX - offX) + 'px';
        ghost.style.top = (e.clientY - offY) + 'px';
      }
      // Reordina: trova la card sotto il puntatore
      var cards = Array.from(grid.children).filter(function(c) {
        return c.classList.contains('card') && c !== dragCard;
      });
      for (var i = 0; i < cards.length; i++) {
        var r = cards[i].getBoundingClientRect();
        if (e.clientX >= r.left && e.clientX <= r.right &&
            e.clientY >= r.top && e.clientY <= r.bottom) {
          if (e.clientY > r.top + r.height / 2) {
            if (cards[i].nextSibling !== dragCard) grid.insertBefore(dragCard, cards[i].nextSibling);
          } else {
            if (cards[i] !== dragCard.nextSibling) grid.insertBefore(dragCard, cards[i]);
          }
          break;
        }
      }
    });

    function endDrag() {
      if (!dragging) return;
      dragging = false;
      if (ghost) { ghost.remove(); ghost = null; }
      if (dragCard) { dragCard.classList.remove('dl-dragging'); dragCard = null; }
      saveLayout(grid);
    }

    document.addEventListener('pointerup', endDrag);
    document.addEventListener('pointercancel', endDrag);
  }

  // ── RESIZE ─────────────────────────────────────────────────────────────

  function enableResize(grid) {
    grid.querySelectorAll(':scope > .card').forEach(function(card) {
      var h = document.createElement('div');
      h.className = 'dl-resize-handle';
      h.title = 'Trascina per ridimensionare';
      card.appendChild(h);

      h.addEventListener('pointerdown', function(e) {
        if (!document.body.classList.contains('layout-edit')) return;
        e.preventDefault();
        e.stopPropagation(); // NON far partire anche il drag
        try { h.setPointerCapture(e.pointerId); } catch (err) { /* pointer sintetico/già rilasciato */ }

        var startX = e.clientX;

        function getColUnit() {
          var tracks = getComputedStyle(grid).gridTemplateColumns
            .split(' ').map(parseFloat).filter(function(v) { return v > 0; });
          var gap = parseFloat(getComputedStyle(grid).columnGap) || 0;
          return (tracks[0] || 50) + gap;
        }

        function onMove(ev) {
          var dx = ev.clientX - startX;
          var unit = getColUnit();
          var curSpan = parseInt(card.dataset.span, 10) || 4;
          var deltaCols = Math.round(dx / unit);
          var newSpan = clamp(curSpan + deltaCols);
          if (String(newSpan) !== card.dataset.span) {
            applySpan(card, newSpan);
          }
        }

        function onUp(ev) {
          document.removeEventListener('pointermove', onMove);
          document.removeEventListener('pointerup', onUp);
          saveLayout(grid);
        }

        document.addEventListener('pointermove', onMove);
        document.addEventListener('pointerup', onUp);
      });
    });

    window.addEventListener('resize', function() {
      grid.querySelectorAll(':scope > .card').forEach(function(c) {
        applySpan(c, parseInt(c.dataset.span, 10) || 2);
      });
    });
  }

  // ── NAVIGAZIONE ────────────────────────────────────────────────────────

  var NAV_MAP = {
    'today-card': 'plan',
    'my-cal-card': 'plan',
    'strength-card': 'plan',
    'daily-adapt-card': 'plan',
    'tid-heatmap-card': 'analysis',
    'last-week-feedback-card': 'plan',
  };

  function enableNav() {
    Object.keys(NAV_MAP).forEach(function(id) {
      var el = document.getElementById(id);
      if (el) el.setAttribute('data-nav', NAV_MAP[id]);
    });
    document.addEventListener('click', function(e) {
      if (document.body.classList.contains('layout-edit')) return;
      if (e.target.closest('a, button, input, select, textarea, canvas, [onclick], .no-nav')) return;
      var card = e.target.closest('.card[data-nav]');
      if (card && typeof gotoTab === 'function') gotoTab(card.getAttribute('data-nav'));
    });
  }

  // ── TOOLBAR ────────────────────────────────────────────────────────────

  function buildToolbar(section) {
    var bar = document.createElement('div');
    bar.id = 'layout-toolbar';
    bar.style.cssText = 'display:flex;align-items:center;gap:8px;margin-bottom:10px;flex-wrap:wrap;';
    bar.innerHTML =
      '<button id="btn-layout-edit" class="btn btn-sm" style="font-size:11px;">\u270f\ufe0f Personalizza layout</button>' +
      '<button id="btn-layout-reset" class="btn btn-sm" style="font-size:11px;display:none;">\u21ba Ripristina</button>' +
      '<span id="layout-edit-hint" style="display:none;font-size:11px;color:var(--text3);">' +
      'Trascina le card \u00b7 trascina \u231f per ridimensionare</span>';
    section.insertBefore(bar, section.firstChild);
    document.getElementById('btn-layout-edit').addEventListener('click', toggleEdit);
    document.getElementById('btn-layout-reset').addEventListener('click', function() {
      resetLayout(document.getElementById(GRID_ID));
      try { showToast('Layout ripristinato', 3000); } catch(_) {}
    });
  }

  function setEditHint(on) {
    var hint = document.getElementById('layout-edit-hint');
    var btnR = document.getElementById('btn-layout-reset');
    var btnE = document.getElementById('btn-layout-edit');
    if (hint) hint.style.display = on ? 'inline' : 'none';
    if (btnR) btnR.style.display = on ? 'inline-flex' : 'none';
    if (btnE) btnE.textContent = on ? '\u2713 Fatto' : '\u270f\ufe0f Personalizza layout';
  }

  function toggleEdit() {
    var on = !document.body.classList.contains('layout-edit');
    document.body.classList.toggle('layout-edit', on);
    setEditHint(on);
    if (!on) saveLayout(document.getElementById(GRID_ID));
  }

  // ── CSS ────────────────────────────────────────────────────────────────

  function injectCSS() {
    var css = [
      '#home-grid > .card { position: relative; min-width: 0; }',
      'body.layout-edit #home-grid > .card { cursor: grab; user-select: none; }',
      'body.layout-edit #home-grid > .card > *:not(.dl-resize-handle):not(h3):not(.dl-card-controls) { pointer-events: none; }',
      '.dl-dragging { opacity: 0.4; outline: 2px dashed var(--accent); outline-offset: -3px; z-index: 10; }',
      '.dl-resize-handle { display:none; position:absolute; right:2px; bottom:2px;',
      '  width:18px; height:18px; cursor:nwse-resize; z-index:5;',
      '  border-right:3px solid var(--accent); border-bottom:3px solid var(--accent);',
      '  border-bottom-right-radius:6px; opacity:0.6; }',
      'body.layout-edit .dl-resize-handle { display:block; }',
      'body.layout-edit #home-grid > .card:hover { outline:1px dashed var(--accent); outline-offset:-2px; }',
      '.card[data-nav] { cursor:pointer; }',
      'body.layout-edit .card[data-nav] { cursor:grab; }',
      '@media(max-width:1100px){ #home-grid{ grid-template-columns:repeat(6,1fr); } }',
      '@media(max-width:760px){ #home-grid>.card{ grid-column:1/-1 !important; } }',
      '.dl-card-controls { display:none; position:absolute; top:2px; right:24px; z-index:6; gap:2px; }',
      'body.layout-edit .dl-card-controls { display:flex; }',
      '.dl-card-controls button { width:20px; height:20px; font-size:10px; line-height:1; border:1px solid var(--border); border-radius:3px; cursor:pointer; background:var(--surface2); color:var(--text2); padding:0; }',
      '.dl-card-controls button:hover { border-color:var(--accent); color:var(--accent); }'
    ].join('\n');
    document.head.appendChild(Object.assign(
      document.createElement('style'), { textContent: css }));
  }

  // ── INIT ───────────────────────────────────────────────────────────────

  
  // ── API PROGRAMMATICHE (per test + accessibilità) ──────────────────────
  window._layoutMoveCard = function(fromIdx, toIdx) {
    var g = document.getElementById(GRID_ID);
    var cards = Array.from(g.children).filter(function(c) { return c.classList.contains('card'); });
    if (fromIdx < 0 || fromIdx >= cards.length || toIdx < 0 || toIdx >= cards.length) return false;
    var el = cards[fromIdx];
    var target = cards[toIdx];
    if (fromIdx < toIdx) g.insertBefore(el, target.nextSibling);
    else g.insertBefore(el, target);
    saveLayout(g);
    return true;
  };
  window._layoutResizeCard = function(id, span) {
    applySpan(document.getElementById(id), span);
    saveLayout(document.getElementById(GRID_ID));
    return true;
  };
  window._layoutResetLayout = function() {
    resetLayout(document.getElementById(GRID_ID));
  };

function init() {
    var grid = document.getElementById(GRID_ID);
    if (!grid) return;
    DEFAULT_ORDER = Array.from(grid.children)
      .filter(function(c) { return c.classList.contains('card') && c.id; })
      .map(function(c) { return c.id; });
    injectCSS();
    loadLayout(grid);
    enableDrag(grid);
    addCardControls(grid);
    enableResize(grid);
    enableNav();
    var sec = grid.closest('.section');
    if (sec) buildToolbar(sec);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
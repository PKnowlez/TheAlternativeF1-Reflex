/**
 * donut_chart.js  –  All Time Points Distribution Donut Interaction Bridge
 *
 * Provides:
 *   1. Robust slice selection (hover, click, touch) completely decoupled from
 *      the header ticker or any background timer re-renders.
 *   2. Center information rendered natively inside the SVG (<text> elements),
 *      ensuring it is fully preserved in saved/downloaded images.
 *   3. Direct Reflex event dispatch (window.__reflex) with hidden input fallback.
 *   4. Instant 0ms visual feedback (slice dimming/highlighting & center text updates).
 *   5. Gray area / background / center hole click to reset to all-time league view.
 */
(function () {
  'use strict';

  var REFLEX_EVENT = 'reflex___state____state.the_alternative_f1___all_time_stats____summary_all_time____summary_state.select_donut_event';

  // Persistent state object: { type, name, pts, meta }
  // Stored by value (not DOM node reference) so it survives React reconciliations
  var activeSelection = null;
  var lastHandledTouchTime = 0;

  // ── Dispatch to Reflex State ──────────────────────────────────────────────
  function dispatchToReflex(payload) {
    if (!payload) payload = 'reset';

    // 1. Primary: Direct Reflex Event Loop
    try {
      var reflex = window.__reflex;
      if (reflex && reflex['$/utils/context'] && reflex['$/utils/state']) {
        var addEvents = reflex['$/utils/context'].addEvents;
        var ReflexEvent = reflex['$/utils/state'].ReflexEvent;
        if (typeof addEvents === 'function' && typeof ReflexEvent === 'function') {
          addEvents([
            ReflexEvent(REFLEX_EVENT, { payload: payload })
          ]);
          return;
        }
      }
    } catch (err) {
      console.warn('[DonutChart] Direct Reflex dispatch error:', err);
    }

    // 2. Fallback: Hidden input element
    try {
      var inp = document.getElementById('taf1_donut_select_input');
      if (inp) {
        var last = inp.value;
        inp.value = payload;
        var tracker = inp._valueTracker;
        if (tracker) {
          tracker.setValue(last);
        }
        inp.dispatchEvent(new Event('input', { bubbles: true }));
        inp.dispatchEvent(new Event('change', { bubbles: true }));
      }
    } catch (err2) {
      console.warn('[DonutChart] Input fallback dispatch error:', err2);
    }
  }

  // ── SVG Element & Attribute Helpers ────────────────────────────────────────
  function getSvgElement() {
    return document.getElementById('summary-donut-svg');
  }

  function getDefaultPoints() {
    var svg = getSvgElement();
    if (svg && svg.getAttribute('data-default-points')) {
      return svg.getAttribute('data-default-points');
    }
    return '';
  }

  function dimExcept(svgEl, keepEl) {
    if (!svgEl) return;
    var slices = svgEl.querySelectorAll('.donut-slice');
    for (var i = 0; i < slices.length; i++) {
      var s = slices[i];
      s.style.transition = 'opacity 0.15s ease';
      s.style.opacity = (s === keepEl) ? '1' : '0.28';
    }
  }

  function restoreAll(svgEl) {
    if (!svgEl) return;
    var slices = svgEl.querySelectorAll('.donut-slice');
    for (var i = 0; i < slices.length; i++) {
      var s = slices[i];
      s.style.transition = 'opacity 0.15s ease';
      s.style.opacity = '1';
    }
  }

  // ── Native SVG Center Text Updates ────────────────────────────────────────
  function updateCenterDom(type, name, pts, meta, isLocked) {
    var typeEl = document.getElementById('donut-center-type');
    var valEl  = document.getElementById('donut-center-value');
    var metaEl = document.getElementById('donut-center-meta');

    if (typeEl) {
      typeEl.textContent = (type || '').toUpperCase();
      typeEl.setAttribute('fill', isLocked ? '#00b4da' : '#8E8E93');
      typeEl.style.fill = isLocked ? '#00b4da' : '#8E8E93';
    }
    if (valEl) {
      valEl.textContent = name || '';
      var sz = (name && name.length > 10) ? '16' : '22';
      valEl.setAttribute('font-size', sz);
      valEl.style.fontSize = sz + 'px';
    }
    if (metaEl) {
      metaEl.textContent = (pts ? pts + ' PTS \u2022 ' : '') + (meta || '');
      metaEl.setAttribute('fill', '#00b4da');
      metaEl.style.fill = '#00b4da';
    }
  }

  function resetCenterDom() {
    var typeEl = document.getElementById('donut-center-type');
    var valEl  = document.getElementById('donut-center-value');
    var metaEl = document.getElementById('donut-center-meta');

    var defPts = getDefaultPoints();
    if (typeEl) {
      typeEl.textContent = 'ALL-TIME LEAGUE';
      typeEl.setAttribute('fill', '#8E8E93');
      typeEl.style.fill = '#8E8E93';
    }
    if (valEl) {
      if (defPts) valEl.textContent = defPts;
      valEl.setAttribute('font-size', '24');
      valEl.style.fontSize = '24px';
    }
    if (metaEl) {
      metaEl.textContent = 'TOTAL POINTS';
      metaEl.setAttribute('fill', '#00b4da');
      metaEl.style.fill = '#00b4da';
    }
  }

  // ── State Persistence across Re-renders / Header Ticker updates ────────────
  function reapplyState() {
    if (!activeSelection) return;
    var svg = getSvgElement();
    if (!svg) return;

    var activeEl = null;
    var slices = svg.querySelectorAll('.donut-slice');
    for (var i = 0; i < slices.length; i++) {
      var s = slices[i];
      if (s.getAttribute('data-name') === activeSelection.name &&
          s.getAttribute('data-type') === activeSelection.type) {
        activeEl = s;
        break;
      }
    }
    dimExcept(svg, activeEl);
    updateCenterDom(activeSelection.type, activeSelection.name, activeSelection.pts, activeSelection.meta, true);
  }

  // ── Core Action Handlers ───────────────────────────────────────────────────
  function handleSliceHover(el) {
    if (activeSelection || !el) return;
    var type = el.getAttribute('data-type') || '';
    var name = el.getAttribute('data-name') || '';
    var pts  = el.getAttribute('data-pts')  || '';
    var meta = el.getAttribute('data-meta') || '';

    var svg = getSvgElement() || el.closest('svg');
    dimExcept(svg, el);
    updateCenterDom(type, name, pts, meta, false);
    dispatchToReflex('hover:' + type + ':' + name + ':' + pts + ':' + meta);
  }

  function handleSliceLeave(el) {
    if (activeSelection) return;
    var svg = getSvgElement() || (el ? el.closest('svg') : null);
    restoreAll(svg);
    resetCenterDom();
    dispatchToReflex('reset');
  }

  function handleSliceClick(el, event) {
    if (event && event.stopPropagation) event.stopPropagation();
    if (!el) return;

    var type = el.getAttribute('data-type') || '';
    var name = el.getAttribute('data-name') || '';
    var pts  = el.getAttribute('data-pts')  || '';
    var meta = el.getAttribute('data-meta') || '';

    var svg = getSvgElement() || el.closest('svg');

    if (activeSelection && activeSelection.name === name && activeSelection.type === type) {
      // Toggle off / deselect
      activeSelection = null;
      restoreAll(svg);
      resetCenterDom();
      dispatchToReflex('reset');
    } else {
      // Select slice
      activeSelection = { type: type, name: name, pts: pts, meta: meta };
      dimExcept(svg, el);
      updateCenterDom(type, name, pts, meta, true);
      dispatchToReflex('click:' + type + ':' + name + ':' + pts + ':' + meta);
    }
  }

  function handleResetAll(event) {
    if (event && event.stopPropagation) event.stopPropagation();
    activeSelection = null;
    var svg = getSvgElement();
    restoreAll(svg);
    resetCenterDom();
    dispatchToReflex('reset');
  }

  // ── Expose Globally for Inline SVG Handlers ────────────────────────────────
  window.taf1DonutEnter = function (el) {
    handleSliceHover(el);
  };

  window.taf1DonutLeave = function (el) {
    handleSliceLeave(el);
  };

  window.taf1DonutClick = function (el, event) {
    handleSliceClick(el, event);
  };

  window.taf1DonutReset = function (event) {
    handleResetAll(event);
  };

  window.taf1DonutBgClick = function (event) {
    if (!event || !event.target) {
      handleResetAll(event);
      return;
    }
    var targetId = event.target.id;
    if (targetId === 'summary-donut-svg' || targetId === 'donut-center-hole') {
      handleResetAll(event);
    }
  };

  // ── Delegated Capture Listeners for High Reliability & Touch ───────────────
  document.addEventListener('click', function (event) {
    var target = event.target;
    if (!target) return;

    // Let download button function normally without resetting
    if (target.closest && target.closest('button')) {
      return;
    }

    // Check if clicked a donut slice
    var slice = target.closest ? target.closest('.donut-slice') : null;
    if (slice) {
      var now = Date.now();
      if (now - lastHandledTouchTime < 350) return;
      handleSliceClick(slice, event);
      return;
    }

    // Check if clicked the donut center hole
    if (target.id === 'donut-center-hole' || (target.closest && target.closest('#donut-center-hole'))) {
      handleResetAll(event);
      return;
    }

    // Check if clicked the gray card area or container background
    var card = target.closest ? target.closest('#donut-chart-card, #donut-download-container, #summary-donut-svg') : null;
    if (card) {
      handleResetAll(event);
    }
  }, true);

  // Touch screen support
  document.addEventListener('touchend', function (event) {
    var target = event.target;
    if (!target) return;

    if (target.closest && target.closest('button')) {
      return;
    }

    var slice = target.closest ? target.closest('.donut-slice') : null;
    if (slice) {
      lastHandledTouchTime = Date.now();
      handleSliceClick(slice, event);
      return;
    }

    var card = target.closest ? target.closest('#donut-chart-card, #donut-download-container, #summary-donut-svg, #donut-center-hole') : null;
    if (card) {
      lastHandledTouchTime = Date.now();
      handleResetAll(event);
    }
  }, { passive: true });

  // ── MutationObserver to Reapply Active State on React Re-renders ───────────
  var observer = new MutationObserver(function () {
    if (activeSelection) {
      reapplyState();
    }
  });
  observer.observe(document.body, { childList: true, subtree: true });

})();

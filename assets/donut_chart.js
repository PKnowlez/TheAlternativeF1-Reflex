/**
 * donut_chart.js  –  All Time Points Distribution Donut Interaction Bridge
 *
 * Mirrors stats_map.js pattern with full direct Reflex event loop dispatch,
 * synthetic input fallback, and immediate DOM visual feedback (0ms latency).
 *
 * Features:
 *   1. Direct dispatch via window.__reflex into the Reflex event loop:
 *      reflex___state____state.the_alternative_f1___all_time_stats____summary_all_time____summary_state.select_donut_event
 *   2. Fallback dispatch via hidden input #taf1_donut_select_input.
 *   3. Instant DOM updates for center text overlay and slice dimming/highlighting.
 *   4. Supports hover, click selection, touch screen taps, and clicking the gray
 *      background or center hole to reset to whole-chart all-time view.
 *   5. Global inline handlers (taf1DonutEnter, taf1DonutLeave, taf1DonutClick,
 *      taf1DonutReset, taf1DonutBgClick) plus delegated document capture listeners.
 */
(function () {
  'use strict';

  var REFLEX_EVENT = 'reflex___state____state.the_alternative_f1___all_time_stats____summary_all_time____summary_state.select_donut_event';

  var activeSlice = null; // currently clicked/locked slice DOM element
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

  // ── Instant DOM Center Overlay & Visual Slice Opacity ──────────────────────
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

  function updateCenterDom(type, name, pts, meta, isLocked) {
    var typeEl = document.getElementById('donut-center-type');
    var valEl  = document.getElementById('donut-center-value');
    var metaEl = document.getElementById('donut-center-meta');

    if (typeEl) {
      typeEl.innerText = (type || '').toUpperCase();
      typeEl.style.color = isLocked ? '#00b4da' : '#8E8E93';
    }
    if (valEl) {
      valEl.innerText = name || '';
      valEl.style.fontSize = (name && name.length > 10) ? '15px' : '22px';
    }
    if (metaEl) {
      metaEl.innerText = (pts ? pts + ' PTS • ' : '') + (meta || '');
      metaEl.style.color = '#00b4da';
    }
  }

  function resetCenterDom() {
    var typeEl = document.getElementById('donut-center-type');
    var valEl  = document.getElementById('donut-center-value');
    var metaEl = document.getElementById('donut-center-meta');

    var defPts = getDefaultPoints();
    if (typeEl) {
      typeEl.innerText = 'ALL-TIME LEAGUE';
      typeEl.style.color = '#8E8E93';
    }
    if (valEl) {
      if (defPts) valEl.innerText = defPts;
      valEl.style.fontSize = '24px';
    }
    if (metaEl) {
      metaEl.innerText = 'TOTAL POINTS';
      metaEl.style.color = '#00b4da';
    }
  }

  // ── Core Action Handlers ───────────────────────────────────────────────────
  function handleSliceHover(el) {
    if (activeSlice || !el) return;
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
    if (activeSlice) return;
    var svg = getSvgElement() || (el ? el.closest('svg') : null);
    restoreAll(svg);
    resetCenterDom();
    dispatchToReflex('reset');
  }

  function handleSliceClick(el, event) {
    if (event && event.stopPropagation) event.stopPropagation();
    if (!el) return;

    var svg = getSvgElement() || el.closest('svg');

    if (activeSlice === el) {
      // Toggle off / deselect
      activeSlice = null;
      restoreAll(svg);
      resetCenterDom();
      dispatchToReflex('reset');
    } else {
      // Select slice
      activeSlice = el;
      var type = el.getAttribute('data-type') || '';
      var name = el.getAttribute('data-name') || '';
      var pts  = el.getAttribute('data-pts')  || '';
      var meta = el.getAttribute('data-meta') || '';

      dimExcept(svg, el);
      updateCenterDom(type, name, pts, meta, true);
      dispatchToReflex('click:' + type + ':' + name + ':' + pts + ':' + meta);
    }
  }

  function handleResetAll(event) {
    if (event && event.stopPropagation) event.stopPropagation();
    activeSlice = null;
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
    // Only reset if clicked the SVG background or center circle
    var targetId = event.target.id;
    if (targetId === 'summary-donut-svg' || targetId === 'donut-center-hole') {
      handleResetAll(event);
    }
  };

  // ── Delegated Capture Listeners for High Reliability & Touch ───────────────
  document.addEventListener('click', function (event) {
    var target = event.target;
    if (!target) return;

    // Check if clicked the download button — let it download
    if (target.closest && target.closest('button')) {
      return;
    }

    // Check if clicked inside a donut slice
    var slice = target.closest ? target.closest('.donut-slice') : null;
    if (slice) {
      // If inline onclick fired recently from touch, avoid double toggle
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

    // Check if clicked the gray area in the background of the chart or card
    var card = target.closest ? target.closest('#donut-chart-card, #donut-download-container, #summary-donut-svg') : null;
    if (card) {
      // Clicked in gray card background
      handleResetAll(event);
    }
  }, true);

  // Touch screen support
  document.addEventListener('touchend', function (event) {
    var target = event.target;
    if (!target) return;

    var slice = target.closest ? target.closest('.donut-slice') : null;
    if (slice) {
      lastHandledTouchTime = Date.now();
      handleSliceClick(slice, event);
      return;
    }

    var card = target.closest ? target.closest('#donut-chart-card, #donut-download-container, #summary-donut-svg, #donut-center-hole') : null;
    if (card && (!target.closest || !target.closest('button'))) {
      lastHandledTouchTime = Date.now();
      handleResetAll(event);
    }
  }, { passive: true });

  // Reset active state if user navigates away or DOM unmounts
  var observer = new MutationObserver(function () {
    var svg = getSvgElement();
    if (!svg) {
      activeSlice = null;
    }
  });
  observer.observe(document.body, { childList: true, subtree: true });

})();

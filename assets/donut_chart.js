/**
 * donut_chart.js  –  Points Distribution Donut Interaction Bridge (All Time & Seasons)
 *
 * Provides:
 *   1. Robust slice selection (hover, click, touch) completely decoupled from
 *      the header ticker or any background timer re-renders.
 *   2. Center information rendered natively inside the SVG (<text> elements),
 *      ensuring it is fully preserved in saved/downloaded images.
 *   3. Independent multi-chart support: All-Time Summary and Season Constructors
 *      maintain their own isolated selections without interference.
 *   4. Instant 0ms visual feedback (slice dimming/highlighting & center text updates).
 *   5. Gray area / background / center hole click to reset to default view.
 */
(function () {
  'use strict';

  var REFLEX_EVENT = 'reflex___state____state.the_alternative_f1___all_time_stats____summary_all_time____summary_state.select_donut_event';

  // Persistent state per SVG: { svgId: { type, name, pts, meta, svgId } }
  var activeSelectionsBySvg = {};
  var lastHandledTouchTime = 0;

  // ── Dispatch to Reflex State (Strictly for All-Time Summary ONLY) ───────────
  function dispatchToReflex(payload, svgEl) {
    if (!payload) payload = 'reset';

    // Season charts MUST NEVER dispatch events to Reflex or trigger state cycles.
    var isSummary = svgEl && (svgEl.id === 'summary-donut-svg' || (svgEl.closest && svgEl.closest('#summary-donut-svg')));
    if (!isSummary) {
      return;
    }
    if (!document.getElementById('summary-donut-svg')) {
      return;
    }

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
  function getSvgElement(el) {
    if (el) {
      var s = el.closest ? el.closest('svg') : null;
      if (s) return s;
    }
    return document.querySelector('.donut-svg, svg[id*="donut-svg"], #summary-donut-svg');
  }

  function getDefaultPoints(svgEl) {
    var svg = svgEl || getSvgElement();
    if (svg && svg.getAttribute('data-default-points')) {
      return svg.getAttribute('data-default-points');
    }
    return '';
  }

  function getDefaultType(svgEl) {
    var svg = svgEl || getSvgElement();
    if (svg && svg.getAttribute('data-default-type')) {
      return svg.getAttribute('data-default-type');
    }
    return 'ALL-TIME LEAGUE';
  }

  function getDefaultMeta(svgEl) {
    var svg = svgEl || getSvgElement();
    if (svg && svg.getAttribute('data-default-meta')) {
      return svg.getAttribute('data-default-meta');
    }
    return 'TOTAL POINTS';
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
  function updateCenterDom(type, name, pts, meta, isLocked, svgEl) {
    var svg = svgEl || getSvgElement();
    if (!svg) return;
    var typeEl = svg.querySelector('.donut-center-type, #donut-center-type');
    var valEl  = svg.querySelector('.donut-center-value, #donut-center-value');
    var metaEl = svg.querySelector('.donut-center-meta, #donut-center-meta');

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

  function resetCenterDom(svgEl) {
    var svg = svgEl || getSvgElement();
    if (!svg) return;
    var typeEl = svg.querySelector('.donut-center-type, #donut-center-type');
    var valEl  = svg.querySelector('.donut-center-value, #donut-center-value');
    var metaEl = svg.querySelector('.donut-center-meta, #donut-center-meta');

    var defType = getDefaultType(svg);
    var defPts = getDefaultPoints(svg);
    var defMeta = getDefaultMeta(svg);

    if (typeEl) {
      typeEl.textContent = defType.toUpperCase();
      typeEl.setAttribute('fill', '#8E8E93');
      typeEl.style.fill = '#8E8E93';
    }
    if (valEl) {
      if (defPts) valEl.textContent = defPts;
      valEl.setAttribute('font-size', '24');
      valEl.style.fontSize = '24px';
    }
    if (metaEl) {
      metaEl.textContent = defMeta;
      metaEl.setAttribute('fill', '#00b4da');
      metaEl.style.fill = '#00b4da';
    }
  }

  // ── Core Action Handlers ───────────────────────────────────────────────────
  function handleSliceHover(el) {
    if (!el) return;
    var svg = el.closest ? el.closest('svg') : getSvgElement(el);
    var svgId = svg ? svg.id : 'default';

    // If a slice on this specific SVG is currently locked/selected, ignore hover
    if (activeSelectionsBySvg[svgId]) return;

    var type = el.getAttribute('data-type') || '';
    var name = el.getAttribute('data-name') || '';
    var pts  = el.getAttribute('data-pts')  || '';
    var meta = el.getAttribute('data-meta') || '';

    dimExcept(svg, el);
    updateCenterDom(type, name, pts, meta, false, svg);
    dispatchToReflex('hover:' + type + ':' + name + ':' + pts + ':' + meta, svg);
  }

  function handleSliceLeave(el) {
    var svg = el ? (el.closest ? el.closest('svg') : null) : getSvgElement();
    var svgId = svg ? svg.id : 'default';

    // If a slice on this specific SVG is currently locked/selected, leave it intact
    if (activeSelectionsBySvg[svgId]) return;

    restoreAll(svg);
    resetCenterDom(svg);
    dispatchToReflex('reset', svg);
  }

  function handleSliceClick(el, event) {
    if (event && event.stopPropagation) event.stopPropagation();
    if (!el) return;

    var type = el.getAttribute('data-type') || '';
    var name = el.getAttribute('data-name') || '';
    var pts  = el.getAttribute('data-pts')  || '';
    var meta = el.getAttribute('data-meta') || '';

    var svg = el.closest ? el.closest('svg') : getSvgElement(el);
    var svgId = svg ? svg.id : 'default';

    var current = activeSelectionsBySvg[svgId];

    if (current && current.name === name && current.type === type) {
      // Toggle off / deselect
      delete activeSelectionsBySvg[svgId];
      restoreAll(svg);
      resetCenterDom(svg);
      dispatchToReflex('reset', svg);
    } else {
      // Select / lock slice
      activeSelectionsBySvg[svgId] = { type: type, name: name, pts: pts, meta: meta, svgId: svgId };
      dimExcept(svg, el);
      updateCenterDom(type, name, pts, meta, true, svg);
      dispatchToReflex('click:' + type + ':' + name + ':' + pts + ':' + meta, svg);
    }
  }

  function handleResetAll(event, targetSvg) {
    if (event && event.stopPropagation) event.stopPropagation();
    if (targetSvg && targetSvg.id) {
      delete activeSelectionsBySvg[targetSvg.id];
      restoreAll(targetSvg);
      resetCenterDom(targetSvg);
      dispatchToReflex('reset', targetSvg);
    } else {
      activeSelectionsBySvg = {};
      var svgs = document.querySelectorAll('.donut-svg, svg[id*="donut-svg"], #summary-donut-svg');
      for (var i = 0; i < svgs.length; i++) {
        restoreAll(svgs[i]);
        resetCenterDom(svgs[i]);
      }
      dispatchToReflex('reset', null);
    }
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
    var svg = event && event.target && event.target.closest ? event.target.closest('svg') : null;
    handleResetAll(event, svg);
  };

  window.taf1DonutBgClick = function (event) {
    if (!event || !event.target) {
      handleResetAll(event, null);
      return;
    }
    var target = event.target;
    var svg = target.closest ? target.closest('svg') : null;
    if (target.classList.contains('donut-svg') || (target.id && target.id.indexOf('donut-svg') !== -1) || target.classList.contains('donut-center-hole') || (target.id && target.id.indexOf('donut-center-hole') !== -1)) {
      handleResetAll(event, svg);
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
    if (target.classList.contains('donut-center-hole') || (target.closest && target.closest('.donut-center-hole')) || (target.id && target.id.indexOf('donut-center-hole') !== -1)) {
      var svgHole = target.closest ? target.closest('svg') : null;
      handleResetAll(event, svgHole);
      return;
    }

    // Check if clicked the gray card area or container background
    var card = target.closest ? target.closest('.donut-chart-card, [id*="donut-chart-card"], [id*="donut-download-container"], .donut-svg, svg[id*="donut-svg"]') : null;
    if (card) {
      var svgCard = card.querySelector ? card.querySelector('.donut-svg, svg[id*="donut-svg"]') : (card.closest ? card.closest('svg') : null);
      handleResetAll(event, svgCard);
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

    var card = target.closest ? target.closest('.donut-chart-card, [id*="donut-chart-card"], [id*="donut-download-container"], .donut-svg, svg[id*="donut-svg"], .donut-center-hole, [id*="donut-center-hole"]') : null;
    if (card) {
      lastHandledTouchTime = Date.now();
      var svgCard = card.querySelector ? card.querySelector('.donut-svg, svg[id*="donut-svg"]') : (card.closest ? card.closest('svg') : null);
      handleResetAll(event, svgCard);
    }
  }, { passive: true });

})();

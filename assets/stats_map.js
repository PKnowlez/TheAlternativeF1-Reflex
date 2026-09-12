/**
 * The Alternative F1 - All Time Stats Map Interaction Bridge
 * Handles direct-on-map clicking for Regions, States, and Metro Area Pins
 */
(function () {
  'use strict';

  function dispatchGroupSelection(groupId) {
    if (!groupId) return;
    var cleanId = String(groupId).trim();

    // 1. Try direct dispatch via Reflex Event Loop
    try {
      var reflex = window.__reflex;
      if (reflex && reflex['$/utils/context'] && reflex['$/utils/state']) {
        var addEvents = reflex['$/utils/context'].addEvents;
        var ReflexEvent = reflex['$/utils/state'].ReflexEvent;
        if (typeof addEvents === 'function' && typeof ReflexEvent === 'function') {
          addEvents([
            ReflexEvent(
              'reflex___state____state.the_alternative_f1___all_time_stats____map_all_time____stats_map_state.select_group',
              { group_id: cleanId }
            )
          ]);
          return;
        }
      }
    } catch (err) {
      console.warn('[StatsMap] Direct Reflex dispatch error:', err);
    }

    // 2. Fallback via hidden input element with synthetic React event
    try {
      var inp = document.getElementById('taf1_map_select_input');
      if (inp) {
        var last = inp.value;
        inp.value = cleanId;
        var tracker = inp._valueTracker;
        if (tracker) {
          tracker.setValue(last);
        }
        inp.dispatchEvent(new Event('input', { bubbles: true }));
        return;
      }
    } catch (err2) {
      console.warn('[StatsMap] Input fallback dispatch error:', err2);
    }
  }

  // Define globally on window for inline SVG onclick attributes
  window.taf1SelectMapGroup = function (groupId) {
    dispatchGroupSelection(groupId);
  };

  // Delegated click listener on document for high reliability
  document.addEventListener('click', function (event) {
    var target = event.target;
    if (!target) return;

    // Check if clicked element or its parent is a state path or metro pin
    var elem = target.closest ? target.closest('.state-path, .metro-pin') : null;
    if (!elem && target.classList) {
      if (target.classList.contains('state-path') || target.classList.contains('metro-pin')) {
        elem = target;
      }
    }

    if (elem) {
      var id = elem.getAttribute('data-code') || elem.id;
      if (id) {
        var cleanId = id.replace(/^st-/, '').replace(/^pin-/, '').replace(/_/g, ' ');
        dispatchGroupSelection(cleanId);
      }
    }
  }, true);

})();

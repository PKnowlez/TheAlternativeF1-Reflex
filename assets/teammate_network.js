/**
 * The Alternative F1 - Teammate Network Interactive Visualization
 * Implements SDDREQ-117 through SDDREQ-123 for TAF1APP-SDDFEAT-14
 *
 * Features:
 * - 60fps high-DPI Canvas simulation
 * - SDDREQ-121: Gentle floating bubbling animation with forward/backward depth fading
 * - SDDREQ-117: Driver bubbles with name, points, and outer ring colored by most recent team
 * - SDDREQ-118: 50/50 gradient connector lines between teammate pairs
 * - SDDREQ-122: Two Drivers shortest path highlighting with animated glowing pulses
 * - SDDREQ-123: Single Driver centered web with radial orbit rings for direct & extended teammates
 * - Direct click & hover interaction with Reflex State event loop bridge
 */
(function () {
  'use strict';

  var canvas = null;
  var ctx = null;
  var animFrameId = null;
  var networkData = null;
  var nodes = [];
  var edges = [];
  var hoveredNode = null;
  var mousePos = { x: -1000, y: -1000 };
  var animTime = 0;
  var currentMode = 'default';
  var selectedDriver1 = 'Nick';
  var selectedDriver2 = 'Randy';
  var selectedSingleDriver = 'Nick';
  var pathNodesSet = new Set();

  // Reflex event name for direct dispatch
  var REFLEX_EVENT = 'reflex___state____state.the_alternative_f1___all_time_stats____teammate_network____teammate_network_state.handle_js_select';

  function dispatchDriverSelect(driverName) {
    if (!driverName) return;
    var payloadStr = JSON.stringify({ driver: driverName });

    // 1. Direct Reflex dispatch
    try {
      var reflex = window.__reflex;
      if (reflex && reflex['$/utils/context'] && reflex['$/utils/state']) {
        var addEvents = reflex['$/utils/context'].addEvents;
        var ReflexEvent = reflex['$/utils/state'].ReflexEvent;
        if (typeof addEvents === 'function' && typeof ReflexEvent === 'function') {
          addEvents([
            ReflexEvent(REFLEX_EVENT, { payload: payloadStr })
          ]);
          return;
        }
      }
    } catch (err) {
      console.warn('[TeammateNetwork] Direct Reflex dispatch error:', err);
    }

    // 2. Fallback via hidden input
    try {
      var inp = document.getElementById('taf1_network_select_input');
      if (inp) {
        var last = inp.value;
        inp.value = payloadStr;
        var tracker = inp._valueTracker;
        if (tracker) {
          tracker.setValue(last);
        }
        inp.dispatchEvent(new Event('input', { bubbles: true }));
      }
    } catch (err2) {
      console.warn('[TeammateNetwork] Input fallback dispatch error:', err2);
    }
  }

  // ── Node Data & Physics ───────────────────────────────────────────────────

  function createNode(raw, idx, total) {
    // Initial circular scatter layout across 24 drivers
    var angle = (idx / total) * Math.PI * 2;
    var dist = 140 + (idx % 3) * 65;
    return {
      id: raw.id,
      name: raw.name,
      points: raw.points || 0,
      recentTeam: raw.recentTeam || 'Unknown',
      color: raw.color || '#FFFFFF',
      // Current simulated positions
      x: 0,
      y: 0,
      // Target center position for smooth lerp transitions
      targetX: 0,
      targetY: 0,
      // Default baseline position
      baseAngle: angle,
      baseDist: dist,
      // Floating oscillation phase offsets (SDDREQ-121)
      phaseX: Math.random() * Math.PI * 2,
      phaseY: Math.random() * Math.PI * 2,
      phaseZ: Math.random() * Math.PI * 2,
      speedX: 0.6 + Math.random() * 0.4,
      speedY: 0.5 + Math.random() * 0.5,
      speedZ: 0.4 + Math.random() * 0.3,
      ampX: 12 + Math.random() * 10,
      ampY: 10 + Math.random() * 8,
      baseRadius: 28,
      radius: 28,
      depth: 0, // -1 (back) to +1 (front)
      opacity: 1.0,
      targetOpacity: 1.0,
    };
  }

  function parsePayload() {
    var bridgeEl = document.getElementById('taf1-network-data-bridge');
    if (!bridgeEl) return false;
    var rawJson = bridgeEl.getAttribute('data-payload') || bridgeEl.getAttribute('data_payload');
    if (!rawJson) return false;

    try {
      var parsed = JSON.parse(rawJson);
      networkData = parsed;
      currentMode = parsed.mode || 'two_drivers';
      selectedDriver1 = parsed.driver1 || '';
      selectedDriver2 = parsed.driver2 || '';
      selectedSingleDriver = parsed.singleDriver || '';
      pathNodesSet = new Set(parsed.pathNodes || []);

      // Build or update nodes list
      if (!nodes.length && parsed.drivers) {
        nodes = parsed.drivers.map(function (d, i) {
          return createNode(d, i, parsed.drivers.length);
        });
      } else if (parsed.drivers) {
        // Sync metadata
        parsed.drivers.forEach(function (d) {
          var existing = nodes.find(function (n) { return n.id === d.id; });
          if (existing) {
            existing.points = d.points;
            existing.recentTeam = d.recentTeam;
            existing.color = d.color;
          }
        });
      }

      edges = parsed.edges || [];
      return true;
    } catch (e) {
      console.warn('[TeammateNetwork] Failed to parse network data bridge:', e);
      return false;
    }
  }

  // ── Layout Calculation ────────────────────────────────────────────────────

  function updateTargets(width, height) {
    var centerX = width / 2;
    var centerY = height / 2;

    if (currentMode === 'single_driver') {
      // SDDREQ-123: Center selected driver; arrange direct teammates in inner ring, degree 2 in outer ring
      var targetCenterId = selectedSingleDriver;
      var directNeighbors = new Set();
      edges.forEach(function (e) {
        if (e.source === targetCenterId) directNeighbors.add(e.target);
        if (e.target === targetCenterId) directNeighbors.add(e.source);
      });

      var degree2Neighbors = new Set();
      edges.forEach(function (e) {
        if (directNeighbors.has(e.source) && e.target !== targetCenterId && !directNeighbors.has(e.target)) {
          degree2Neighbors.add(e.target);
        }
        if (directNeighbors.has(e.target) && e.source !== targetCenterId && !directNeighbors.has(e.source)) {
          degree2Neighbors.add(e.source);
        }
      });

      var directList = Array.from(directNeighbors);
      var degree2List = Array.from(degree2Neighbors);
      var otherList = [];

      nodes.forEach(function (n) {
        if (n.id === targetCenterId) {
          n.targetX = centerX;
          n.targetY = centerY;
          n.targetOpacity = 1.0;
        } else if (directNeighbors.has(n.id)) {
          var idx = directList.indexOf(n.id);
          var ang = (idx / Math.max(1, directList.length)) * Math.PI * 2 - Math.PI / 2;
          var r = Math.min(width, height) * 0.25;
          n.targetX = centerX + Math.cos(ang) * r;
          n.targetY = centerY + Math.sin(ang) * r;
          n.targetOpacity = 1.0;
        } else if (degree2Neighbors.has(n.id)) {
          var idx2 = degree2List.indexOf(n.id);
          var ang2 = (idx2 / Math.max(1, degree2List.length)) * Math.PI * 2 - Math.PI / 3;
          var r2 = Math.min(width, height) * 0.42;
          n.targetX = centerX + Math.cos(ang2) * r2;
          n.targetY = centerY + Math.sin(ang2) * r2;
          n.targetOpacity = 0.8;
        } else {
          otherList.push(n);
        }
      });

      // Scatter remaining unrelated drivers around outermost boundary
      otherList.forEach(function (n, idx) {
        var ang3 = (idx / Math.max(1, otherList.length)) * Math.PI * 2;
        var r3 = Math.min(width, height) * 0.47;
        n.targetX = centerX + Math.cos(ang3) * r3;
        n.targetY = centerY + Math.sin(ang3) * r3;
        n.targetOpacity = 0.22;
      });

    } else if (currentMode === 'two_drivers') {
      // SDDREQ-122: Highlight shortest path between Driver 1 and Driver 2
      var hasPath = pathNodesSet.size > 0;
      var pathArray = networkData && networkData.pathNodes ? networkData.pathNodes : [];

      if (hasPath && pathArray.length > 1) {
        // Place path nodes in a clear, visible arc / curve across the canvas
        var numPath = pathArray.length;
        var startX = width * 0.2;
        var endX = width * 0.8;
        var midY = centerY;

        nodes.forEach(function (n) {
          var pathIdx = pathArray.indexOf(n.id);
          if (pathIdx !== -1) {
            var t = numPath === 1 ? 0.5 : pathIdx / (numPath - 1);
            n.targetX = startX + (endX - startX) * t;
            // Slight curve arch
            var arch = Math.sin(t * Math.PI) * (height * 0.18);
            n.targetY = midY - arch;
            n.targetOpacity = 1.0;
          } else {
            // Natural scatter around margins
            var ang = n.baseAngle;
            var r = Math.min(width, height) * 0.38 + (n.phaseX % 40);
            n.targetX = centerX + Math.cos(ang) * r;
            n.targetY = centerY + Math.sin(ang) * r;
            n.targetOpacity = 0.16; // Dim non-path drivers
          }
        });
      } else {
        // Disconnected or single node fallback layout
        nodes.forEach(function (n) {
          var isSelected = n.id === selectedDriver1 || n.id === selectedDriver2;
          var ang = n.baseAngle;
          var r = Math.min(width, height) * 0.34;
          n.targetX = centerX + Math.cos(ang) * r;
          n.targetY = centerY + Math.sin(ang) * r;
          n.targetOpacity = isSelected ? 1.0 : 0.3;
        });
      }

    } else {
      // SDDREQ-121: Default mode — harmonious organic spiderweb constellation
      nodes.forEach(function (n) {
        var ang = n.baseAngle;
        var r = Math.min(width, height) * 0.34;
        n.targetX = centerX + Math.cos(ang) * r;
        n.targetY = centerY + Math.sin(ang) * r;
        n.targetOpacity = 0.95;
      });
    }
  }

  // ── Render Frame Loop ─────────────────────────────────────────────────────

  function render() {
    if (!canvas || !ctx) return;
    animTime += 0.016;

    var rect = canvas.getBoundingClientRect();
    var width = rect.width;
    var height = rect.height;

    // Check high DPI sizing
    var dpr = window.devicePixelRatio || 1;
    if (canvas.width !== Math.round(width * dpr) || canvas.height !== Math.round(height * dpr)) {
      canvas.width = Math.round(width * dpr);
      canvas.height = Math.round(height * dpr);
      ctx.scale(dpr, dpr);
    }

    ctx.clearRect(0, 0, width, height);

    // Dark Map Background (SDDREQ-119)
    ctx.fillStyle = '#15151A';
    ctx.fillRect(0, 0, width, height);

    // Subtle dark space constellation grid
    ctx.save();
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.025)';
    ctx.lineWidth = 1;
    for (var x = 0; x < width; x += 48) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    for (var y = 0; y < height; y += 48) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }
    ctx.restore();

    updateTargets(width, height);

    // Update positions with smooth lerp + organic floating (SDDREQ-121)
    nodes.forEach(function (n) {
      // Sinusoidal floating offsets
      var floatX = Math.sin(animTime * n.speedX + n.phaseX) * n.ampX;
      var floatY = Math.cos(animTime * n.speedY + n.phaseY) * n.ampY;
      var floatZ = Math.sin(animTime * n.speedZ + n.phaseZ); // -1 to +1

      // Lerp towards target
      if (n.x === 0 && n.y === 0) {
        n.x = n.targetX + floatX;
        n.y = n.targetY + floatY;
      } else {
        n.x += (n.targetX + floatX - n.x) * 0.08;
        n.y += (n.targetY + floatY - n.y) * 0.08;
      }

      n.depth = floatZ;
      // Scale radius and opacity with depth (fading forward and backward)
      n.radius = n.baseRadius * (0.92 + 0.16 * ((floatZ + 1) / 2));
      n.opacity += (n.targetOpacity - n.opacity) * 0.1;
    });

    // ── 1. Draw Connector Lines (SDDREQ-118) ─────────────────────────────────
    var nodeMap = {};
    nodes.forEach(function (n) { nodeMap[n.id] = n; });

    edges.forEach(function (e) {
      var n1 = nodeMap[e.source];
      var n2 = nodeMap[e.target];
      if (!n1 || !n2) return;

      var isPathEdge = false;
      if (currentMode === 'two_drivers' && pathNodesSet.size > 1) {
        var pathArr = networkData.pathNodes || [];
        for (var i = 0; i < pathArr.length - 1; i++) {
          if ((pathArr[i] === e.source && pathArr[i + 1] === e.target) ||
              (pathArr[i] === e.target && pathArr[i + 1] === e.source)) {
            isPathEdge = true;
            break;
          }
        }
      }

      var isSingleActive = false;
      if (currentMode === 'single_driver') {
        isSingleActive = e.source === selectedSingleDriver || e.target === selectedSingleDriver;
      }

      ctx.save();
      var lineGrad = ctx.createLinearGradient(n1.x, n1.y, n2.x, n2.y);
      // 50/50 gradient based on team colors (SDDREQ-118)
      lineGrad.addColorStop(0.0, e.color1 || n1.color);
      lineGrad.addColorStop(0.48, e.color1 || n1.color);
      lineGrad.addColorStop(0.52, e.color2 || n2.color);
      lineGrad.addColorStop(1.0, e.color2 || n2.color);

      var edgeOpacity = 0.35;
      var lineWidth = 1.6;

      if (isPathEdge) {
        edgeOpacity = 0.95;
        lineWidth = 3.8;
      } else if (isSingleActive) {
        edgeOpacity = 0.85;
        lineWidth = 2.8;
      } else if (currentMode === 'two_drivers' && pathNodesSet.size > 1) {
        edgeOpacity = 0.06; // Dim background edges
      } else if (currentMode === 'single_driver') {
        edgeOpacity = 0.10;
      }

      ctx.strokeStyle = lineGrad;
      ctx.globalAlpha = Math.min(n1.opacity, n2.opacity) * edgeOpacity;
      ctx.lineWidth = lineWidth;

      ctx.beginPath();
      ctx.moveTo(n1.x, n1.y);
      ctx.lineTo(n2.x, n2.y);
      ctx.stroke();

      ctx.restore();
    });

    // ── 2. Draw Driver Bubbles (SDDREQ-117) ──────────────────────────────────
    // Sort nodes by depth so closer ones render on top
    var sortedNodes = nodes.slice().sort(function (a, b) {
      return a.depth - b.depth;
    });

    sortedNodes.forEach(function (n) {
      var isHovered = hoveredNode && hoveredNode.id === n.id;
      var isSelected = (currentMode === 'two_drivers' && (n.id === selectedDriver1 || n.id === selectedDriver2)) ||
                       (currentMode === 'single_driver' && n.id === selectedSingleDriver);
      var isInPath = pathNodesSet.has(n.id);

      ctx.save();
      var nodeAlpha = n.opacity * (0.80 + 0.20 * ((n.depth + 1) / 2));
      ctx.globalAlpha = Math.min(1.0, Math.max(0.1, nodeAlpha));

      // Glow halo for selected or path nodes
      if (isSelected || isHovered) {
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.radius + 6, 0, Math.PI * 2);
        ctx.fillStyle = n.color;
        ctx.globalAlpha = 0.35;
        ctx.fill();
        ctx.globalAlpha = Math.min(1.0, Math.max(0.1, nodeAlpha));
      } else if (isInPath) {
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.radius + 4, 0, Math.PI * 2);
        ctx.fillStyle = '#00b4da';
        ctx.globalAlpha = 0.25;
        ctx.fill();
        ctx.globalAlpha = Math.min(1.0, Math.max(0.1, nodeAlpha));
      }

      // Bubble Body (sleek glass dark circle)
      ctx.beginPath();
      ctx.arc(n.x, n.y, n.radius, 0, Math.PI * 2);
      ctx.fillStyle = '#1A1A22';
      ctx.fill();

      // Outer circle outline in driver's most recent team color (SDDREQ-117)
      ctx.lineWidth = isSelected || isHovered ? 3.5 : 2.5;
      ctx.strokeStyle = n.color;
      ctx.stroke();

      // Text 1: Driver Name (bold white Outfit font)
      ctx.fillStyle = '#FFFFFF';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      var fontSize = Math.max(10, Math.round(n.radius * 0.38));
      ctx.font = '700 ' + fontSize + 'px Outfit, -apple-system, sans-serif';
      ctx.fillText(n.name, n.x, n.y - (n.radius * 0.18));

      // Text 2: Total Career Points (subtle cyan/gray)
      var ptsFontSize = Math.max(8, Math.round(n.radius * 0.30));
      ctx.font = '600 ' + ptsFontSize + 'px Outfit, -apple-system, sans-serif';
      ctx.fillStyle = isSelected ? '#00E5FF' : '#00b4da';
      var formattedPts = n.points % 1 === 0 ? String(Math.round(n.points)) : n.points.toFixed(1);
      ctx.fillText(formattedPts + ' pts', n.x, n.y + (n.radius * 0.28));

      ctx.restore();
    });

    // ── 3. Tooltip on Hover ─────────────────────────────────────────────────
    if (hoveredNode) {
      drawTooltip(hoveredNode, width, height);
    }

    animFrameId = requestAnimationFrame(render);
  }

  function drawTooltip(node, width, height) {
    ctx.save();
    var text1 = node.name;
    var text2 = 'Team: ' + node.recentTeam;
    var formattedPts = node.points % 1 === 0 ? String(Math.round(node.points)) : node.points.toFixed(1);
    var text3 = 'Career: ' + formattedPts + ' pts';

    ctx.font = '700 12px Outfit, sans-serif';
    var w1 = ctx.measureText(text1).width;
    ctx.font = '500 11px Outfit, sans-serif';
    var w2 = ctx.measureText(text2).width;
    var w3 = ctx.measureText(text3).width;
    var boxW = Math.max(w1, w2, w3) + 24;
    var boxH = 56;

    var tx = node.x + node.radius + 10;
    var ty = node.y - boxH / 2;
    if (tx + boxW > width - 10) tx = node.x - node.radius - boxW - 10;
    if (ty < 10) ty = 10;
    if (ty + boxH > height - 10) ty = height - boxH - 10;

    // Background pill
    ctx.fillStyle = 'rgba(20, 20, 26, 0.95)';
    ctx.strokeStyle = node.color;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.roundRect(tx, ty, boxW, boxH, 8);
    ctx.fill();
    ctx.stroke();

    // Text lines
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';
    ctx.fillStyle = '#FFFFFF';
    ctx.font = '700 12px Outfit, sans-serif';
    ctx.fillText(text1, tx + 12, ty + 8);

    ctx.fillStyle = '#AAAAAA';
    ctx.font = '500 11px Outfit, sans-serif';
    ctx.fillText(text2, tx + 12, ty + 24);

    ctx.fillStyle = '#00b4da';
    ctx.font = '600 11px Outfit, sans-serif';
    ctx.fillText(text3, tx + 12, ty + 38);
    ctx.restore();
  }

  // ── Mouse & Interaction Listeners ─────────────────────────────────────────

  function getNodeAt(x, y) {
    for (var i = nodes.length - 1; i >= 0; i--) {
      var n = nodes[i];
      var dx = x - n.x;
      var dy = y - n.y;
      if (Math.sqrt(dx * dx + dy * dy) <= n.radius + 4) {
        return n;
      }
    }
    return null;
  }

  function handleMouseMove(e) {
    if (!canvas) return;
    var rect = canvas.getBoundingClientRect();
    var x = e.clientX - rect.left;
    var y = e.clientY - rect.top;
    mousePos = { x: x, y: y };

    var prevHover = hoveredNode;
    hoveredNode = getNodeAt(x, y);
    if (canvas) {
      canvas.style.cursor = hoveredNode ? 'pointer' : 'default';
    }
  }

  function handleClick(e) {
    if (!canvas) return;
    var rect = canvas.getBoundingClientRect();
    var x = e.clientX - rect.left;
    var y = e.clientY - rect.top;
    var clicked = getNodeAt(x, y);
    if (clicked) {
      currentMode = 'single_driver';
      selectedSingleDriver = clicked.id;
      dispatchDriverSelect(clicked.id);
    }
  }

  // ── Touchscreen Single-Tap Support ────────────────────────────────────────
  var touchStartX = 0;
  var touchStartY = 0;
  var touchStartTime = 0;

  function handleTouchStart(e) {
    if (!canvas || !e.touches || e.touches.length === 0) return;
    var touch = e.touches[0];
    var rect = canvas.getBoundingClientRect();
    touchStartX = touch.clientX - rect.left;
    touchStartY = touch.clientY - rect.top;
    touchStartTime = Date.now();
  }

  function handleTouchEnd(e) {
    if (!canvas) return;
    var duration = Date.now() - touchStartTime;
    var touch = (e.changedTouches && e.changedTouches.length > 0) ? e.changedTouches[0] : null;
    if (touch && duration < 600) {
      var rect = canvas.getBoundingClientRect();
      var endX = touch.clientX - rect.left;
      var endY = touch.clientY - rect.top;
      var moveDist = Math.hypot(endX - touchStartX, endY - touchStartY);
      if (moveDist < 14) {
        var clicked = getNodeAt(endX, endY);
        if (clicked) {
          if (e.cancelable) e.preventDefault();
          currentMode = 'single_driver';
          selectedSingleDriver = clicked.id;
          dispatchDriverSelect(clicked.id);
        }
      }
    }
  }

  function handleMouseLeave() {
    hoveredNode = null;
    if (canvas) canvas.style.cursor = 'default';
  }

  // ── Initialization & Mutation Observer ────────────────────────────────────

  function initNetwork() {
    canvas = document.getElementById('teammate-network-canvas');
    if (!canvas) return;

    ctx = canvas.getContext('2d');
    canvas.removeEventListener('mousemove', handleMouseMove);
    canvas.removeEventListener('click', handleClick);
    canvas.removeEventListener('mouseleave', handleMouseLeave);
    canvas.removeEventListener('touchstart', handleTouchStart);
    canvas.removeEventListener('touchend', handleTouchEnd);

    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('click', handleClick);
    canvas.addEventListener('mouseleave', handleMouseLeave);
    canvas.addEventListener('touchstart', handleTouchStart, { passive: false });
    canvas.addEventListener('touchend', handleTouchEnd, { passive: false });

    parsePayload();

    if (!animFrameId) {
      animFrameId = requestAnimationFrame(render);
    }
  }

  // Watch for state payload updates from Reflex
  function setupObserver() {
    var bridgeEl = document.getElementById('taf1-network-data-bridge');
    if (!bridgeEl) return;

    var observer = new MutationObserver(function () {
      parsePayload();
    });
    observer.observe(bridgeEl, { attributes: true, childList: true, subtree: true });
  }

  // Periodic bootstrap checker to mount cleanly upon tab switches
  var checkInterval = setInterval(function () {
    var c = document.getElementById('teammate-network-canvas');
    if (c && (!canvas || canvas !== c)) {
      initNetwork();
      setupObserver();
    }
  }, 300);

  // Global hooks for direct testing or external invocation
  window.taf1InitTeammateNetwork = initNetwork;
  window.taf1SelectNetworkDriver = dispatchDriverSelect;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initNetwork);
  } else {
    initNetwork();
  }
})();

/**
 * The Alternative F1 - Circuit Replay Animation Engine
 * Implements SDD Requirements TAF1APP-SDDREQ-124 through SDDREQ-133 for TAF1APP-SDDFEAT-15.
 *
 * Requirements:
 * - SDDREQ-124: Track Maps from /TrackMaps/ or Cloudflare (white outline on #15151E)
 * - SDDREQ-125: Driver Dot Colors matched from that season's standings
 * - SDDREQ-126: DNF Drivers stop at end of Lap 2, fade out within 1/2 lap
 * - SDDREQ-127: Passing across 5 laps with pseudo-random timing & lateral passing maneuvers
 * - SDDREQ-128: Restart animation after 3s hold at completion, fading original grid back in
 * - SDDREQ-129: Starts immediately when a race results expander is opened
 * - SDDREQ-130: Official track direction (clockwise / counter-clockwise)
 * - SDDREQ-131: Official start line for grid start
 * - SDDREQ-132: Starting grid has 50% dot overlap
 * - SDDREQ-133: Racing spacing is 1 full dot length between dots
 */

(function () {
  'use strict';

  const CANVAS_W = 1920;
  const CANVAS_H = 920; // 15% smaller vertically
  const Y_OFFSET = -80; // Centers Y=540 track geometry at Y=460 in 920px height

  // Global cache of precomputed track point geometries (fallback if not embedded)
  let circuitTracksCache = null;
  let isFetchingTracks = false;
  const pendingInits = [];

  function fetchCircuitTracks(callback) {
    if (circuitTracksCache) {
      if (callback) callback(circuitTracksCache);
      return;
    }
    if (callback) pendingInits.push(callback);
    if (isFetchingTracks) return;
    isFetchingTracks = true;

    const paths = ['/circuit_tracks.json', '/assets/circuit_tracks.json'];
    function tryFetch(idx) {
      if (idx >= paths.length) {
        console.warn('[CircuitReplay] Could not load circuit_tracks.json from fallback paths.');
        isFetchingTracks = false;
        return;
      }
      fetch(paths[idx])
        .then(res => {
          if (!res.ok) throw new Error('HTTP ' + res.status);
          return res.json();
        })
        .then(data => {
          circuitTracksCache = data;
          isFetchingTracks = false;
          while (pendingInits.length > 0) {
            const cb = pendingInits.shift();
            cb(circuitTracksCache);
          }
        })
        .catch(() => tryFetch(idx + 1));
    }
    tryFetch(0);
  }

  // Registry of all active replay instances on the page keyed by container DOM element
  const replayInstances = new Map();

  class CircuitReplayPlayer {
    constructor(container) {
      this.container = container;
      this.raceName = container.getAttribute('data-race-name') || '';
      this.canvas = container.querySelector('canvas');
      if (!this.canvas) return;

      // Coordinate buffer resolution: 1920x920
      this.canvas.width = CANVAS_W;
      this.canvas.height = CANVAS_H;
      this.ctx = this.canvas.getContext('2d');

      // Enforce full transparency on canvas and container elements
      this.canvas.style.setProperty('background', 'transparent', 'important');
      this.canvas.style.setProperty('border', 'none', 'important');
      this.container.style.setProperty('background', 'transparent', 'important');
      this.container.style.setProperty('border', 'none', 'important');
      this.container.style.setProperty('box-shadow', 'none', 'important');

      // Parsed driver data
      this.drivers = [];
      try {
        const payloadAttr = container.getAttribute('data-drivers');
        if (payloadAttr) {
          this.drivers = JSON.parse(payloadAttr);
        }
      } catch (e) {
        console.error('[CircuitReplay] Failed to parse drivers payload for', this.raceName, e);
      }

      // Fallback if drivers array is empty
      if (!this.drivers || this.drivers.length === 0) {
        const defaultColors = ['#E8002D', '#FF8000', '#00D2BE', '#0600EF', '#0090FF', '#229971', '#52E252', '#B6BABD', '#C92D4B', '#5E8FAA'];
        for (let i = 1; i <= 10; i++) {
          this.drivers.push({
            name: 'Driver ' + i,
            team: 'Team ' + i,
            color: defaultColors[(i - 1) % defaultColors.length],
            grid_pos: i,
            finish_pos: i,
            is_dnf: false,
          });
        }
      }

      // Ensure active drivers have sequential finish_pos from 1 to numActive
      const activeList = this.drivers.filter(d => !d.is_dnf).sort((a, b) => (a.finish_pos || 0) - (b.finish_pos || 0));
      activeList.forEach((d, i) => {
        d.finish_pos = i + 1;
      });
      const dnfList = this.drivers.filter(d => !!d.is_dnf).sort((a, b) => (a.finish_pos || 0) - (b.finish_pos || 0));
      dnfList.forEach((d, i) => {
        d.finish_pos = activeList.length + i + 1;
      });

      this.trackData = null;
      this.trackImg = null;
      this.imgLoaded = false;
      this.isPlaying = false;
      this.isPausedByUser = false;
      this.wasVisible = false;
      this.animFrameId = null;

      // Simulation parameters
      this.totalLaps = 5; // SDDREQ-127: 5 laps
      this.lapDurationSec = 9.0; // ~9s per lap -> ~45s full race
      this.simTime = 0; // In seconds
      this.state = 'grid'; // 'grid' | 'racing' | 'finished' | 'restarting'
      this.finishHoldTime = 0; // Timer for 3-second hold (SDDREQ-128)
      this.restartFade = 1.0;

      // Visual parameters: 25% larger bubbles (radius 75 vs 60, diameter 150px)
      this.dotRadius = 75; // Dot diameter = 150px (~20px on mini-map)
      this.gridOverlapSpacing = 75; // SDDREQ-132: 50% overlap = 75px center-to-center
      this.racingGapSpacing = 150; // SDDREQ-133: 1 full dot length gap = 150px gap
      this.racingSpacing = 300; // Center-to-center in racing condition

      this.initTrackData();
      this.initEvents();
      this.render(); // Immediate initial render
    }

    resolveTrack(tracks, name) {
      if (!tracks || !name) return null;
      if (tracks[name]) return tracks[name];

      let clean = name;
      if (clean.includes(':')) {
        clean = clean.split(':')[1].trim();
      } else if (/^(pre-season|post-season)/i.test(clean)) {
        clean = clean.replace(/^(pre-season|post-season)[\s:-]+(test\s+)?/i, '').trim();
      }

      if (tracks[clean]) return tracks[clean];

      const aliases = {
        'vegas': 'Las Vegas',
        'barcelona': 'Spain',
        'sakhir': 'Bahrain',
      };
      if (aliases[clean.toLowerCase()] && tracks[aliases[clean.toLowerCase()]]) {
        return tracks[aliases[clean.toLowerCase()]];
      }

      const stripped = clean.replace(' Sprint', '').replace(' (S)', '').replace(' Reverse', '').trim();
      if (tracks[stripped]) return tracks[stripped];
      if (aliases[stripped.toLowerCase()] && tracks[aliases[stripped.toLowerCase()]]) {
        return tracks[aliases[stripped.toLowerCase()]];
      }

      for (const k of Object.keys(tracks)) {
        if (k.toLowerCase() === name.toLowerCase() || k.toLowerCase() === clean.toLowerCase() || k.toLowerCase() === stripped.toLowerCase()) {
          return tracks[k];
        }
      }
      return null;
    }

    initTrackData() {
      // 1. Check if track data was embedded directly by the server in data-track-data
      const embedded = this.container.getAttribute('data-track-data');
      if (embedded && embedded.length > 20) {
        try {
          const parsed = JSON.parse(embedded);
          if (parsed && parsed.points && parsed.points.length > 0) {
            this.trackData = parsed;
            this.render();
            return;
          }
        } catch (e) {
          console.warn('[CircuitReplay] Error parsing embedded data-track-data:', e);
        }
      }

      // 2. Fallback to client-side fetch if not embedded
      fetchCircuitTracks((tracks) => {
        const td = this.resolveTrack(tracks, this.raceName);
        if (td) {
          this.trackData = td;
          this.render();
        }
      });
    }

    initEvents() {
      // Click mini-map to toggle pause / play
      this.canvas.addEventListener('click', (e) => {
        e.stopPropagation();
        if (this.isPlaying) {
          this.pause();
          this.isPausedByUser = true;
        } else {
          this.isPausedByUser = false;
          this.play();
        }
      });
    }

    play() {
      if (this.isPlaying) return;
      this.isPlaying = true;
      let lastTime = performance.now();

      const loop = (now) => {
        if (!this.isPlaying) return;
        const dt = Math.min((now - lastTime) / 1000, 0.1);
        lastTime = now;

        this.update(dt);
        this.render();

        this.animFrameId = requestAnimationFrame(loop);
      };

      this.animFrameId = requestAnimationFrame(loop);
    }

    pause() {
      this.isPlaying = false;
      if (this.animFrameId) {
        cancelAnimationFrame(this.animFrameId);
        this.animFrameId = null;
      }
    }

    restart() {
      this.simTime = 0;
      this.state = 'racing';
      this.finishHoldTime = 0;
      this.restartFade = 1.0;
      this.isPausedByUser = false;
      this.play();
    }

    // Schedule overtakes and compute dynamic position for each driver
    update(dt) {
      if (this.state === 'restarting') {
        this.restartFade -= dt * 1.5;
        if (this.restartFade <= 0) {
          this.simTime = 0;
          this.state = 'racing';
          this.restartFade = 1.0;
        }
        return;
      }

      if (this.state === 'finished') {
        this.finishHoldTime += dt;
        if (this.finishHoldTime >= 3.0) { // SDDREQ-128: 3 seconds pause
          this.state = 'restarting';
          this.restartFade = 1.0;
        }
        return;
      }

      this.simTime += dt;
      const totalRaceTime = this.totalLaps * this.lapDurationSec;

      if (this.simTime >= totalRaceTime) {
        this.simTime = totalRaceTime;
        this.state = 'finished';
        this.finishHoldTime = 0;
      }
    }

    // Interpolate point along the precomputed spline points
    getPointAtProgress(t) {
      if (!this.trackData || !this.trackData.points || this.trackData.points.length === 0) {
        return { x: 960, y: 540, nx: 0, ny: 0 };
      }
      const pts = this.trackData.points;
      const total = pts.length;
      let norm = t % 1;
      if (norm < 0) norm += 1;

      const idxFloat = norm * total;
      const i1 = Math.floor(idxFloat) % total;
      const i2 = (i1 + 1) % total;
      const frac = idxFloat - Math.floor(idxFloat);

      const p1 = pts[i1];
      const p2 = pts[i2];

      const x = p1[0] + (p2[0] - p1[0]) * frac;
      const y = p1[1] + (p2[1] - p1[1]) * frac;

      // Tangent vector for lateral passing offsets
      const dx = p2[0] - p1[0];
      const dy = p2[1] - p1[1];
      const len = Math.hypot(dx, dy) || 1;
      // Normal vector (perpendicular to tangent)
      const nx = -dy / len;
      const ny = dx / len;

      return { x, y, nx, ny };
    }

    render() {
      if (!this.canvas) return;

      const w = CANVAS_W;
      const h = CANVAS_H;

      if (this.canvas.width !== w) this.canvas.width = w;
      if (this.canvas.height !== h) this.canvas.height = h;

      const ctx = this.ctx;

      // Enforce full transparency
      this.canvas.style.setProperty('background', 'transparent', 'important');
      this.canvas.style.setProperty('border', 'none', 'important');
      this.container.style.setProperty('background', 'transparent', 'important');
      this.container.style.setProperty('border', 'none', 'important');
      this.container.style.setProperty('box-shadow', 'none', 'important');

      // 1. Clear with full transparency so track seamlessly integrates into results
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.clearRect(0, 0, w, h);

      // Save before vertical centering shift
      ctx.save();
      ctx.translate(0, Y_OFFSET);

      // 3. Always draw crisp vector track path from spline points
      if (this.trackData && this.trackData.points && this.trackData.points.length > 1) {
        const pts = this.trackData.points;
        ctx.save();
        // Crisp clean white vector track outline only (no background road bed or marker artifacts)
        ctx.beginPath();
        ctx.moveTo(pts[0][0], pts[0][1]);
        for (let i = 1; i < pts.length; i++) {
          ctx.lineTo(pts[i][0], pts[i][1]);
        }
        ctx.closePath();
        ctx.strokeStyle = '#FFFFFF';
        ctx.lineWidth = 10;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.stroke();
        ctx.restore();
      }

      if (!this.trackData || !this.trackData.points || this.drivers.length === 0) {
        ctx.restore();
        return;
      }

      const totalRaceTime = this.totalLaps * this.lapDurationSec;
      const raceProgress = Math.min(1.0, this.simTime / totalRaceTime);

      const numActive = this.drivers.filter(d => !d.is_dnf).length || this.drivers.length || 1;

      // Track length & spacing fractions
      const trackLengthPx = this.trackData.track_length_px || 4000;
      // Cap maximum spacing so that all active cars fit sequentially within 80% of the circuit loop without wrapping
      const maxAllowedSpacingFrac = 0.80 / Math.max(1, numActive - 1);
      const gridSpacingFrac = Math.min(this.gridOverlapSpacing / trackLengthPx, maxAllowedSpacingFrac);
      const desiredRacingSpacingFrac = this.racingSpacing / trackLengthPx;
      const racingSpacingFrac = Math.min(desiredRacingSpacingFrac, maxAllowedSpacingFrac);

      // Transition from compact 50% overlapping starting grid into racing spacing
      const launchDuration = 1.2; // 1.2s grid launch
      const launchFrac = Math.min(1.0, this.simTime / launchDuration);
      const easeLaunch = 1 - Math.pow(1 - launchFrac, 2);
      const currentSpacingFrac = gridSpacingFrac + (racingSpacingFrac - gridSpacingFrac) * easeLaunch;

      // Leader progression across 5 laps
      const leaderLapsProgress = (this.simTime / this.lapDurationSec);

      // Overtakes occur strictly within laps 1-4 (simTime: 0 -> 4 * lapDurationSec).
      // By the beginning of lap 5 for the front runner (leaderLapsProgress = 4.0), overtakeProgress reaches 1.0!
      const overtakeDuration = 4.0 * this.lapDurationSec;
      const overtakeProgress = Math.min(1.0, this.simTime / overtakeDuration);

      // Compute positions of all drivers
      const activeCars = [];

      this.drivers.forEach((drv, index) => {
        const gridPos = drv.grid_pos || (index + 1);
        const finishPos = drv.finish_pos || (index + 1);
        const isDnf = !!drv.is_dnf;

        // Pseudo-random deterministic seed for passing timing
        const seed = ((gridPos * 37 + finishPos * 17) % 100) / 100.0;
        // Overtakes begin between 15% and 55% of the first 4 laps
        const passStart = 0.15 + seed * 0.40;
        // Overtakes strictly complete between 60% and 95% of the first 4 laps (prior to lap 5!)
        const passEnd = Math.min(0.96, passStart + 0.25 + seed * 0.16);

        let currentRank;
        if (overtakeProgress <= 0) {
          currentRank = gridPos;
        } else if (overtakeProgress >= passEnd) {
          // By the beginning of lap 5 (and throughout lap 5), car is locked into exact finish position
          currentRank = finishPos;
        } else if (overtakeProgress < passStart) {
          const p = overtakeProgress / passStart;
          currentRank = gridPos + (finishPos - gridPos) * (0.25 * Math.sin(p * Math.PI / 2));
        } else {
          const p = (overtakeProgress - passStart) / (passEnd - passStart);
          const easeP = p * p * (3 - 2 * p); // smoothstep
          currentRank = gridPos + (finishPos - gridPos) * (0.25 + 0.75 * easeP);
        }

        // SDDREQ-126: DNF drivers come to a stop at the end of the second lap (simTime = 2 * lapDurationSec)
        // and fade out within 1/2 a lap's time for the rest of the grid
        let dnfStopped = false;
        let dnfOpacity = 1.0;
        let dnfLateralOffset = 0;

        if (isDnf) {
          const dnfStopTime = 2.0 * this.lapDurationSec;
          const dnfFadeDuration = 0.5 * this.lapDurationSec; // 1/2 lap's time
          if (this.simTime >= dnfStopTime) {
            dnfStopped = true;
            dnfLateralOffset = 38; // Pulls to track shoulder/edge
            const timeSinceStop = this.simTime - dnfStopTime;
            dnfOpacity = Math.max(0, 1.0 - (timeSinceStop / dnfFadeDuration));
          }
        }

        // Compute track distance progress for this car
        let carLapsProgress;
        if (dnfStopped) {
          carLapsProgress = 1.98;
        } else {
          const rankOffset = (currentRank - 1) * currentSpacingFrac;
          carLapsProgress = Math.max(0, leaderLapsProgress - rankOffset);
        }

        // Lateral lane offset for overtaking maneuvers (SDDREQ-127)
        let laneOffset = dnfLateralOffset;
        if (!dnfStopped && Math.abs(finishPos - gridPos) > 0) {
          // Passing lane offset only while actively overtaking before lap 5
          if (overtakeProgress > passStart && overtakeProgress < passEnd) {
            const passP = (overtakeProgress - passStart) / (passEnd - passStart);
            const passCycle = Math.sin(passP * Math.PI);
            const side = (gridPos % 2 === 0) ? 1 : -1;
            laneOffset = side * 28 * passCycle;
          }
        }

        const pt = this.getPointAtProgress(carLapsProgress);
        const posX = pt.x + pt.nx * laneOffset;
        const posY = pt.y + pt.ny * laneOffset;

        // Driver's first initial
        const rawName = (drv.name || 'D').trim();
        const initial = rawName.charAt(0).toUpperCase();

        activeCars.push({
          driver: drv,
          x: posX,
          y: posY,
          opacity: dnfOpacity,
          isDnf: isDnf,
          dnfStopped: dnfStopped,
          currentRank: currentRank,
          gridPos: gridPos,
          finishPos: finishPos,
          color: drv.color || '#00b4da',
          name: rawName,
          initial: initial,
        });
      });

      // Sort cars for drawing: lowest rank (trailing) first, leader on top
      activeCars.sort((a, b) => b.currentRank - a.currentRank);

      // Draw Restart Fade overlay if restarting (SDDREQ-128)
      let globalAlpha = 1.0;
      if (this.state === 'restarting') {
        globalAlpha = this.restartFade;
      }

      // Draw all driver dots (dotRadius = 75, diameter = 150)
      activeCars.forEach(c => {
        if (c.opacity <= 0) return;

        ctx.save();
        ctx.globalAlpha = c.opacity * globalAlpha;

        const r = this.dotRadius;

        // Glowing outer accent
        ctx.beginPath();
        ctx.arc(c.x, c.y, r + 12, 0, Math.PI * 2);
        ctx.fillStyle = c.color;
        ctx.globalAlpha = (c.opacity * globalAlpha) * 0.45;
        ctx.fill();
        ctx.globalAlpha = c.opacity * globalAlpha;

        // Solid Dot Body (SDDREQ-125: driver color from standings)
        ctx.beginPath();
        ctx.arc(c.x, c.y, r, 0, Math.PI * 2);
        ctx.fillStyle = c.color;
        ctx.fill();

        // Crisp Border
        ctx.lineWidth = 6;
        ctx.strokeStyle = '#14141E';
        ctx.stroke();

        // Inside label: driver's first initial scaled up 35% (65px)
        ctx.fillStyle = '#FFFFFF';
        ctx.font = '900 65px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(c.initial, c.x, c.y + 3);

        // DNF indicator badge if stopped
        if (c.dnfStopped) {
          ctx.fillStyle = '#E53E3E';
          ctx.font = 'bold 24px sans-serif';
          ctx.fillText('DNF', c.x, c.y - r - 14);
        }

        ctx.restore();
      });

      // Restore vertical centering translate
      ctx.restore();
    }
  }

  // Check visibility and start/pause replay on accordion expand (SDDREQ-129)
  function checkAndTriggerReplays() {
    const containers = document.querySelectorAll('.taf1-circuit-replay');
    containers.forEach(container => {
      const hasDimensions = (container.offsetWidth > 0 && container.offsetHeight > 0);
      const accordionItem = container.closest('[data-state="open"]');
      const isVisible = hasDimensions || (accordionItem !== null);

      let player = replayInstances.get(container);
      if (!player) {
        player = new CircuitReplayPlayer(container);
        replayInstances.set(container, player);
      }

      if (isVisible) {
        // If it just became visible on accordion open, restart so user sees full race start
        if (!player.wasVisible) {
          player.wasVisible = true;
          player.restart();
        } else if (!player.isPlaying && !player.isPausedByUser) {
          player.play();
        }
      } else {
        if (player.wasVisible) {
          player.wasVisible = false;
          player.pause();
        }
      }
    });
  }

  // Click listener for instant trigger when user clicks any accordion item
  document.addEventListener('click', () => {
    setTimeout(checkAndTriggerReplays, 50);
    setTimeout(checkAndTriggerReplays, 200);
  });

  // MutationObserver on DOM state changes
  const observer = new MutationObserver(() => {
    checkAndTriggerReplays();
  });

  function startObserving() {
    if (document.body) {
      observer.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['data-state', 'class', 'style', 'aria-expanded', 'hidden']
      });
    }
    checkAndTriggerReplays();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', startObserving);
  } else {
    startObserving();
  }

  // Fast heartbeat timer to guarantee detection
  setInterval(checkAndTriggerReplays, 300);

  window.addEventListener('resize', checkAndTriggerReplays);
  window.taf1InitCircuitReplays = checkAndTriggerReplays;
})();

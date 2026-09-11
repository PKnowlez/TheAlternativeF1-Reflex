/**
 * The Alternative F1 - Interactive Power Rankings Animated Bar / Bump Chart
 * Web Component: <power-rankings-chart>
 *
 * Implements:
 * - Left-to-right animated trajectory of power rankings across race checkpoints
 * - Each state is level for 1 second, transitions for 1 second, and is level for 1 second at the new state
 * - Stops cleanly at its current final state with the full chart completely readable and usable
 * - No circular bubble around car icons: direct car graphics ride cleanly at tips, reducing vertical line spacing
 * - Reduced vertical spacing between lines (dy = 44px, compact chart height)
 * - Immune to header ticker updates: persistent global store preserves state across Reflex/React reconciliations
 * - Once animation reaches end state, it STOPS permanently; ONLY user clicking Play/Replay or page refresh restarts it
 * - Responsive mobile scaling: zero horizontal scrolling required on narrow mobile screens
 * - Single Play/Pause/Replay toggle button
 * - Horizontal week/checkpoint headers at >= 12pt (16px) font
 * - Paused scrubber behavior: scrubbing never resumes playback until user explicitly clicks Play
 * - Interactive hover and click highlights with summary tooltips
 * - Dark mode theme integration and responsive SVG layout
 */

(function () {
  const PRC_STORE = (window.__TAF1_PRC_STORE = window.__TAF1_PRC_STORE || {
    initialized: false,
    progress: 0.0,
    isPlaying: false,
    userPaused: false,
    hasCompleted: false,
    speed: 1.0,
    activeTeamId: null,
    currentSeason: null
  });

  function splitBezier(p0, p1, p2, p3, t) {
    const q1 = {
      x: (1 - t) * p0.x + t * p1.x,
      y: (1 - t) * p0.y + t * p1.y
    };
    const r0 = {
      x: (1 - t) * p1.x + t * p2.x,
      y: (1 - t) * p1.y + t * p2.y
    };
    const q2 = {
      x: (1 - t) * q1.x + t * r0.x,
      y: (1 - t) * q1.y + t * r0.y
    };
    const r1 = {
      x: (1 - t) * p2.x + t * p3.x,
      y: (1 - t) * p2.y + t * p3.y
    };
    const r2 = {
      x: (1 - t) * r0.x + t * r1.x,
      y: (1 - t) * r0.y + t * r1.y
    };
    const q3 = {
      x: (1 - t) * q2.x + t * r2.x,
      y: (1 - t) * q2.y + t * r2.y
    };
    return { q1, q2, q3 };
  }

  class PowerRankingsChart extends HTMLElement {
    constructor() {
      super();
      this.attachShadow({ mode: 'open' });

      // Initialize from persistent store
      this.chartData = null;
      this.progress = PRC_STORE.progress || 0.0;
      this.isPlaying = PRC_STORE.isPlaying || false;
      this.userPaused = PRC_STORE.userPaused || false;
      this.speed = PRC_STORE.speed || 1.0;
      this.activeTeamId = PRC_STORE.activeTeamId || null;
      this.lastTimestamp = null;
      this.rafId = null;

      // Bound event handlers
      this.onPlayPauseClick = this.onPlayPauseClick.bind(this);
      this.onSpeedClick = this.onSpeedClick.bind(this);
      this.onSliderInput = this.onSliderInput.bind(this);
      this.onSliderChange = this.onSliderChange.bind(this);
      this.animateFrame = this.animateFrame.bind(this);
    }

    static get observedAttributes() {
      return ['data-chart', 'datachart'];
    }

    get dataChart() {
      return this.chartData;
    }

    set dataChart(val) {
      this._dataChart = val;
      this.parseData();
      const newSeason = this.chartData ? this.chartData.season : null;

      // If season has not changed, do NOT reset animation!
      if (PRC_STORE.initialized && PRC_STORE.currentSeason === newSeason) return;

      PRC_STORE.initialized = true;
      PRC_STORE.currentSeason = newSeason;
      PRC_STORE.progress = 0.0;
      PRC_STORE.isPlaying = true;
      PRC_STORE.userPaused = false;
      PRC_STORE.hasCompleted = false;
      this.render();
      this.resetAndPlay();
    }

    attributeChangedCallback(name, oldValue, newValue) {
      if (oldValue === newValue) return;
      if (oldValue && newValue && oldValue.trim() === newValue.trim()) return;
      if (name === 'data-chart' || name === 'datachart') {
        this.parseData();
        const newSeason = this.chartData ? this.chartData.season : null;

        // If season has not changed, do NOT reset animation!
        if (PRC_STORE.initialized && PRC_STORE.currentSeason === newSeason) return;

        PRC_STORE.initialized = true;
        PRC_STORE.currentSeason = newSeason;
        PRC_STORE.progress = 0.0;
        PRC_STORE.isPlaying = true;
        PRC_STORE.userPaused = false;
        PRC_STORE.hasCompleted = false;
        this.render();
        this.resetAndPlay();
      }
    }

    connectedCallback() {
      this.parseData();
      if (!this.hasRendered) {
        this.render();
        this.hasRendered = true;
      }

      const currentSeason = this.chartData ? this.chartData.season : null;
      const isSeasonChange = PRC_STORE.initialized && PRC_STORE.currentSeason !== null && PRC_STORE.currentSeason !== currentSeason;

      if (!PRC_STORE.initialized || isSeasonChange) {
        // Initial page load or explicit season change: start animation once
        PRC_STORE.initialized = true;
        PRC_STORE.currentSeason = currentSeason;
        PRC_STORE.progress = 0.0;
        PRC_STORE.isPlaying = true;
        PRC_STORE.userPaused = false;
        PRC_STORE.hasCompleted = false;
        this.progress = 0.0;
        this.isPlaying = true;
        this.userPaused = false;
        this.resetAndPlay();
      } else {
        // Re-mount / re-render from header ticker or screen interaction:
        // RESTORE exact state! Ticker MUST NOT reset or restart the animation!
        this.progress = PRC_STORE.progress;
        this.isPlaying = PRC_STORE.isPlaying;
        this.userPaused = PRC_STORE.userPaused;
        this.speed = PRC_STORE.speed;
        this.activeTeamId = PRC_STORE.activeTeamId;

        this.updatePlayBtnVisual();
        this.updateVisuals(this.progress);
        this.applyTeamHighlight();

        if (PRC_STORE.hasCompleted || this.progress >= 1.0) {
          // Animation reached end state: STAY STOPPED!
          this.progress = 1.0;
          this.stopAnimation();
          this.updateVisuals(1.0);
          this.updatePlayBtnVisual();
        } else if (this.isPlaying && !this.userPaused) {
          // Continue playing current animation smoothly
          if (!this.rafId) {
            this.lastTimestamp = performance.now();
            this.rafId = requestAnimationFrame(this.animateFrame);
          }
        } else {
          this.stopAnimation();
        }
      }
    }

    disconnectedCallback() {
      // Delay cancellation slightly to prevent hitching if DOM is reconciled
      setTimeout(() => {
        if (!this.isConnected && this.rafId) {
          cancelAnimationFrame(this.rafId);
          this.rafId = null;
        }
      }, 50);
    }

    parseData() {
      const raw = this.getAttribute('data-chart') || this.getAttribute('datachart') || this._dataChart;
      if (!raw) {
        this.chartData = null;
        return;
      }
      try {
        this.chartData = typeof raw === 'string' ? JSON.parse(raw) : raw;
      } catch (err) {
        console.error('power-rankings-chart: failed to parse data-chart JSON', err);
        this.chartData = null;
      }
    }

    /**
     * Total playback duration in ms at 1x speed:
     * For M races:
     * M plateaus (1 second each) + (M - 1) transitions (1 second each)
     * Total = (2 * M - 1) * 1000 ms.
     */
    getTotalDurationMs() {
      if (!this.chartData || !this.chartData.races || this.chartData.races.length === 0) {
        return 3000;
      }
      const M = this.chartData.races.length;
      return Math.max(1000, (2 * M - 1) * 1000);
    }

    resetAndPlay() {
      this.stopAnimation();
      this.userPaused = false;
      PRC_STORE.userPaused = false;
      this.progress = 0.0;
      PRC_STORE.progress = 0.0;
      PRC_STORE.hasCompleted = false;
      this.isPlaying = true;
      PRC_STORE.isPlaying = true;
      this.lastTimestamp = null;
      this.updatePlayBtnVisual();
      this.updateVisuals(0.0);
      this.rafId = requestAnimationFrame(this.animateFrame);
    }

    startAnimation() {
      if (this.rafId) {
        cancelAnimationFrame(this.rafId);
        this.rafId = null;
      }
      if (this.progress >= 1.0 || PRC_STORE.hasCompleted) {
        this.progress = 0.0;
        PRC_STORE.progress = 0.0;
        PRC_STORE.hasCompleted = false;
      }
      this.isPlaying = true;
      PRC_STORE.isPlaying = true;
      this.userPaused = false;
      PRC_STORE.userPaused = false;
      this.lastTimestamp = null;
      this.updatePlayBtnVisual();
      this.updateVisuals(this.progress);
      this.rafId = requestAnimationFrame(this.animateFrame);
    }

    stopAnimation() {
      this.isPlaying = false;
      PRC_STORE.isPlaying = false;
      if (this.rafId) {
        cancelAnimationFrame(this.rafId);
        this.rafId = null;
      }
      this.lastTimestamp = null;
      this.updatePlayBtnVisual();
    }

    animateFrame(timestamp) {
      if (!this.isPlaying) return;

      if (!this.lastTimestamp) {
        this.lastTimestamp = timestamp;
      }

      let delta = timestamp - this.lastTimestamp;
      this.lastTimestamp = timestamp;

      // Clamp delta to prevent sudden jumps if a background frame is delayed
      if (delta > 100) delta = 100;

      const totalDuration = this.getTotalDurationMs();
      const step = delta / (totalDuration / this.speed);
      this.progress = Math.min(1.0, this.progress + step);
      PRC_STORE.progress = this.progress;

      this.updateVisuals(this.progress);

      if (this.progress >= 1.0) {
        // END STATE: Halt permanently until user explicitly clicks Play/Replay or refreshes page
        this.progress = 1.0;
        PRC_STORE.progress = 1.0;
        this.isPlaying = false;
        PRC_STORE.isPlaying = false;
        PRC_STORE.hasCompleted = true;
        this.stopAnimation();
        this.updatePlayBtnVisual();
      } else {
        this.rafId = requestAnimationFrame(this.animateFrame);
      }
    }

    onPlayPauseClick() {
      if (this.isPlaying) {
        this.userPaused = true;
        PRC_STORE.userPaused = true;
        this.stopAnimation();
      } else {
        // User explicitly tapped Play / Replay
        this.startAnimation();
      }
    }

    onSpeedClick() {
      const speeds = [1.0, 1.5, 2.0, 0.5];
      const curIdx = speeds.indexOf(this.speed);
      const nextIdx = (curIdx + 1) % speeds.length;
      this.speed = speeds[nextIdx];
      PRC_STORE.speed = this.speed;

      const btn = this.shadowRoot.getElementById('speed-btn');
      if (btn) btn.textContent = `${this.speed}x`;
    }

    /**
     * When user scrubs the slider:
     * Animation is stopped and strictly DOES NOT resume automatically.
     */
    onSliderInput(e) {
      this.userPaused = true;
      this.isPlaying = false;
      PRC_STORE.userPaused = true;
      PRC_STORE.isPlaying = false;
      this.stopAnimation();
      const val = parseFloat(e.target.value);
      this.progress = Math.max(0.0, Math.min(1.0, val / 1000.0));
      PRC_STORE.progress = this.progress;
      PRC_STORE.hasCompleted = this.progress >= 1.0;
      this.updateVisuals(this.progress);
      this.updatePlayBtnVisual();
    }

    onSliderChange(e) {
      this.userPaused = true;
      this.isPlaying = false;
      PRC_STORE.userPaused = true;
      PRC_STORE.isPlaying = false;
      this.stopAnimation();
      const val = parseFloat(e.target.value);
      this.progress = Math.max(0.0, Math.min(1.0, val / 1000.0));
      PRC_STORE.progress = this.progress;
      PRC_STORE.hasCompleted = this.progress >= 1.0;
      this.updateVisuals(this.progress);
      this.updatePlayBtnVisual();
    }

    updatePlayBtnVisual() {
      const btn = this.shadowRoot.getElementById('play-btn');
      if (!btn) return;
      if (this.isPlaying) {
        btn.innerHTML = `
          <svg viewBox="0 0 24 24" fill="currentColor">
            <rect x="5" y="3" width="5" height="18" rx="1.5"></rect>
            <rect x="14" y="3" width="5" height="18" rx="1.5"></rect>
          </svg>
          <span>Pause</span>
        `;
        btn.setAttribute('aria-label', 'Pause');
      } else if (this.progress >= 1.0 || PRC_STORE.hasCompleted) {
        btn.innerHTML = `
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M1 4v6h6"></path>
            <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path>
          </svg>
          <span>Replay</span>
        `;
        btn.setAttribute('aria-label', 'Replay');
      } else {
        btn.innerHTML = `
          <svg viewBox="0 0 24 24" fill="currentColor">
            <polygon points="6 3 20 12 6 21 6 3"></polygon>
          </svg>
          <span>Play</span>
        `;
        btn.setAttribute('aria-label', 'Play');
      }
    }

    updateVisuals(p) {
      const slider = this.shadowRoot.getElementById('scrubber');
      if (slider && document.activeElement !== slider) {
        const sliderVal = Math.round(p * 1000);
        if (this._lastSliderVal !== sliderVal) {
          slider.value = sliderVal;
          const pct = (sliderVal / 10).toFixed(1);
          slider.style.background = `linear-gradient(to right, #00b4da 0%, #00b4da ${pct}%, #2C2C32 ${pct}%, #2C2C32 100%)`;
          this._lastSliderVal = sliderVal;
        }
      }

      if (!this.chartData || !this.computedLayout) return;

      const { races, teams, plateaus, totalIntervals, windowViewW, viewH, raceIncW, numRaces } = this.computedLayout;
      const K = totalIntervals;

      // Calculate current interval and fraction
      const u = p * K;
      const s = Math.min(K - 1, Math.floor(u));
      const f = p >= 1.0 ? 1.0 : Math.min(1.0, Math.max(0.0, u - s));

      // Pan With Cars (TAF1APP-SDDREQ-91): After 2 race increments, pan with the cars keeping 3 increments visible (next 1 and previous 2)
      let panX = 0;
      if (numRaces > 3) {
        const raceCoord = (s + f) / 2.0;
        if (raceCoord > 2.0) {
          panX = (raceCoord - 2.0) * raceIncW;
          const maxPanX = (numRaces - 3) * raceIncW;
          panX = Math.min(panX, maxPanX);
        }
      }

      const chartSvg = this.shadowRoot.getElementById('chart-svg');
      if (chartSvg) {
        chartSvg.setAttribute('viewBox', `${panX.toFixed(1)} 0 ${windowViewW} ${viewH}`);
      }

      const yAxisLayer = this.shadowRoot.getElementById('y-axis-layer');
      if (yAxisLayer) {
        yAxisLayer.setAttribute('transform', `translate(${panX.toFixed(1)}, 0)`);
      }

      // Update Status / Checkpoint Badge in Toolbar (cached to avoid layout thrashing)
      const stageEl = this.shadowRoot.getElementById('stage-name');
      const stageContainer = this.shadowRoot.getElementById('stage-badge-container');
      if (stageEl && races.length > 0) {
        let newStageHtml = '';
        let newBorderColor = '';
        if (p >= 1.0) {
          const finalRace = races[races.length - 1];
          newStageHtml = `<span style="color:#00E700;">🏁 Final:</span> ${finalRace}`;
          newBorderColor = 'rgba(0, 231, 0, 0.45)';
        } else if (s % 2 === 0) {
          // Plateau interval
          const raceIdx = s / 2;
          newStageHtml = `<span style="color:#00b4da;">Level:</span> ${races[raceIdx] || ''}`;
          newBorderColor = 'rgba(0, 180, 218, 0.35)';
        } else {
          // Transition interval
          const fromIdx = Math.floor(s / 2);
          const toIdx = fromIdx + 1;
          const fromRace = races[fromIdx] || '';
          const toRace = races[toIdx] || '';
          newStageHtml = `<span style="color:#FFB800;">→</span> ${fromRace} to ${toRace}`;
          newBorderColor = 'rgba(255, 184, 0, 0.35)';
        }
        if (this._lastStageHtml !== newStageHtml) {
          stageEl.innerHTML = newStageHtml;
          this._lastStageHtml = newStageHtml;
          if (stageContainer) stageContainer.style.borderColor = newBorderColor;
        }
      }

      // Update SVG Paths and Leading Car Icons
      teams.forEach((team) => {
        const pathEl = this.shadowRoot.getElementById(`path-${team.id}`);
        const carEl = this.shadowRoot.getElementById(`car-group-${team.id}`);
        if (!pathEl || !carEl) return;

        // Construct path string from interval 0 up to s
        const pathCommands = [];
        let currX = plateaus[0].startX;
        let currY = team.racePoints[0].y;

        for (let i = 0; i <= s; i++) {
          if (i % 2 === 0) {
            // Plateau for race j
            const j = i / 2;
            const plat = plateaus[j];
            const y = team.racePoints[j].y;

            if (i === 0) {
              pathCommands.push(`M ${plat.startX.toFixed(1)} ${y.toFixed(1)}`);
            }

            if (i < s) {
              // Completed plateau
              pathCommands.push(`L ${plat.endX.toFixed(1)} ${y.toFixed(1)}`);
              currX = plat.endX;
              currY = y;
            } else {
              // Current active plateau
              currX = plat.startX + f * (plat.endX - plat.startX);
              currY = y;
              pathCommands.push(`L ${currX.toFixed(1)} ${currY.toFixed(1)}`);
            }
          } else {
            // Transition from race j to j+1
            const j = Math.floor(i / 2);
            const platCurr = plateaus[j];
            const platNext = plateaus[j + 1];
            const y0 = team.racePoints[j].y;
            const y1 = team.racePoints[j + 1].y;

            const p0 = { x: platCurr.endX, y: y0 };
            const p3 = { x: platNext.startX, y: y1 };
            const dx = p3.x - p0.x;
            // Exact 1/3 and 2/3 horizontal control points guarantee 100% constant horizontal velocity
            const p1 = { x: p0.x + dx / 3, y: y0 };
            const p2 = { x: p0.x + (2 * dx) / 3, y: y1 };

            if (i < s) {
              // Completed transition - full 6 arguments for C command
              pathCommands.push(
                `C ${p1.x.toFixed(1)} ${p1.y.toFixed(1)}, ${p2.x.toFixed(1)} ${p2.y.toFixed(1)}, ${p3.x.toFixed(1)} ${p3.y.toFixed(1)}`
              );
              currX = p3.x;
              currY = p3.y;
            } else {
              // Active transition using de Casteljau split
              const { q1, q2, q3 } = splitBezier(p0, p1, p2, p3, f);
              currX = q3.x;
              currY = q3.y;
              pathCommands.push(
                `C ${q1.x.toFixed(1)} ${q1.y.toFixed(1)}, ${q2.x.toFixed(1)} ${q2.y.toFixed(1)}, ${q3.x.toFixed(1)} ${q3.y.toFixed(1)}`
              );
            }
          }
        }

        pathEl.setAttribute('d', pathCommands.join(' '));
        carEl.setAttribute('transform', `translate(${currX.toFixed(1)}, ${currY.toFixed(1)})`);

        // Determine current rank for badge
        let currentRank = team.racePoints[0].rank;
        if (s % 2 === 0) {
          const j = s / 2;
          currentRank = team.racePoints[j].rank;
        } else {
          const j = Math.floor(s / 2);
          const r0 = team.racePoints[j].rank;
          const r1 = team.racePoints[j + 1].rank;
          currentRank = f >= 0.5 ? r1 : r0;
        }

        // Update rank badge text only when changed to avoid DOM thrashing
        if (!team._rankTextEl) {
          team._rankTextEl = carEl.querySelector('.car-rank-text');
        }
        const newRankStr = `#${currentRank} ${team.shortName}`;
        if (team._lastRankStr !== newRankStr) {
          if (team._rankTextEl) {
            team._rankTextEl.textContent = newRankStr;
          }
          team._lastRankStr = newRankStr;
        }
      });
    }

    highlightTeam(teamId) {
      if (this.activeTeamId === teamId) {
        this.activeTeamId = null;
      } else {
        this.activeTeamId = teamId;
      }
      PRC_STORE.activeTeamId = this.activeTeamId;
      this.applyTeamHighlight();
    }

    applyTeamHighlight() {
      if (!this.computedLayout) return;
      const { teams } = this.computedLayout;
      teams.forEach((t) => {
        const pathEl = this.shadowRoot.getElementById(`path-${t.id}`);
        const carEl = this.shadowRoot.getElementById(`car-group-${t.id}`);
        if (!pathEl || !carEl) return;

        if (!this.activeTeamId) {
          pathEl.style.opacity = '0.92';
          pathEl.style.strokeWidth = '14';
          carEl.style.opacity = '1.0';
        } else if (t.id === this.activeTeamId) {
          pathEl.style.opacity = '1.0';
          pathEl.style.strokeWidth = '18';
          carEl.style.opacity = '1.0';
        } else {
          pathEl.style.opacity = '0.16';
          pathEl.style.strokeWidth = '10';
          carEl.style.opacity = '0.3';
        }
      });

      const legendItems = this.shadowRoot.querySelectorAll('.prc-legend-item');
      legendItems.forEach((item) => {
        const tId = item.getAttribute('data-team-id');
        if (!this.activeTeamId) {
          item.style.opacity = '1.0';
          item.style.borderColor = '#2A2A34';
          item.style.background = '#1B1B22';
        } else if (tId === this.activeTeamId) {
          item.style.opacity = '1.0';
          item.style.borderColor = '#00b4da';
          item.style.background = '#252532';
        } else {
          item.style.opacity = '0.35';
          item.style.borderColor = '#2A2A34';
          item.style.background = '#1B1B22';
        }
      });
    }

    render() {
      if (!this.chartData || !this.chartData.races || this.chartData.races.length === 0) {
        this.shadowRoot.innerHTML = `
          <style>
            :host { display: block; width: 100%; color: #888; text-align: center; padding: 40px; font-family: 'Outfit', -apple-system, sans-serif; }
          </style>
          <div>No power rankings data available.</div>
        `;
        return;
      }

      const { races, teams } = this.chartData;
      const numRaces = races.length;
      const numTeams = teams.length;

      // Intervals: M plateaus + (M - 1) transitions = 2M - 1 intervals
      const totalIntervals = Math.max(1, 2 * numRaces - 1);

      // Reduced vertical spacing (dy = 44px) now that circular bubbles are removed!
      const dy = 44;
      const marginL = 60;
      const marginR = 120; // room for car (56px) + badge (76px)
      const marginT = 65;
      const marginB = 22;

      // Fixed comfortable step width for race intervals
      const stepW = 130;
      const raceIncW = 2 * stepW;

      // Pan With Cars (TAF1APP-SDDREQ-91): Keep only 3 x-axis increments visible at all times
      // 3 race increments: 2 full race intervals (4 * stepW) + 3rd plateau (stepW) + margins
      const windowViewW = marginL + 5 * stepW + marginR; // 60 + 650 + 120 = 830px

      // Total view width for horizontal grid lines spanning all races
      const totalViewW = marginL + (2 * numRaces - 1) * stepW + marginR;

      const chartH = numTeams > 1 ? (numTeams - 1) * dy : 300;
      const viewH = marginT + chartH + marginB;

      // Compute Plateaus for each race
      const plateaus = [];
      for (let k = 0; k < numRaces; k++) {
        const startX = marginL + 2 * k * stepW;
        const endX = marginL + (2 * k + 1) * stepW;
        const midX = (startX + endX) / 2;
        plateaus.push({
          raceIndex: k,
          raceName: races[k],
          startX,
          endX,
          midX,
          width: endX - startX
        });
      }

      // Compute Team Points
      const processedTeams = teams.map((t, tIdx) => {
        const teamId = `team-${t.name.replace(/[^a-zA-Z0-9]/g, '_')}`;
        const racePoints = [];

        races.forEach((rName, rIdx) => {
          const rObj = t.rankings ? t.rankings.find((item) => item.race === rName) : null;
          const rank = rObj ? rObj.rank : tIdx + 1;
          const y = marginT + (rank - 1) * dy;
          racePoints.push({
            raceName: rName,
            raceIndex: rIdx,
            rank: rank,
            y: y
          });
        });

        const initialRank = racePoints[0].rank;
        const finalRank = racePoints[racePoints.length - 1].rank;
        const delta = initialRank - finalRank;

        const hasIcon = Boolean(t.has_icon !== false && t.icon && t.icon.length > 0);

        return {
          id: teamId,
          name: t.name,
          shortName: t.short_name || t.name.slice(0, 3).toUpperCase(),
          color: t.color || '#00b4da',
          icon: t.icon || '',
          hasIcon: hasIcon,
          racePoints,
          initialRank,
          finalRank,
          delta
        };
      });

      this.computedLayout = {
        races,
        teams: processedTeams,
        plateaus,
        totalIntervals,
        dy,
        marginT,
        marginL,
        marginR,
        viewW: windowViewW,
        windowViewW,
        totalViewW,
        viewH,
        chartH,
        stepW,
        raceIncW,
        numRaces,
        numTeams
      };

      this.shadowRoot.innerHTML = `
        <style>
          :host {
            display: block;
            width: 100%;
            max-width: 100%;
            font-family: 'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            color: #FFFFFF;
            user-select: none;
            box-sizing: border-box;
          }

          * {
            box-sizing: border-box;
          }

          .prc-container {
            width: 100%;
            max-width: 100%;
            overflow-x: hidden;
            display: flex;
            flex-direction: column;
            gap: 10px;
          }

          /* Control Toolbar */
          .prc-toolbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 10px;
            background: #141418;
            border: 1px solid #28282E;
            padding: 9px 14px;
            border-radius: 12px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
            max-width: 100%;
          }

          .prc-controls-group {
            display: flex;
            align-items: center;
            gap: 8px;
          }

          /* Compact toolbar buttons */
          .prc-btn {
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 7px !important;
            background: #202026;
            color: #FFFFFF;
            border: 1px solid #32323A;
            border-radius: 8px;
            padding: 0 13px !important;
            height: 36px !important;
            max-height: 36px !important;
            width: auto !important;
            font-size: 13px !important;
            font-weight: 700 !important;
            cursor: pointer;
            box-sizing: border-box !important;
            line-height: 1 !important;
            transition: all 0.18s ease;
          }

          .prc-btn * {
            pointer-events: none;
          }

          .prc-btn:hover {
            background: #2A2A33;
            border-color: #00b4da;
            color: #00b4da;
            transform: translateY(-1px);
          }

          .prc-btn:active {
            transform: translateY(0);
          }

          .prc-play-btn {
            min-width: 90px !important;
            background: #00b4da !important;
            color: #0A0A0C !important;
            border-color: #00b4da !important;
          }

          .prc-play-btn:hover {
            background: #1ed0f7 !important;
            border-color: #1ed0f7 !important;
            color: #0A0A0C !important;
          }

          .prc-btn svg {
            display: inline-block !important;
            width: 15px !important;
            height: 15px !important;
            min-width: 15px !important;
            max-width: 15px !important;
            min-height: 15px !important;
            max-height: 15px !important;
            flex-shrink: 0 !important;
            vertical-align: middle !important;
          }

          .prc-btn span {
            display: inline-block !important;
            font-size: 13px !important;
            font-weight: 700 !important;
            line-height: 1 !important;
          }

          /* Scrubber Track */
          .prc-scrubber-container {
            display: flex;
            align-items: center;
            gap: 10px;
            flex: 1 1 160px;
            min-width: 120px;
            margin: 0;
          }

          .prc-slider {
            -webkit-appearance: none;
            appearance: none;
            width: 100%;
            height: 7px;
            border-radius: 4px;
            background: #2C2C32;
            outline: none;
            cursor: pointer;
            transition: background 0.1s;
          }

          .prc-slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 19px;
            height: 19px;
            border-radius: 50%;
            background: #FFFFFF;
            border: 3px solid #00b4da;
            box-shadow: 0 0 10px rgba(0, 180, 218, 0.85);
            cursor: pointer;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
          }

          .prc-slider::-webkit-slider-thumb:hover {
            transform: scale(1.2);
            box-shadow: 0 0 14px rgba(0, 180, 218, 1.0);
          }

          .prc-slider::-moz-range-thumb {
            width: 19px;
            height: 19px;
            border-radius: 50%;
            background: #FFFFFF;
            border: 3px solid #00b4da;
            box-shadow: 0 0 10px rgba(0, 180, 218, 0.85);
            cursor: pointer;
          }

          /* Stage Badge */
          .prc-stage-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: #1A1A22;
            border: 1px solid #30303C;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 700;
            color: #C0C0C8;
            white-space: nowrap;
            transition: border-color 0.25s ease;
          }

          /* SVG Container: Scales cleanly on mobile, zero horizontal scroll */
          .prc-svg-wrapper {
            position: relative;
            width: 100%;
            max-width: 100%;
            overflow: hidden;
            border-radius: 14px;
            background: #15151A;
            border: 1px solid #28282E;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45);
            padding: 6px 0 10px 0;
          }

          #chart-svg {
            display: block;
            width: 100%;
            height: auto;
            max-width: 100%;
            overflow: hidden;
          }

          .grid-line {
            stroke: rgba(255, 255, 255, 0.08);
            stroke-width: 1.2;
          }

          .state-column-bg {
            fill: rgba(255, 255, 255, 0.025);
            stroke: rgba(255, 255, 255, 0.06);
            stroke-width: 1;
            rx: 8;
          }

          .y-axis-badge {
            fill: #1A1A22;
            stroke: rgba(255, 255, 255, 0.16);
            stroke-width: 1.2;
            rx: 6;
          }

          .y-axis-label {
            fill: #9E9EA8;
            font-size: 13px;
            font-weight: 800;
            font-family: 'Outfit', sans-serif;
            text-anchor: middle;
            dominant-baseline: central;
          }

          /* Top State Column Badges (>= 12pt font = 16px) */
          .state-header-pill {
            fill: #1B1B24;
            stroke: #343444;
            stroke-width: 1.2;
            rx: 16;
          }

          .state-header-title {
            fill: #FFFFFF;
            font-size: 16px; /* 12pt */
            font-weight: 800;
            letter-spacing: 0.5px;
            font-family: 'Outfit', sans-serif;
            text-anchor: middle;
            dominant-baseline: central;
          }

          .team-path {
            fill: none;
            stroke-width: 14;
            stroke-linecap: round;
            stroke-linejoin: round;
            opacity: 0.92;
            cursor: pointer;
            transition: stroke-width 0.2s ease, opacity 0.2s ease;
            filter: drop-shadow(0 2px 5px rgba(0, 0, 0, 0.45));
          }

          .team-path:hover {
            opacity: 1.0 !important;
            stroke-width: 18 !important;
          }

          .car-group {
            cursor: pointer;
            transition: opacity 0.2s ease;
          }

          /* Rank & Name Badge */
          .car-rank-badge {
            fill: #111116;
            stroke: rgba(255, 255, 255, 0.25);
            stroke-width: 1.3;
            rx: 5;
          }

          .car-rank-text {
            fill: #FFFFFF;
            font-size: 13px;
            font-weight: 800;
            letter-spacing: 0.4px;
            font-family: 'Outfit', sans-serif;
            text-anchor: start;
            dominant-baseline: central;
          }

          /* Bottom Legend Bar */
          .prc-info-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 8px;
            background: #141418;
            border: 1px solid #28282E;
            padding: 7px 12px;
            border-radius: 10px;
            font-size: 12px;
            color: #9A9AA4;
            max-width: 100%;
            overflow-x: auto;
          }

          .prc-legend {
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 7px;
          }

          .prc-legend-item {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            cursor: pointer;
            padding: 3px 7px;
            border-radius: 6px;
            background: #1B1B22;
            border: 1px solid #2A2A34;
            font-size: 12px;
            font-weight: 700;
            color: #FFFFFF;
            transition: all 0.15s ease;
          }

          .prc-legend-item:hover {
            border-color: #00b4da;
            color: #00b4da;
            transform: translateY(-1px);
          }

          .prc-legend-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
          }
        </style>

        <div class="prc-container">
          <!-- Toolbar -->
          <div class="prc-toolbar">
            <div class="prc-controls-group">
              <button id="play-btn" class="prc-btn prc-play-btn" aria-label="Play">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <polygon points="6 3 20 12 6 21 6 3"></polygon>
                </svg>
                <span>Play</span>
              </button>
              <button id="speed-btn" class="prc-btn" aria-label="Playback Speed">1x</button>
            </div>

            <!-- Scrubber -->
            <div class="prc-scrubber-container">
              <input type="range" id="scrubber" class="prc-slider" min="0" max="1000" value="0" aria-label="Animation Scrubber">
            </div>

            <!-- Stage Badge -->
            <div id="stage-badge-container" class="prc-stage-badge">
              <span id="stage-name"><span style="color:#00b4da;">Level:</span> ${races[0] || 'Start'}</span>
            </div>
          </div>

          <!-- SVG Chart (Pan With Cars: TAF1APP-SDDREQ-91 - keeping only 3 increments visible at all times) -->
          <div class="prc-svg-wrapper">
            <svg id="chart-svg" viewBox="0 0 ${windowViewW} ${viewH}" preserveAspectRatio="xMidYMid meet">
              <defs>
                <filter id="car-glow" x="-20%" y="-20%" width="140%" height="140%">
                  <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#000" flood-opacity="0.8" />
                </filter>
              </defs>

              <!-- State Column Background Shading & Horizontal Headers -->
              ${plateaus.map((plat) => `
                <rect class="state-column-bg" x="${plat.startX}" y="${marginT - 14}" width="${plat.width}" height="${chartH + 28}" />
                <line x1="${plat.midX}" y1="${marginT - 14}" x2="${plat.midX}" y2="${marginT + chartH + 14}" stroke="rgba(255,255,255,0.05)" stroke-dasharray="4 4" />
                
                <!-- Column Header Pill at Top -->
                <rect class="state-header-pill" x="${plat.midX - 68}" y="${marginT - 48}" width="136" height="34" />
                <text class="state-header-title" x="${plat.midX}" y="${marginT - 31}">${plat.raceName.toUpperCase()}</text>
              `).join('')}

              <!-- Horizontal Rank Grid Lines spanning totalViewW -->
              <g id="grid-layer">
                ${Array.from({ length: numTeams }).map((_, r) => {
                  const y = marginT + r * dy;
                  return `<line class="grid-line" x1="0" y1="${y}" x2="${totalViewW}" y2="${y}"></line>`;
                }).join('')}
              </g>

              <!-- Team Trajectory Paths -->
              <g id="paths-layer">
                ${processedTeams.map(team => `
                  <path id="path-${team.id}" class="team-path" stroke="${team.color}" d=""></path>
                `).join('')}
              </g>

              <!-- Leading Car Icons & Badges -->
              <g id="cars-layer">
                ${processedTeams.map(team => `
                  <g id="car-group-${team.id}" class="car-group" transform="translate(-100, -100)" filter="url(#car-glow)">
                    ${team.hasIcon ? `
                      <!-- Car Icon Graphic mirrored horizontally (1:1 mirror, facing forward right) -->
                      <g transform="scale(-1, 1)">
                        <image href="${team.icon}" x="-28" y="-13" width="56" height="26" preserveAspectRatio="xMidYMid meet" onerror="this.style.display='none'; if(this.parentElement.nextElementSibling) this.parentElement.nextElementSibling.style.display='block';" />
                      </g>
                    ` : `
                      <!-- Team colored circle fallback -->
                      <circle cx="0" cy="0" r="11" fill="${team.color}" stroke="#FFFFFF" stroke-width="2" />
                    `}
                    ${team.hasIcon ? `<circle cx="0" cy="0" r="11" fill="${team.color}" stroke="#FFFFFF" stroke-width="2" style="display:none;" />` : ''}
                    <!-- Compact Rank & Code Badge -->
                    <rect class="car-rank-badge" x="30" y="-12" width="76" height="24" />
                    <text class="car-rank-text" x="36" y="0">#1 ${team.shortName}</text>
                  </g>
                `).join('')}
              </g>

              <!-- Pinned Left Y-Axis Badges with dark mask -->
              <g id="y-axis-layer" transform="translate(0, 0)">
                <rect x="-10" y="0" width="${marginL - 4 + 10}" height="${viewH}" fill="#15151A" />
                ${Array.from({ length: numTeams }).map((_, r) => {
                  const y = marginT + r * dy;
                  return `
                    <rect class="y-axis-badge" x="${marginL - 38}" y="${y - 12}" width="28" height="24" />
                    <text class="y-axis-label" x="${marginL - 24}" y="${y}">#${r + 1}</text>
                  `;
                }).join('')}
              </g>
            </svg>
          </div>

          <!-- Bottom Legend & Team Filter Bar -->
          <div class="prc-info-bar">
            <span>Click constructor to highlight:</span>
            <div class="prc-legend">
              ${processedTeams.map(t => `
                <div class="prc-legend-item" data-team-id="${t.id}" title="${t.name}: Initial #${t.initialRank} → Final #${t.finalRank} (${t.delta > 0 ? '+' + t.delta : t.delta === 0 ? 'Equal' : t.delta})">
                  <span class="prc-legend-dot" style="background-color: ${t.color};"></span>
                  <span>${t.shortName}</span>
                  <span style="opacity: 0.75; font-size: 11px;">#${t.finalRank}</span>
                </div>
              `).join('')}
            </div>
          </div>
        </div>
      `;

      // Attach event listeners
      const playBtn = this.shadowRoot.getElementById('play-btn');
      if (playBtn) playBtn.addEventListener('click', this.onPlayPauseClick);

      const speedBtn = this.shadowRoot.getElementById('speed-btn');
      if (speedBtn) speedBtn.addEventListener('click', this.onSpeedClick);

      const scrubber = this.shadowRoot.getElementById('scrubber');
      if (scrubber) {
        scrubber.addEventListener('input', this.onSliderInput);
        scrubber.addEventListener('change', this.onSliderChange);
      }

      // Legend and Team Click Highlights
      const legendItems = this.shadowRoot.querySelectorAll('.prc-legend-item');
      legendItems.forEach((item) => {
        item.addEventListener('click', () => {
          const teamId = item.getAttribute('data-team-id');
          this.highlightTeam(teamId);
        });
      });

      processedTeams.forEach((t) => {
        const pathEl = this.shadowRoot.getElementById(`path-${t.id}`);
        const carEl = this.shadowRoot.getElementById(`car-group-${t.id}`);
        if (pathEl) {
          pathEl.addEventListener('click', () => this.highlightTeam(t.id));
        }
        if (carEl) {
          carEl.addEventListener('click', () => this.highlightTeam(t.id));
        }
      });

      this.updatePlayBtnVisual();
      this.applyTeamHighlight();
    }
  }

  // Register Custom Element
  if (!customElements.get('power-rankings-chart')) {
    customElements.define('power-rankings-chart', PowerRankingsChart);
  }
})();

/**
 * The Alternative F1 - Interactive Image & GIF Carousel Web Component
 * Features:
 * - Touch and mouse drag swipe gestures
 * - Left and right side click navigation & chevron buttons
 * - 5-second automatic progression with animated progress bar
 * - Pause on hover / touch interaction
 * - Pagination dots and item counter
 * - Support for responsive images and animated GIFs
 */

(function () {
  if (customElements.get('f1-carousel')) return;

  class F1Carousel extends HTMLElement {
    constructor() {
      super();
      this.attachShadow({ mode: 'open' });
      this.currentIndex = 0;
      this.items = [];
      this.autoProgressMs = 5000;
      this.timer = null;
      this.animFrame = null;
      this.progressStartTime = null;
      this.isPaused = false;
      this.touchStartX = 0;
      this.touchStartY = 0;
      this.touchDeltaX = 0;
      this.isDragging = false;
      this.swipeThreshold = 40;
    }

    static get observedAttributes() {
      return ['data-items', 'auto-progress'];
    }

    attributeChangedCallback(name, oldValue, newValue) {
      if (oldValue !== newValue) {
        if (name === 'data-items') {
          this.parseItems();
          this.render();
        } else if (name === 'auto-progress') {
          const val = parseInt(newValue, 10);
          if (!isNaN(val) && val > 0) {
            this.autoProgressMs = val;
            this.restartTimer();
          }
        }
      }
    }

    connectedCallback() {
      this.parseItems();
      this.render();
      this.startTimer();
    }

    disconnectedCallback() {
      this.stopTimer();
    }

    parseItems() {
      const raw = this.getAttribute('data-items');
      if (!raw) {
        this.items = [];
        return;
      }
      try {
        const parsed = JSON.parse(raw);
        this.items = Array.isArray(parsed)
          ? parsed.map((item) => {
              if (typeof item === 'string') return { src: item, caption: '' };
              return { src: item.src || '', caption: item.caption || item.title || '' };
            })
          : [];
      } catch (e) {
        console.error('f1-carousel: Failed to parse data-items JSON', e);
        this.items = [];
      }
      const autoProgAttr = this.getAttribute('auto-progress');
      if (autoProgAttr) {
        const val = parseInt(autoProgAttr, 10);
        if (!isNaN(val) && val > 0) this.autoProgressMs = val;
      }
    }

    render() {
      if (!this.shadowRoot) return;
      if (this.items.length === 0) {
        this.shadowRoot.innerHTML = `
          <style>
            :host { display: block; width: 100%; }
            .empty { color: #888; text-align: center; padding: 40px 0; font-family: 'Outfit', sans-serif; }
          </style>
          <div class="empty">No carousel items provided.</div>
        `;
        return;
      }

      this.shadowRoot.innerHTML = `
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap');

          :host {
            display: block;
            position: relative;
            width: 100%;
            height: 100%;
            user-select: none;
            -webkit-user-select: none;
            font-family: 'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            box-sizing: border-box;
          }

          *, *::before, *::after {
            box-sizing: border-box;
          }

          .carousel-container {
            position: relative;
            width: 100%;
            height: 100%;
            background: #111115;
            border-radius: inherit;
            overflow: hidden;
            border: 1px solid #2C2C32;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45);
            display: flex;
            align-items: center;
            justify-content: center;
          }

          .slides-track {
            display: flex;
            height: 100%;
            width: 100%;
            align-items: center;
            justify-content: flex-start;
            transition: transform 0.4s cubic-bezier(0.22, 1, 0.36, 1);
            will-change: transform;
          }

          .slide {
            flex: 0 0 100%;
            width: 100%;
            height: 100%;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #0b0b0e;
            overflow: hidden;
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            text-align: center;
          }

          .slide-img {
            max-width: 100%;
            max-height: 100%;
            width: 100%;
            height: 100%;
            object-fit: contain;
            object-position: center center;
            margin: auto;
            display: block;
            pointer-events: none;
          }

          /* Click Zones */
          .click-zone {
            position: absolute;
            top: 0;
            bottom: 0;
            width: 25%;
            z-index: 10;
            cursor: pointer;
            display: flex;
            align-items: center;
            opacity: 0.85;
            transition: opacity 0.2s ease;
          }

          .click-zone:hover {
            opacity: 1;
          }

          .click-zone-left {
            left: 0;
            justify-content: flex-start;
            padding-left: 16px;
          }

          .click-zone-right {
            right: 0;
            justify-content: flex-end;
            padding-right: 16px;
          }

          .nav-btn {
            width: 44px;
            height: 44px;
            border-radius: 50%;
            background: rgba(20, 20, 26, 0.75);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.18);
            color: #ffffff;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.5);
            transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
            pointer-events: auto;
          }

          .nav-btn svg {
            width: 22px;
            height: 22px;
            stroke-width: 2.5;
            stroke: currentColor;
            fill: none;
            stroke-linecap: round;
            stroke-linejoin: round;
          }

          .click-zone:hover .nav-btn,
          .nav-btn:hover {
            background: #00b4da;
            border-color: #00b4da;
            color: #ffffff;
            transform: scale(1.12);
            box-shadow: 0 4px 18px rgba(0, 180, 218, 0.55);
          }

          /* Top Info Bar (Counter & Auto Indicator) */
          .top-bar {
            position: absolute;
            top: 14px;
            right: 14px;
            z-index: 20;
            display: flex;
            align-items: center;
            gap: 8px;
            pointer-events: none;
          }

          .counter-pill {
            background: rgba(15, 15, 18, 0.8);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: #e2e8f0;
            font-size: 11px;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 20px;
            letter-spacing: 0.5px;
          }

          /* Caption */
          .caption-bar {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 36px 20px 24px;
            background: linear-gradient(to top, rgba(10, 10, 14, 0.92) 0%, rgba(10, 10, 14, 0.5) 60%, transparent 100%);
            color: #ffffff;
            font-size: 14px;
            font-weight: 600;
            letter-spacing: 0.2px;
            text-align: center;
            pointer-events: none;
            z-index: 15;
            text-shadow: 0 1px 4px rgba(0, 0, 0, 0.9);
            line-height: 1.4;
          }

          /* Dots Indicator */
          .dots-container {
            position: absolute;
            bottom: 10px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            align-items: center;
            gap: 8px;
            z-index: 25;
            padding: 4px 10px;
            background: rgba(15, 15, 18, 0.65);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.08);
          }

          .dot {
            width: 8px;
            height: 8px;
            border-radius: 4px;
            background: rgba(255, 255, 255, 0.4);
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
          }

          .dot:hover {
            background: rgba(255, 255, 255, 0.8);
          }

          .dot.active {
            width: 22px;
            background: #00b4da;
            box-shadow: 0 0 10px rgba(0, 180, 218, 0.7);
          }

          /* Progress Bar */
          .progress-bar-container {
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background: rgba(255, 255, 255, 0.08);
            z-index: 30;
          }

          .progress-bar-fill {
            height: 100%;
            width: 0%;
            background: #00b4da;
            box-shadow: 0 0 8px #00b4da;
            will-change: width;
          }

          @media (max-width: 640px) {
            .nav-btn {
              width: 36px;
              height: 36px;
            }
            .nav-btn svg {
              width: 18px;
              height: 18px;
            }
            .click-zone {
              width: 35%;
            }
            .click-zone-left {
              padding-left: 8px;
            }
            .click-zone-right {
              padding-right: 8px;
            }
            .caption-bar {
              font-size: 12px;
              padding: 28px 12px 20px;
            }
          }
        </style>

        <div class="carousel-container" id="container">
          <div class="slides-track" id="track">
            ${this.items
              .map(
                (item, idx) => `
                <div class="slide" data-index="${idx}">
                  <img class="slide-img" src="${item.src}" alt="${item.caption || 'Slide ' + (idx + 1)}" loading="lazy" />
                </div>
              `
              )
              .join('')}
          </div>

          <!-- Left Click Zone & Chevron -->
          <div class="click-zone click-zone-left" id="zone-left" title="Previous Image (Click or Swipe)">
            <button class="nav-btn" id="btn-prev" aria-label="Previous image">
              <svg viewBox="0 0 24 24"><polyline points="15 18 9 12 15 6"></polyline></svg>
            </button>
          </div>

          <!-- Right Click Zone & Chevron -->
          <div class="click-zone click-zone-right" id="zone-right" title="Next Image (Click or Swipe)">
            <button class="nav-btn" id="btn-next" aria-label="Next image">
              <svg viewBox="0 0 24 24"><polyline points="9 18 15 12 9 6"></polyline></svg>
            </button>
          </div>

          <!-- Counter Pill -->
          <div class="top-bar">
            <div class="counter-pill" id="counter">1 / ${this.items.length}</div>
          </div>

          <!-- Caption Bar -->
          <div class="caption-bar" id="caption" style="display: ${this.items[0] && this.items[0].caption ? 'block' : 'none'};">
            ${(this.items[0] && this.items[0].caption) || ''}
          </div>

          <!-- Dots Indicator -->
          <div class="dots-container" id="dots">
            ${this.items
              .map(
                (_, idx) => `
                <div class="dot ${idx === 0 ? 'active' : ''}" data-index="${idx}" title="Go to slide ${idx + 1}"></div>
              `
              )
              .join('')}
          </div>

          <!-- Auto-Progress Bar -->
          <div class="progress-bar-container">
            <div class="progress-bar-fill" id="progress-fill"></div>
          </div>
        </div>
      `;

      this.bindEvents();
      this.updateSlide(0, false);
    }

    bindEvents() {
      const root = this.shadowRoot;
      if (!root) return;

      const container = root.getElementById('container');
      const track = root.getElementById('track');
      const zoneLeft = root.getElementById('zone-left');
      const zoneRight = root.getElementById('zone-right');
      const btnPrev = root.getElementById('btn-prev');
      const btnNext = root.getElementById('btn-next');
      const dots = root.querySelectorAll('.dot');

      // Click on left zone or prev button
      zoneLeft.addEventListener('click', (e) => {
        e.stopPropagation();
        this.prev();
        this.restartTimer();
      });

      // Click on right zone or next button
      zoneRight.addEventListener('click', (e) => {
        e.stopPropagation();
        this.next();
        this.restartTimer();
      });

      // Click on indicator dots
      dots.forEach((dot) => {
        dot.addEventListener('click', (e) => {
          e.stopPropagation();
          const targetIndex = parseInt(dot.getAttribute('data-index'), 10);
          if (!isNaN(targetIndex)) {
            this.goTo(targetIndex);
            this.restartTimer();
          }
        });
      });

      // Pause auto-progression on mouse hover
      container.addEventListener('mouseenter', () => {
        this.isPaused = true;
      });
      container.addEventListener('mouseleave', () => {
        this.isPaused = false;
        this.progressStartTime = performance.now() - (this.pausedProgress || 0) * this.autoProgressMs;
      });

      // Touch events for swiping
      container.addEventListener(
        'touchstart',
        (e) => {
          if (e.touches.length === 1) {
            this.touchStartX = e.touches[0].clientX;
            this.touchStartY = e.touches[0].clientY;
            this.touchDeltaX = 0;
            this.isDragging = true;
            this.isPaused = true;
            track.style.transition = 'none';
          }
        },
        { passive: true }
      );

      container.addEventListener(
        'touchmove',
        (e) => {
          if (!this.isDragging || e.touches.length !== 1) return;
          const currentX = e.touches[0].clientX;
          const currentY = e.touches[0].clientY;
          const deltaX = currentX - this.touchStartX;
          const deltaY = currentY - this.touchStartY;

          // If horizontal gesture is dominant, prevent page scrolling
          if (Math.abs(deltaX) > Math.abs(deltaY)) {
            this.touchDeltaX = deltaX;
            const offset = -this.currentIndex * 100 + (deltaX / container.offsetWidth) * 100;
            track.style.transform = `translateX(${offset}%)`;
          }
        },
        { passive: true }
      );

      container.addEventListener('touchend', () => {
        if (!this.isDragging) return;
        this.isDragging = false;
        this.isPaused = false;
        track.style.transition = 'transform 0.4s cubic-bezier(0.22, 1, 0.36, 1)';

        if (this.touchDeltaX < -this.swipeThreshold) {
          // Swiped left -> next
          this.next();
        } else if (this.touchDeltaX > this.swipeThreshold) {
          // Swiped right -> prev
          this.prev();
        } else {
          // Snap back
          this.updateSlide(this.currentIndex);
        }
        this.touchDeltaX = 0;
        this.restartTimer();
      });

      // Mouse drag gestures (for desktop swiping)
      let mouseStartX = 0;
      let mouseDeltaX = 0;
      let isMouseDown = false;

      container.addEventListener('mousedown', (e) => {
        // Only trigger on primary button
        if (e.button !== 0) return;
        // Don't drag if clicking buttons directly
        if (e.target.closest('.nav-btn') || e.target.closest('.dot')) return;

        isMouseDown = true;
        mouseStartX = e.clientX;
        mouseDeltaX = 0;
        track.style.transition = 'none';
      });

      window.addEventListener('mousemove', (e) => {
        if (!isMouseDown) return;
        mouseDeltaX = e.clientX - mouseStartX;
        const offset = -this.currentIndex * 100 + (mouseDeltaX / container.offsetWidth) * 100;
        track.style.transform = `translateX(${offset}%)`;
      });

      window.addEventListener('mouseup', (e) => {
        if (!isMouseDown) return;
        isMouseDown = false;
        track.style.transition = 'transform 0.4s cubic-bezier(0.22, 1, 0.36, 1)';

        if (mouseDeltaX < -this.swipeThreshold) {
          this.next();
          this.restartTimer();
        } else if (mouseDeltaX > this.swipeThreshold) {
          this.prev();
          this.restartTimer();
        } else {
          this.updateSlide(this.currentIndex);
        }
        mouseDeltaX = 0;
      });

      // Keyboard navigation when focused
      container.setAttribute('tabindex', '0');
      container.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft') {
          this.prev();
          this.restartTimer();
        } else if (e.key === 'ArrowRight') {
          this.next();
          this.restartTimer();
        }
      });
    }

    updateSlide(index, animate = true) {
      if (this.items.length === 0) return;
      this.currentIndex = ((index % this.items.length) + this.items.length) % this.items.length;

      const root = this.shadowRoot;
      if (!root) return;

      const track = root.getElementById('track');
      if (track) {
        if (!animate) track.style.transition = 'none';
        track.style.transform = `translateX(-${this.currentIndex * 100}%)`;
        if (!animate) {
          // Force layout reflow
          void track.offsetHeight;
          track.style.transition = 'transform 0.4s cubic-bezier(0.22, 1, 0.36, 1)';
        }
      }

      // Update counter pill
      const counter = root.getElementById('counter');
      if (counter) {
        counter.textContent = `${this.currentIndex + 1} / ${this.items.length}`;
      }

      // Update caption
      const caption = root.getElementById('caption');
      if (caption) {
        const currentItem = this.items[this.currentIndex];
        if (currentItem && currentItem.caption) {
          caption.textContent = currentItem.caption;
          caption.style.display = 'block';
        } else {
          caption.style.display = 'none';
        }
      }

      // Update dots
      const dots = root.querySelectorAll('.dot');
      dots.forEach((dot, idx) => {
        dot.classList.toggle('active', idx === this.currentIndex);
      });
    }

    next() {
      this.updateSlide(this.currentIndex + 1);
    }

    prev() {
      this.updateSlide(this.currentIndex - 1);
    }

    goTo(index) {
      this.updateSlide(index);
    }

    startTimer() {
      this.stopTimer();
      this.progressStartTime = performance.now();
      this.pausedProgress = 0;

      const tick = (now) => {
        if (!this.isConnected) return;

        if (!this.isPaused) {
          const elapsed = now - this.progressStartTime;
          const progress = Math.min(elapsed / this.autoProgressMs, 1);

          const root = this.shadowRoot;
          if (root) {
            const progressFill = root.getElementById('progress-fill');
            if (progressFill) {
              progressFill.style.width = `${progress * 100}%`;
            }
          }

          if (elapsed >= this.autoProgressMs) {
            this.next();
            this.progressStartTime = now;
          }
        } else {
          // Update paused progress ratio so resuming is seamless
          const root = this.shadowRoot;
          if (root) {
            const progressFill = root.getElementById('progress-fill');
            if (progressFill) {
              const currentWidth = parseFloat(progressFill.style.width) || 0;
              this.pausedProgress = currentWidth / 100;
            }
          }
        }

        this.animFrame = requestAnimationFrame(tick);
      };

      this.animFrame = requestAnimationFrame(tick);
    }

    stopTimer() {
      if (this.animFrame) {
        cancelAnimationFrame(this.animFrame);
        this.animFrame = null;
      }
    }

    restartTimer() {
      const root = this.shadowRoot;
      if (root) {
        const progressFill = root.getElementById('progress-fill');
        if (progressFill) progressFill.style.width = '0%';
      }
      this.progressStartTime = performance.now();
      this.pausedProgress = 0;
    }
  }

  customElements.define('f1-carousel', F1Carousel);
})();

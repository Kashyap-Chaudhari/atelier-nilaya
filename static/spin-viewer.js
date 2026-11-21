/**
 * ============================================================================
 * ATELIER NILAYA — LUXURY 360° SPIN VIEWER ENGINE (spin-viewer.js)
 * High Jewellery Photographic Turntable Controller (Vanilla JS, Zero Frameworks)
 * 
 * Features:
 * - Direct photographic 36-frame sequence scrub (no procedural 3D).
 * - Drag left/right with momentum / inertia on release.
 * - Gentle auto-rotate once on first viewport entry (skipped if prefers-reduced-motion).
 * - Arrow keys step 1 frame forward/backward.
 * - Vertical touch swipes pass through to page scroll (touch-action: pan-y).
 * - Viewport preloading: frame 001 on load, frames 002-036 via IntersectionObserver(rootMargin: 200px).
 * - Instant metal dot switching with dynamic price & discount update.
 * - 12-frame minimum requirement: hides 360 badge and disables rotation if < 12 frames.
 * - Hover second view for lifestyle photography (worn on hand/neck).
 * - Fallback order: 360 Spin -> front.webp -> Neutral "Photo coming soon" tile.
 * - Full console logging of any 404 or missing image URLs.
 * ============================================================================
 */

(function (window, document) {
  'use strict';

  // Check for reduced motion preference
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Single Shared IntersectionObserver for preloading frames near viewport
  let preloadObserver = null;
  const activeViewers = new Map(); // element -> SpinViewer instance

  /**
   * Helper to format 3-digit padded number: 1 -> "001"
   */
  function pad3(num) {
    return num.toString().padStart(3, '0');
  }

  /**
   * Normalize metal string: 'yellow-gold' -> 'yellow_gold'
   */
  function normalizeMetal(metal) {
    if (!metal) return 'yellow_gold';
    const clean = metal.toString().trim().toLowerCase().replace(/-/g, '_');
    if (clean === 'yellow' || clean === 'gold') return 'yellow_gold';
    if (clean === 'rose') return 'rose_gold';
    if (clean === 'white_gold' || clean === 'white') return 'platinum';
    return clean;
  }

  /**
   * Helper to format Indian Rupee currency: 382950 -> "₹3,82,950"
   */
  function formatINR(price) {
    if (!price && price !== 0) return '';
    const rounded = Math.round(Number(price));
    const str = rounded.toString();
    if (str.length <= 3) return '₹' + str;
    const lastThree = str.substring(str.length - 3);
    const otherNumbers = str.substring(0, str.length - 3);
    const formatted = otherNumbers.replace(/\B(?=(\d{2})+(?!\d))/g, ',') + ',' + lastThree;
    return '₹' + formatted;
  }

  /**
   * Main SpinViewer Class
   */
  class SpinViewer {
    constructor(containerEl, options = {}) {
      this.container = containerEl;
      this.options = Object.assign({
        totalFrames: 36,
        pixelsPerFrame: 10,
        inertiaFriction: 0.92,
        autoRotateSpeedMs: 45
      }, options);

      this.slug = this.container.getAttribute('data-product-slug') || '';
      this.currentMetal = normalizeMetal(this.container.getAttribute('data-current-metal') || 'yellow_gold');
      this.currentFrame = 1;
      this.fallbackStep = 0; // 0 = spin 001, 1 = front still, 2 = fallback tile

      // Metals metadata map
      this.tileRoot = this.container.closest('.product-tile') || this.container.closest('.product-page-container') || this.container.parentElement;
      this.metalsData = {};
      const metalsJson = this.container.getAttribute('data-metals') || (this.tileRoot && this.tileRoot.getAttribute('data-metals'));
      if (metalsJson) {
        try {
          this.metalsData = JSON.parse(metalsJson);
        } catch (e) {
          console.warn('[Atelier Nilaya] Could not parse metals JSON:', e);
        }
      }

      // Frame count and 12-frame minimum check
      const currentMetalInfo = this.metalsData[this.currentMetal];
      const framesAttr = this.container.getAttribute('data-spin-frames');
      const framesCount = (currentMetalInfo && typeof currentMetalInfo.frames === 'number') 
        ? currentMetalInfo.frames 
        : (framesAttr !== null ? parseInt(framesAttr, 10) : 36);

      this.totalFrames = isNaN(framesCount) ? 0 : framesCount;
      this.canSpin = this.totalFrames >= 12;

      // Preloaded image caches: { metal: { 1: HTMLImageElement, ... } }
      this.imageCache = {};
      this.isFullyPreloaded = false;
      this.hasAutoRotated = false;
      this.autoRotateActive = false;
      this.autoRotateTimeout = null;

      // Drag & Inertia state
      this.isDragging = false;
      this.dragStartX = 0;
      this.dragStartY = 0;
      this.lastDragX = 0;
      this.velocity = 0;
      this.isHorizontalDrag = false;
      this.dragThresholdPassed = false;
      this.inertiaRAF = null;

      // Elements
      this.imgEl = this.container.querySelector('.spin-active-img');
      this.lifestyleImgEl = this.container.querySelector('.spin-lifestyle-img');
      this.fallbackTileEl = this.container.querySelector('.spin-fallback-tile');
      this.indicatorEl = this.container.querySelector('.spin-360-badge');

      // Price & Badge elements (within same product tile or page container)
      this.priceEl = this.tileRoot ? this.tileRoot.querySelector('.tile-current-price, [data-price-display], .tile-price-current, #product-price-display') : null;
      this.oldPriceEl = this.tileRoot ? this.tileRoot.querySelector('.tile-old-price, [data-old-price-display], .tile-price-old, #product-old-price-display') : null;
      this.saveBadgeEl = this.tileRoot ? this.tileRoot.querySelector('.tile-discount-badge, [data-discount-badge], .tile-save-badge, #product-save-badge') : null;

      this.init();
    }

    init() {
      if (!this.imgEl) return;

      // Enforce 360 badge display condition: minimum 12 frames
      this.updateSpinBadge();

      // Initial frame setup
      this.renderFrame(1);

      // Event bindings
      this.bindDragEvents();
      this.bindKeyboardEvents();
      this.bindHoverEvents();
      this.bindMetalDots();

      // Register with active viewers
      activeViewers.set(this.container, this);

      // Register with IntersectionObserver for preloading & auto-rotate
      if (preloadObserver) {
        preloadObserver.observe(this.container);
      }
    }

    updateSpinBadge() {
      if (this.indicatorEl) {
        if (this.canSpin) {
          this.indicatorEl.removeAttribute('hidden');
          this.indicatorEl.style.display = '';
        } else {
          this.indicatorEl.setAttribute('hidden', '');
          this.indicatorEl.style.display = 'none';
        }
      }
    }

    /**
     * Constructs the frame path for given frame index and metal
     */
    getFramePath(frameIdx, metal = this.currentMetal) {
      return `/static/products/${this.slug}/${metal}/spin/${pad3(frameIdx)}.webp`;
    }

    /**
     * Constructs still view paths
     */
    getStillPath(kind, metal = this.currentMetal) {
      return `/static/products/${this.slug}/${metal}/${kind}.webp`;
    }

    /**
     * Preloads all frames for the current metal (only if product has >= 12 frames)
     */
    preloadCurrentMetalFrames() {
      if (this.isFullyPreloaded || !this.canSpin) return;
      const metal = this.currentMetal;
      if (!this.imageCache[metal]) {
        this.imageCache[metal] = {};
      }

      for (let i = 1; i <= this.totalFrames; i++) {
        if (!this.imageCache[metal][i]) {
          const preImg = new Image();
          const frameUrl = this.getFramePath(i, metal);
          preImg.onerror = () => {
            console.warn(`[Atelier Nilaya Image 404] Missing frame: ${frameUrl} (Product: ${this.slug}, Metal: ${metal})`);
          };
          preImg.src = frameUrl;
          this.imageCache[metal][i] = preImg;
        }
      }
      this.isFullyPreloaded = true;
    }

    /**
     * Updates the visible <img> with the requested frame index
     */
    renderFrame(frameIdx) {
      if (this.totalFrames > 0) {
        if (frameIdx < 1) frameIdx = this.totalFrames;
        if (frameIdx > this.totalFrames) frameIdx = 1;
      }
      this.currentFrame = frameIdx;

      const fallbackAttr = this.container.getAttribute('data-image-fallback');
      const targetSrc = this.canSpin 
        ? this.getFramePath(frameIdx, this.currentMetal)
        : (fallbackAttr || this.getStillPath('front', this.currentMetal));

      // Robust fallback handling: Spin -> front.webp / fallback -> "Photo coming soon"
      this.imgEl.onerror = () => {
        if (this.fallbackStep === 0 && fallbackAttr && this.imgEl.src !== fallbackAttr) {
          this.fallbackStep = 1;
          this.imgEl.src = fallbackAttr;
        } else if (this.fallbackStep <= 1) {
          this.fallbackStep = 2;
          const frontSrc = this.getStillPath('front', this.currentMetal);
          if (frontSrc && this.imgEl.src !== frontSrc) {
            this.imgEl.src = frontSrc;
          } else {
            this.fallbackStep = 3;
            this.imgEl.style.display = 'none';
            if (this.fallbackTileEl) {
              this.fallbackTileEl.removeAttribute('hidden');
              this.fallbackTileEl.style.display = 'flex';
            }
          }
        } else {
          this.imgEl.style.display = 'none';
          if (this.fallbackTileEl) {
            this.fallbackTileEl.removeAttribute('hidden');
            this.fallbackTileEl.style.display = 'flex';
          }
        }
      };

      this.imgEl.onload = () => {
        this.imgEl.style.display = 'block';
        if (this.fallbackTileEl) {
          this.fallbackTileEl.setAttribute('hidden', '');
          this.fallbackTileEl.style.display = 'none';
        }
      };

      this.imgEl.src = targetSrc;
    }

    /**
     * Slow auto-rotate once (gentle 360 preview on first entry)
     */
    triggerAutoRotate() {
      if (this.hasAutoRotated || prefersReducedMotion || this.autoRotateActive || !this.canSpin) return;
      this.hasAutoRotated = true;
      this.autoRotateActive = true;

      // Show indicator briefly
      if (this.indicatorEl) {
        this.indicatorEl.classList.add('is-visible');
        setTimeout(() => {
          if (this.indicatorEl) this.indicatorEl.classList.remove('is-visible');
        }, 2200);
      }

      let step = 0;
      const totalSteps = this.totalFrames;

      const rotateStep = () => {
        if (!this.autoRotateActive) return;
        step++;
        let nextFrame = this.currentFrame + 1;
        if (nextFrame > this.totalFrames) nextFrame = 1;
        this.renderFrame(nextFrame);

        if (step < totalSteps) {
          this.autoRotateTimeout = setTimeout(rotateStep, this.options.autoRotateSpeedMs);
        } else {
          this.autoRotateActive = false;
        }
      };

      this.autoRotateTimeout = setTimeout(rotateStep, 100);
    }

    cancelAutoRotate() {
      this.autoRotateActive = false;
      if (this.autoRotateTimeout) {
        clearTimeout(this.autoRotateTimeout);
        this.autoRotateTimeout = null;
      }
    }

    /**
     * Pointer & Touch Drag Bindings with natural vertical scroll preservation
     */
    bindDragEvents() {
      const stage = this.container;

      const onPointerDown = (e) => {
        if (e.target.closest('.tile-wishlist-btn') || e.target.closest('.tile-tag-badge') || e.target.closest('.swatch-btn') || e.target.closest('.swatch-dot')) {
          return;
        }

        if (!this.canSpin) return; // Only rotate if piece has >= 12 frames

        this.cancelAutoRotate();
        this.stopInertia();
        this.preloadCurrentMetalFrames();

        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const clientY = e.touches ? e.touches[0].clientY : e.clientY;

        this.isDragging = true;
        this.dragStartX = clientX;
        this.dragStartY = clientY;
        this.lastDragX = clientX;
        this.velocity = 0;
        this.isHorizontalDrag = false;
        this.dragThresholdPassed = false;
      };

      const onPointerMove = (e) => {
        if (!this.isDragging || !this.canSpin) return;

        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const clientY = e.touches ? e.touches[0].clientY : e.clientY;

        const deltaX = clientX - this.dragStartX;
        const deltaY = clientY - this.dragStartY;

        // Check intent: if user moved vertically first, let page scroll freely!
        if (!this.dragThresholdPassed) {
          const absX = Math.abs(deltaX);
          const absY = Math.abs(deltaY);
          if (absY > 6 && absY > absX) {
            // User is scrolling vertically: cancel drag
            this.isDragging = false;
            return;
          }
          if (absX > 6 && absX >= absY) {
            this.dragThresholdPassed = true;
            this.isHorizontalDrag = true;
          }
        }

        if (this.isHorizontalDrag) {
          if (e.cancelable) e.preventDefault(); // Scrub horizontally

          const frameDelta = clientX - this.lastDragX;
          this.velocity = frameDelta;
          this.lastDragX = clientX;

          const framesToStep = Math.round(frameDelta / this.options.pixelsPerFrame);
          if (framesToStep !== 0) {
            let targetFrame = this.currentFrame - framesToStep;
            while (targetFrame < 1) targetFrame += this.totalFrames;
            while (targetFrame > this.totalFrames) targetFrame -= this.totalFrames;
            this.renderFrame(targetFrame);
          }
        }
      };

      const onPointerUp = () => {
        if (!this.isDragging) return;
        this.isDragging = false;

        if (this.canSpin && this.isHorizontalDrag && Math.abs(this.velocity) > 1.5) {
          this.startInertia();
        }
      };

      // Mouse events
      stage.addEventListener('mousedown', onPointerDown);
      window.addEventListener('mousemove', onPointerMove);
      window.addEventListener('mouseup', onPointerUp);

      // Touch events (passive start allows browser scroll; cancelable move locked if horizontal)
      stage.addEventListener('touchstart', onPointerDown, { passive: true });
      stage.addEventListener('touchmove', onPointerMove, { passive: false });
      stage.addEventListener('touchend', onPointerUp, { passive: true });
    }

    /**
     * Keyboard Arrow Key Navigation
     */
    bindKeyboardEvents() {
      this.container.addEventListener('keydown', (e) => {
        if (!this.canSpin) return;

        if (e.key === 'ArrowLeft') {
          e.preventDefault();
          this.cancelAutoRotate();
          this.renderFrame(this.currentFrame - 1);
        } else if (e.key === 'ArrowRight') {
          e.preventDefault();
          this.cancelAutoRotate();
          this.renderFrame(this.currentFrame + 1);
        }
      });
    }

    /**
     * Second view on hover (desktop): smoothly show lifestyle photo
     */
    bindHoverEvents() {
      if (!this.lifestyleImgEl) return;

      this.lifestyleImgEl.onerror = () => {
        console.warn(`[Atelier Nilaya Lifestyle 404] Missing: ${this.lifestyleImgEl.src} (Product: ${this.slug})`);
        this.lifestyleImgEl.style.display = 'none';
      };

      this.container.addEventListener('mouseenter', () => {
        if (window.innerWidth >= 1024 && !this.isDragging) {
          this.lifestyleImgEl.classList.add('is-active');
        }
      });

      this.container.addEventListener('mouseleave', () => {
        if (this.lifestyleImgEl) {
          this.lifestyleImgEl.classList.remove('is-active');
        }
      });
    }

    /**
     * Metal Swatches: switches metal, price, discount and active frames
     */
    bindMetalDots() {
      const swatches = this.tileRoot ? this.tileRoot.querySelectorAll('.swatch-btn, .swatch-dot') : [];
      swatches.forEach((dot) => {
        dot.addEventListener('click', (e) => {
          e.preventDefault();
          e.stopPropagation();

          const rawMetal = dot.getAttribute('data-metal');
          const newMetal = normalizeMetal(rawMetal);
          if (!newMetal || dot.classList.contains('is-disabled')) return;

          this.switchMetal(newMetal);

          // Update active dot UI
          swatches.forEach(d => {
            d.classList.remove('is-selected', 'is-active');
            d.setAttribute('aria-pressed', 'false');
          });
          dot.classList.add('is-selected');
          dot.setAttribute('aria-pressed', 'true');
        });
      });
    }

    switchMetal(newMetal) {
      newMetal = normalizeMetal(newMetal);
      if (this.currentMetal === newMetal) return;
      this.currentMetal = newMetal;
      this.fallbackStep = 0;
      this.isFullyPreloaded = false;

      // Update current metal attribute on container and product-tile
      this.container.setAttribute('data-current-metal', newMetal);
      if (this.tileRoot) this.tileRoot.setAttribute('data-current-metal', newMetal);

      // Recheck frames count for newly chosen metal
      const metalInfo = this.metalsData[newMetal];
      const frames = (metalInfo && typeof metalInfo.frames === 'number') ? metalInfo.frames : 36;
      this.totalFrames = frames || 36;
      this.canSpin = this.totalFrames >= 12;

      this.updateSpinBadge();

      // Re-render current frame with new metal
      this.renderFrame(this.currentFrame);
      if (this.canSpin) {
        this.preloadCurrentMetalFrames();
      }

      // Update price and discount badge
      if (metalInfo && typeof metalInfo.price === 'number') {
        const newPrice = metalInfo.price;

        if (this.priceEl) {
          this.priceEl.textContent = formatINR(newPrice);
        }

        const oldPriceVal = parseFloat(this.tileRoot ? this.tileRoot.getAttribute('data-old-price') : 0);
        if (oldPriceVal && oldPriceVal > newPrice) {
          const discountPct = Math.round(((oldPriceVal - newPrice) / oldPriceVal) * 100);
          if (this.oldPriceEl) {
            this.oldPriceEl.textContent = formatINR(oldPriceVal);
            this.oldPriceEl.style.display = '';
          }
          if (this.saveBadgeEl) {
            this.saveBadgeEl.textContent = `Save ${discountPct}%`;
            this.saveBadgeEl.style.display = '';
          }
        } else {
          if (this.oldPriceEl) this.oldPriceEl.style.display = 'none';
          if (this.saveBadgeEl) this.saveBadgeEl.style.display = 'none';
        }

        // Update material line label if present
        if (this.tileRoot) {
          const matEl = this.tileRoot.querySelector('[data-material-line]');
          if (matEl && metalInfo && metalInfo.label) {
            const currentText = matEl.textContent;
            const parts = currentText.split('•');
            if (parts.length > 1) {
              matEl.textContent = `${metalInfo.label} •${parts.slice(1).join('•')}`;
            } else {
              matEl.textContent = metalInfo.label;
            }
          }
        }
      }
    }

    /**
     * Inertia release physics
     */
    startInertia() {
      const step = () => {
        this.velocity *= this.options.inertiaFriction;
        if (Math.abs(this.velocity) < 0.2) {
          this.stopInertia();
          return;
        }

        const frames = Math.round(this.velocity / this.options.pixelsPerFrame);
        if (frames !== 0) {
          let next = this.currentFrame - frames;
          while (next < 1) next += this.totalFrames;
          while (next > this.totalFrames) next -= this.totalFrames;
          this.renderFrame(next);
        }
        this.inertiaRAF = requestAnimationFrame(step);
      };
      this.inertiaRAF = requestAnimationFrame(step);
    }

    stopInertia() {
      if (this.inertiaRAF) {
        cancelAnimationFrame(this.inertiaRAF);
        this.inertiaRAF = null;
      }
      this.velocity = 0;
    }
  }

  /**
   * Initialize Global IntersectionObserver for Viewport Preloading & Auto-rotate
   */
  function initPreloadObserver() {
    if (!('IntersectionObserver' in window)) return;

    preloadObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        const viewer = activeViewers.get(entry.target);
        if (!viewer) return;

        if (entry.isIntersecting) {
          // In or near viewport: preload all frames
          if (viewer.canSpin) {
            viewer.preloadCurrentMetalFrames();
          }

          // Gentle auto-rotate once when visible
          if (entry.intersectionRatio >= 0.25 && !viewer.hasAutoRotated) {
            viewer.triggerAutoRotate();
          }
        }
      });
    }, {
      root: null,
      rootMargin: '200px 0px 200px 0px',
      threshold: [0.1, 0.25]
    });
  }

  /**
   * Auto-discover and attach SpinViewers across the page
   */
  function initAllSpinViewers() {
    initPreloadObserver();

    const stageContainers = document.querySelectorAll('[data-spin-viewer]');
    stageContainers.forEach((stage) => {
      if (!activeViewers.has(stage)) {
        new SpinViewer(stage);
      }
    });
  }

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAllSpinViewers);
  } else {
    initAllSpinViewers();
  }

  // Export to window for external scripting
  window.AtelierSpinViewer = SpinViewer;
  window.initAllSpinViewers = initAllSpinViewers;

})(window, document);

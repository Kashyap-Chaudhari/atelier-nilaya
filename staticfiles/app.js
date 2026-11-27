/**
 * Atelier Nilaya â€” Luxury Jewellery, Surat
 * Velvet Curtains Opening Cover Controller
 * Plays whenever the page is loaded or refreshed.
 */
(function () {
  'use strict';

  function initVelvetCurtains() {
    var cover = document.getElementById('curtains-cover');
    if (!cover) return;

    var hasHash = window.location.hash && window.location.hash.length > 1;

    function revealHero() {
      var heroHeadline = document.querySelector('.hero-headline');
      if (heroHeadline) {
        heroHeadline.classList.add('is-revealed');
      }
    }

    // If URL contains a specific in-page deep link hash, suppress
    if (hasHash) {
      document.documentElement.classList.remove('has-curtains');
      if (cover.parentNode) {
        cover.parentNode.removeChild(cover);
      }
      revealHero();
      return;
    }

    var isDismissed = false;
    var autoEndTimer = null;

    function dismissCover() {
      if (isDismissed) return;
      isDismissed = true;

      if (autoEndTimer) {
        clearTimeout(autoEndTimer);
        autoEndTimer = null;
      }

      document.documentElement.classList.remove('has-curtains');
      if (cover && cover.parentNode) {
        cover.parentNode.removeChild(cover);
      }

      revealHero();
      cleanupListeners();
    }

    function onKeyDown(e) {
      dismissCover();
    }

    function onClick(e) {
      dismissCover();
    }

    function cleanupListeners() {
      document.removeEventListener('keydown', onKeyDown);
      if (cover) {
        cover.removeEventListener('click', onClick);
      }
    }

    // Global skip handlers: click anywhere, pressing any key
    document.addEventListener('keydown', onKeyDown);
    cover.addEventListener('click', onClick);

    // Skip button click handler
    var skipBtn = document.getElementById('curtains-skip-btn');
    if (skipBtn) {
      skipBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        dismissCover();
      });
    }

    // Prefers reduced motion handling: Static cover under 1 second (700ms), then remove
    var prefersReduced = false;
    try {
      prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    } catch (e) {}

    if (prefersReduced) {
      cover.classList.add('is-animating');
      autoEndTimer = setTimeout(function () {
        dismissCover();
      }, 700);
      return;
    }

    // Wait for fonts to load before starting animation sequence (document.fonts.ready with 900ms fallback)
    function startSequence() {
      if (isDismissed) return;
      cover.classList.add('is-animating');

      // 3.0s total sequence: curtains open at 2.0s-2.9s, cover removed and page interactive at 3.0s
      autoEndTimer = setTimeout(function () {
        dismissCover();
      }, 3000);
    }

    if (document.fonts && document.fonts.ready) {
      var fontTimer = setTimeout(function () {
        startSequence();
      }, 900);

      document.fonts.ready.then(function () {
        clearTimeout(fontTimer);
        startSequence();
      }).catch(function () {
        clearTimeout(fontTimer);
        startSequence();
      });
    } else {
      startSequence();
    }
  }

  /* ==========================================================================
     THE SKETCHBOOK: FROM PENCIL TO JEWEL CONTROLLER
     Interactive before & after slider, real product spin, metal swap & thumbnails.
     ========================================================================== */
  function initSketchbook() {
    var section = document.getElementById('sketchbook-section');
    var page = document.getElementById('sketchbook-page');
    var divider = document.getElementById('sketchbook-divider');
    var handle = document.getElementById('sketchbook-handle');
    var dataEl = document.getElementById('sketchbook-data');

    if (!section || !page || !divider || !handle || !dataEl) return;

    var designs = [];
    try {
      designs = JSON.parse(dataEl.textContent);
    } catch (e) {
      console.error('Failed to parse sketchbook data', e);
      return;
    }

    if (!designs || designs.length === 0) return;

    var activeIdx = 0;
    var sliderPos = 50; // Default starts at 50% so half sketch and half finished ring are visible
    var currentMetal = designs[0].default_metal || (designs[0].metals && designs[0].metals[0]) || 'platinum';
    var isDragging = false;
    var isScrubbingSpin = false;
    var spinStartX = 0;
    var currentFrameIdx = 0;
    var hasNudged = false;

    // DOM Elements
    var sketchImg = document.getElementById('sketchbook-sketch-img');
    var finishedImg = document.getElementById('sketchbook-finished-img');
    var finishedLayer = document.getElementById('sketchbook-finished-layer');
    var fallbackEl = document.getElementById('sketchbook-fallback');
    var yearEl = document.getElementById('sketchbook-year');
    var titleEl = document.getElementById('sketchbook-title');
    var storyEl = document.getElementById('sketchbook-story');
    var viewBtn = document.getElementById('sketchbook-view-btn');
    var metalDotsContainer = document.getElementById('sketchbook-metal-dots');
    var thumbBtns = document.querySelectorAll('.sketchbook-thumb-btn');

    // Update slider position across CSS variables, divider and ARIA
    function setSliderPosition(pos, isInstant) {
      sliderPos = Math.max(0, Math.min(100, pos));
      page.style.setProperty('--slider-pos', sliderPos + '%');
      divider.style.left = sliderPos + '%';
      handle.setAttribute('aria-valuenow', Math.round(sliderPos));
    }

    // Pointer Dragging for the Before/After Divider
    function onPointerDown(e) {
      // If clicking directly on a thumbnail or metal dot, do not capture
      if (e.target.closest('.sketchbook-metal-dots-row') || e.target.closest('.sketchbook-thumbnails-row')) {
        return;
      }

      var rect = page.getBoundingClientRect();
      var clickPercent = ((e.clientX - rect.left) / rect.width) * 100;

      // Check if user is scrubbing 360 spin (when divider is past 70% and click is on right side)
      if (sliderPos >= 70 && clickPercent > sliderPos) {
        isScrubbingSpin = true;
        spinStartX = e.clientX;
        return;
      }

      isDragging = true;
      try {
        handle.setPointerCapture(e.pointerId);
      } catch (err) {}

      setSliderPosition(clickPercent);
      e.preventDefault();
    }

    function onPointerMove(e) {
      if (isScrubbingSpin) {
        var deltaX = e.clientX - spinStartX;
        if (Math.abs(deltaX) > 8) {
          var step = deltaX > 0 ? 1 : -1;
          spinStartX = e.clientX;
          scrubSpinFrame(step);
        }
        return;
      }

      if (!isDragging) return;
      var rect = page.getBoundingClientRect();
      var movePercent = ((e.clientX - rect.left) / rect.width) * 100;
      setSliderPosition(movePercent);
    }

    function onPointerUp(e) {
      if (isDragging) {
        isDragging = false;
        try {
          handle.releasePointerCapture(e.pointerId);
        } catch (err) {}
      }
      if (isScrubbingSpin) {
        isScrubbingSpin = false;
      }
    }

    page.addEventListener('pointerdown', onPointerDown);
    window.addEventListener('pointermove', onPointerMove);
    window.addEventListener('pointerup', onPointerUp);
    window.addEventListener('pointercancel', onPointerUp);

    // Keyboard Accessibility for Slider
    handle.addEventListener('keydown', function (e) {
      var step = 5;
      if (e.key === 'ArrowLeft' || e.key === 'ArrowDown') {
        e.preventDefault();
        setSliderPosition(sliderPos - step);
      } else if (e.key === 'ArrowRight' || e.key === 'ArrowUp') {
        e.preventDefault();
        setSliderPosition(sliderPos + step);
      } else if (e.key === 'Home') {
        e.preventDefault();
        setSliderPosition(0);
      } else if (e.key === 'End') {
        e.preventDefault();
        setSliderPosition(100);
      }
    });

    // 360 Spin Frame Scrubber (When divider is pulled past 70%)
    function scrubSpinFrame(direction) {
      var design = designs[activeIdx];
      if (!design || !design.images_by_metal || !design.images_by_metal[currentMetal]) return;

      var frames = design.images_by_metal[currentMetal].spin;
      if (!frames || frames.length === 0) return;

      currentFrameIdx = (currentFrameIdx + direction + frames.length) % frames.length;
      if (finishedImg) {
        finishedImg.src = frames[currentFrameIdx];
      }
    }

    // Update Finished Jewel Image and Metal Dots
    function updateFinishedView() {
      var design = designs[activeIdx];
      if (!design) return;

      var metalData = design.images_by_metal ? design.images_by_metal[currentMetal] : null;
      var photoPath = metalData ? (metalData.front || (metalData.spin && metalData.spin[0])) : null;

      if (!photoPath) {
        photoPath = design.finished_photo;
      }

      if (photoPath) {
        finishedImg.style.display = 'block';
        if (fallbackEl) fallbackEl.style.display = 'none';
        finishedImg.src = photoPath;
        finishedImg.alt = 'Finished ' + design.title + ' in ' + currentMetal.replace(/_/g, ' ');
      } else {
        finishedImg.style.display = 'none';
        if (fallbackEl) fallbackEl.style.display = 'flex';
      }
    }

    // Render Metal Dots strictly for offered metals of the active design
    function renderMetalDots() {
      if (!metalDotsContainer) return;
      var design = designs[activeIdx];
      var offeredMetals = design.metals || ['yellow_gold', 'platinum', 'rose_gold'];

      // If current metal is not offered in new design, switch to first offered
      if (offeredMetals.indexOf(currentMetal) === -1) {
        currentMetal = offeredMetals[0] || 'yellow_gold';
      }

      metalDotsContainer.innerHTML = '';
      offeredMetals.forEach(function (m) {
        var dot = document.createElement('button');
        dot.type = 'button';
        dot.className = 'sketchbook-metal-dot metal-dot-' + m + (m === currentMetal ? ' is-active' : '');
        dot.setAttribute('data-metal', m);
        var label = m.replace(/_/g, ' ').replace(/\b\w/g, function (l) { return l.toUpperCase(); });
        dot.setAttribute('aria-label', label);
        dot.setAttribute('title', label);

        dot.addEventListener('click', function () {
          currentMetal = m;
          var dots = metalDotsContainer.querySelectorAll('.sketchbook-metal-dot');
          dots.forEach(function (d) { d.classList.remove('is-active'); });
          dot.classList.add('is-active');
          updateFinishedView();
        });

        metalDotsContainer.appendChild(dot);
      });
    }

    // Switch Active Design (Preserving divider position)
    function setActiveDesign(index) {
      if (index < 0 || index >= designs.length) return;
      activeIdx = index;
      var design = designs[activeIdx];

      // Update sketch
      if (sketchImg) {
        sketchImg.src = design.sketch_path;
        sketchImg.alt = design.sketch_alt;
      }

      // Update caption metadata
      if (yearEl) yearEl.textContent = design.year;
      if (titleEl) titleEl.textContent = design.title;
      if (storyEl) storyEl.textContent = design.story;
      if (viewBtn) {
        viewBtn.href = '/p/' + design.product_slug;
      }

      // Re-render metal dots and update finished view
      renderMetalDots();
      updateFinishedView();

      // Update thumbnails active state
      thumbBtns.forEach(function (btn, i) {
        if (i === activeIdx) {
          btn.classList.add('is-active');
          btn.setAttribute('aria-selected', 'true');
        } else {
          btn.classList.remove('is-active');
          btn.setAttribute('aria-selected', 'false');
        }
      });
    }

    // Thumbnail Click Listeners
    thumbBtns.forEach(function (btn, idx) {
      btn.addEventListener('click', function () {
        setActiveDesign(idx);
      });
    });

    // IntersectionObserver: Lazy Preload & Subtle First-View Nudge Hint
    if ('IntersectionObserver' in window) {
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            // Preload thumbnails & spin frames of active design in background
            preloadDesignAssets(designs[activeIdx]);

            // Subtle nudge animation on first view only
            if (!hasNudged) {
              hasNudged = true;
              var prefersReduced = false;
              try {
                prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
              } catch (e) {}

              if (!prefersReduced) {
                page.classList.add('has-nudge');
                setTimeout(function () {
                  page.classList.remove('has-nudge');
                }, 1600);
              }
            }
            observer.unobserve(section);
          }
        });
      }, { rootMargin: '120px' });

      observer.observe(section);
    }

    function preloadDesignAssets(design) {
      if (!design || !design.images_by_metal) return;
      var metal = design.default_metal || 'yellow_gold';
      var metalData = design.images_by_metal[metal];
      if (metalData && metalData.spin) {
        metalData.spin.slice(0, 8).forEach(function (frameUrl) {
          var img = new Image();
          img.src = frameUrl;
        });
      }
    }

    // Initial setup
    setSliderPosition(50);
    renderMetalDots();
  }

  /* ==========================================================================
     FEATURED EDIT CONTROLLER (Hexagons Scroll Fade-In)
     ========================================================================== */
  function initFeaturedEdit() {
    var hexItems = document.querySelectorAll('.fe-hex-item, .featured-hex-item');
    if (!hexItems || hexItems.length === 0) return;

    var prefersReduced = false;
    try {
      prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    } catch (e) {}

    if (prefersReduced || !('IntersectionObserver' in window)) {
      hexItems.forEach(function (hex) {
        hex.classList.add('is-visible');
      });
      return;
    }

    var observer = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          hexItems.forEach(function (hex) {
            hex.classList.add('is-visible');
          });
          obs.disconnect();
        }
      });
    }, { threshold: 0.15 });

    var target = document.querySelector('#edit') || document.querySelector('.fe-band') || document.querySelector('.featured-photo-band');
    if (target) {
      observer.observe(target);
    }
  }

  function initApp() {
    initVelvetCurtains();
    initSketchbook();
    initFeaturedEdit();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
  } else {
    initApp();
  }
})();

/**
 * Atelier Nilaya â€” Luxury Jewellery, Surat
 * Velvet Curtains Opening Cover Controller (Django Campaign Hero)
 * Plays whenever the page is loaded or refreshed.
 */
(function () {
  'use strict';

  function initVelvetCurtains() {
    var cover = document.getElementById('curtains-cover');
    if (!cover) return;

    var hasHash = window.location.hash && window.location.hash.length > 1;

    // Suppress if URL has an explicit in-page deep link hash
    if (hasHash) {
      document.documentElement.classList.remove('has-curtains');
      if (cover.parentNode) {
        cover.parentNode.removeChild(cover);
      }
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

    // Prefers reduced motion: static cover under 1s (700ms)
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

    // Wait for fonts to load before starting animation sequence
    function startSequence() {
      if (isDismissed) return;
      cover.classList.add('is-animating');

      // 3.0s total sequence: curtains slide apart, cover removed at 3.0s
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
      return;
    }

    if (!designs || designs.length === 0) return;

    var activeIdx = 0;
    var sliderPos = 50;
    var currentMetal = designs[0].default_metal || (designs[0].metals && designs[0].metals[0]) || 'platinum';
    var isDragging = false;

    var sketchImg = document.getElementById('sketchbook-sketch-img');
    var finishedImg = document.getElementById('sketchbook-finished-img');
    var yearEl = document.getElementById('sketchbook-year');
    var titleEl = document.getElementById('sketchbook-title');
    var storyEl = document.getElementById('sketchbook-story');
    var viewBtn = document.getElementById('sketchbook-view-btn');
    var metalDotsContainer = document.getElementById('sketchbook-metal-dots');
    var thumbBtns = document.querySelectorAll('.sketchbook-thumb-btn');

    function setSliderPosition(pos) {
      sliderPos = Math.max(0, Math.min(100, pos));
      page.style.setProperty('--slider-pos', sliderPos + '%');
      divider.style.left = sliderPos + '%';
      handle.setAttribute('aria-valuenow', Math.round(sliderPos));
    }

    function onPointerDown(e) {
      if (e.target.closest('.sketchbook-metal-dots-row') || e.target.closest('.sketchbook-thumbnails-row')) return;
      isDragging = true;
      try { handle.setPointerCapture(e.pointerId); } catch (err) {}
      var rect = page.getBoundingClientRect();
      var clickPercent = ((e.clientX - rect.left) / rect.width) * 100;
      setSliderPosition(clickPercent);
      e.preventDefault();
    }

    function onPointerMove(e) {
      if (!isDragging) return;
      var rect = page.getBoundingClientRect();
      var movePercent = ((e.clientX - rect.left) / rect.width) * 100;
      setSliderPosition(movePercent);
    }

    function onPointerUp(e) {
      if (isDragging) {
        isDragging = false;
        try { handle.releasePointerCapture(e.pointerId); } catch (err) {}
      }
    }

    page.addEventListener('pointerdown', onPointerDown);
    window.addEventListener('pointermove', onPointerMove);
    window.addEventListener('pointerup', onPointerUp);
    window.addEventListener('pointercancel', onPointerUp);

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

    function updateFinishedView() {
      var design = designs[activeIdx];
      if (!design) return;
      var metalData = design.images_by_metal ? design.images_by_metal[currentMetal] : null;
      var photoPath = metalData ? (metalData.front || (metalData.spin && metalData.spin[0])) : null;
      if (!photoPath) photoPath = design.finished_photo;
      if (photoPath && finishedImg) {
        finishedImg.src = photoPath;
        finishedImg.alt = 'Finished ' + design.title + ' in ' + currentMetal.replace(/_/g, ' ');
      }
    }

    function renderMetalDots() {
      if (!metalDotsContainer) return;
      var design = designs[activeIdx];
      var offeredMetals = design.metals || ['platinum', 'rose_gold', 'yellow_gold'];
      if (offeredMetals.indexOf(currentMetal) === -1) {
        currentMetal = offeredMetals[0] || 'platinum';
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

    function setActiveDesign(index) {
      if (index < 0 || index >= designs.length) return;
      activeIdx = index;
      var design = designs[activeIdx];

      if (sketchImg) {
        sketchImg.src = design.sketch_path;
        sketchImg.alt = design.sketch_alt;
      }
      if (yearEl) yearEl.textContent = design.year;
      if (titleEl) titleEl.textContent = design.title;
      if (storyEl) storyEl.textContent = design.story;
      if (viewBtn) viewBtn.href = '/p/' + design.product_slug;

      renderMetalDots();
      updateFinishedView();

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

    thumbBtns.forEach(function (btn, idx) {
      btn.addEventListener('click', function () {
        setActiveDesign(idx);
      });
    });

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

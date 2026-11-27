/**
 * THE UNVEILING ATELIER — HERO ORCHESTRATOR
 * Main initialization, event binding, autoplay cycle, touch gestures,
 * keyboard controls, and lifecycle hooks.
 */

document.addEventListener('DOMContentLoaded', () => {
  const campaignsDataEl = document.getElementById('atelier-campaigns-data');
  if (!campaignsDataEl) return;

  let campaignsData = [];
  try {
    campaignsData = JSON.parse(campaignsDataEl.textContent);
  } catch (e) {
    console.error('Failed to parse campaign metadata:', e);
    return;
  }

  if (!campaignsData.length) return;

  // Cache DOM Elements
  const elements = {
    heroSection: document.querySelector('.atelier-hero-section'),
    stageViewport: document.querySelector('.stage-viewport'),
    veilMask: document.querySelector('.unveil-mask-layer'),
    stagePoster: document.querySelector('.stage-poster'),
    videoPrimary: document.getElementById('stage-video-primary'),
    videoSecondary: document.getElementById('stage-video-secondary'),
    
    // Zone A
    catalogueOrder: document.querySelector('.catalogue-order'),
    odometerDigit: document.querySelector('.odometer-digit'),
    storyEyebrow: document.querySelector('.story-eyebrow span'),
    storyHeadline: document.querySelector('.story-headline'),
    storyHeadlineSub: document.querySelector('.story-headline-sub'),
    storyDescription: document.querySelector('.story-description'),
    storyCuratorNote: document.querySelector('.story-curator-text'),
    storyProvenanceTag: document.querySelector('.story-provenance-tag'),
    storyCta: document.querySelector('.story-cta-link'),
    storyCtaText: document.querySelector('.story-cta-text'),

    // Zone C
    previewCard: document.querySelector('.preview-interactive-card'),
    previewOrder: document.querySelector('.preview-next-order'),
    previewEyebrow: document.querySelector('.preview-upcoming-eyebrow'),
    previewTitle: document.querySelector('.preview-upcoming-title'),
    previewImg: document.querySelector('.preview-poster-img'),

    // Controls
    btnPrev: document.querySelector('.btn-prev'),
    btnNext: document.querySelector('.btn-next'),
    btnPlayPause: document.querySelector('.btn-play-pause'),
    timelineProgress: document.querySelector('.timeline-progress-fill'),
    slidePills: document.querySelector('.direct-slide-pills')
  };

  // Instantiate State & Transition Controller
  const state = new AtelierState(campaignsData);
  const transition = new AtelierTransitionController(elements, state);

  // Autoplay Configuration
  const AUTOPLAY_DURATION = 7000; // 7 seconds
  let autoplayStartTime = null;
  let autoplayRafId = null;
  let isPaused = false;
  let isNavigating = false;

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /**
   * Navigate to slide
   */
  async function navigate(targetIndex, direction = 'forward') {
    if (isNavigating || targetIndex === state.currentIndex) return;
    isNavigating = true;
    resetAutoplayTimer();

    state.setCurrentIndex(targetIndex);
    const targetCampaign = state.getCurrent();

    try {
      await transition.unveil(targetCampaign, direction);
    } finally {
      isNavigating = false;
      if (!isPaused && !prefersReducedMotion) {
        startAutoplayProgress();
      }
    }
  }

  function nextSlide() {
    const nextIdx = state.getNextIndex(1);
    navigate(nextIdx, 'forward');
  }

  function prevSlide() {
    const prevIdx = state.getNextIndex(-1);
    navigate(prevIdx, 'backward');
  }

  /**
   * Autoplay Timeline Progress Bar
   */
  function startAutoplayProgress() {
    if (prefersReducedMotion || isPaused) return;
    cancelAnimationFrame(autoplayRafId);
    autoplayStartTime = performance.now();

    function frame(now) {
      if (isPaused) return;
      const elapsed = now - autoplayStartTime;
      const progress = Math.min((elapsed / AUTOPLAY_DURATION) * 100, 100);

      if (elements.timelineProgress) {
        elements.timelineProgress.style.width = `${progress}%`;
      }

      if (elapsed < AUTOPLAY_DURATION) {
        autoplayRafId = requestAnimationFrame(frame);
      } else {
        nextSlide();
      }
    }

    autoplayRafId = requestAnimationFrame(frame);
  }

  function resetAutoplayTimer() {
    cancelAnimationFrame(autoplayRafId);
    if (elements.timelineProgress) {
      elements.timelineProgress.style.width = '0%';
    }
  }

  function togglePlayPause() {
    isPaused = !isPaused;
    state.isAutoplayPaused = isPaused;

    if (elements.btnPlayPause) {
      elements.btnPlayPause.setAttribute('aria-label', isPaused ? 'Resume autoplay' : 'Pause autoplay');
      const iconPath = isPaused
        ? '<polygon points="5 3 19 12 5 21 5 3"></polygon>'
        : '<rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect>';
      elements.btnPlayPause.querySelector('svg').innerHTML = iconPath;
    }

    if (isPaused) {
      cancelAnimationFrame(autoplayRafId);
    } else {
      startAutoplayProgress();
    }
  }

  /**
   * Event Listeners Binding
   */
  if (elements.btnNext) {
    elements.btnNext.addEventListener('click', (e) => {
      e.preventDefault();
      nextSlide();
    });
  }

  if (elements.btnPrev) {
    elements.btnPrev.addEventListener('click', (e) => {
      e.preventDefault();
      prevSlide();
    });
  }

  if (elements.previewCard) {
    elements.previewCard.addEventListener('click', (e) => {
      e.preventDefault();
      nextSlide();
    });
  }

  if (elements.btnPlayPause) {
    elements.btnPlayPause.addEventListener('click', (e) => {
      e.preventDefault();
      togglePlayPause();
    });
  }

  // Direct Slide Pill selection
  if (elements.slidePills) {
    const pills = elements.slidePills.querySelectorAll('.slide-pill-dot');
    pills.forEach((pill) => {
      pill.addEventListener('click', () => {
        const targetIdx = parseInt(pill.getAttribute('data-slide-index'), 10);
        if (!isNaN(targetIdx)) {
          const dir = targetIdx > state.currentIndex ? 'forward' : 'backward';
          navigate(targetIdx, dir);
        }
      });
    });
  }

  // Keyboard Navigation
  window.addEventListener('keydown', (e) => {
    // Only capture when not typing in form inputs
    if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) return;

    if (e.key === 'ArrowRight') {
      nextSlide();
    } else if (e.key === 'ArrowLeft') {
      prevSlide();
    } else if (e.key === ' ') {
      e.preventDefault();
      togglePlayPause();
    }
  });

  // Mobile Touch Swipe Navigation
  let touchStartX = 0;
  let touchStartY = 0;
  let touchStartTime = 0;

  if (elements.heroSection) {
    elements.heroSection.addEventListener('touchstart', (e) => {
      if (e.touches.length === 1) {
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
        touchStartTime = performance.now();
      }
    }, { passive: true });

    elements.heroSection.addEventListener('touchend', (e) => {
      if (e.changedTouches.length === 1) {
        const deltaX = e.changedTouches[0].clientX - touchStartX;
        const deltaY = e.changedTouches[0].clientY - touchStartY;
        const duration = performance.now() - touchStartTime;

        // If swipe is predominantly horizontal and passes threshold
        if (Math.abs(deltaX) > 40 && Math.abs(deltaX) > Math.abs(deltaY) && duration < 600) {
          if (deltaX < 0) {
            nextSlide(); // Swiped left -> next
          } else {
            prevSlide(); // Swiped right -> prev
          }
        }
      }
    }, { passive: true });
  }

  // Page Visibility API — pause when visitor leaves tab
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      cancelAnimationFrame(autoplayRafId);
      const activeVideo = transition.activeVideoSlot === 1 ? elements.videoPrimary : elements.videoSecondary;
      if (activeVideo) activeVideo.pause();
    } else if (!isPaused && !prefersReducedMotion) {
      const activeVideo = transition.activeVideoSlot === 1 ? elements.videoPrimary : elements.videoSecondary;
      if (activeVideo) activeVideo.play().catch(() => {});
      startAutoplayProgress();
    }
  });

  // Initial Video Playback & Autoplay Start
  const firstVideo = elements.videoPrimary;
  if (firstVideo) {
    firstVideo.play()
      .then(() => {
        firstVideo.classList.add('playing');
        if (elements.stagePoster) elements.stagePoster.classList.add('hidden');
      })
      .catch((err) => {
        console.warn('Initial autoplay restricted; fallback poster engaged:', err);
        if (elements.stagePoster) elements.stagePoster.classList.remove('hidden');
      });
  }

  // Start Autoplay Loop
  if (!prefersReducedMotion) {
    startAutoplayProgress();
  }
});

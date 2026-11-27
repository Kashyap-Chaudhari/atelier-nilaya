/**
 * ============================================================================
 * ATELIER NILAYA — THE VELVET TRAY STORY MOTION CONTROLLER
 * Single scroll-triggered effect: velvet lids lift and slide away (staggered 120ms).
 * Once unveiled, nothing else animates. Respects prefers-reduced-motion.
 * ============================================================================
 */

(function () {
  'use strict';

  function initVelvetTray() {
    const traySection = document.getElementById('atelier-velvet-tray');
    if (!traySection) return;

    // Check user's motion preference
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (prefersReducedMotion) {
      traySection.classList.add('is-unveiled');
      return;
    }

    // Single Scroll-Triggered Reveal via IntersectionObserver
    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver(
        function (entries, obs) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              traySection.classList.add('is-unveiled');
              // Ensure video is playing quietly
              const video = traySection.querySelector('.wide-video-element');
              if (video && video.paused) {
                video.play().catch(function () {
                  // Autoplay policy fallback
                });
              }
              // Stop observing: single trigger only, then nothing else animates
              obs.unobserve(entry.target);
            }
          });
        },
        {
          root: null,
          threshold: 0.15,
          rootMargin: '0px 0px -50px 0px'
        }
      );

      observer.observe(traySection);
    } else {
      // Fallback for legacy browsers without IntersectionObserver
      traySection.classList.add('is-unveiled');
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initVelvetTray);
  } else {
    initVelvetTray();
  }
})();

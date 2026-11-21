/**
 * Atelier Nilaya — Mobile Application Navigation Controller
 * Handles smart scroll-hide, bottom tab routing, drawer opening,
 * keyboard detection, and bag count synchronization.
 */
(function () {
  'use strict';

  function initMobileAppNav() {
    // Only initialize if mobile navigation elements exist
    const topBar = document.getElementById('nilaya-mobile-top-bar');
    const bottomBar = document.getElementById('nilaya-mobile-bottom-bar');
    if (!topBar && !bottomBar) return;

    // 1. Path-based active bottom tab detection
    const pathname = window.location.pathname;
    const homeBtn = document.getElementById('mobile-nav-home');
    const ordersBtn = document.getElementById('mobile-nav-orders');
    const trackBtn = document.getElementById('mobile-nav-track');
    const accountBtn = document.getElementById('mobile-nav-account');

    function setActiveTab(el) {
      if (!el) return;
      document.querySelectorAll('.nilaya-bottom-btn').forEach(btn => {
        btn.classList.remove('active');
        btn.removeAttribute('aria-current');
      });
      el.classList.add('active');
      el.setAttribute('aria-current', 'page');
    }

    if (pathname === '/' || pathname === '/home/') {
      setActiveTab(homeBtn);
    } else if (pathname.includes('/orders/history/')) {
      setActiveTab(ordersBtn);
    } else if (pathname.includes('/orders/track/')) {
      setActiveTab(trackBtn);
    } else if (pathname.includes('/account/') || pathname.includes('/login/')) {
      setActiveTab(accountBtn);
    }

    // 2. Checkout / Payment page hide guard
    if (pathname.includes('/checkout/') || pathname.includes('/payment/')) {
      document.body.classList.add('page-checkout');
    }

    // 3. Top bar scroll slide-out / slide-in
    if (topBar) {
      let lastScrollY = window.pageYOffset || document.documentElement.scrollTop;
      let ticking = false;
      const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

      if (!prefersReducedMotion) {
        window.addEventListener('scroll', function () {
          if (!ticking) {
            window.requestAnimationFrame(function () {
              const currentScrollY = window.pageYOffset || document.documentElement.scrollTop;
              if (currentScrollY > lastScrollY && currentScrollY > 60) {
                // Scrolling down -> hide top bar
                topBar.classList.add('is-hidden');
              } else if (currentScrollY < lastScrollY) {
                // Scrolling up -> show top bar
                topBar.classList.remove('is-hidden');
              }
              lastScrollY = Math.max(0, currentScrollY);
              ticking = false;
            });
            ticking = true;
          }
        }, { passive: true });
      }

      // Connect top bar menu toggle to existing drawer
      const topMenuBtn = document.getElementById('nilaya-mobile-top-menu-btn');
      if (topMenuBtn) {
        topMenuBtn.addEventListener('click', function (e) {
          e.preventDefault();
          const oldBtn = document.getElementById('aaranya-mobile-menu-btn');
          if (oldBtn) {
            oldBtn.click();
          } else {
            const drawer = document.getElementById('aaranya-mobile-drawer');
            const backdrop = document.getElementById('aaranya-mobile-backdrop');
            if (drawer) drawer.classList.add('is-open');
            if (backdrop) backdrop.classList.add('is-open');
            document.body.style.overflow = 'hidden';
          }
        });
      }

      // Connect top bar search button to open drawer search
      const topSearchBtn = document.getElementById('nilaya-mobile-top-search-btn');
      if (topSearchBtn) {
        topSearchBtn.addEventListener('click', function (e) {
          e.preventDefault();
          const topMenu = document.getElementById('nilaya-mobile-top-menu-btn');
          if (topMenu) topMenu.click();
          setTimeout(function () {
            const searchInput = document.querySelector('.aaranya-mobile-input');
            if (searchInput) searchInput.focus();
          }, 300);
        });
      }
    }

    // 4. Connect bottom bar Shop button to open category drawer
    const shopBtn = document.getElementById('mobile-nav-shop');
    if (shopBtn) {
      shopBtn.addEventListener('click', function (e) {
        e.preventDefault();
        const topMenu = document.getElementById('nilaya-mobile-top-menu-btn') || document.getElementById('aaranya-mobile-menu-btn');
        if (topMenu) topMenu.click();
      });
    }

    // 5. On-screen keyboard detection via visualViewport
    if (window.visualViewport) {
      const initialHeight = window.innerHeight;
      window.visualViewport.addEventListener('resize', function () {
        const currentHeight = window.visualViewport.height;
        // If viewport shrunk by > 120px, keyboard is active
        if (initialHeight - currentHeight > 120) {
          document.body.classList.add('is-keyboard-open');
        } else {
          document.body.classList.remove('is-keyboard-open');
        }
      });
    } else {
      // Fallback for older browsers
      document.addEventListener('focusin', function (e) {
        if (e.target.matches('input, textarea, select')) {
          document.body.classList.add('is-keyboard-open');
        }
      });
      document.addEventListener('focusout', function (e) {
        if (e.target.matches('input, textarea, select')) {
          document.body.classList.remove('is-keyboard-open');
        }
      });
    }

    // 6. Synchronize bottom bag count badge with existing header bag badge
    const headerBagCount = document.getElementById('header-bag-count');
    const bottomBagCount = document.getElementById('mobile-bottom-bag-count');

    function syncBagBadge(count) {
      if (!bottomBagCount) return;
      const num = parseInt(count, 10) || 0;
      bottomBagCount.textContent = num;
      bottomBagCount.style.display = num > 0 ? 'block' : 'none';
    }

    if (headerBagCount && bottomBagCount) {
      syncBagBadge(headerBagCount.textContent);

      // Observe mutations on headerBagCount
      const observer = new MutationObserver(function (mutations) {
        mutations.forEach(function () {
          syncBagBadge(headerBagCount.textContent);
        });
      });
      observer.observe(headerBagCount, { childList: true, characterData: true, subtree: true });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMobileAppNav);
  } else {
    initMobileAppNav();
  }
})();

/**
 * Mobile-Only Floating Bottom Navigation Controller
 * Features:
 * - Route-based active tab detection with aria-current="page"
 * - Smart scroll hide / show (hides on scroll down, reveals on scroll up)
 * - Safe area & viewport keyboard detection
 * - Bag badge synchronization with pop animation
 * - Accessible tap handling & bag drawer integration
 */
(function () {
  'use strict';

  function initMobileAppNav() {
    const floatingNav = document.getElementById('mobile-floating-nav');
    const topBar = document.getElementById('nilaya-mobile-top-bar');
    if (!floatingNav && !topBar) return;

    // ------------------------------------------------------------------------
    // 1. Path-based Active Tab Highlighting
    // ------------------------------------------------------------------------
    const pathname = window.location.pathname.toLowerCase();
    const homeTab = document.getElementById('mobile-nav-home');
    const shopTab = document.getElementById('mobile-nav-shop');
    const trackTab = document.getElementById('mobile-nav-track');
    const bagTab = document.getElementById('mobile-nav-bag');
    const accountTab = document.getElementById('mobile-nav-account');

    function setActiveTab(activeEl) {
      if (!floatingNav) return;
      const allTabs = floatingNav.querySelectorAll('.mobile-nav-tab');
      allTabs.forEach(tab => {
        tab.classList.remove('is-active');
        tab.removeAttribute('aria-current');
      });
      if (activeEl) {
        activeEl.classList.add('is-active');
        activeEl.setAttribute('aria-current', 'page');
      }
    }

    if (pathname === '/' || pathname === '/home/' || pathname === '/campaigns/') {
      setActiveTab(homeTab);
    } else if (
      pathname.includes('/vault') ||
      pathname.includes('/category/') ||
      pathname.includes('/c/') ||
      pathname.includes('/p/') ||
      pathname.includes('/product/')
    ) {
      setActiveTab(shopTab);
    } else if (pathname.includes('/track') || pathname.includes('/orders/track/')) {
      setActiveTab(trackTab);
    } else if (pathname.includes('/cart') || pathname.includes('/checkout')) {
      setActiveTab(bagTab);
    } else if (
      pathname.includes('/account') ||
      pathname.includes('/login') ||
      pathname.includes('/register') ||
      pathname.includes('/signup') ||
      pathname.includes('/profile')
    ) {
      setActiveTab(accountTab);
    }

    // ------------------------------------------------------------------------
    // 2. Checkout & Payment Page Guard
    // ------------------------------------------------------------------------
    if (pathname.includes('/checkout/') || pathname.includes('/payment/')) {
      document.body.classList.add('page-checkout');
    }

    // ------------------------------------------------------------------------
    // 3. Smart Scroll Direction Detection (Hide down / Reveal up)
    // ------------------------------------------------------------------------
    let lastScrollY = window.pageYOffset || document.documentElement.scrollTop;
    let ticking = false;
    const scrollThreshold = 10;
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (!prefersReducedMotion) {
      window.addEventListener('scroll', function () {
        if (!ticking) {
          window.requestAnimationFrame(function () {
            const currentScrollY = window.pageYOffset || document.documentElement.scrollTop;
            const diff = currentScrollY - lastScrollY;

            if (currentScrollY > 70 && diff > scrollThreshold) {
              // Scrolling down -> hide both top bar and floating bottom nav
              if (floatingNav) floatingNav.classList.add('is-hidden');
              if (topBar) topBar.classList.add('is-hidden');
            } else if (diff < -scrollThreshold || currentScrollY <= 30) {
              // Scrolling up or near top -> reveal
              if (floatingNav) floatingNav.classList.remove('is-hidden');
              if (topBar) topBar.classList.remove('is-hidden');
            }

            lastScrollY = Math.max(0, currentScrollY);
            ticking = false;
          });
          ticking = true;
        }
      }, { passive: true });
    }

    // ------------------------------------------------------------------------
    // 4. Mobile Top Bar Navigation Drawer Hooks
    // ------------------------------------------------------------------------
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

    const topSearchBtn = document.getElementById('nilaya-mobile-top-search-btn');
    const searchOverlay = document.getElementById('nilaya-mobile-search-overlay');
    const searchCloseBtn = document.getElementById('nilaya-mobile-search-close');
    const searchInput = document.getElementById('nilaya-mobile-search-input');

    if (topSearchBtn && searchOverlay) {
      topSearchBtn.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        const isOpen = searchOverlay.classList.contains('is-active');
        if (isOpen) {
          searchOverlay.classList.remove('is-active');
          searchOverlay.setAttribute('aria-hidden', 'true');
          topSearchBtn.setAttribute('aria-expanded', 'false');
        } else {
          searchOverlay.classList.add('is-active');
          searchOverlay.setAttribute('aria-hidden', 'false');
          topSearchBtn.setAttribute('aria-expanded', 'true');
          if (searchInput) {
            setTimeout(function () {
              searchInput.focus();
            }, 50);
          }
        }
      });
    }

    if (searchCloseBtn && searchOverlay) {
      searchCloseBtn.addEventListener('click', function (e) {
        e.preventDefault();
        searchOverlay.classList.remove('is-active');
        searchOverlay.setAttribute('aria-hidden', 'true');
        if (topSearchBtn) topSearchBtn.setAttribute('aria-expanded', 'false');
      });
    }

    // Close mobile search on Escape key
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && searchOverlay && searchOverlay.classList.contains('is-active')) {
        searchOverlay.classList.remove('is-active');
        searchOverlay.setAttribute('aria-hidden', 'true');
        if (topSearchBtn) topSearchBtn.setAttribute('aria-expanded', 'false');
      }
    });

    // ------------------------------------------------------------------------
    // 5. Bag Drawer Trigger on Mobile
    // ------------------------------------------------------------------------
    if (bagTab) {
      bagTab.addEventListener('click', function (e) {
        e.preventDefault();
        // If sliding bag drawer is available on page, open it smoothly
        const bagDrawer = document.getElementById('nilaya-bag-drawer') || document.getElementById('bag-drawer') || document.getElementById('velvet-bag-drawer');
        if (typeof window.openBagDrawer === 'function') {
          window.openBagDrawer();
        } else if (window.NilayaBag && typeof window.NilayaBag.open === 'function') {
          window.NilayaBag.open();
        } else if (bagDrawer) {
          bagDrawer.classList.add('is-open');
          document.body.classList.add('bag-open');
        } else {
          // Fallback if not on an exhibition page with drawer
          window.location.href = '/vault/';
        }
      });
    }

    // ------------------------------------------------------------------------
    // 6. Bag Badge Count Sync & Pop Animation
    // ------------------------------------------------------------------------
    const bottomBadge = document.getElementById('mobile-bottom-bag-count');

    function animateBadgePop(badgeEl, count) {
      if (!badgeEl) return;
      const num = parseInt(count, 10) || 0;
      badgeEl.textContent = num;
      badgeEl.setAttribute('aria-label', num + ' items in bag');

      if (num > 0) {
        badgeEl.style.display = 'inline-flex';
        // Trigger quick pop animation
        badgeEl.classList.remove('is-popping');
        void badgeEl.offsetWidth; // trigger reflow
        badgeEl.classList.add('is-popping');
      } else {
        badgeEl.style.display = 'none';
      }
    }

    // Expose global badge update function for cart event dispatchers
    window.updateMobileNavBagBadge = function (newCount) {
      animateBadgePop(bottomBadge, newCount);
    };

    // Synchronize with existing header badges if present
    const headerBagCount = document.getElementById('header-bag-count');
    if (headerBagCount && bottomBadge) {
      const initialCount = parseInt(headerBagCount.textContent, 10) || 0;
      if (initialCount > 0) {
        bottomBadge.textContent = initialCount;
        bottomBadge.style.display = 'inline-flex';
      }

      // Observe mutations on header badge to trigger animated pop
      try {
        const observer = new MutationObserver(function (mutations) {
          mutations.forEach(function (mutation) {
            if (mutation.type === 'characterData' || mutation.type === 'childList') {
              const val = headerBagCount.textContent.trim();
              animateBadgePop(bottomBadge, val);
            }
          });
        });
        observer.observe(headerBagCount, { characterData: true, childList: true, subtree: true });
      } catch (err) {}
    }

    // Also listen for custom cart events (cart:updated, bag:updated)
    window.addEventListener('cart:updated', function (e) {
      if (e.detail && typeof e.detail.itemCount !== 'undefined') {
        animateBadgePop(bottomBadge, e.detail.itemCount);
      }
    });

    // ------------------------------------------------------------------------
    // 7. On-Screen Keyboard Handling
    // ------------------------------------------------------------------------
    if (window.visualViewport) {
      const initialHeight = window.innerHeight;
      window.visualViewport.addEventListener('resize', function () {
        const currentHeight = window.visualViewport.height;
        if (initialHeight - currentHeight > 120) {
          document.body.classList.add('is-keyboard-open');
        } else {
          document.body.classList.remove('is-keyboard-open');
        }
      });
    } else {
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
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMobileAppNav);
  } else {
    initMobileAppNav();
  }
})();

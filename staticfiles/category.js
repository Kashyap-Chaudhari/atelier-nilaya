/**
 * ============================================================================
 * ATELIER NILAYA — CATEGORY & VAULT GALLERY CONTROLLER (category.js)
 * Clean, lightweight luxury gallery controller (Vanilla JS, Zero Frameworks)
 * - Pandora-inspired minimal product cards
 * - Image error recovery & card protection
 * - Mobile horizontal swipe photo toggle (Primary <-> Secondary)
 * - Load More with progress track and URL query parameter (?page=N)
 * - Wishlist authentication redirection and persistence
 * - Add to Bag AJAX with double-click protection
 * ============================================================================
 */

(function () {
  'use strict';

  // Global Image Error Handler (Retry once, then hide card gracefully)
  window.handleProductImageError = function (img) {
    if (!img) return;
    if (!img.dataset.retried) {
      img.dataset.retried = '1';
      const fallback = img.getAttribute('data-fallback');
      if (fallback && img.src !== fallback) {
        img.src = fallback;
        return;
      }
    }
    const tile = img.closest('.product-tile');
    if (tile) {
      tile.style.display = 'none';
    }
  };

  // Filter Panel & URL State Manager
  function initFilterPanel() {
    const toggleBtn = document.getElementById('filter-toggle-btn');
    const filterPanel = document.getElementById('filter-panel');
    const filterForm = document.getElementById('filter-form');

    if (toggleBtn && filterPanel) {
      toggleBtn.addEventListener('click', () => {
        const isHidden = filterPanel.hasAttribute('hidden');
        if (isHidden) {
          filterPanel.removeAttribute('hidden');
          toggleBtn.setAttribute('aria-expanded', 'true');
          toggleBtn.classList.add('is-active');
        } else {
          filterPanel.setAttribute('hidden', '');
          toggleBtn.setAttribute('aria-expanded', 'false');
          toggleBtn.classList.remove('is-active');
        }
      });
    }

    // Individual Chip Removal
    const chipsContainer = document.getElementById('active-filter-chips');
    if (chipsContainer && filterForm) {
      chipsContainer.addEventListener('click', (e) => {
        const chip = e.target.closest('[data-filter-key]');
        if (!chip) return;
        const key = chip.getAttribute('data-filter-key');
        const targetSelect = filterForm.querySelector(`select[name="${key}"]`);
        if (targetSelect) {
          targetSelect.value = 'all';
          filterForm.submit();
        }
      });
    }

    // Auto-update on select dropdown changes
    if (filterForm) {
      const selects = filterForm.querySelectorAll('select');
      selects.forEach(sel => {
        sel.addEventListener('change', () => {
          filterForm.submit();
        });
      });
    }
  }

  // "Load More" Batching with Progress Track and URL State
  function initLoadMore() {
    const loadMoreBtn = document.getElementById('load-more-btn');
    const loadMoreSection = document.getElementById('load-more-section');
    const visibleCounter = document.getElementById('visible-count');
    const progressBar = document.getElementById('load-more-progress-bar');
    const tiles = Array.from(document.querySelectorAll('.products-grid .product-tile'));

    if (tiles.length === 0) return;

    const batchSize = 12;
    const totalCount = tiles.length;

    // Check initial page from URL (?page=N)
    const urlParams = new URLSearchParams(window.location.search);
    const initialPage = parseInt(urlParams.get('page') || '1', 10);
    let currentlyVisible = Math.min(Math.max(1, initialPage) * batchSize, totalCount);

    function updateVisibility() {
      tiles.forEach((tile, index) => {
        tile.style.display = (index < currentlyVisible) ? '' : 'none';
      });

      if (visibleCounter) visibleCounter.textContent = currentlyVisible;
      if (progressBar) {
        const pct = Math.round((currentlyVisible / totalCount) * 100);
        progressBar.style.width = `${pct}%`;
      }

      if (loadMoreBtn) {
        if (currentlyVisible >= totalCount) {
          loadMoreBtn.style.display = 'none';
        } else {
          loadMoreBtn.style.display = '';
        }
      }

      if (loadMoreSection && totalCount <= batchSize) {
        loadMoreSection.style.display = 'none';
      }
    }

    updateVisibility();

    if (loadMoreBtn) {
      loadMoreBtn.addEventListener('click', () => {
        currentlyVisible = Math.min(currentlyVisible + batchSize, totalCount);
        const currentPage = Math.ceil(currentlyVisible / batchSize);

        // Update URL query parameter without reloading
        const url = new URL(window.location.href);
        url.searchParams.set('page', currentPage);
        window.history.pushState({ page: currentPage }, '', url.toString());

        updateVisibility();
      });
    }

    // Handle browser back/forward buttons
    window.addEventListener('popstate', (e) => {
      const params = new URLSearchParams(window.location.search);
      const page = parseInt(params.get('page') || '1', 10);
      currentlyVisible = Math.min(Math.max(1, page) * batchSize, totalCount);
      updateVisibility();
    });
  }

  // Mobile Horizontal Swipe for Cards (Photo 1 <-> Photo 2)
  function initMobileCardSwipe() {
    const stages = document.querySelectorAll('.tile-stage');
    stages.forEach(stage => {
      let startX = 0;
      let startY = 0;
      let isHorizontal = false;

      stage.addEventListener('touchstart', (e) => {
        if (e.touches.length === 1) {
          startX = e.touches[0].clientX;
          startY = e.touches[0].clientY;
          isHorizontal = false;
        }
      }, { passive: true });

      stage.addEventListener('touchmove', (e) => {
        if (e.touches.length === 1) {
          const diffX = Math.abs(e.touches[0].clientX - startX);
          const diffY = Math.abs(e.touches[0].clientY - startY);
          if (diffX > 10 && diffX > diffY) {
            isHorizontal = true;
          }
        }
      }, { passive: true });

      stage.addEventListener('touchend', (e) => {
        if (!isHorizontal) return;
        const diffX = e.changedTouches[0].clientX - startX;
        const tile = stage.closest('.product-tile');
        if (!tile) return;

        const dot1 = tile.querySelector('.image-dot[data-dot="1"]');
        const dot2 = tile.querySelector('.image-dot[data-dot="2"]');

        if (diffX < -30) {
          // Swiped left -> show secondary photo
          tile.classList.add('is-secondary-active');
          if (dot1) dot1.classList.remove('is-active');
          if (dot2) dot2.classList.add('is-active');
        } else if (diffX > 30) {
          // Swiped right -> show primary photo
          tile.classList.remove('is-secondary-active');
          if (dot2) dot2.classList.remove('is-active');
          if (dot1) dot1.classList.add('is-active');
        }
      });
    });
  }

  // Wishlist Handling with Authentication Redirect
  function initWishlist() {
    const WISH_KEY = 'nilaya_wishlist';
    let localWishlist = [];
    try {
      localWishlist = JSON.parse(localStorage.getItem(WISH_KEY) || '[]');
    } catch (e) {
      localWishlist = [];
    }

    const wishlistBtns = document.querySelectorAll('[data-wishlist-btn]');
    wishlistBtns.forEach(btn => {
      const pid = parseInt(btn.getAttribute('data-product-id'), 10);
      if (localWishlist.includes(pid)) {
        btn.classList.add('is-active');
        btn.setAttribute('aria-pressed', 'true');
      }

      btn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();

        const isCurrentlyActive = btn.classList.contains('is-active');
        const nextState = !isCurrentlyActive;

        btn.classList.toggle('is-active', nextState);
        btn.setAttribute('aria-pressed', nextState ? 'true' : 'false');

        if (nextState) {
          if (!localWishlist.includes(pid)) localWishlist.push(pid);
        } else {
          localWishlist = localWishlist.filter(id => id !== pid);
        }
        localStorage.setItem(WISH_KEY, JSON.stringify(localWishlist));

        const countElements = [
          document.getElementById('header-wishlist-count'),
          document.getElementById('footer-wishlist-count')
        ];
        countElements.forEach(el => {
          if (el) el.textContent = localWishlist.length;
        });

        fetch('/api/wishlist/toggle', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ product_id: pid })
        })
        .then(res => {
          if (res.status === 401) {
            return res.json().then(data => {
              if (data && data.login_url) {
                window.location.href = data.login_url;
              } else {
                window.location.href = `/login/?next=${encodeURIComponent(window.location.pathname + window.location.search)}&wishlist_add=${pid}`;
              }
            });
          }
        })
        .catch(err => console.warn('Wishlist API offline:', err));
      });
    });
  }

  // Plain, Accessible Notification Toast
  function showToast(message, isError = false) {
    let toast = document.getElementById('toast-notification');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'toast-notification';
      toast.className = 'toast-notification';
      document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.classList.toggle('is-error', isError);
    toast.removeAttribute('hidden');
    toast.style.display = 'block';

    if (window._toastTimeout) clearTimeout(window._toastTimeout);
    window._toastTimeout = setTimeout(() => {
      toast.setAttribute('hidden', '');
      toast.style.display = 'none';
    }, 3500);
  }

  // "Add to Bag" API Handler with Double-Click Protection
  function initAddToBag() {
    document.addEventListener('click', (e) => {
      const btn = e.target.closest('[data-add-to-bag]');
      if (!btn) return;

      // If unified BagDrawer controller is available, delegate to BagDrawer for drawer slide-in & cart_v2 sync
      if (window.NilayaBag && typeof window.NilayaBag.addToBag === 'function') {
        return;
      }

      e.preventDefault();
      e.stopPropagation();

      const tile = btn.closest('.product-tile');
      const sku = btn.getAttribute('data-sku') || (tile && tile.getAttribute('data-sku'));
      const pid = parseInt(btn.getAttribute('data-product-id') || (tile && tile.getAttribute('data-product-id')), 10);
      const metal = tile ? (tile.getAttribute('data-current-metal') || 'yellow_gold') : 'yellow_gold';
      const productName = tile ? (tile.querySelector('.tile-name')?.textContent?.trim() || 'Piece') : 'Piece';

      const originalText = btn.innerHTML;
      btn.textContent = 'Adding...';
      btn.disabled = true;

      fetch('/api/cart/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sku: sku, product_id: pid, metal: metal, quantity: 1 })
      })
      .then(res => res.json().then(data => ({ status: res.status, ok: res.ok, data })))
      .then(({ status, ok, data }) => {
        if (ok && data.success) {
          btn.textContent = 'Added ✓';
          const headerCount = document.getElementById('header-bag-count');
          const footerCount = document.getElementById('footer-bag-count');
          if (headerCount) headerCount.textContent = data.count;
          if (footerCount) footerCount.textContent = data.count;

          showToast(`Added to your bag: ${productName}`);

          setTimeout(() => {
            btn.innerHTML = originalText;
            btn.disabled = false;
          }, 2000);
        } else {
          const errorMsg = (data && data.error) ? data.error : 'Selected piece is unavailable. Please try again.';
          btn.textContent = 'Unavailable';
          showToast(errorMsg, true);

          setTimeout(() => {
            btn.innerHTML = originalText;
            btn.disabled = false;
          }, 2500);
        }
      })
      .catch((err) => {
        console.error('[Add to Bag Error]', err);
        btn.textContent = 'Try Again';
        showToast('Unable to connect to boutique server. Please retry.', true);

        setTimeout(() => {
          btn.innerHTML = originalText;
          btn.disabled = false;
        }, 2500);
      });
    });
  }

  // Document Ready Initialization
  function initCategoryPage() {
    initFilterPanel();
    initLoadMore();
    initMobileCardSwipe();
    initWishlist();
    initAddToBag();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCategoryPage);
  } else {
    initCategoryPage();
  }
})();

/**
 * ============================================================================
 * ATELIER NILAYA — CATEGORY GALLERY CONTROLLER (category.js)
 * Clean, lightweight luxury gallery controller (Vanilla JS, Zero Frameworks)
 * - Photographic 360° turntable spin engine (AtelierSpinViewer)
 * - Filter panel with URL parameter synchronization (history.pushState)
 * - Swatch switcher: changes metal, price, discount badge
 * - "Load more" batching (Showing X of Y pieces)
 * - Wishlist local & server persistence
 * - Add to Bag AJAX
 * ============================================================================
 */

(function () {
  'use strict';

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
    if (chipsContainer) {
      chipsContainer.addEventListener('click', (e) => {
        const chip = e.target.closest('.filter-chip');
        if (!chip) return;
        const key = chip.getAttribute('data-filter-key');
        const url = new URL(window.location.href);
        url.searchParams.delete(key);
        window.location.href = url.toString();
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

  // "Load More" Batching (Showing 8 of 16 pieces)
  function initLoadMore() {
    const loadMoreBtn = document.getElementById('load-more-btn');
    const loadMoreSection = document.getElementById('load-more-section');
    const visibleCounter = document.getElementById('visible-count');
    const tiles = Array.from(document.querySelectorAll('.product-tile'));

    const batchSize = 8;
    let currentlyVisible = batchSize;

    if (tiles.length <= batchSize) {
      if (loadMoreSection) loadMoreSection.style.display = 'none';
      return;
    }

    // Hide tiles beyond initial batch
    tiles.forEach((tile, index) => {
      if (index >= batchSize) {
        tile.style.display = 'none';
      }
    });

    if (visibleCounter) visibleCounter.textContent = batchSize;

    if (loadMoreBtn) {
      loadMoreBtn.addEventListener('click', () => {
        const nextBatch = currentlyVisible + batchSize;
        tiles.forEach((tile, index) => {
          if (index < nextBatch) {
            tile.style.display = '';
          }
        });

        currentlyVisible = Math.min(nextBatch, tiles.length);
        if (visibleCounter) visibleCounter.textContent = currentlyVisible;

        if (currentlyVisible >= tiles.length) {
          loadMoreBtn.style.display = 'none';
        }
      });
    }
  }

  // Wishlist LocalStorage & Database Persistence
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
        }).catch(err => console.warn('Wishlist API offline:', err));
      });
    });
  }

  // Plain, Accessible Notification Toast
  function showToast(message, isError = false) {
    const toast = document.getElementById('toast-notification');
    if (!toast) return;
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

  // "Add to Bag" API Handler
  function initAddToBag() {
    document.addEventListener('click', (e) => {
      const btn = e.target.closest('[data-add-to-bag]');
      if (!btn) return;

      e.preventDefault();
      const tile = btn.closest('.product-tile');
      const pid = parseInt(btn.getAttribute('data-product-id') || (tile && tile.getAttribute('data-product-id')), 10);
      const metal = tile ? (tile.getAttribute('data-current-metal') || 'yellow_gold') : 'yellow_gold';
      const productName = tile ? (tile.querySelector('.tile-name')?.textContent?.trim() || 'Piece') : 'Piece';

      const originalText = btn.textContent;
      btn.textContent = 'Adding...';
      btn.disabled = true;

      fetch('/api/cart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: pid, metal: metal, quantity: 1 })
      })
      .then(res => res.json().then(data => ({ status: res.status, ok: res.ok, data })))
      .then(({ status, ok, data }) => {
        console.log('[Add to Bag Result]', { status, ok, data, pid, metal });
        if (ok && data.success) {
          // Success: update bag count immediately
          btn.textContent = 'Added to your bag ✓';
          const headerCount = document.getElementById('header-bag-count');
          const footerCount = document.getElementById('footer-bag-count');
          if (headerCount) headerCount.textContent = data.count;
          if (footerCount) footerCount.textContent = data.count;

          showToast(`Added to your bag: ${productName} (${metal.replace(/_/g, ' ')})`);

          setTimeout(() => {
            btn.textContent = originalText;
            btn.disabled = false;
          }, 2000);
        } else {
          // Plain, actionable error
          const errorMsg = (data && data.error) ? data.error : 'Selected metal is unavailable. Please choose another metal or refresh the page.';
          btn.textContent = 'Try Again';
          showToast(errorMsg, true);

          setTimeout(() => {
            btn.textContent = originalText;
            btn.disabled = false;
          }, 2500);
        }
      })
      .catch((err) => {
        console.error('[Add to Bag Error]', err);
        btn.textContent = 'Try Again';
        showToast('Unable to connect to server. Please check your internet connection and try again.', true);

        setTimeout(() => {
          btn.textContent = originalText;
          btn.disabled = false;
        }, 2500);
      });
    });
  }

  // Document Ready Initialization
  function initCategoryPage() {
    initFilterPanel();
    initLoadMore();
    initWishlist();
    initAddToBag();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCategoryPage);
  } else {
    initCategoryPage();
  }
})();

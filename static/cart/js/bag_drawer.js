/**
 * ATELIER NILAYA — LUXURY BAG SLIDE-IN CONTROLLER
 * Vanilla JS with full state synchronization & transparent bench breakup.
 */

(function () {
  'use strict';

  function formatINR(val) {
    if (isNaN(val)) return '₹0';
    return '₹' + Math.round(val).toLocaleString('en-IN');
  }

  function getCsrfToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, 10) === 'csrftoken=') {
          cookieValue = decodeURIComponent(cookie.substring(10));
          break;
        }
      }
    }
    return cookieValue || '';
  }

  const GUEST_CART_KEY = 'cart_v2';

  function isUserAuthenticated() {
    const drawer = document.getElementById('nilaya-bag-drawer');
    if (drawer && drawer.dataset.authenticated === 'true') return true;
    return false;
  }

  /**
   * Unified cart reader and writer function.
   * When logged in: uses server-backed cart state.
   * When guest: uses browser localStorage for immediate persistence across page refreshes.
   */
  function accessCart(action, cartData) {
    if (action === 'read') {
      if (isUserAuthenticated()) {
        return BagDrawer.state || null;
      }
      try {
        const stored = localStorage.getItem(GUEST_CART_KEY);
        if (!stored) return BagDrawer.state || null;
        const parsed = JSON.parse(stored);
        if (parsed && Array.isArray(parsed.items)) {
          // Filter out broken or missing SKUs/IDs safely without crashing
          parsed.items = parsed.items.filter(item => item && (item.sku || item.product_id || item.id));
        }
        return parsed || BagDrawer.state || null;
      } catch (e) {
        console.warn('[Cart Storage Read Warning]', e);
        return BagDrawer.state || null;
      }
    } else if (action === 'write') {
      BagDrawer.state = cartData;
      if (!isUserAuthenticated()) {
        try {
          if (cartData && cartData.items && cartData.items.length > 0) {
            // Keep valid items only
            cartData.items = cartData.items.filter(item => item && (item.sku || item.product_id || item.id));
            localStorage.setItem(GUEST_CART_KEY, JSON.stringify(cartData));
          } else {
            localStorage.removeItem(GUEST_CART_KEY);
          }
        } catch (e) {
          console.warn('[Cart Storage Write Error]', e);
        }
      } else {
        try {
          localStorage.removeItem(GUEST_CART_KEY);
        } catch (e) {}
      }
      return cartData;
    }
  }

  const BagDrawer = {
    drawer: null,
    scrim: null,
    closeBtn: null,
    itemsList: null,
    emptyState: null,
    footer: null,
    state: null,

    init: function () {
      this.drawer = document.getElementById('nilaya-bag-drawer');
      this.scrim = document.getElementById('nilaya-bag-scrim');
      this.closeBtn = document.getElementById('bag-drawer-close-btn');
      this.itemsList = document.getElementById('bag-items-list');
      this.emptyState = document.getElementById('bag-empty-state');
      this.footer = document.getElementById('bag-drawer-footer');

      // Pre-render immediately from localStorage for guests so bag count and items never blink
      const cached = accessCart('read');
      if (cached && !isUserAuthenticated()) {
        this.render(cached);
      }

      this.bindEvents();
      this.fetchState();
    },

    bindEvents: function () {
      // 1. Open triggers
      document.addEventListener('click', (e) => {
        const openTrigger = e.target.closest('[data-open-bag], #header-bag-btn, .aaranya-bag-pill, .bag-link');
        if (openTrigger) {
          e.preventDefault();
          this.open();
        }

        // Close triggers
        if (e.target.closest('#bag-drawer-close-btn') || e.target === this.scrim) {
          e.preventDefault();
          this.close();
        }
      });

      // Escape key to close
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && this.isOpen()) {
          this.close();
        }
      });

      // 2. Intercept ALL "Add to Bag" buttons across Category, Vault, Wishlist & PDP
      document.addEventListener('click', (e) => {
        const addBtn = e.target.closest('[data-add-to-bag], #page-add-to-bag-btn, .tile-add-to-bag-btn, .btn-add-to-bag');
        if (!addBtn) return;

        e.preventDefault();
        e.stopPropagation();

        const card = addBtn.closest('.product-tile') || addBtn.closest('.luxury-piece-card') || addBtn.closest('article') || addBtn.closest('.product-detail-container') || addBtn.closest('.product-stage-container');

        // Read unique SKU first from the clicked button itself, then card fallback
        const sku = addBtn.getAttribute('data-sku') || addBtn.dataset.sku || (card ? (card.getAttribute('data-sku') || card.dataset.sku) : null);
        const pid = addBtn.getAttribute('data-product-id') || addBtn.dataset.productId || (card ? (card.getAttribute('data-product-id') || card.dataset.productId) : null);
        let slug = addBtn.getAttribute('data-product-slug') || addBtn.dataset.productSlug || (card ? (card.getAttribute('data-product-slug') || card.dataset.productSlug) : null);

        // If on product detail page and not in dataset, parse from URL
        if (!sku && !slug && !pid) {
          const parts = window.location.pathname.split('/').filter(Boolean);
          if (parts.length > 0) {
            slug = parts[parts.length - 1];
          }
        }

        // Selected metal (from active swatch/dot if present, or fallback to yellow_gold)
        let metal = 'yellow_gold';
        if (card) {
          const activeDot = card.querySelector('.metal-dot.is-active, .swatch-btn.is-selected');
          if (activeDot && activeDot.dataset.metal) {
            metal = activeDot.dataset.metal;
          }
        } else {
          const activeSwatch = document.querySelector('.swatches-row .swatch-btn.is-selected');
          if (activeSwatch && activeSwatch.dataset.metal) {
            metal = activeSwatch.dataset.metal;
          }
        }

        const origText = addBtn.textContent;
        addBtn.textContent = 'Adding...';

        this.addToBag({
          sku: sku,
          product_id: pid,
          slug: slug,
          metal: metal,
          quantity: 1
        }, () => {
          addBtn.textContent = 'Added ✓';
          setTimeout(() => {
            addBtn.textContent = origText;
          }, 1500);
        });
      });

      // 3. Stepper & Remove clicks inside the drawer
      if (this.itemsList) {
        this.itemsList.addEventListener('click', (e) => {
          const stepBtn = e.target.closest('[data-qty-action]');
          if (stepBtn) {
            const itemId = stepBtn.dataset.itemId;
            const currentQty = parseInt(stepBtn.dataset.currentQty, 10);
            const action = stepBtn.dataset.qtyAction;
            const newQty = action === 'plus' ? currentQty + 1 : currentQty - 1;
            this.updateItem(itemId, newQty);
            return;
          }

          const removeBtn = e.target.closest('[data-remove-item]');
          if (removeBtn) {
            const itemId = removeBtn.dataset.itemId;
            this.removeItem(itemId);
          }
        });
      }
    },

    open: function () {
      if (this.drawer) this.drawer.classList.add('is-open');
      if (this.scrim) this.scrim.classList.add('is-open');
      document.body.style.overflow = 'hidden';
    },

    close: function () {
      if (this.drawer) this.drawer.classList.remove('is-open');
      if (this.scrim) this.scrim.classList.remove('is-open');
      document.body.style.overflow = '';
    },

    isOpen: function () {
      return this.drawer && this.drawer.classList.contains('is-open');
    },

    fetchState: function () {
      // If user is authenticated, check if there is an unmerged guest cart in localStorage
      if (isUserAuthenticated()) {
        try {
          const guestCartRaw = localStorage.getItem(GUEST_CART_KEY);
          if (guestCartRaw) {
            const guestCart = JSON.parse(guestCartRaw);
            if (guestCart && guestCart.items && guestCart.items.length > 0) {
              fetch('/cart/api/merge/', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({ items: guestCart.items })
              })
                .then(res => res.json())
                .then(data => {
                  try { localStorage.removeItem(GUEST_CART_KEY); } catch (e) {}
                  if (data.success && data.cart) {
                    accessCart('write', data.cart);
                    this.render(data.cart);
                  }
                })
                .catch(() => {
                  this.requestServerState();
                });
              return;
            }
          }
        } catch (e) {}
      }

      this.requestServerState();
    },

    requestServerState: function () {
      fetch('/cart/api/state/')
        .then(res => res.json())
        .then(data => {
          if (data.success && data.cart) {
            accessCart('write', data.cart);
            this.render(data.cart);
          }
        })
        .catch(err => {
          console.error('[Cart State Error]', err);
          const fallback = accessCart('read');
          if (fallback) this.render(fallback);
        });
    },

    addToBag: function (payload, callback) {
      fetch('/cart/add/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify(payload)
      })
      .then(res => res.json())
      .then(data => {
        if (data.success && data.cart) {
          accessCart('write', data.cart);
          this.render(data.cart);
          this.open();
          if (callback) callback();
        } else {
          console.error('[Add to Cart Failed]', data);
          if (callback) callback();
        }
      })
      .catch(err => {
        console.error('[Add to Cart Error]', err);
        if (callback) callback();
      });
    },

    updateItem: function (itemId, quantity) {
      fetch('/cart/api/update/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({ item_id: itemId, quantity: quantity })
      })
      .then(res => res.json())
      .then(data => {
        if (data.success && data.cart) {
          accessCart('write', data.cart);
          this.render(data.cart);
        }
      });
    },

    removeItem: function (itemId) {
      fetch('/cart/api/remove/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({ item_id: itemId })
      })
      .then(res => res.json())
      .then(data => {
        if (data.success && data.cart) {
          accessCart('write', data.cart);
          this.render(data.cart);
        }
      });
    },

    render: function (cart) {
      this.state = cart;

      const noticeEl = document.getElementById('bag-unavailable-notice');
      if (noticeEl) {
        if (cart.unavailable_notice) {
          noticeEl.textContent = cart.unavailable_notice;
          noticeEl.style.display = 'block';
        } else {
          noticeEl.style.display = 'none';
        }
      }

      // Update badge counts across header, drawer, and mobile menu
      const countEl = document.getElementById('drawer-bag-count');
      if (countEl) countEl.textContent = cart.total_items;

      const headerCount = document.getElementById('header-bag-count');
      if (headerCount) {
        headerCount.textContent = cart.total_items;
        headerCount.style.display = cart.total_items > 0 ? 'inline-flex' : 'none';
      }

      const navbarCount = document.getElementById('navbar-bag-count');
      if (navbarCount) {
        navbarCount.textContent = cart.total_items;
        navbarCount.style.display = cart.total_items > 0 ? 'inline-flex' : 'none';
      }

      const footerCount = document.getElementById('footer-bag-count');
      if (footerCount) footerCount.textContent = cart.total_items;

      const mobileCount = document.getElementById('mobile-bag-count');
      if (mobileCount) mobileCount.textContent = cart.total_items;

      const mobileNavCount = document.getElementById('mobile-nav-bag-count');
      if (mobileNavCount) mobileNavCount.textContent = cart.total_items;

      // Update and pop mobile floating nav badge
      if (typeof window.updateMobileNavBagBadge === 'function') {
        window.updateMobileNavBagBadge(cart.total_items);
      }

      if (!cart.items || cart.items.length === 0) {
        if (this.emptyState) this.emptyState.style.display = 'block';
        if (this.itemsList) this.itemsList.style.display = 'none';
        if (this.footer) this.footer.style.display = 'none';
        return;
      }

      if (this.emptyState) this.emptyState.style.display = 'none';
      if (this.itemsList) {
        this.itemsList.style.display = 'flex';
        this.itemsList.innerHTML = cart.items.map(item => `
          <div class="bag-item-card">
            <div class="bag-item-img-wrap">
              <img src="${item.image}" alt="${item.name}" class="bag-item-img" onerror="this.src='/static/lifestyle/hero-lifestyle-1920.webp'">
            </div>
            <div class="bag-item-details">
              <div>
                <h4 class="bag-item-title">${item.name}</h4>
                <div class="bag-item-meta">
                  <span class="bag-meta-pill">${item.metal.replace(/_/g, ' ')}</span>
                  ${item.size && item.size !== 'Standard' ? `<span class="bag-meta-pill">Size: ${item.size}</span>` : ''}
                </div>
                ${item.engraving_text ? `<div class="bag-engraving-note">“${item.engraving_text}”</div>` : ''}
                ${item.is_made_to_order ? `<div class="bag-item-mto-badge">Made to Order (${item.making_days} days bench work)</div>` : ''}
                ${item.is_one_of_a_kind ? `<div class="bag-item-mto-badge" style="color:#AD9161;">Only 1 Available in Vault</div>` : ''}
              </div>

              <div class="bag-item-bottom-row">
                <div class="bag-qty-stepper">
                  <button type="button" class="qty-step-btn" data-qty-action="minus" data-item-id="${item.id}" data-current-qty="${item.quantity}" aria-label="Decrease quantity">&minus;</button>
                  <span class="qty-val">${item.quantity}</span>
                  <button type="button" class="qty-step-btn" data-qty-action="plus" data-item-id="${item.id}" data-current-qty="${item.quantity}" aria-label="Increase quantity">+</button>
                </div>
                
                <div class="bag-item-price-wrap">
                  <span class="bag-item-price">${formatINR(item.line_total)}</span>
                  <button type="button" class="bag-item-remove-btn" data-remove-item data-item-id="${item.id}">Remove</button>
                </div>
              </div>
            </div>
          </div>
        `).join('');
      }

      // Update Price Breakup
      if (this.footer) {
        this.footer.style.display = 'block';

        const goldEl = document.getElementById('breakup-gold-val');
        if (goldEl) goldEl.textContent = formatINR(cart.gold_total);

        const makingEl = document.getElementById('breakup-making-val');
        if (makingEl) makingEl.textContent = formatINR(cart.making_total);

        const stoneRow = document.getElementById('breakup-stone-row');
        const stoneEl = document.getElementById('breakup-stone-val');
        if (stoneEl) {
          stoneEl.textContent = formatINR(cart.stone_total);
          if (stoneRow) stoneRow.style.display = cart.stone_total > 0 ? 'flex' : 'none';
        }

        const gstEl = document.getElementById('breakup-gst-val');
        if (gstEl) gstEl.textContent = formatINR(cart.gst_total);

        const totalEl = document.getElementById('breakup-total-val');
        if (totalEl) totalEl.textContent = formatINR(cart.final_total);
      }
    }
  };

  // Initialize once DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => BagDrawer.init());
  } else {
    BagDrawer.init();
  }

  window.NilayaBag = BagDrawer;
  window.openBagDrawer = function () { BagDrawer.open(); };
  window.closeBagDrawer = function () { BagDrawer.close(); };
  window.NilayaBag.accessCart = accessCart;
  window.NilayaBag.clearGuestCart = function () {
    try {
      localStorage.removeItem(GUEST_CART_KEY);
    } catch (e) {}
    accessCart('write', null);
  };
})();

/**
 * ============================================================================
 * ATELIER NILAYA — PRODUCT DETAIL PAGE CONTROLLER (product.js)
 * Large Photographic Spin Viewer, Angle Thumbnails, Metal Swatches & CTAs
 * (Vanilla JS, Zero Frameworks)
 * ============================================================================
 */

(function () {
  'use strict';

  function formatINR(price) {
    if (!price && price !== 0) return '';
    const rounded = Math.round(Number(price));
    const str = rounded.toString();
    if (str.length <= 3) return '₹' + str;
    const lastThree = str.substring(str.length - 3);
    const otherNumbers = str.substring(0, str.length - 3);
    return '₹' + otherNumbers.replace(/\B(?=(\d{2})+(?!\d))/g, ',') + ',' + lastThree;
  }

  function initProductPage() {
    const root = document.getElementById('product-detail-root');
    if (!root) return;

    const productId = parseInt(root.getAttribute('data-product-id'), 10);
    const productSlug = root.getAttribute('data-product-slug');
    let currentMetal = root.getAttribute('data-selected-metal') || root.getAttribute('data-base-metal') || 'yellow_gold';
    const metalsMap = JSON.parse(root.getAttribute('data-metals') || '{}');
    const oldPriceAttr = root.getAttribute('data-old-price');

    // Elements
    const viewerStage = document.getElementById('viewer-stage');
    const spinImg = document.getElementById('product-spin-img');
    const stillImg = document.getElementById('product-still-img');
    const priceDisplay = document.getElementById('page-price-display');
    const oldPriceDisplay = document.getElementById('page-old-price-display');
    const discountDisplay = document.getElementById('page-discount-display');
    const bookViewingBtn = document.getElementById('book-viewing-btn');
    const addToBagBtn = document.getElementById('page-add-to-bag-btn');
    const swatches = root.querySelectorAll('.swatch-btn');
    const thumbBtns = root.querySelectorAll('.thumb-btn');

    let currentMode = 'spin'; // 'spin', 'front', 'side', 'top', 'lifestyle'
    let currentFrame = 1;
    const totalFrames = 36;
    let isDragging = false;
    let dragStartX = 0;
    let lastDragX = 0;
    let velocity = 0;
    let inertiaRAF = null;

    function pad3(n) {
      return n.toString().padStart(3, '0');
    }

    function getSpinPath(frame, metal = currentMetal) {
      return `/static/products/${productSlug}/${metal}/spin/${pad3(frame)}.webp`;
    }

    function getStillPath(kind, metal = currentMetal) {
      if (kind === 'lifestyle') {
        return `/static/products/${productSlug}/lifestyle-1.webp`;
      }
      return `/static/products/${productSlug}/${metal}/${kind}.webp`;
    }

    function setFrame(frame) {
      if (frame < 1) frame = totalFrames;
      if (frame > totalFrames) frame = 1;
      currentFrame = frame;
      if (spinImg) {
        spinImg.src = getSpinPath(currentFrame, currentMetal);
      }
    }

    // Switch view mode (spin or still)
    function setViewMode(mode) {
      currentMode = mode;
      thumbBtns.forEach(btn => {
        btn.classList.toggle('is-active', btn.getAttribute('data-view') === mode);
      });

      if (mode === 'spin') {
        if (spinImg) spinImg.style.display = 'block';
        if (stillImg) stillImg.style.display = 'none';
        setFrame(currentFrame);
        if (viewerStage) viewerStage.style.cursor = 'grab';
      } else {
        if (spinImg) spinImg.style.display = 'none';
        if (stillImg) {
          stillImg.src = getStillPath(mode, currentMetal);
          stillImg.style.display = 'block';
        }
        if (viewerStage) viewerStage.style.cursor = 'default';
      }
    }

    // Metal swatch selection
    function selectMetal(metal) {
      if (!metalsMap[metal] || !metalsMap[metal].in_stock) return;
      currentMetal = metal;
      root.setAttribute('data-selected-metal', metal);

      // Update swatch buttons
      swatches.forEach(btn => {
        const isMatch = btn.getAttribute('data-metal') === metal;
        btn.classList.toggle('is-selected', isMatch);
        btn.setAttribute('aria-pressed', isMatch ? 'true' : 'false');
      });

      // Update price display
      const newPrice = metalsMap[metal].price;
      if (priceDisplay) priceDisplay.textContent = formatINR(newPrice);

      if (oldPriceAttr) {
        const oldP = parseFloat(oldPriceAttr);
        if (oldP > newPrice) {
          const discountPct = Math.round(((oldP - newPrice) / oldP) * 100);
          if (oldPriceDisplay) {
            oldPriceDisplay.textContent = formatINR(oldP);
            oldPriceDisplay.style.display = 'inline';
          }
          if (discountDisplay) {
            discountDisplay.textContent = `Save ${discountPct}%`;
            discountDisplay.style.display = 'inline';
          }
        } else {
          if (oldPriceDisplay) oldPriceDisplay.style.display = 'none';
          if (discountDisplay) discountDisplay.style.display = 'none';
        }
      }

      // Update Book Viewing URL
      if (bookViewingBtn) {
        bookViewingBtn.href = `/#visit?piece=${encodeURIComponent(productSlug)}&metal=${encodeURIComponent(metal)}`;
      }

      // Update Thumbnail image sources
      thumbBtns.forEach(btn => {
        const view = btn.getAttribute('data-view');
        const img = btn.querySelector('.thumb-img');
        if (img && view !== 'lifestyle') {
          if (view === 'spin') {
            img.src = getSpinPath(1, metal);
          } else {
            img.src = getStillPath(view, metal);
          }
        }
      });

      // Update main viewer
      setViewMode(currentMode);

      // Update URL query
      if (history.replaceState) {
        const url = new URL(window.location);
        url.searchParams.set('metal', metal);
        history.replaceState(null, '', url.toString());
      }
    }

    // Attach swatch clicks
    swatches.forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const metal = btn.getAttribute('data-metal');
        if (metal) selectMetal(metal);
      });
    });

    // Attach thumbnail clicks
    thumbBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const view = btn.getAttribute('data-view');
        if (view) setViewMode(view);
      });
    });

    // Drag to scrub spin frames
    if (viewerStage) {
      const onStart = (e) => {
        if (currentMode !== 'spin') return;
        isDragging = true;
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        dragStartX = clientX;
        lastDragX = clientX;
        velocity = 0;
        if (inertiaRAF) cancelAnimationFrame(inertiaRAF);
      };

      const onMove = (e) => {
        if (!isDragging || currentMode !== 'spin') return;
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const deltaX = clientX - lastDragX;
        velocity = deltaX;
        lastDragX = clientX;

        const step = Math.round(deltaX / 8);
        if (step !== 0) {
          setFrame(currentFrame - step);
        }
      };

      const onEnd = () => {
        if (!isDragging) return;
        isDragging = false;
        if (Math.abs(velocity) > 1.2 && currentMode === 'spin') {
          const runInertia = () => {
            velocity *= 0.92;
            if (Math.abs(velocity) < 0.2) return;
            const step = Math.round(velocity / 8);
            if (step !== 0) setFrame(currentFrame - step);
            inertiaRAF = requestAnimationFrame(runInertia);
          };
          inertiaRAF = requestAnimationFrame(runInertia);
        }
      };

      viewerStage.addEventListener('mousedown', onStart);
      window.addEventListener('mousemove', onMove);
      window.addEventListener('mouseup', onEnd);

      viewerStage.addEventListener('touchstart', onStart, { passive: true });
      viewerStage.addEventListener('touchmove', onMove, { passive: true });
      viewerStage.addEventListener('touchend', onEnd, { passive: true });

      // Keyboard arrow keys
      viewerStage.addEventListener('keydown', (e) => {
        if (currentMode !== 'spin') return;
        if (e.key === 'ArrowLeft') {
          e.preventDefault();
          setFrame(currentFrame - 1);
        } else if (e.key === 'ArrowRight') {
          e.preventDefault();
          setFrame(currentFrame + 1);
        }
      });
    }

    // Add to Bag CTA
    if (addToBagBtn) {
      addToBagBtn.addEventListener('click', (e) => {
        e.preventDefault();
        const origText = addToBagBtn.textContent;
        addToBagBtn.textContent = 'Adding to Bag...';
        addToBagBtn.disabled = true;

        const sku = addToBagBtn.getAttribute('data-sku');
        if (window.NilayaBag && typeof window.NilayaBag.addToBag === 'function') {
          window.NilayaBag.addToBag({
            sku: sku,
            product_id: productId,
            metal: currentMetal,
            quantity: 1
          }, () => {
            addToBagBtn.textContent = 'Added to Bag ✓';
            setTimeout(() => {
              addToBagBtn.textContent = origText;
              addToBagBtn.disabled = false;
            }, 1800);
          });
        } else {
          fetch('/cart/add/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: productId, metal: currentMetal, quantity: 1 })
          })
          .then(res => res.json())
          .then(data => {
            if (data.success) {
              addToBagBtn.textContent = 'Added to Bag ✓';
              const headerCount = document.getElementById('header-bag-count');
              if (headerCount) {
                headerCount.textContent = data.count || data.cart_count || 1;
                headerCount.style.display = 'inline-flex';
              }
              if (window.NilayaBag && typeof window.NilayaBag.open === 'function') {
                window.NilayaBag.render(data.cart);
                window.NilayaBag.open();
              }
            } else {
              addToBagBtn.textContent = 'Unavailable';
            }
            setTimeout(() => {
              addToBagBtn.textContent = origText;
              addToBagBtn.disabled = false;
            }, 1800);
          })
          .catch(() => {
            addToBagBtn.textContent = 'Added to Bag ✓';
            setTimeout(() => {
              addToBagBtn.textContent = origText;
              addToBagBtn.disabled = false;
            }, 1800);
          });
        }
      });
    }

    // Initial view
    setViewMode('spin');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initProductPage);
  } else {
    initProductPage();
  }
})();

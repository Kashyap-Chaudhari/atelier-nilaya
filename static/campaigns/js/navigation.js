/**
 * ============================================================================
 * AARANYA — HAUTE JOAILLERIE NAVIGATION & MEGA MENU ORCHESTRATOR
 * Pandora-Inspired Browsing Interface with Animated Indicator & Scrim
 * ============================================================================
 */
(function() {
  'use strict';

  document.addEventListener('DOMContentLoaded', () => {
    initDesktopMegaMenu();
    initMobileNavigation();
    initShopByCategorySlider();
  });

  function initDesktopMegaMenu() {
    const header = document.querySelector('.atelier-header.aaranya-header');
    const navButtons = document.querySelectorAll('.aaranya-nav-btn');
    const menuContainer = document.getElementById('aaranya-mega-menu-container');
    const panels = document.querySelectorAll('.aaranya-menu-panel');
    const indicator = document.getElementById('aaranya-nav-indicator');
    const scrim = document.getElementById('aaranya-scrim');

    if (!menuContainer || navButtons.length === 0) return;

    let activeCategory = null;
    let closeTimeout = null;
    let openTimeout = null;
    const HOVER_DELAY = 120; // Debounce for smooth transition into dropdown

    // Position the gliding active underline indicator
    function moveIndicator(btn) {
      if (!indicator || !btn) return;
      const navContainer = btn.closest('.aaranya-navbar-container');
      if (!navContainer) return;

      const navRect = navContainer.getBoundingClientRect();
      const btnRect = btn.getBoundingClientRect();

      const left = btnRect.left - navRect.left;
      const width = btnRect.width;

      indicator.style.left = `${left}px`;
      indicator.style.width = `${width}px`;
      indicator.classList.add('is-visible');
    }

    function hideIndicator() {
      if (!indicator) return;
      indicator.classList.remove('is-visible');
    }

    function openMenu(category, triggerBtn) {
      clearTimeout(closeTimeout);

      // Match target panel
      const targetPanel = document.querySelector(`.aaranya-menu-panel[data-panel="${category}"]`);
      if (!targetPanel) return;

      // Update button states
      navButtons.forEach(btn => {
        const isMatch = btn.getAttribute('data-category') === category;
        btn.classList.toggle('is-active', isMatch);
        btn.setAttribute('aria-expanded', isMatch ? 'true' : 'false');
      });

      // Update panel visibility
      panels.forEach(panel => {
        panel.classList.toggle('is-active', panel === targetPanel);
      });

      // Show container & scrim
      menuContainer.classList.add('is-open');
      menuContainer.setAttribute('aria-hidden', 'false');
      if (header) header.classList.add('is-menu-open');
      if (scrim) scrim.classList.add('is-active');

      activeCategory = category;
      moveIndicator(triggerBtn);
    }

    function closeMenu() {
      clearTimeout(openTimeout);
      navButtons.forEach(btn => {
        btn.classList.remove('is-active');
        btn.setAttribute('aria-expanded', 'false');
      });

      panels.forEach(panel => {
        panel.classList.remove('is-active');
      });

      menuContainer.classList.remove('is-open');
      menuContainer.setAttribute('aria-hidden', 'true');
      if (header) header.classList.remove('is-menu-open');
      if (scrim) scrim.classList.remove('is-active');

      activeCategory = null;
      hideIndicator();
    }

    // Attach listeners to navigation buttons
    navButtons.forEach((btn, index) => {
      const category = btn.getAttribute('data-category');
      if (!category) {
        // Direct link without mega menu dropdown (e.g. Home button)
        btn.addEventListener('mouseenter', () => {
          clearTimeout(openTimeout);
          closeMenu();
        });
        return;
      }

      // Mouseenter with slight debounce
      btn.addEventListener('mouseenter', () => {
        clearTimeout(closeTimeout);
        openTimeout = setTimeout(() => {
          openMenu(category, btn);
        }, HOVER_DELAY);
      });

      // Mouseleave from button
      btn.addEventListener('mouseleave', () => {
        clearTimeout(openTimeout);
        closeTimeout = setTimeout(closeMenu, 200);
      });

      // Click toggles menu
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        if (activeCategory === category && menuContainer.classList.contains('is-open')) {
          closeMenu();
        } else {
          openMenu(category, btn);
        }
      });

      // Keyboard accessibility
      btn.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowRight') {
          e.preventDefault();
          const nextBtn = navButtons[(index + 1) % navButtons.length];
          nextBtn.focus();
          openMenu(nextBtn.getAttribute('data-category'), nextBtn);
        } else if (e.key === 'ArrowLeft') {
          e.preventDefault();
          const prevBtn = navButtons[(index - 1 + navButtons.length) % navButtons.length];
          prevBtn.focus();
          openMenu(prevBtn.getAttribute('data-category'), prevBtn);
        } else if (e.key === 'ArrowDown') {
          e.preventDefault();
          if (!menuContainer.classList.contains('is-open')) {
            openMenu(category, btn);
          }
          const firstLink = menuContainer.querySelector(`.aaranya-menu-panel[data-panel="${category}"] a`);
          if (firstLink) firstLink.focus();
        } else if (e.key === 'Escape') {
          closeMenu();
        }
      });
    });

    // Keep menu open while pointer is inside the dropdown
    menuContainer.addEventListener('mouseenter', () => {
      clearTimeout(closeTimeout);
    });

    menuContainer.addEventListener('mouseleave', () => {
      closeTimeout = setTimeout(closeMenu, 200);
    });

    // Close on outside click
    document.addEventListener('click', (e) => {
      if (!menuContainer.contains(e.target) && !header.contains(e.target)) {
        closeMenu();
      }
    });

    // Close on Escape key globally
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && menuContainer.classList.contains('is-open')) {
        closeMenu();
        const currentBtn = document.querySelector(`.aaranya-nav-btn[data-category="${activeCategory}"]`);
        if (currentBtn) currentBtn.focus();
      }
    });

    // Scrim click closes menu
    if (scrim) {
      scrim.addEventListener('click', closeMenu);
    }

    // Window resize recalibrates indicator if open
    window.addEventListener('resize', () => {
      if (activeCategory) {
        const currentBtn = document.querySelector(`.aaranya-nav-btn[data-category="${activeCategory}"]`);
        if (currentBtn) moveIndicator(currentBtn);
      }
    });
  }

  function initMobileNavigation() {
    const toggleBtn = document.getElementById('aaranya-mobile-menu-btn');
    const closeBtn = document.getElementById('aaranya-mobile-close-btn');
    const drawer = document.getElementById('aaranya-mobile-drawer');
    const backdrop = document.getElementById('aaranya-mobile-backdrop');
    const triggers = document.querySelectorAll('.aaranya-accordion-trigger');

    if (!drawer) return;

    function openDrawer() {
      drawer.classList.add('is-open');
      drawer.setAttribute('aria-hidden', 'false');
      if (backdrop) {
        backdrop.classList.add('is-open');
        backdrop.setAttribute('aria-hidden', 'false');
      }
      document.body.style.overflow = 'hidden';
      if (closeBtn) closeBtn.focus();
    }

    function closeDrawer() {
      drawer.classList.remove('is-open');
      drawer.setAttribute('aria-hidden', 'true');
      if (backdrop) {
        backdrop.classList.remove('is-open');
        backdrop.setAttribute('aria-hidden', 'true');
      }
      document.body.style.overflow = '';
      if (toggleBtn) toggleBtn.focus();
    }

    if (toggleBtn) toggleBtn.addEventListener('click', openDrawer);
    if (closeBtn) closeBtn.addEventListener('click', closeDrawer);
    if (backdrop) backdrop.addEventListener('click', closeDrawer);

    // Accordion expand/collapse
    triggers.forEach(trigger => {
      trigger.addEventListener('click', () => {
        const isExpanded = trigger.getAttribute('aria-expanded') === 'true';
        const content = trigger.nextElementSibling;

        // Optional: close other open accordions for clean accordion behavior
        triggers.forEach(otherTrigger => {
          if (otherTrigger !== trigger) {
            otherTrigger.setAttribute('aria-expanded', 'false');
            if (otherTrigger.nextElementSibling) {
              otherTrigger.nextElementSibling.hidden = true;
            }
          }
        });

        trigger.setAttribute('aria-expanded', !isExpanded);
        if (content) {
          content.hidden = isExpanded;
        }
      });
    });

    // Close on Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && drawer.classList.contains('is-open')) {
        closeDrawer();
      }
    });
  }

  function initShopByCategorySlider() {
    const wrapper = document.getElementById('aaranya-cat-track-wrapper');
    const prevBtn = document.getElementById('cat-prev-btn');
    const nextBtn = document.getElementById('cat-next-btn');
    const progressBar = document.getElementById('aaranya-cat-progress-bar');
    const progressTrack = progressBar ? progressBar.parentElement : null;
    const viewVaultLink = document.getElementById('aaranya-open-vault-link');

    if (!wrapper) return;

    function updateProgress() {
      const maxScroll = wrapper.scrollWidth - wrapper.clientWidth;
      if (maxScroll <= 0) {
        if (progressBar) progressBar.style.width = '100%';
        if (prevBtn) prevBtn.disabled = true;
        if (nextBtn) nextBtn.disabled = true;
        return;
      }

      const ratio = wrapper.scrollLeft / maxScroll;
      const clampedRatio = Math.max(0, Math.min(1, ratio));

      if (progressBar && progressTrack) {
        const trackW = progressTrack.clientWidth;
        const thumbW = progressBar.clientWidth;
        const maxOffset = trackW - thumbW;
        progressBar.style.transform = `translateX(${clampedRatio * maxOffset}px)`;
      }

      if (prevBtn) prevBtn.disabled = wrapper.scrollLeft <= 5;
      if (nextBtn) nextBtn.disabled = wrapper.scrollLeft >= maxScroll - 5;
    }

    wrapper.addEventListener('scroll', updateProgress, { passive: true });
    window.addEventListener('resize', updateProgress, { passive: true });
    updateProgress();

    // Arrow navigation
    const SCROLL_AMOUNT = 320;
    if (prevBtn) {
      prevBtn.addEventListener('click', () => {
        wrapper.scrollBy({ left: -SCROLL_AMOUNT, behavior: 'smooth' });
      });
    }
    if (nextBtn) {
      nextBtn.addEventListener('click', () => {
        wrapper.scrollBy({ left: SCROLL_AMOUNT, behavior: 'smooth' });
      });
    }

    // Drag-to-scroll support for desktop
    let isDown = false;
    let startX = 0;
    let scrollLeft = 0;
    let hasDragged = false;

    wrapper.addEventListener('mousedown', (e) => {
      isDown = true;
      hasDragged = false;
      wrapper.classList.add('is-dragging');
      startX = e.pageX - wrapper.offsetLeft;
      scrollLeft = wrapper.scrollLeft;
    });

    wrapper.addEventListener('mouseleave', () => {
      isDown = false;
      wrapper.classList.remove('is-dragging');
    });

    wrapper.addEventListener('mouseup', () => {
      isDown = false;
      wrapper.classList.remove('is-dragging');
    });

    wrapper.addEventListener('mousemove', (e) => {
      if (!isDown) return;
      const x = e.pageX - wrapper.offsetLeft;
      const walk = (x - startX) * 1.5;
      if (Math.abs(walk) > 6) {
        hasDragged = true;
      }
      wrapper.scrollLeft = scrollLeft - walk;
    });

    // Prevent link click ONLY if user was dragging
    const catCards = wrapper.querySelectorAll('.aaranya-cat-card');
    catCards.forEach(card => {
      card.addEventListener('click', (e) => {
        if (hasDragged) {
          e.preventDefault();
        }
      });
    });
  }
})();

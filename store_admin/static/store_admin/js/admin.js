/**
 * ATELIER NILAYA — SOVEREIGN ADMIN CONTROLLER
 * Vanilla JS orchestrating Global Search (Ctrl+K), Mobile drawer, Autosave drafts.
 */

(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    initGlobalSearch();
    initMobileSidebar();
  });

  // ==========================================================================
  // 1. GLOBAL SEARCH (CTRL+K / CMD+K)
  // ==========================================================================
  function initGlobalSearch() {
    const trigger = document.getElementById('admin-search-trigger');
    const modal = document.getElementById('admin-search-modal');
    const input = document.getElementById('admin-search-input');
    const resultsContainer = document.getElementById('admin-search-results');

    if (!modal || !input) return;

    function openSearch() {
      modal.classList.add('is-open');
      input.value = '';
      if (resultsContainer) resultsContainer.innerHTML = '<div style="padding: 24px; text-align: center; color: var(--adm-text-muted); font-size: 0.85rem;">Type a piece name, SKU, order reference, or customer name...</div>';
      setTimeout(() => input.focus(), 50);
    }

    function closeSearch() {
      modal.classList.remove('is-open');
    }

    if (trigger) {
      trigger.addEventListener('click', openSearch);
    }

    modal.addEventListener('click', function (e) {
      if (e.target === modal) closeSearch();
    });

    document.addEventListener('keydown', function (e) {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        if (modal.classList.contains('is-open')) {
          closeSearch();
        } else {
          openSearch();
        }
      } else if (e.key === 'Escape' && modal.classList.contains('is-open')) {
        closeSearch();
      }
    });

    // Debounced Live Query Search
    let debounceTimer = null;
    input.addEventListener('input', function () {
      clearTimeout(debounceTimer);
      const query = input.value.trim();

      if (query.length < 2) {
        if (resultsContainer) resultsContainer.innerHTML = '<div style="padding: 24px; text-align: center; color: var(--adm-text-muted); font-size: 0.85rem;">Type at least 2 characters to search...</div>';
        return;
      }

      debounceTimer = setTimeout(function () {
        fetch('/admin/api/search/?q=' + encodeURIComponent(query))
          .then(res => res.json())
          .then(data => {
            if (!resultsContainer) return;
            if (!data.results || data.results.length === 0) {
              resultsContainer.innerHTML = '<div style="padding: 24px; text-align: center; color: var(--adm-text-muted); font-size: 0.85rem;">No vault heirlooms, orders, or patrons found matching "' + query + '".</div>';
              return;
            }

            let html = '';
            data.results.forEach(item => {
              html += `
                <a href="${item.url}" class="admin-search-result-item">
                  <div style="width: 28px; height: 28px; border-radius: 4px; background: var(--adm-wine-light); color: var(--adm-wine); display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: 700;">✦</div>
                  <div style="flex: 1; min-width: 0;">
                    <div style="font-weight: 600; font-size: 0.88rem; color: var(--adm-text);">${item.title}</div>
                    <div style="font-size: 0.75rem; color: var(--adm-text-muted);">${item.subtitle}</div>
                  </div>
                  <span style="font-size: 0.68rem; text-transform: uppercase; background: var(--adm-bg); padding: 2px 8px; border-radius: 10px; font-weight: 600; color: var(--adm-text-muted);">${item.type}</span>
                </a>
              `;
            });
            resultsContainer.innerHTML = html;
          })
          .catch(err => {
            console.error('[Admin Search Error]', err);
          });
      }, 200);
    });
  }

  // ==========================================================================
  // 2. MOBILE SIDEBAR DRAWER & NAVIGATION CONTROLLER
  // ==========================================================================
  function initMobileSidebar() {
    const toggleBtn = document.getElementById('admin-sidebar-toggle');
    const dockMenuBtn = document.getElementById('admin-dock-toggle-menu');
    const closeBtn = document.getElementById('admin-sidebar-close');
    const backdrop = document.getElementById('admin-sidebar-backdrop');
    const sidebar = document.getElementById('admin-sidebar') || document.querySelector('.admin-sidebar');
    
    if (!sidebar) return;

    function openSidebar() {
      sidebar.classList.add('is-open');
      if (backdrop) backdrop.classList.add('is-open');
      document.body.classList.add('admin-sidebar-locked');
    }

    function closeSidebar() {
      sidebar.classList.remove('is-open');
      if (backdrop) backdrop.classList.remove('is-open');
      document.body.classList.remove('admin-sidebar-locked');
    }

    if (toggleBtn) {
      toggleBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        if (sidebar.classList.contains('is-open')) {
          closeSidebar();
        } else {
          openSidebar();
        }
      });
    }

    if (dockMenuBtn) {
      dockMenuBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        if (sidebar.classList.contains('is-open')) {
          closeSidebar();
        } else {
          openSidebar();
        }
      });
    }

    if (closeBtn) {
      closeBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        closeSidebar();
      });
    }

    if (backdrop) {
      backdrop.addEventListener('click', function () {
        closeSidebar();
      });
    }

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && sidebar.classList.contains('is-open')) {
        closeSidebar();
      }
    });
  }
})();

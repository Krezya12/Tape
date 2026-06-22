/**
 * PDP Academy LMS — Interactions & UI Logic
 */

(function () {
  'use strict';

  /* ─── Sidebar ───────────────────────────────────── */
  function initSidebar() {
    const sidebar      = document.getElementById('sidebar');
    const mainWrapper  = document.querySelector('.main-wrapper');
    const menuToggle   = document.getElementById('menuToggle');
    const collapseBtn  = document.getElementById('sidebarCollapse');
    const overlay      = document.getElementById('sidebarOverlay');

    if (!sidebar) return;

    const isMobile = () => window.innerWidth <= 1024;

    function openMobile() {
      sidebar.classList.add('mobile-open');
      overlay && overlay.classList.add('visible');
      document.body.style.overflow = 'hidden';
    }
    function closeMobile() {
      sidebar.classList.remove('mobile-open');
      overlay && overlay.classList.remove('visible');
      document.body.style.overflow = '';
    }
    function toggleCollapse() {
      sidebar.classList.toggle('collapsed');
      mainWrapper && mainWrapper.classList.toggle('expanded');
      localStorage.setItem('pdp-sidebar-collapsed', sidebar.classList.contains('collapsed'));
    }

    // Restore collapse state
    if (!isMobile() && localStorage.getItem('pdp-sidebar-collapsed') === 'true') {
      sidebar.classList.add('collapsed');
      mainWrapper && mainWrapper.classList.add('expanded');
    }

    menuToggle   && menuToggle.addEventListener('click', () => isMobile() ? openMobile() : toggleCollapse());
    collapseBtn  && collapseBtn.addEventListener('click', toggleCollapse);
    overlay      && overlay.addEventListener('click', closeMobile);

    window.addEventListener('resize', () => {
      if (!isMobile()) { closeMobile(); }
    });
  }

  /* ─── Modals ────────────────────────────────────── */
  function initModals() {
    // Open via data-modal-open="modalId"
    document.addEventListener('click', e => {
      const opener = e.target.closest('[data-modal-open]');
      if (opener) openModal(opener.dataset.modalOpen);

      const closer = e.target.closest('[data-modal-close]');
      if (closer) {
        const modal = closer.closest('.modal-overlay');
        if (modal) closeModal(modal.id);
      }

      // Click on overlay background to close
      if (e.target.classList.contains('modal-overlay')) {
        closeModal(e.target.id);
      }
    });

    // Escape key
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') {
        document.querySelectorAll('.modal-overlay.open').forEach(m => closeModal(m.id));
      }
    });
  }

  function openModal(id) {
    const overlay = document.getElementById(id);
    if (!overlay) return;
    overlay.classList.add('open');
    document.body.style.overflow = 'hidden';
    const firstInput = overlay.querySelector('input, select, textarea');
    if (firstInput) setTimeout(() => firstInput.focus(), 100);
  }

  function closeModal(id) {
    const overlay = document.getElementById(id);
    if (!overlay) return;
    overlay.classList.remove('open');
    document.body.style.overflow = '';
  }

  window.openModal  = openModal;
  window.closeModal = closeModal;

  /* ─── Dropdowns ─────────────────────────────────── */
  function initDropdowns() {
    document.addEventListener('click', e => {
      const trigger = e.target.closest('[data-dropdown]');

      // Close all others
      document.querySelectorAll('.dropdown-menu.open').forEach(menu => {
        const parent = menu.closest('[data-dropdown]');
        if (!parent || parent !== trigger) menu.classList.remove('open');
      });

      if (trigger) {
        const menuId = trigger.dataset.dropdown;
        const menu = menuId
          ? document.getElementById(menuId)
          : trigger.querySelector('.dropdown-menu');
        if (menu) menu.classList.toggle('open');
        e.stopPropagation();
      }
    });
  }

  /* ─── Tabs ──────────────────────────────────────── */
  function initTabs() {
    document.querySelectorAll('.tabs').forEach(tabsEl => {
      tabsEl.addEventListener('click', e => {
        const btn = e.target.closest('.tab-btn');
        if (!btn) return;

        const tabGroup = btn.dataset.tabGroup || tabsEl.dataset.tabGroup;
        const target   = btn.dataset.tab;

        // Deactivate all in group
        tabsEl.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // Show target panel
        const scope = tabGroup
          ? document.querySelectorAll(`[data-tab-group="${tabGroup}"] .tab-panel`)
          : document.querySelectorAll('.tab-panel');

        scope.forEach(panel => {
          panel.classList.toggle('active', panel.id === target || panel.dataset.panel === target);
        });
      });
    });
  }

  /* ─── Table Filter & Search ─────────────────────── */
  function initTableSearch() {
    document.querySelectorAll('.table-search input').forEach(input => {
      const tableId = input.dataset.table;
      const table   = tableId ? document.getElementById(tableId) : input.closest('.card, .section')?.querySelector('.data-table');
      if (!table) return;

      input.addEventListener('input', () => {
        const q = input.value.toLowerCase().trim();
        table.querySelectorAll('tbody tr').forEach(row => {
          const text = row.textContent.toLowerCase();
          row.style.display = text.includes(q) ? '' : 'none';
        });
        updateEmptyTableState(table);
      });
    });

    // Filter selects
    document.querySelectorAll('.table-filter-select').forEach(sel => {
      const tableId = sel.dataset.table;
      const col     = parseInt(sel.dataset.col ?? '0');
      const table   = tableId ? document.getElementById(tableId) : sel.closest('.card, .section')?.querySelector('.data-table');
      if (!table) return;

      sel.addEventListener('change', () => {
        const val = sel.value.toLowerCase();
        table.querySelectorAll('tbody tr').forEach(row => {
          const cell = row.cells[col];
          if (!val) { row.style.display = ''; return; }
          row.style.display = cell && cell.textContent.toLowerCase().includes(val) ? '' : 'none';
        });
        updateEmptyTableState(table);
      });
    });
  }

  function updateEmptyTableState(table) {
    const visibleRows = table.querySelectorAll('tbody tr:not([style*="none"])');
    let emptyRow = table.querySelector('.empty-table-row');
    if (visibleRows.length === 0) {
      if (!emptyRow) {
        emptyRow = document.createElement('tr');
        emptyRow.className = 'empty-table-row';
        const cols = table.querySelectorAll('thead th').length || 5;
        emptyRow.innerHTML = `<td colspan="${cols}" style="text-align:center;padding:40px;color:var(--text-muted);font-size:0.875rem;">No results found</td>`;
        table.querySelector('tbody')?.appendChild(emptyRow);
      }
    } else {
      emptyRow?.remove();
    }
  }

  /* ─── Toast Notifications ───────────────────────── */
  let toastContainer;

  function getToastContainer() {
    if (!toastContainer) {
      toastContainer = document.getElementById('toastContainer');
      if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.className = 'toast-container';
        document.body.appendChild(toastContainer);
      }
    }
    return toastContainer;
  }

  function showToast(message, type = 'success', duration = 3500) {
    const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
    const container = getToastContainer();

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
      <span class="toast-icon">${icons[type] || '📌'}</span>
      <span class="toast-text">${message}</span>
      <span class="toast-close" onclick="this.closest('.toast').remove()">✕</span>
    `;
    container.appendChild(toast);

    requestAnimationFrame(() => {
      requestAnimationFrame(() => toast.classList.add('show'));
    });

    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 350);
    }, duration);
  }

  window.showToast = showToast;

  /* ─── Progress Bar Animations ───────────────────── */
  function initProgressBars() {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const bar = entry.target;
          const pct = bar.dataset.progress || bar.style.getPropertyValue('--progress') || '0';
          bar.style.width = pct + '%';
          observer.unobserve(bar);
        }
      });
    }, { threshold: 0.2 });

    document.querySelectorAll('.progress-bar[data-progress]').forEach(bar => {
      bar.style.width = '0%';
      observer.observe(bar);
    });
  }

  /* ─── Animated Counters ─────────────────────────── */
  function initCounters() {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.3 });

    document.querySelectorAll('[data-count]').forEach(el => observer.observe(el));
  }

  function animateCounter(el) {
    const target = parseFloat(el.dataset.count);
    const suffix = el.dataset.suffix || '';
    const duration = 1200;
    const start = performance.now();

    function update(time) {
      const elapsed = time - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const value = target * eased;

      el.textContent = Number.isInteger(target)
        ? Math.round(value) + suffix
        : value.toFixed(1) + suffix;

      if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
  }

  /* ─── Circular Progress (SVG rings) ─────────────── */
  function initRings() {
    document.querySelectorAll('.ring-progress').forEach(ring => {
      const fill  = ring.querySelector('.ring-fill');
      const pct   = ring.dataset.percent || 0;
      const r     = fill?.getAttribute('r') || 36;
      const circ  = 2 * Math.PI * r;

      if (fill) {
        fill.style.strokeDasharray  = circ;
        fill.style.strokeDashoffset = circ;

        setTimeout(() => {
          fill.style.strokeDashoffset = circ - (pct / 100) * circ;
        }, 200);
      }

      const label = ring.querySelector('.ring-pct');
      if (label) {
        label.textContent = '0%';
        const start = performance.now();
        const duration = 1100;
        const tick = (t) => {
          const p = Math.min((t - start) / duration, 1);
          const e = 1 - Math.pow(1 - p, 3);
          label.textContent = Math.round(e * pct) + '%';
          if (p < 1) requestAnimationFrame(tick);
        };
        setTimeout(() => requestAnimationFrame(tick), 200);
      }
    });
  }

  /* ─── Accordion ─────────────────────────────────── */
  function initAccordions() {
    document.querySelectorAll('.accordion').forEach(acc => {
      acc.addEventListener('click', e => {
        const header = e.target.closest('.accordion-header');
        if (!header) return;
        const item = header.closest('.accordion-item');
        const body = item?.querySelector('.accordion-body');
        if (!body) return;

        const isOpen = item.classList.contains('open');

        // Close all in same accordion group
        if (acc.dataset.exclusive !== 'false') {
          acc.querySelectorAll('.accordion-item.open').forEach(i => {
            i.classList.remove('open');
            i.querySelector('.accordion-body').style.maxHeight = null;
          });
        }

        if (!isOpen) {
          item.classList.add('open');
          body.style.maxHeight = body.scrollHeight + 'px';
        }
      });
    });
  }

  /* ─── Form Handling ─────────────────────────────── */
  function initForms() {
    document.querySelectorAll('form[data-ajax]').forEach(form => {
      form.addEventListener('submit', e => {
        e.preventDefault();
        const btn = form.querySelector('[type="submit"]');
        if (btn) {
          const orig = btn.textContent;
          btn.textContent = 'Saving…';
          btn.disabled = true;
          setTimeout(() => {
            btn.textContent = orig;
            btn.disabled = false;
            showToast('Saved successfully', 'success');
          }, 1200);
        }
      });
    });

    // Password confirm validation
    document.querySelectorAll('[data-confirm]').forEach(input => {
      const targetId = input.dataset.confirm;
      input.addEventListener('input', () => {
        const target = document.getElementById(targetId);
        if (target && input.value !== target.value) {
          input.classList.add('error');
        } else {
          input.classList.remove('error');
        }
      });
    });
  }

  /* ─── User Dropdown in Header ───────────────────── */
  function initHeaderDropdown() {
    const btn = document.getElementById('userMenuBtn');
    const menu = document.getElementById('userDropdownMenu');
    if (!btn || !menu) return;

    btn.addEventListener('click', e => {
      e.stopPropagation();
      menu.classList.toggle('open');
    });
    document.addEventListener('click', () => menu.classList.remove('open'));
  }

  /* ─── Notification Panel ────────────────────────── */
  function initNotifPanel() {
    const btn   = document.getElementById('notifBtn');
    const panel = document.getElementById('notifPanel');
    if (!btn || !panel) return;

    btn.addEventListener('click', e => {
      e.stopPropagation();
      panel.classList.toggle('open');

      // Mark badge as seen
      const dot = btn.querySelector('.notif-dot');
      if (dot && panel.classList.contains('open')) {
        setTimeout(() => dot.remove(), 800);
      }
    });
    document.addEventListener('click', e => {
      if (!panel.contains(e.target) && e.target !== btn) {
        panel.classList.remove('open');
      }
    });
  }

  /* ─── Table Row Actions ─────────────────────────── */
  function initTableActions() {
    document.addEventListener('click', e => {
      const row = e.target.closest('tr[data-href]');
      if (row && !e.target.closest('button, a, .dropdown')) {
        window.location.href = row.dataset.href;
      }
    });
  }

  /* ─── Copy to Clipboard ─────────────────────────── */
  document.addEventListener('click', e => {
    const btn = e.target.closest('[data-copy]');
    if (!btn) return;
    const text = btn.dataset.copy;
    navigator.clipboard?.writeText(text).then(() => showToast('Copied to clipboard', 'success', 2000));
  });

  /* ─── Lazy Image fallback ───────────────────────── */
  function initImages() {
    document.querySelectorAll('img[data-src]').forEach(img => {
      const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            img.src = img.dataset.src;
            observer.unobserve(img);
          }
        });
      });
      observer.observe(img);
    });
  }

  /* ─── Avatar initials fallback ──────────────────── */
  function initAvatars() {
    document.querySelectorAll('.avatar[data-name]').forEach(el => {
      if (el.tagName === 'IMG') {
        el.addEventListener('error', () => {
          const div = document.createElement('div');
          div.className = el.className;
          div.textContent = el.dataset.name.charAt(0).toUpperCase();
          el.replaceWith(div);
        });
      }
    });
  }

  /* ─── Video player mock ─────────────────────────── */
  function initVideoPlayers() {
    document.querySelectorAll('.video-play-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const card = btn.closest('.video-player-card');
        const placeholder = card?.querySelector('.video-placeholder');
        if (placeholder) {
          placeholder.style.display = 'none';
          showToast('Starting video lesson…', 'info', 2000);
        }
      });
    });
  }

  /* ─── Realtime clock ────────────────────────────── */
  function initClock() {
    const el = document.getElementById('headerClock');
    if (!el) return;
    const tick = () => {
      const now = new Date();
      el.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };
    tick();
    setInterval(tick, 30000);
  }

  /* ─── Init All ──────────────────────────────────── */
  function init() {
    initSidebar();
    initModals();
    initDropdowns();
    initTabs();
    initTableSearch();
    initProgressBars();
    initCounters();
    initRings();
    initAccordions();
    initForms();
    initHeaderDropdown();
    initNotifPanel();
    initTableActions();
    initImages();
    initAvatars();
    initVideoPlayers();
    initClock();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

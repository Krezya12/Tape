/**
 * PDP Academy LMS — Theme Manager
 * Handles Light / Dark mode toggle with localStorage persistence
 */

(function () {
  'use strict';

  const STORAGE_KEY = 'pdp-theme';
  const DARK = 'dark';
  const LIGHT = 'light';

  /** Read saved theme or fall back to system preference */
  function getInitialTheme() {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved === DARK || saved === LIGHT) return saved;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? DARK : LIGHT;
  }

  /** Apply theme to <html> and update all toggle UI */
  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(STORAGE_KEY, theme);

    // Update all toggle buttons
    document.querySelectorAll('[data-theme-toggle]').forEach(btn => {
      const icon = btn.querySelector('.theme-icon') || btn;
      icon.textContent = theme === DARK ? '☀️' : '🌙';
      btn.setAttribute('title', theme === DARK ? 'Switch to Light mode' : 'Switch to Dark mode');
    });

    // Update theme option buttons (the pill toggle)
    document.querySelectorAll('.theme-opt').forEach(opt => {
      opt.classList.toggle('active', opt.dataset.mode === theme);
    });

    // Update Chart.js colors if charts exist
    if (window.updateChartsTheme) updateChartsTheme(theme);
  }

  /** Toggle between dark and light */
  function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || LIGHT;
    applyTheme(current === DARK ? LIGHT : DARK);
  }

  /** Listen for system preference changes */
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
    if (!localStorage.getItem(STORAGE_KEY)) {
      applyTheme(e.matches ? DARK : LIGHT);
    }
  });

  /** Initialize on DOM ready */
  function init() {
    applyTheme(getInitialTheme());

    // Wire up single-toggle buttons
    document.querySelectorAll('[data-theme-toggle]').forEach(btn => {
      btn.addEventListener('click', toggleTheme);
    });

    // Wire up multi-option pill toggles
    document.querySelectorAll('.theme-opt').forEach(opt => {
      opt.addEventListener('click', () => {
        if (opt.dataset.mode) applyTheme(opt.dataset.mode);
      });
    });
  }

  // Run before paint to avoid flash
  if (document.readyState === 'loading') {
    // Apply immediately to avoid FOUC
    const earlyTheme = getInitialTheme();
    document.documentElement.setAttribute('data-theme', earlyTheme);
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Expose globally
  window.pdpTheme = { toggle: toggleTheme, apply: applyTheme, get: getInitialTheme };
})();

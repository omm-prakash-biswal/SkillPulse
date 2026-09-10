/**
 * SKILLPULSE / SKILLPULSE — CLIENT CONFIGURATION, THEME & SESSION CACHE
 * Configures the backend REST API base URL, dark/light theme, and compulsory session memory cache.
 */

// Immediate Theme Pre-hydration (Prevents flash of wrong theme before DOM paints)
(function() {
  'use strict';
  try {
    const savedTheme = localStorage.getItem('field_atlas_theme') || 
      (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', savedTheme);
    if (savedTheme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  } catch (e) {}
})();

// ─── Theme Controller ──────────────────────────────────────────────────────────
window.SkillPulseTheme = (function() {
  'use strict';

  function getTheme() {
    return document.documentElement.getAttribute('data-theme') || 'light';
  }

  function setTheme(theme) {
    if (theme !== 'dark') theme = 'light';
    document.documentElement.setAttribute('data-theme', theme);
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    try {
      localStorage.setItem('field_atlas_theme', theme);
    } catch (e) {}
    updateToggleButtons();
    window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: theme } }));
  }

  function toggle() {
    const current = getTheme();
    const next = current === 'dark' ? 'light' : 'dark';
    setTheme(next);
    return next;
  }

  function updateToggleButtons() {
    const currentTheme = getTheme();
    const isDark = (currentTheme === 'dark');
    document.querySelectorAll('.theme-toggle-btn').forEach(btn => {
      const icon = btn.querySelector('.theme-icon');
      const text = btn.querySelector('.theme-text');
      if (icon) {
        icon.innerHTML = isDark ? '🌙' : '☀️';
      }
      if (text) {
        text.textContent = isDark ? 'Dark' : 'Light';
      }
      btn.setAttribute('aria-label', isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode');
      btn.setAttribute('title', isDark ? 'Dark Mode active (click to switch to Light)' : 'Light Mode active (click to switch to Dark)');
    });
  }

  function init() {
    updateToggleButtons();
    // Global delegated listener for any theme toggle button
    document.addEventListener('click', function(e) {
      const btn = e.target.closest('.theme-toggle-btn');
      if (btn) {
        e.preventDefault();
        toggle();
      }
    });
  }

  return {
    getTheme: getTheme,
    setTheme: setTheme,
    toggle: toggle,
    updateToggleButtons: updateToggleButtons,
    init: init
  };
})();

// ─── Compulsory Session Memory Cache ───────────────────────────────────────────
window.SkillPulseCache = (function() {
  'use strict';
  const CACHE_PREFIX = 'fa_session_cache_';

  function set(key, value) {
    try {
      const item = {
        data: value,
        timestamp: Date.now()
      };
      const serialized = JSON.stringify(item);
      sessionStorage.setItem(CACHE_PREFIX + key, serialized);
      localStorage.setItem(CACHE_PREFIX + key, serialized);
    } catch (e) {
      console.warn('[SessionCache] Error writing to session cache:', e);
    }
  }

  function get(key, fallback = null) {
    try {
      let raw = sessionStorage.getItem(CACHE_PREFIX + key);
      if (!raw) {
        raw = localStorage.getItem(CACHE_PREFIX + key);
      }
      if (!raw) return fallback;
      const parsed = JSON.parse(raw);
      return parsed.data !== undefined ? parsed.data : parsed;
    } catch (e) {
      return fallback;
    }
  }

  function remove(key) {
    try {
      sessionStorage.removeItem(CACHE_PREFIX + key);
      localStorage.removeItem(CACHE_PREFIX + key);
    } catch (e) {}
  }

  function clear() {
    try {
      Object.keys(sessionStorage).forEach(k => {
        if (k.startsWith(CACHE_PREFIX)) sessionStorage.removeItem(k);
      });
      Object.keys(localStorage).forEach(k => {
        if (k.startsWith(CACHE_PREFIX)) localStorage.removeItem(k);
      });
    } catch (e) {}
  }

  return {
    set: set,
    get: get,
    remove: remove,
    clear: clear
  };
})();

// ─── API Configuration ────────────────────────────────────────────────────────
window.FIELD_ATLAS_CONFIG = (function() {
  'use strict';

  const storedUrl = window.localStorage.getItem('FIELD_ATLAS_API_BASE_URL');
  const PRODUCTION_BACKEND_URL = 'https://skillpulse-backend.vercel.app';

  let defaultBaseUrl = 'http://127.0.0.1:8000';
  if (window.location.protocol === 'https:' && window.location.hostname !== 'localhost') {
    defaultBaseUrl = PRODUCTION_BACKEND_URL;
  }

  if (window.location.protocol === 'https:') {
    window.localStorage.removeItem('FIELD_ATLAS_API_BASE_URL');
    window.localStorage.removeItem('FIELD_ATLAS_PROD_API_URL');
  }

  const API_BASE_URL = (window.location.protocol === 'https:' && window.location.hostname !== 'localhost')
    ? defaultBaseUrl
    : (storedUrl || defaultBaseUrl);

  return {
    API_BASE_URL: API_BASE_URL,

    setApiBaseUrl: function(url) {
      if (url) {
        window.localStorage.setItem('FIELD_ATLAS_API_BASE_URL', url.replace(/\/+$/, ''));
      } else {
        window.localStorage.removeItem('FIELD_ATLAS_API_BASE_URL');
      }
      window.location.reload();
    },

    resetApiBaseUrl: function() {
      window.localStorage.removeItem('FIELD_ATLAS_API_BASE_URL');
      window.location.reload();
    }
  };
})();

// Automatically bind theme toggle on DOM ready
document.addEventListener('DOMContentLoaded', function() {
  window.SkillPulseTheme.init();
});

window.FIELD_ATLAS_CONFIG = window.SKILLPULSE_CONFIG || window.FIELD_ATLAS_CONFIG || {};
window.SKILLPULSE_CONFIG = window.FIELD_ATLAS_CONFIG;

/*
 * SKILLPULSE — REST API CLIENT & UI UTILITIES
 * Pure Vanilla JavaScript module for API interaction, CSRF token management, modals, and toasts
 */

const SkillPulseAPI = (function() {
  'use strict';

  // Extracts the Django CSRF token from the browser cookie store
  function getCsrfToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, 10) === ('csrftoken=')) {
          cookieValue = decodeURIComponent(cookie.substring(10));
          break;
        }
      }
    }
    return cookieValue;
  }

  // Displays a floating toast notification message with auto-dismiss
  function showToast(message, type = 'success') {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
      <div style="display: flex; align-items: center; gap: 0.5rem;">
        <span>${message}</span>
      </div>
      <button style="background: none; border: none; color: inherit; cursor: pointer; font-size: 1.1rem;" onclick="this.parentElement.remove()">&times;</button>
    `;

    container.appendChild(toast);
    setTimeout(() => {
      if (toast.parentElement) {
        toast.remove();
      }
    }, 4500);
  }

  // Opens a specified dialog modal and manages backdrop focus
  function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add('active');
      const firstInput = modal.querySelector('input, select, textarea, button');
      if (firstInput) firstInput.focus();
    }
  }

  // Closes an active dialog modal
  function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove('active');
    }
  }

  // Retrieves the configured backend API base URL
  function getApiBaseUrl() {
    if (window.FIELD_ATLAS_CONFIG && window.FIELD_ATLAS_CONFIG.API_BASE_URL) {
      return window.FIELD_ATLAS_CONFIG.API_BASE_URL.replace(/\/+$/, '');
    }
    return '';
  }

  // Core asynchronous fetch wrapper managing headers, CSRF token, and standard error handling
  async function request(endpoint, options = {}) {
    const baseUrl = getApiBaseUrl();
    const fullUrl = endpoint.startsWith('http') ? endpoint : `${baseUrl}${endpoint}`;

    const defaultHeaders = {
      'Accept': 'application/json',
    };

    if (!(options.body instanceof FormData)) {
      defaultHeaders['Content-Type'] = 'application/json';
    }

    const csrfToken = getCsrfToken();
    if (csrfToken && ['POST', 'PATCH', 'PUT', 'DELETE'].includes((options.method || 'GET').toUpperCase())) {
      defaultHeaders['X-CSRFToken'] = csrfToken;
    }

    // Always include credentials for cross-origin session cookies
    options.credentials = options.credentials || 'include';
    options.headers = {
      ...defaultHeaders,
      ...(options.headers || {})
    };

    try {
      const response = await fetch(fullUrl, options);
      
      // Handle download responses
      const contentType = response.headers.get('content-type');
      if (contentType && (contentType.includes('text/csv') || contentType.includes('application/pdf'))) {
        return response;
      }

      const data = await response.json();
      if (!response.ok) {
        const errorMsg = data.error 
          ? (typeof data.error === 'object' ? JSON.stringify(data.error) : data.error)
          : (data.detail || 'An unexpected error occurred.');
        throw new Error(errorMsg);
      }
      return data;
    } catch (err) {
      if (!options.silent) {
        showToast(err.message, 'error');
      }
      throw err;
    }
  }

  // Sends an authenticated HTTP GET request
  async function get(endpoint, params = {}, options = {}) {
    const baseUrl = getApiBaseUrl() || window.location.origin;
    const fullUrl = endpoint.startsWith('http') ? endpoint : `${baseUrl}${endpoint}`;
    const url = new URL(fullUrl, window.location.origin);
    Object.keys(params).forEach(key => {
      if (params[key] !== null && params[key] !== undefined && params[key] !== '') {
        url.searchParams.append(key, params[key]);
      }
    });
    return request(url.toString(), { method: 'GET', ...options });
  }

  // Sends an authenticated HTTP POST request
  async function post(endpoint, data = {}, options = {}) {
    const isFormData = data instanceof FormData;
    return request(endpoint, {
      method: 'POST',
      body: isFormData ? data : JSON.stringify(data),
      ...options
    });
  }

  // Sends an authenticated HTTP PATCH request
  async function patch(endpoint, data = {}, options = {}) {
    const isFormData = data instanceof FormData;
    return request(endpoint, {
      method: 'PATCH',
      body: isFormData ? data : JSON.stringify(data),
      ...options
    });
  }

  // Helper to fetch current logged-in user profile
  async function getCurrentUser() {
    return get('/api/auth/me/');
  }

  // Helper to log out
  async function logout() {
    return post('/api/auth/logout/');
  }

  return {
    getApiBaseUrl: getApiBaseUrl,
    getCsrfToken: getCsrfToken,
    showToast: showToast,
    openModal: openModal,
    closeModal: closeModal,
    request: request,
    get: get,
    post: post,
    patch: patch,
    getCurrentUser: getCurrentUser,
    logout: logout
  };
})();

// Attach globally
window.SkillPulseAPI = SkillPulseAPI;
window.FieldAtlasAPI = SkillPulseAPI;


/*
 * FIELD ATLAS — TRAINER DASHBOARD INTERACTION CONTROLLER
 * Controls Overview metrics, Chart.js graphs, Follow-up queue & outreach simulator,
 * Trainees search/filters/modal creation/consent/CSV export, and Reports downloads
 */

document.addEventListener('DOMContentLoaded', function() {
  'use strict';

  // State variables for trainer dashboard operations
  let currentFollowUpQueue = [];
  let selectedFollowUp = null;
  let activeTab = 'overview';
  let currentChannel = 'whatsapp';

  // Switches between trainer dashboard view panels (Overview, Follow-ups, Trainees, Providers, Reports)
  function switchView(targetTabId) {
    activeTab = targetTabId;

    // Update navigation styles
    document.querySelectorAll('.nav-link[data-tab]').forEach(link => {
      link.classList.toggle('active', link.getAttribute('data-tab') === targetTabId);
    });

    document.querySelectorAll('.bottom-nav-item[data-tab]').forEach(item => {
      item.classList.toggle('active', item.getAttribute('data-tab') === targetTabId);
    });

    // Toggle view visibility
    document.querySelectorAll('.tab-view-panel').forEach(panel => {
      panel.style.display = (panel.id === `view-${targetTabId}`) ? 'block' : 'none';
    });

    // Update breadcrumb
    const breadcrumbLabel = document.getElementById('header-active-view-name');
    if (breadcrumbLabel) {
      breadcrumbLabel.textContent = targetTabId.charAt(0).toUpperCase() + targetTabId.slice(1);
    }

    // Trigger tab-specific loaders
    if (targetTabId === 'overview') {
      loadOverviewData();
    } else if (targetTabId === 'followups') {
      loadFollowUpsData();
    } else if (targetTabId === 'trainees') {
      loadTraineesData();
    } else if (targetTabId === 'providers') {
      loadProvidersData();
    }
  }

  // Fetches aggregated summary statistics and renders overview visualizations
  async function loadOverviewData() {
    try {
      const data = await FieldAtlasAPI.get('/api/trainer/dashboard/');

      // Render Charts
      if (window.FieldAtlasCharts) {
        FieldAtlasCharts.renderWageChart('wageProgressionCanvas', data.wage_chart);
        FieldAtlasCharts.renderFunnelChart('funnelConversionCanvas', data.funnel_chart);
        FieldAtlasCharts.renderProviderPulseChart('providerPulseCanvas', data.providers_pulse);
        FieldAtlasCharts.renderNonPlacementChart('nonPlacementCanvas', data.non_placement_reasons);
      }
    } catch (err) {
      console.error('Failed to load overview data:', err);
    }
  }

  // Fetches the assisted follow-up queue and populates priority cards
  async function loadFollowUpsData() {
    try {
      const res = await FieldAtlasAPI.get('/api/outcomes/follow-ups/');
      currentFollowUpQueue = res.follow_ups || [];
      renderFollowUpQueue();
      if (currentFollowUpQueue.length > 0) {
        selectFollowUpItem(currentFollowUpQueue[0]);
      }
    } catch (err) {
      console.error('Failed to load follow-up queue:', err);
    }
  }

  // Renders the list of selectable follow-up candidate records
  function renderFollowUpQueue() {
    const listContainer = document.getElementById('followup-queue-list');
    if (!listContainer) return;

    listContainer.innerHTML = '';
    if (currentFollowUpQueue.length === 0) {
      listContainer.innerHTML = '<div style="padding: 1.5rem; text-align: center; color: var(--color-text-muted);">No follow-ups pending in this queue.</div>';
      return;
    }

    currentFollowUpQueue.forEach(item => {
      const el = document.createElement('div');
      const isSelected = selectedFollowUp && selectedFollowUp.id === item.id;
      el.className = `queue-item ${isSelected ? 'selected' : ''}`;
      
      const badgeClass = item.status === 'sent' ? 'badge-teal' : (item.status === 'needs_assistance' ? 'badge-coral' : 'badge-ochre');
      const consentBadge = item.trainee_consent === 'active' 
        ? '<span class="badge badge-teal" style="font-size: 0.7rem;">Consent Active</span>'
        : '<span class="badge badge-neutral" style="font-size: 0.7rem;">Consent Withdrawn</span>';

      el.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.35rem;">
          <div>
            <strong style="color: var(--color-deep-indigo); font-size: 0.95rem;">${item.trainee_name}</strong>
            <span style="font-size: 0.75rem; color: var(--color-text-muted); margin-left: 0.4rem;">${item.trainee_unified_id}</span>
          </div>
          <span class="badge ${badgeClass}">${item.status.replace('_', ' ')}</span>
        </div>
        <div style="font-size: 0.8rem; color: var(--color-text-secondary); margin-bottom: 0.5rem;">
          ${item.trainee_course} · ${item.trainee_district}
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.75rem; color: var(--color-text-muted);">
          <span>${item.milestone.replace('_', ' ')} · ${item.attempts} attempt(s)</span>
          ${consentBadge}
        </div>
      `;

      el.addEventListener('click', () => {
        selectFollowUpItem(item);
      });

      listContainer.appendChild(el);
    });
  }

  // Selects a follow-up item and updates the outreach preview message
  function selectFollowUpItem(item) {
    selectedFollowUp = item;
    renderFollowUpQueue();

    const nameEl = document.getElementById('preview-trainee-name');
    const idEl = document.getElementById('preview-trainee-id');
    const courseEl = document.getElementById('preview-trainee-course');
    const bubbleEl = document.getElementById('simulator-message-text');
    const statusNoteEl = document.getElementById('simulator-status-note');
    const sendBtn = document.getElementById('btn-dispatch-followup');

    if (nameEl) nameEl.textContent = item.trainee_name;
    if (idEl) idEl.textContent = item.trainee_unified_id;
    if (courseEl) courseEl.textContent = `${item.trainee_course} (${item.trainee_district})`;

    if (bubbleEl) {
      const channelGreeting = currentChannel === 'whatsapp' ? '👋 Namaste' : 'Hello';
      bubbleEl.textContent = `${channelGreeting} ${item.trainee_name}, this is Field Atlas checking in on your employment after completing your ${item.trainee_course} training. Could you please share your current work status?`;
    }

    if (statusNoteEl) {
      if (item.trainee_consent !== 'active') {
        statusNoteEl.innerHTML = `<span style="color: var(--color-coral); font-weight: 700;">⚠️ Participant has withdrawn consent. Outreach is blocked.</span>`;
        if (sendBtn) sendBtn.disabled = true;
      } else {
        statusNoteEl.innerHTML = `<span style="color: var(--color-teal);">✓ Consent verified active. Safe to contact.</span>`;
        if (sendBtn) sendBtn.disabled = false;
      }
    }
  }

  // Sends an outreach attempt via the simulated gateway, verifying active consent and updating state
  async function dispatchFollowUpOutreach() {
    if (!selectedFollowUp) {
      FieldAtlasAPI.showToast('Please select a participant from the queue.', 'warning');
      return;
    }

    const sendBtn = document.getElementById('btn-dispatch-followup');
    const originalText = sendBtn.innerHTML;
    sendBtn.disabled = true;
    sendBtn.innerHTML = 'Dispatching...';

    // Show simulated typing state
    const bubbleEl = document.getElementById('simulator-message-text');
    if (bubbleEl) bubbleEl.classList.add('typing');

    try {
      const res = await FieldAtlasAPI.post(`/api/outcomes/follow-ups/${selectedFollowUp.id}/send/`);
      FieldAtlasAPI.showToast(res.message, 'success');

      // Update local item
      selectedFollowUp.attempts += 1;
      selectedFollowUp.status = 'sent';
      selectedFollowUp.last_attempt_at = new Date().toISOString();

      setTimeout(() => {
        if (bubbleEl) bubbleEl.classList.remove('typing');
        renderFollowUpQueue();
        sendBtn.disabled = false;
        sendBtn.innerHTML = originalText;
      }, 750);
    } catch (err) {
      if (bubbleEl) bubbleEl.classList.remove('typing');
      sendBtn.disabled = false;
      sendBtn.innerHTML = originalText;
    }
  }

  // Fetches trainees with optional search query and dropdown filters
  async function loadTraineesData() {
    const searchVal = document.getElementById('trainee-search-input') ? document.getElementById('trainee-search-input').value.trim() : '';
    const providerVal = document.getElementById('filter-provider') ? document.getElementById('filter-provider').value : '';
    const stageVal = document.getElementById('filter-stage') ? document.getElementById('filter-stage').value : '';
    const consentVal = document.getElementById('filter-consent') ? document.getElementById('filter-consent').value : '';

    try {
      const data = await FieldAtlasAPI.get('/api/outcomes/trainees/', {
        q: searchVal,
        provider: providerVal,
        stage: stageVal,
        consent: consentVal
      });

      renderTraineeTable(data.trainees || []);
    } catch (err) {
      console.error('Failed to load trainees:', err);
    }
  }

  // Renders the searchable trainee data table
  function renderTraineeTable(trainees) {
    const tbody = document.getElementById('trainees-table-body');
    if (!tbody) return;

    tbody.innerHTML = '';
    if (trainees.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; padding: 2rem; color: var(--color-text-muted);">No learners match the selected filters.</td></tr>`;
      return;
    }

    trainees.forEach(t => {
      const tr = document.createElement('tr');
      const placement = t.latest_placement;
      const wageDisplay = (placement && placement.wage) ? `₹${Number(placement.wage).toLocaleString()}` : '—';
      const employerSignal = placement ? placement.validation_status.charAt(0).toUpperCase() + placement.validation_status.slice(1) : 'Unreported';
      const signalBadgeClass = employerSignal === 'Verified' ? 'badge-teal' : (employerSignal === 'Pending' ? 'badge-ochre' : 'badge-neutral');
      
      const stageBadgeClass = t.stage === 'retained' ? 'badge-teal' : (t.stage === 'placed' ? 'badge-indigo' : (t.stage === 'follow_up_due' ? 'badge-coral' : 'badge-neutral'));
      const consentBadge = t.consent_status === 'active'
        ? '<span class="badge badge-teal">Active</span>'
        : '<span class="badge badge-neutral">Withdrawn</span>';

      tr.innerHTML = `
        <td>
          <div style="font-weight: 700; color: var(--color-deep-indigo);">${t.name}</div>
          <div style="font-size: 0.75rem; color: var(--color-text-muted); font-family: var(--font-mono);">${t.unified_id} · ${t.course}</div>
        </td>
        <td><span class="badge ${stageBadgeClass}">${t.stage.replace('_', ' ')}</span></td>
        <td>${t.provider} <br><span style="font-size: 0.75rem; color: var(--color-text-muted);">${t.district}</span></td>
        <td><span class="badge ${signalBadgeClass}">${employerSignal}</span></td>
        <td style="font-weight: 700;">${wageDisplay}</td>
        <td>${consentBadge}</td>
        <td>
          <div style="display: flex; gap: 0.4rem;">
            <button class="btn btn-outline btn-sm btn-edit-trainee" data-id="${t.id}" title="Edit trainee details">Edit</button>
            <button class="btn btn-outline btn-sm btn-toggle-consent" data-id="${t.id}" data-current="${t.consent_status}" title="Update consent status">Consent</button>
          </div>
        </td>
      `;

      tbody.appendChild(tr);
    });

    // Attach row action listeners
    attachTraineeRowListeners();
  }

  // Attaches click handlers to table action buttons
  function attachTraineeRowListeners() {
    document.querySelectorAll('.btn-edit-trainee').forEach(btn => {
      btn.addEventListener('click', async function() {
        const id = this.getAttribute('data-id');
        openEditTraineeModal(id);
      });
    });

    document.querySelectorAll('.btn-toggle-consent').forEach(btn => {
      btn.addEventListener('click', async function() {
        const id = this.getAttribute('data-id');
        const current = this.getAttribute('data-current');
        const nextStatus = current === 'active' ? 'withdrawn' : 'granted';
        if (confirm(`Are you sure you want to change participant consent status to '${nextStatus}'?`)) {
          try {
            await FieldAtlasAPI.post('/api/outcomes/consents/', {
              trainee_id: id,
              status: nextStatus
            });
            FieldAtlasAPI.showToast(`Consent updated to ${nextStatus}.`, 'success');
            loadTraineesData();
          } catch (err) {}
        }
      });
    });
  }

  // Loads single trainee record and populates the edit modal
  async function openEditTraineeModal(traineeId) {
    try {
      const t = await FieldAtlasAPI.get(`/api/outcomes/trainees/${traineeId}/`);
      document.getElementById('edit-trainee-id').value = t.id;
      document.getElementById('edit-trainee-name').value = t.name;
      document.getElementById('edit-trainee-course').value = t.course;
      document.getElementById('edit-trainee-provider').value = t.provider;
      document.getElementById('edit-trainee-district').value = t.district;
      document.getElementById('edit-trainee-state').value = t.state;
      document.getElementById('edit-trainee-stage').value = t.stage;
      FieldAtlasAPI.openModal('modal-edit-trainee');
    } catch (err) {}
  }

  // Loads provider benchmarking charts and performance cards
  async function loadProvidersData() {
    try {
      const data = await FieldAtlasAPI.get('/api/trainer/dashboard/');
      if (window.FieldAtlasCharts && data.providers_pulse) {
        FieldAtlasCharts.renderProviderPulseChart('providerComparisonCanvas', data.providers_pulse);
      }
    } catch (err) {
      console.error('Failed to load provider metrics:', err);
    }
  }

  // Sets up universal tab switching, search input debouncing, modals, and report exports
  function setupEventListeners() {
    // Navigation tab clicks
    document.querySelectorAll('.nav-link[data-tab], .bottom-nav-item[data-tab]').forEach(btn => {
      btn.addEventListener('click', function(e) {
        e.preventDefault();
        const tab = this.getAttribute('data-tab');
        if (tab) {
          switchView(tab);
          // Close mobile sidebar if open
          document.getElementById('app-sidebar').classList.remove('open');
          document.getElementById('mobile-backdrop').classList.remove('active');
        }
      });
    });

    // Mobile drawer toggle
    const drawerToggle = document.getElementById('mobile-drawer-toggle');
    const sidebar = document.getElementById('app-sidebar');
    const backdrop = document.getElementById('mobile-backdrop');

    if (drawerToggle && sidebar && backdrop) {
      drawerToggle.addEventListener('click', () => {
        sidebar.classList.toggle('open');
        backdrop.classList.toggle('active');
      });

      backdrop.addEventListener('click', () => {
        sidebar.classList.remove('open');
        backdrop.classList.remove('active');
      });
    }

    // Follow-up tab switcher (WhatsApp vs SMS)
    document.querySelectorAll('.simulator-tab-btn').forEach(tabBtn => {
      tabBtn.addEventListener('click', function() {
        document.querySelectorAll('.simulator-tab-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        currentChannel = this.getAttribute('data-channel');
        if (selectedFollowUp) {
          selectFollowUpItem(selectedFollowUp);
        }
      });
    });

    // Outreach dispatch button
    const sendBtn = document.getElementById('btn-dispatch-followup');
    if (sendBtn) {
      sendBtn.addEventListener('click', dispatchFollowUpOutreach);
    }

    // Trainee search filter
    const searchInput = document.getElementById('trainee-search-input');
    if (searchInput) {
      let debounceTimer;
      searchInput.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(loadTraineesData, 350);
      });
    }

    // Dropdown filters
    ['filter-provider', 'filter-stage', 'filter-consent'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.addEventListener('change', loadTraineesData);
    });

    // New Trainee form submission
    const newTraineeForm = document.getElementById('form-new-trainee');
    if (newTraineeForm) {
      newTraineeForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const payload = {
          unified_id: document.getElementById('new-trainee-id').value.trim(),
          name: document.getElementById('new-trainee-name').value.trim(),
          course: document.getElementById('new-trainee-course').value.trim(),
          provider: document.getElementById('new-trainee-provider').value.trim(),
          district: document.getElementById('new-trainee-district').value.trim(),
          state: document.getElementById('new-trainee-state').value.trim(),
          stage: document.getElementById('new-trainee-stage').value,
          gender: document.getElementById('new-trainee-gender').value,
          age_band: document.getElementById('new-trainee-age').value,
          consent_status: 'active'
        };

        try {
          await FieldAtlasAPI.post('/api/outcomes/trainees/', payload);
          FieldAtlasAPI.showToast('Trainee registered with active consent record.', 'success');
          FieldAtlasAPI.closeModal('modal-new-trainee');
          newTraineeForm.reset();
          loadTraineesData();
        } catch (err) {}
      });
    }

    // Edit Trainee form submission
    const editTraineeForm = document.getElementById('form-edit-trainee');
    if (editTraineeForm) {
      editTraineeForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const id = document.getElementById('edit-trainee-id').value;
        const payload = {
          name: document.getElementById('edit-trainee-name').value.trim(),
          course: document.getElementById('edit-trainee-course').value.trim(),
          provider: document.getElementById('edit-trainee-provider').value.trim(),
          district: document.getElementById('edit-trainee-district').value.trim(),
          state: document.getElementById('edit-trainee-state').value.trim(),
          stage: document.getElementById('edit-trainee-stage').value
        };

        try {
          await FieldAtlasAPI.patch(`/api/outcomes/trainees/${id}/`, payload);
          FieldAtlasAPI.showToast('Trainee record updated successfully.', 'success');
          FieldAtlasAPI.closeModal('modal-edit-trainee');
          loadTraineesData();
        } catch (err) {}
      });
    }

    // Seed Demo Data button
    document.querySelectorAll('.btn-seed-demo-trigger').forEach(btn => {
      btn.addEventListener('click', async function() {
        try {
          const res = await FieldAtlasAPI.post('/api/outcomes/trainees/seed-demo/');
          FieldAtlasAPI.showToast(res.message || 'Demo data verified and loaded.', 'success');
          loadOverviewData();
          loadTraineesData();
          loadFollowUpsData();
        } catch (err) {}
      });
    });

    // CSV Impact Export download
    document.querySelectorAll('.btn-download-impact-csv').forEach(btn => {
      btn.addEventListener('click', () => {
        window.location.href = '/api/reports/impact-export/';
      });
    });

    // CSV Provider Export download
    document.querySelectorAll('.btn-download-provider-csv').forEach(btn => {
      btn.addEventListener('click', () => {
        window.location.href = '/api/reports/provider-export/';
      });
    });
  }

  // Initialize
  setupEventListeners();
  switchView('overview');
});

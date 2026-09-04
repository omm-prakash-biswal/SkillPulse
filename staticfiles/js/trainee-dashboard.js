/*
 * FIELD ATLAS — TRAINEE PORTAL CONTROLLER
 * Mobile-first controller managing learner stage timeline, profile completeness,
 * upcoming check-in response actions, consent toggle, and progress report generation
 */

document.addEventListener('DOMContentLoaded', function() {
  'use strict';

  let currentDashboardData = null;

  // Fetches personalized dashboard details for the logged-in learner
  async function loadTraineeDashboard() {
    try {
      const data = await FieldAtlasAPI.get('/api/trainee/me/dashboard/');
      currentDashboardData = data;
      renderTraineeInterface(data);
    } catch (err) {
      console.error('Failed to load trainee portal:', err);
    }
  }

  // Populates learner cards, milestone rail, placement card, and check-in prompt
  function renderTraineeInterface(data) {
    const t = data.trainee;

    // Populate learner identity
    const nameEl = document.getElementById('trainee-name-display');
    const courseEl = document.getElementById('trainee-course-display');
    const idEl = document.getElementById('trainee-id-display');
    const completionEl = document.getElementById('trainee-completion-pct');
    const completionBar = document.getElementById('trainee-completion-bar');

    if (nameEl) nameEl.textContent = t.name;
    if (courseEl) courseEl.textContent = `${t.course} · ${t.provider}`;
    if (idEl) idEl.textContent = t.unified_id;
    if (completionEl) completionEl.textContent = `${data.completion_percentage}%`;
    if (completionBar) completionBar.style.width = `${data.completion_percentage}%`;

    // Render Stage Timeline Rail
    const railSteps = document.querySelectorAll('.trainee-stage-step');
    railSteps.forEach((stepEl, idx) => {
      if (idx <= data.current_stage_index) {
        stepEl.classList.add('active');
      } else {
        stepEl.classList.remove('active');
      }
    });

    // Render Placement Card
    const placementCard = document.getElementById('trainee-placement-card');
    const placementEmpty = document.getElementById('trainee-placement-empty');
    if (data.latest_placement) {
      if (placementCard) placementCard.style.display = 'block';
      if (placementEmpty) placementEmpty.style.display = 'none';

      const p = data.latest_placement;
      document.getElementById('placement-employer').textContent = p.employer_name;
      document.getElementById('placement-role').textContent = p.role;
      document.getElementById('placement-wage').textContent = p.wage ? `₹${Number(p.wage).toLocaleString()}/month` : 'Self-Reported Wage';
      document.getElementById('placement-status').textContent = p.validation_status.toUpperCase();
    } else {
      if (placementCard) placementCard.style.display = 'none';
      if (placementEmpty) placementEmpty.style.display = 'block';
    }

    // Render Upcoming Check-in Card
    const checkinCard = document.getElementById('trainee-checkin-card');
    const checkinPrompt = document.getElementById('trainee-checkin-prompt');
    const checkinEmpty = document.getElementById('trainee-checkin-empty');

    if (data.upcoming_follow_up) {
      if (checkinCard) checkinCard.style.display = 'block';
      if (checkinEmpty) checkinEmpty.style.display = 'none';
      if (checkinPrompt) {
        checkinPrompt.textContent = `Scheduled ${data.upcoming_follow_up.milestone.replace('_', ' ')} check-in. How has your employment progressed recently?`;
      }
    } else {
      if (checkinCard) checkinCard.style.display = 'none';
      if (checkinEmpty) checkinEmpty.style.display = 'block';
    }

    // Render Consent Status
    const consentBadge = document.getElementById('trainee-consent-badge');
    const consentBtn = document.getElementById('btn-toggle-my-consent');
    if (consentBadge) {
      if (t.consent_status === 'active') {
        consentBadge.className = 'badge badge-teal';
        consentBadge.textContent = 'Active & Protected';
        if (consentBtn) consentBtn.textContent = 'Withdraw Consent';
      } else {
        consentBadge.className = 'badge badge-neutral';
        consentBadge.textContent = 'Consent Withdrawn';
        if (consentBtn) consentBtn.textContent = 'Grant Consent';
      }
    }
  }

  // Submits the learner's self-reported check-in status
  async function respondToCheckIn(responseChoice) {
    if (!currentDashboardData || !currentDashboardData.upcoming_follow_up) {
      FieldAtlasAPI.showToast('No active check-in pending.', 'warning');
      return;
    }

    const followUpId = currentDashboardData.upcoming_follow_up.id;
    try {
      const res = await FieldAtlasAPI.post(`/api/trainee/me/follow-ups/${followUpId}/respond/`, {
        response_choice: responseChoice
      });
      FieldAtlasAPI.showToast(res.message || 'Check-in response saved successfully!', 'success');
      loadTraineeDashboard();
    } catch (err) {}
  }

  // Toggles learner consent status between active and withdrawn
  async function toggleConsent() {
    if (!currentDashboardData) return;
    const current = currentDashboardData.trainee.consent_status;
    const nextStatus = current === 'active' ? 'withdrawn' : 'granted';

    const confirmMsg = (nextStatus === 'withdrawn')
      ? 'Withdrawing consent will mask your contact details from outreach queues and anonymize your record in reports. Proceed?'
      : 'Grant consent to allow your training provider to assist with verified employment records?';

    if (confirm(confirmMsg)) {
      try {
        const res = await FieldAtlasAPI.post('/api/trainee/me/consent/', {
          status: nextStatus
        });
        FieldAtlasAPI.showToast(res.message, 'success');
        loadTraineeDashboard();
      } catch (err) {}
    }
  }

  // Generates and downloads the learner progress summary document
  async function downloadProgressReport() {
    try {
      const res = await FieldAtlasAPI.get('/api/trainee/me/progress-report/');
      const rep = res.report;

      // Generate formatted printable HTML report window
      const printWindow = window.open('', '_blank');
      printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
          <title>Field Atlas Progress Report — ${rep.learner_name}</title>
          <style>
            body { font-family: 'Plus Jakarta Sans', sans-serif; padding: 40px; color: #1E2749; line-height: 1.6; }
            .header { border-bottom: 3px solid #0E8176; padding-bottom: 15px; margin-bottom: 25px; }
            .badge { display: inline-block; padding: 4px 12px; border-radius: 999px; background: #E0F2F1; color: #0E8176; font-weight: bold; }
            .row { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #E2E8F0; }
            .footer { margin-top: 40px; font-size: 0.85rem; color: #64748B; border-top: 1px solid #E2E8F0; padding-top: 15px; }
          </style>
        </head>
        <body>
          <div class="header">
            <h2>FIELD ATLAS — LEARNER PROGRESS REPORT</h2>
            <p>Unified ID: <strong>${rep.unified_id}</strong> | Generated: ${rep.generated_at}</p>
          </div>
          <div class="row"><span>Learner Name:</span><strong>${rep.learner_name}</strong></div>
          <div class="row"><span>Vocational Course:</span><strong>${rep.course}</strong></div>
          <div class="row"><span>Training Provider:</span><strong>${rep.provider}</strong></div>
          <div class="row"><span>District & State:</span><strong>${rep.location}</strong></div>
          <div class="row"><span>Current Outcome Stage:</span><span class="badge">${rep.current_stage}</span></div>
          <div class="row"><span>Consent Status:</span><strong>${rep.consent_status}</strong></div>
          <div class="row"><span>Recorded Placements:</span><strong>${rep.placements_count}</strong></div>
          <div class="footer">
            <p>${rep.program_verification}</p>
            <p>Consent-aware by design · No raw Aadhaar stored</p>
          </div>
          <script>window.print();</script>
        </body>
        </html>
      `);
      printWindow.document.close();
    } catch (err) {}
  }

  // Setup click listeners for check-in action buttons
  function setupTraineeListeners() {
    const btnWork = document.getElementById('btn-trainee-working');
    if (btnWork) btnWork.addEventListener('click', () => respondToCheckIn('working'));

    const btnBusiness = document.getElementById('btn-trainee-business');
    if (btnBusiness) btnBusiness.addEventListener('click', () => respondToCheckIn('own_work'));

    const btnSupport = document.getElementById('btn-trainee-support');
    if (btnSupport) btnSupport.addEventListener('click', () => respondToCheckIn('need_help'));

    const btnConsent = document.getElementById('btn-toggle-my-consent');
    if (btnConsent) btnConsent.addEventListener('click', toggleConsent);

    const btnReport = document.getElementById('btn-trainee-download-report');
    if (btnReport) btnReport.addEventListener('click', downloadProgressReport);
  }

  setupTraineeListeners();
  loadTraineeDashboard();
});

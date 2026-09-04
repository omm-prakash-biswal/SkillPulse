/*
 * FIELD ATLAS — EDITABLE PROFILE CONTROLLER
 * Manages user profile fields updating, profile avatar upload, password change,
 * and loading of enrolled or instructed vocational courses
 */

document.addEventListener('DOMContentLoaded', function() {
  'use strict';

  // Escapes HTML content to prevent XSS injection
  function escapeHTML(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  // Loads authenticated user profile into the editor form and triggers course listing
  async function loadUserProfile() {
    try {
      const res = await FieldAtlasAPI.get('/api/profile/');
      const u = res.user;

      const nameInput = document.getElementById('profile-name');
      const emailInput = document.getElementById('profile-email');
      const phoneInput = document.getElementById('profile-phone');
      const idInput = document.getElementById('profile-id');
      const langInput = document.getElementById('profile-language');
      const providerInput = document.getElementById('profile-provider');
      const districtInput = document.getElementById('profile-district');
      const stateInput = document.getElementById('profile-state');
      const addressInput = document.getElementById('profile-address');
      const bioInput = document.getElementById('profile-bio');
      const avatarImg = document.getElementById('profile-avatar-preview');

      if (nameInput) nameInput.value = u.full_name || '';
      if (emailInput) emailInput.value = u.email || '';
      if (phoneInput) phoneInput.value = u.phone_number || '';
      if (idInput) idInput.value = u.field_atlas_id || '';
      if (langInput) langInput.value = u.preferred_language || 'en';
      if (providerInput) providerInput.value = u.provider || '';
      if (districtInput) districtInput.value = u.district || '';
      if (stateInput) stateInput.value = u.state || '';
      if (addressInput) addressInput.value = u.address || '';
      if (bioInput) bioInput.value = u.bio || '';

      if (avatarImg && u.profile_photo_url) {
        avatarImg.src = u.profile_photo_url;
      }

      loadProfileCourses(u.role);
    } catch (err) {
      console.error('Failed to load profile:', err);
    }
  }

  // Fetches and displays enrolled or instructed courses based on user role
  async function loadProfileCourses(role) {
    const container = document.getElementById('profile-courses-container');
    if (!container) return;

    try {
      if (role === 'trainee') {
        const enrollments = await FieldAtlasAPI.get('/api/trainee/me/enrollments/');
        if (!enrollments || enrollments.length === 0) {
          container.innerHTML = '<div style="color: var(--color-text-muted); font-size: 0.85rem; text-align: center; padding: 1rem;">No course enrollments on record.</div>';
          return;
        }

        container.innerHTML = enrollments.map(e => {
          const certBadge = e.certificate && e.certificate.status === 'issued'
            ? `<a href="/api/certificates/${e.certificate.id}/download/" target="_blank" class="btn btn-outline btn-sm" style="font-size: 0.75rem; padding: 3px 8px;">Download Certificate</a>`
            : '';

          return `
            <div style="padding: 10px 14px; border: 1px solid var(--color-border); border-radius: var(--radius-md); margin-bottom: 8px; background: var(--color-bg); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
              <div>
                <strong style="font-size: 0.95rem; color: var(--color-deep-indigo);">${escapeHTML(e.course_title)}</strong>
                <div style="font-size: 0.75rem; color: var(--color-text-muted);">
                  ${escapeHTML(e.category || 'Vocational')} · Progress: ${e.completion_percent}% · Status: ${e.status}
                </div>
              </div>
              <div style="display: flex; align-items: center; gap: 0.5rem;">
                ${certBadge}
                <span class="badge ${e.status === 'completed' ? 'badge-teal' : 'badge-indigo'}">${e.status.toUpperCase()}</span>
              </div>
            </div>
          `;
        }).join('');
      } else {
        const courses = await FieldAtlasAPI.get('/api/courses/');
        if (!courses || courses.length === 0) {
          container.innerHTML = '<div style="color: var(--color-text-muted); font-size: 0.85rem; text-align: center; padding: 1rem;">No courses created under this instructor account.</div>';
          return;
        }

        container.innerHTML = courses.map(c => {
          return `
            <div style="padding: 10px 14px; border: 1px solid var(--color-border); border-radius: var(--radius-md); margin-bottom: 8px; background: var(--color-bg); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
              <div>
                <strong style="font-size: 0.95rem; color: var(--color-deep-indigo);">${escapeHTML(c.title)}</strong>
                <div style="font-size: 0.75rem; color: var(--color-text-muted);">
                  Code: ${escapeHTML(c.course_code)} · ${c.enrolled_count}/${c.capacity} enrolled · ${c.duration_weeks} weeks
                </div>
              </div>
              <div>
                <span class="badge ${c.status === 'published' ? 'badge-teal' : (c.status === 'closed' ? 'badge-coral' : 'badge-neutral')}">${c.status.toUpperCase()}</span>
              </div>
            </div>
          `;
        }).join('');
      }
    } catch (err) {
      container.innerHTML = '<div style="color: var(--color-coral); font-size: 0.85rem;">Failed to load course records.</div>';
    }
  }

  // Handles updating profile fields via PATCH /api/profile/
  const profileForm = document.getElementById('profile-form');
  if (profileForm) {
    profileForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      const submitBtn = profileForm.querySelector('button[type="submit"]');
      const originalText = submitBtn.innerHTML;
      submitBtn.disabled = true;
      submitBtn.innerHTML = 'Saving...';

      const payload = {
        full_name: document.getElementById('profile-name').value.trim(),
        phone_number: document.getElementById('profile-phone').value.trim(),
        preferred_language: document.getElementById('profile-language').value,
        district: document.getElementById('profile-district').value.trim(),
        state: document.getElementById('profile-state').value.trim(),
        address: document.getElementById('profile-address').value.trim(),
      };

      const bioEl = document.getElementById('profile-bio');
      if (bioEl) payload.bio = bioEl.value.trim();

      const providerEl = document.getElementById('profile-provider');
      if (providerEl && !providerEl.disabled) payload.provider = providerEl.value.trim();

      try {
        const res = await FieldAtlasAPI.patch('/api/profile/', payload);
        FieldAtlasAPI.showToast(res.message || 'Profile updated successfully!', 'success');

        // Apply updated language if changed
        if (payload.preferred_language && window.FieldAtlasI18N) {
          FieldAtlasI18N.setLanguage(payload.preferred_language, false);
        }
      } catch (err) {} finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
      }
    });
  }

  // Handles profile photo selection and asynchronous upload
  const photoInput = document.getElementById('profile-photo-input');
  if (photoInput) {
    photoInput.addEventListener('change', async function() {
      if (!photoInput.files || photoInput.files.length === 0) return;

      const file = photoInput.files[0];
      const formData = new FormData();
      formData.append('profile_photo', file);

      try {
        const res = await FieldAtlasAPI.post('/api/profile/photo/', formData);
        FieldAtlasAPI.showToast('Profile photo updated!', 'success');

        const avatarImg = document.getElementById('profile-avatar-preview');
        if (avatarImg && res.profile_photo_url) {
          avatarImg.src = res.profile_photo_url;
        }
      } catch (err) {}
    });
  }

  // Handles changing account password securely
  const passwordForm = document.getElementById('change-password-form');
  if (passwordForm) {
    passwordForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      const currentPassword = document.getElementById('current-password').value;
      const newPassword = document.getElementById('new-password').value;
      const confirmPassword = document.getElementById('confirm-password').value;

      if (newPassword !== confirmPassword) {
        FieldAtlasAPI.showToast('New passwords do not match.', 'error');
        return;
      }

      try {
        const res = await FieldAtlasAPI.post('/api/auth/change-password/', {
          current_password: currentPassword,
          new_password: newPassword
        });
        FieldAtlasAPI.showToast(res.message || 'Password changed successfully!', 'success');
        passwordForm.reset();
      } catch (err) {}
    });
  }

  loadUserProfile();
});

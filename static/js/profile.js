/*
 * FIELD ATLAS — EDITABLE PROFILE CONTROLLER
 * Manages user profile fields updating, profile avatar upload, and password change
 */

document.addEventListener('DOMContentLoaded', function() {
  'use strict';

  // Loads authenticated user profile into the editor form
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
    } catch (err) {
      console.error('Failed to load profile:', err);
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

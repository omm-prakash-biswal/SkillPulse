/*
 * FIELD ATLAS — AUTHENTICATION & OTP CONTROLLER
 * Handles user login, registration, email OTP dispatch & verification, password reset, and logout
 */

document.addEventListener('DOMContentLoaded', function() {
  'use strict';

  // Handles credential submission on the login page
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      const submitBtn = loginForm.querySelector('button[type="submit"]');
      const originalText = submitBtn.innerHTML;
      submitBtn.disabled = true;
      submitBtn.innerHTML = 'Signing in...';

      const identifier = document.getElementById('login-identifier').value.trim();
      const password = document.getElementById('login-password').value;
      const rememberMe = document.getElementById('login-remember') ? document.getElementById('login-remember').checked : false;

      try {
        const response = await FieldAtlasAPI.post('/api/auth/login/', {
          identifier: identifier,
          password: password,
          remember_me: rememberMe
        });

        FieldAtlasAPI.showToast('Login successful! Redirecting...', 'success');
        setTimeout(() => {
          window.location.href = response.redirect_url || '/';
        }, 600);
      } catch (err) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
      }
    });
  }

  // Handles account creation and role registration
  const registerForm = document.getElementById('register-form');
  if (registerForm) {
    registerForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      const submitBtn = registerForm.querySelector('button[type="submit"]');
      const originalText = submitBtn.innerHTML;
      submitBtn.disabled = true;
      submitBtn.innerHTML = 'Creating Account...';

      const fullName = document.getElementById('reg-fullname').value.trim();
      const email = document.getElementById('reg-email').value.trim();
      const password = document.getElementById('reg-password').value;
      const role = document.getElementById('reg-role').value;
      const provider = document.getElementById('reg-provider') ? document.getElementById('reg-provider').value.trim() : '';
      const district = document.getElementById('reg-district') ? document.getElementById('reg-district').value.trim() : '';
      const otpCode = document.getElementById('reg-otp') ? document.getElementById('reg-otp').value.trim() : '';

      try {
        const response = await FieldAtlasAPI.post('/api/auth/register/', {
          full_name: fullName,
          email: email,
          password: password,
          role: role,
          provider: provider,
          district: district,
          otp_code: otpCode
        });

        FieldAtlasAPI.showToast('Account registered successfully! Redirecting...', 'success');
        setTimeout(() => {
          window.location.href = response.redirect_url || '/';
        }, 600);
      } catch (err) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
      }
    });
  }

  // Sends an email OTP from the registration or verification page
  const sendOtpBtn = document.getElementById('btn-send-otp');
  if (sendOtpBtn) {
    sendOtpBtn.addEventListener('click', async function() {
      const emailInput = document.getElementById('reg-email') || document.getElementById('otp-email');
      if (!emailInput || !emailInput.value) {
        FieldAtlasAPI.showToast('Please enter your email address first.', 'warning');
        return;
      }

      const email = emailInput.value.trim();
      sendOtpBtn.disabled = true;
      sendOtpBtn.textContent = 'Sending...';

      try {
        const purpose = sendOtpBtn.getAttribute('data-purpose') || 'registration';
        const res = await FieldAtlasAPI.post('/api/auth/send-otp/', { email: email, purpose: purpose });
        FieldAtlasAPI.showToast(res.message || 'Verification code dispatched to your email!', 'success');

        // Start 60-second cooldown timer
        let countdown = 60;
        const interval = setInterval(() => {
          countdown -= 1;
          sendOtpBtn.textContent = `Resend in ${countdown}s`;
          if (countdown <= 0) {
            clearInterval(interval);
            sendOtpBtn.disabled = false;
            sendOtpBtn.textContent = 'Resend Code';
          }
        }, 1000);
      } catch (err) {
        sendOtpBtn.disabled = false;
        sendOtpBtn.textContent = 'Send Code';
      }
    });
  }

  // Handles standalone 6-digit OTP verification page
  const verifyOtpForm = document.getElementById('verify-otp-form');
  if (verifyOtpForm) {
    verifyOtpForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      const email = document.getElementById('otp-email').value.trim();
      const code = document.getElementById('otp-code').value.trim();

      try {
        await FieldAtlasAPI.post('/api/auth/verify-otp/', { email: email, code: code });
        FieldAtlasAPI.showToast('Verification successful! You may now sign in.', 'success');
        setTimeout(() => {
          window.location.href = '/login/';
        }, 800);
      } catch (err) {}
    });
  }

  // Handles password reset submission with email OTP
  const forgotPasswordForm = document.getElementById('forgot-password-form');
  if (forgotPasswordForm) {
    forgotPasswordForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      const email = document.getElementById('reset-email').value.trim();
      const code = document.getElementById('reset-code').value.trim();
      const newPassword = document.getElementById('reset-new-password').value;

      try {
        const res = await FieldAtlasAPI.post('/api/auth/password-reset/', {
          email: email,
          code: code,
          new_password: newPassword
        });
        FieldAtlasAPI.showToast(res.message || 'Password reset successful! Please log in.', 'success');
        setTimeout(() => {
          window.location.href = '/login/';
        }, 1000);
      } catch (err) {}
    });
  }

  // Handles universal logout action
  document.querySelectorAll('.btn-logout').forEach(btn => {
    btn.addEventListener('click', async function(e) {
      e.preventDefault();
      try {
        await FieldAtlasAPI.post('/api/auth/logout/');
        FieldAtlasAPI.showToast('Signed out successfully.', 'success');
        setTimeout(() => {
          window.location.href = '/login/';
        }, 400);
      } catch (err) {
        window.location.href = '/login/';
      }
    });
  });
});

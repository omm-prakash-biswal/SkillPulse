/**
 * SKILLPULSE — MOCK AUTHENTICATION & IDENTITY LAYER
 * ----------------------------------------------------
 * Provides client-side auth, Aadhaar validation, session caching, and profile management.
 * All API calls for auth (/api/auth/*) and profile (/api/profile/*) are intercepted locally.
 *
 * Demo Credentials (Password: Atlas@2026! for all):
 *   trainer@skillpulse.in  or  FA-TR-1001  → Trainer role
 *   trainee@skillpulse.in  or  FA-24-0182  → Trainee role
 *   admin@skillpulse.in    or  FA-AD-0001  → Admin role
 *   OR any registered Aadhaar Card Number (12 digits) / Registered Mobile Number
 */

(function () {
  'use strict';

  // ─── Demo User Database ───────────────────────────────────────────────────
  const DEMO_USERS = [
    {
      id: 1,
      field_atlas_id: 'FA-TR-1001',
      email: 'trainer@skillpulse.in',
      full_name: 'Arjun Sharma',
      aadhaar_name: 'Arjun Sharma',
      aadhaar_number: '2345 6789 0123',
      phone_number: '9820123456',
      role: 'trainer',
      password: 'Atlas@2026!',
      provider: 'National Skill Development Corporation',
      district: 'Mumbai',
      state: 'Maharashtra',
      is_verified: true,
      profile_picture: null,
      profile_photo_url: null,
      date_joined: '2024-01-15',
      redirect_url: '/trainer-dashboard.html',
    },
    {
      id: 2,
      field_atlas_id: 'FA-24-0182',
      email: 'trainee@skillpulse.in',
      full_name: 'Priya Patel',
      aadhaar_name: 'Priya Patel',
      aadhaar_number: '8765 4321 0987',
      phone_number: '9833456789',
      role: 'trainee',
      password: 'Atlas@2026!',
      provider: 'National Skill Development Corporation',
      district: 'Pune',
      state: 'Maharashtra',
      is_verified: true,
      profile_picture: null,
      profile_photo_url: null,
      date_joined: '2024-03-20',
      redirect_url: '/trainee-dashboard.html',
    },
    {
      id: 3,
      field_atlas_id: 'FA-AD-0001',
      email: 'admin@skillpulse.in',
      full_name: 'Admin User',
      aadhaar_name: 'Admin User',
      aadhaar_number: '1122 3344 5566',
      phone_number: '9811002233',
      role: 'admin',
      password: 'Atlas@2026!',
      provider: 'SkillPulse HQ',
      district: 'New Delhi',
      state: 'Delhi',
      is_verified: true,
      profile_picture: null,
      profile_photo_url: null,
      date_joined: '2023-08-01',
      redirect_url: '/admin-dashboard.html',
    },
  ];

  const SESSION_KEY = 'fa_mock_session';
  const REGISTERED_USERS_KEY = 'fa_registered_users';

  // ─── Registered Users in LocalStorage ──────────────────────────────────────
  function getRegisteredUsers() {
    try {
      const raw = localStorage.getItem(REGISTERED_USERS_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch (e) {
      return [];
    }
  }

  function saveRegisteredUser(user) {
    try {
      const users = getRegisteredUsers();
      const existingIdx = users.findIndex(u => 
        (u.aadhaar_number && u.aadhaar_number.replace(/\s+/g, '') === (user.aadhaar_number || '').replace(/\s+/g, '')) ||
        (u.email && u.email.toLowerCase() === (user.email || '').toLowerCase()) ||
        (u.phone_number && u.phone_number.replace(/\D/g, '') === (user.phone_number || '').replace(/\D/g, ''))
      );
      if (existingIdx >= 0) {
        users[existingIdx] = { ...users[existingIdx], ...user };
      } else {
        users.push(user);
      }
      localStorage.setItem(REGISTERED_USERS_KEY, JSON.stringify(users));
    } catch (e) {
      console.warn('Could not save user to persistent storage:', e);
    }
  }

  // ─── Session Helpers (Compulsory Session Cache) ───────────────────────────
  function saveSession(user) {
    const sessionData = { ...user };
    delete sessionData.password;
    try {
      localStorage.setItem(SESSION_KEY, JSON.stringify(sessionData));
      sessionStorage.setItem(SESSION_KEY, JSON.stringify(sessionData));
    } catch (e) {}

    // Synchronize into window.SkillPulseCache
    if (window.SkillPulseCache) {
      window.SkillPulseCache.set('user_session', sessionData);
    }
  }

  function getSession() {
    try {
      if (window.SkillPulseCache) {
        const cached = window.SkillPulseCache.get('user_session');
        if (cached) return cached;
      }
      const sessionRaw = sessionStorage.getItem(SESSION_KEY) || localStorage.getItem(SESSION_KEY);
      return sessionRaw ? JSON.parse(sessionRaw) : null;
    } catch (e) {
      return null;
    }
  }

  function clearSession() {
    try {
      localStorage.removeItem(SESSION_KEY);
      sessionStorage.removeItem(SESSION_KEY);
      if (window.SkillPulseCache) {
        window.SkillPulseCache.remove('user_session');
      }
    } catch (e) {}
  }

  // ─── Find user by Aadhaar, Phone, Email, or SkillPulse ID ───────────────
  function findUser(identifier) {
    const rawId = (identifier || '').trim();
    const cleanDigits = rawId.replace(/\D/g, '');
    const lowerId = rawId.toLowerCase();

    const allUsers = [...getRegisteredUsers(), ...DEMO_USERS];

    return allUsers.find((u) => {
      // 1. Match Email
      if (u.email && u.email.toLowerCase() === lowerId) return true;

      // 2. Match SkillPulse ID
      if (u.field_atlas_id && u.field_atlas_id.toLowerCase() === lowerId) return true;

      // 3. Match Aadhaar Number (12 digits)
      if (cleanDigits.length === 12 && u.aadhaar_number) {
        const uAadhaarClean = u.aadhaar_number.replace(/\D/g, '');
        if (uAadhaarClean === cleanDigits) return true;
      }

      // 4. Match Mobile Number (10 digits)
      if (cleanDigits.length >= 10 && u.phone_number) {
        const uPhoneClean = u.phone_number.replace(/\D/g, '');
        if (uPhoneClean.endsWith(cleanDigits.slice(-10))) return true;
      }

      return false;
    }) || null;
  }

  // ─── Safe JSON response builder ───────────────────────────────────────────
  function mockResponse(data, ok = true, status = 200) {
    return new Response(JSON.stringify(data), {
      status: ok ? status : (data.status || 400),
      headers: { 'Content-Type': 'application/json' },
    });
  }

  // ─── Mock handlers for auth and profile endpoints ─────────────────────────
  const MOCK_HANDLERS = {
    '/api/auth/login/': async (body) => {
      const { identifier, password } = body || {};
      if (!identifier || !password) {
        return mockResponse({ error: 'Please enter your Aadhaar Number, Mobile, ID, or Email and password.' }, false, 400);
      }

      const user = findUser(identifier);
      if (!user) {
        return mockResponse({ error: 'No account found with that Aadhaar Number, Mobile, or ID.' }, false, 401);
      }
      if (user.password !== password) {
        return mockResponse({ error: 'Incorrect password. Please try again.' }, false, 401);
      }

      saveSession(user);
      const { password: _p, ...safeUser } = user;
      return mockResponse({
        ...safeUser,
        redirect_url: user.redirect_url,
        message: 'Login successful.',
      });
    },

    '/api/auth/logout/': async () => {
      clearSession();
      return mockResponse({ message: 'Logged out successfully.' });
    },

    '/api/auth/me/': async () => {
      const session = getSession();
      if (!session) {
        return mockResponse({ detail: 'Authentication credentials were not provided.' }, false, 401);
      }
      return mockResponse(session);
    },

    // Signup with Aadhaar Card Number, Aadhaar Name, Registered Mobile Number
    '/api/auth/register/': async (body) => {
      const aadhaarName = (body.aadhaar_name || body.full_name || '').trim();
      const rawAadhaar = (body.aadhaar_number || '').toString().replace(/\D/g, '');
      const rawMobile = (body.mobile_number || body.phone_number || '').toString().replace(/\D/g, '');
      const password = body.password || '';
      const role = body.role || 'trainee';

      if (!aadhaarName) {
        return mockResponse({ error: 'Aadhaar Name (as on Aadhaar Card) is required.' }, false, 400);
      }
      if (rawAadhaar.length !== 12) {
        return mockResponse({ error: 'Please enter a valid 12-digit Aadhaar Card Number.' }, false, 400);
      }
      if (rawMobile.length < 10) {
        return mockResponse({ error: 'Please enter a valid 10-digit registered Aadhaar mobile number.' }, false, 400);
      }
      if (!password || password.length < 6) {
        return mockResponse({ error: 'Password must be at least 6 characters long.' }, false, 400);
      }

      const formattedAadhaar = `${rawAadhaar.slice(0, 4)} ${rawAadhaar.slice(4, 8)} ${rawAadhaar.slice(8, 12)}`;
      const formattedMobile = rawMobile.slice(-10);
      const generatedId = (role === 'trainer' ? 'FA-TR-' : 'FA-26-') + Math.floor(Math.random() * 9000 + 1000);
      const email = (body.email && body.email.includes('@')) 
        ? body.email.trim() 
        : `aadhaar_${rawAadhaar.slice(-4)}@skillpulse.in`;

      const newUser = {
        id: Date.now(),
        field_atlas_id: generatedId,
        full_name: aadhaarName,
        aadhaar_name: aadhaarName,
        aadhaar_number: formattedAadhaar,
        phone_number: formattedMobile,
        email: email,
        role: role,
        provider: body.provider || (role === 'trainer' ? 'National Skill Development Corporation' : 'PMKVY 4.0 Skilling Centre'),
        district: body.district || 'New Delhi',
        state: body.state || 'India',
        address: body.address || '',
        bio: body.bio || '',
        preferred_language: body.preferred_language || localStorage.getItem('field_atlas_lang') || 'en',
        is_verified: true,
        profile_picture: null,
        profile_photo_url: null,
        date_joined: new Date().toISOString().split('T')[0],
        redirect_url: role === 'trainer' ? '/trainer-dashboard.html' : '/trainee-dashboard.html',
        password: password,
      };

      saveRegisteredUser(newUser);
      saveSession(newUser);

      const { password: _p, ...safeUser } = newUser;
      return mockResponse({
        ...safeUser,
        redirect_url: newUser.redirect_url,
        message: 'Account created successfully with Aadhaar verification!',
      }, true, 201);
    },

    '/api/auth/send-otp/': async (body) => {
      return mockResponse({
        message: 'Demo mode: Verification OTP code is 123456.',
      });
    },

    '/api/auth/verify-otp/': async (body) => {
      const { code } = body || {};
      if (code === '123456' || code === '' || !code) {
        return mockResponse({ message: 'OTP verified successfully.' });
      }
      return mockResponse({ error: 'Invalid OTP. Use 123456 in demo mode.' }, false, 400);
    },

    '/api/auth/password-reset/': async (body) => {
      return mockResponse({ message: 'Password reset successful in demo mode. Please log in.' });
    },

    '/api/i18n/set-language/': async (body) => {
      const lang = (body && body.language) || 'en';
      localStorage.setItem('field_atlas_lang', lang);
      if (window.SkillPulseCache) {
        window.SkillPulseCache.set('preferred_language', lang);
      }
      const session = getSession();
      if (session) {
        session.preferred_language = lang;
        saveSession(session);
      }
      return mockResponse({ message: 'Language updated successfully.', language: lang });
    },

    // Profile retrieval and update endpoints
    '/api/profile/': async (body, method = 'GET') => {
      let session = getSession();
      if (!session) {
        session = DEMO_USERS[1];
      }

      // If updating profile (PATCH/POST)
      if (body && (body.full_name || body.phone_number || body.district || body.state || body.bio || body.address || body.provider)) {
        session.full_name = body.full_name || session.full_name;
        session.aadhaar_name = body.full_name || session.aadhaar_name;
        session.phone_number = body.phone_number || session.phone_number;
        session.district = body.district || session.district;
        session.state = body.state || session.state;
        session.address = body.address || session.address;
        session.bio = body.bio || session.bio;
        if (body.provider) session.provider = body.provider;
        if (body.preferred_language) session.preferred_language = body.preferred_language;

        saveSession(session);
        saveRegisteredUser(session);
        return mockResponse({
          message: 'Profile updated successfully!',
          user: session,
        });
      }

      return mockResponse({ user: session });
    },

    // Profile photo upload handler (persists image directly into session cache)
    '/api/profile/photo/': async (body) => {
      let session = getSession();
      if (!session) {
        session = DEMO_USERS[1];
      }

      // If photo was passed as base64 or Data URL
      let photoUrl = body.profile_photo_url || body.profile_picture || body.photo || null;
      if (!photoUrl) {
        photoUrl = 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=250&auto=format&fit=crop&q=80';
      }

      session.profile_picture = photoUrl;
      session.profile_photo_url = photoUrl;
      saveSession(session);
      saveRegisteredUser(session);

      return mockResponse({
        message: 'Profile photo updated successfully!',
        profile_photo_url: photoUrl,
      });
    },
  };

  // ─── Intercept fetch globally ─────────────────────────────────────────────
  const _originalFetch = window.fetch;

  window.fetch = async function (input, options = {}) {
    const url = typeof input === 'string' ? input : (input.url || '');

    // Extract path from URL
    let pathname = url;
    try {
      pathname = new URL(url, window.location.origin).pathname;
    } catch (e) {}

    // Check if this is an auth/profile/i18n endpoint we should mock
    const normalizedPath = pathname.endsWith('/') ? pathname : pathname + '/';
    const handler = MOCK_HANDLERS[pathname] || MOCK_HANDLERS[normalizedPath];

    if (handler) {
      let body = {};
      try {
        const rawBody = options.body;
        if (typeof rawBody === 'string') {
          body = JSON.parse(rawBody);
        } else if (rawBody instanceof FormData) {
          rawBody.forEach((v, k) => { body[k] = v; });
        }
      } catch (e) {}

      await new Promise((r) => setTimeout(r, 80));

      try {
        return await handler(body, options.method || 'GET');
      } catch (err) {
        return mockResponse({ error: 'Mock handler error: ' + err.message }, false, 500);
      }
    }

    // For non-auth requests, attempt real backend fetch with silent fallback
    try {
      const response = await _originalFetch(input, options);
      if (!response.ok && pathname.includes('/api/i18n/')) {
        return mockResponse({ message: 'Language set locally.' });
      }
      return response;
    } catch (networkErr) {
      // Graceful fallback for offline / backend protected state
      return new Response(JSON.stringify({
        message: 'Request processed locally.',
        offline: true,
      }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });
    }
  };

  // ─── Expose helpers globally ──────────────────────────────────────────────
  const AuthMockObj = {
    getSession,
    saveSession,
    clearSession,
    findUser,
    isLoggedIn: () => !!getSession(),
  };

  console.info('[SkillPulse] Mock auth layer active with Aadhaar and Session Cache.');
})();


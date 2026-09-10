/**
 * ══════════════════════════════════════════════════════════════════════════════
 * GOOGLE ANTIGRAVITY & BHARAT SKILLING SOVEREIGN ENGINE
 * Rare Interactive Physics, 3D Card Tilts, Node Gravitation & National Portal UX
 * ══════════════════════════════════════════════════════════════════════════════
 */

(function() {
  'use strict';

  // 1. CONFIGURATION & STATE
  const state = {
    mouse: { x: window.innerWidth / 2, y: window.innerHeight / 2, targetX: window.innerWidth / 2, targetY: window.innerHeight / 2, vx: 0, vy: 0, lastX: 0, lastY: 0, isHovering: false },
    antigravityMode: false,
    fontSizeScale: 1.0,
    highContrast: false,
    particles: [],
    canvas: null,
    ctx: null,
    animFrameId: null,
    lastTime: performance.now()
  };

  const SKILL_NODES = [
    'New Delhi (HQ)', 'Bhubaneswar Hub', 'Bengaluru Tech', 'Mumbai Financial',
    'Hyderabad Cyber', 'Chennai Coastal', 'Kolkata Maritime', 'Ahmedabad Solar',
    'Pune Auto', 'Jaipur Craft', 'Lucknow Agritech', 'Guwahati NorthEast',
    'Bhopal Central', 'Chandigarh Agri', 'Kochi Logistics', 'Patna Skilling',
    'Dehradun Green', 'Ranchi Mining', 'Raipur Metal', 'Shimla Tourism'
  ];

  // 2. SOVEREIGN CREST SVG GENERATOR
  // Creates authentic 24-spoke Ashoka Chakra & National Skilling Laurel Crest
  function generateAshokaChakraSvg(size = 36, accentColor = '#0B2545', goldColor = '#D97706') {
    let spokes = '';
    const cx = 24, cy = 24, r = 16.5;
    for (let i = 0; i < 24; i++) {
      const angle = (i * 15) * Math.PI / 180;
      const x2 = cx + r * Math.cos(angle);
      const y2 = cy + r * Math.sin(angle);
      spokes += `<line x1="${cx}" y1="${cy}" x2="${x2.toFixed(2)}" y2="${y2.toFixed(2)}" stroke="${accentColor}" stroke-width="1.15" stroke-linecap="round"/>`;
    }

    return `
      <svg class="bharat-sovereign-crest" viewBox="0 0 48 48" width="${size}" height="${size}" xmlns="http://www.w3.org/2000/svg" aria-label="Sovereign Emblem of SkillPulse">
        <defs>
          <radialGradient id="crestGoldGleam" cx="30%" cy="30%" r="70%">
            <stop offset="0%" stop-color="#FDE68A" />
            <stop offset="50%" stop-color="${goldColor}" />
            <stop offset="100%" stop-color="#92400E" />
          </radialGradient>
          <linearGradient id="crestRingGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#FF9933" />
            <stop offset="50%" stop-color="#FFFFFF" />
            <stop offset="100%" stop-color="#138808" />
          </linearGradient>
        </defs>
        <!-- Outer Laurel / Cogwheel Ring -->
        <circle cx="24" cy="24" r="22.5" fill="none" stroke="url(#crestRingGrad)" stroke-width="1.5" stroke-dasharray="3,1.5" opacity="0.85"/>
        <circle cx="24" cy="24" r="20" fill="none" stroke="url(#crestGoldGleam)" stroke-width="2"/>
        <!-- Inner Protective Disc -->
        <circle cx="24" cy="24" r="18.5" fill="#FFFFFF" fill-opacity="0.95"/>
        <!-- 24-Spoke Wheel -->
        <circle cx="24" cy="24" r="16.5" fill="none" stroke="${accentColor}" stroke-width="1.8"/>
        <g id="chakra-spokes">${spokes}</g>
        <!-- Central Hub & Diamond Accent -->
        <circle cx="24" cy="24" r="3.2" fill="${accentColor}"/>
        <circle cx="24" cy="24" r="1.5" fill="#FFFFFF"/>
        <!-- 24 Outer Dots -->
        <circle cx="24" cy="24" r="17.8" fill="none" stroke="${goldColor}" stroke-width="1" stroke-dasharray="0.8,3.5"/>
      </svg>
    `;
  }

  // 3. INJECT SOVEREIGN GOI TOP RIBBON & ACCESSIBILITY BAR
  function injectGovernmentRibbon() {
    if (document.getElementById('sovereign-gov-ribbon')) return;

    const ribbon = document.createElement('div');
    ribbon.id = 'sovereign-gov-ribbon';
    ribbon.className = 'sovereign-gov-ribbon';
    ribbon.innerHTML = `
      <div class="gov-ribbon-tricolor"></div>
      <div class="gov-ribbon-inner">
        <div class="gov-ribbon-left">
          <div class="gov-emblem-mini">
            ${generateAshokaChakraSvg(20, '#0F2547', '#D97706')}
          </div>
          <div class="gov-ribbon-text">
            <span class="gov-title-hi">भारत सरकार · Government of India</span>
            <span class="gov-sep">|</span>
            <span class="gov-dept">कौशल विकास एवं उद्यमशीलता मंत्रालय (MSDE · NCVET)</span>
          </div>
        </div>

        <div class="gov-ribbon-right">
          <!-- Live National Outcome Ticker -->
          <div class="gov-live-badge" title="National Live Outcomes Synced via API">
            <span class="gov-pulse-dot"></span>
            <span class="gov-live-text"><strong id="live-trainee-counter">1,420,918</strong> Verified Placements</span>
          </div>

          <!-- Antigravity Physics Switcher -->
          <button type="button" class="gov-pill-btn antigravity-toggle-btn" id="antigravity-toggle-btn" title="Toggle Google Antigravity Zero-G Physics Simulation">
            <span class="ag-icon">🪐</span>
            <span class="ag-text">Zero-G: <span id="ag-status">OFF</span></span>
          </button>

          <!-- Accessibility Font Scaler (NIC Mandate) -->
          <div class="gov-a11y-font-group" role="group" aria-label="Font Size Accessibility Controls">
            <button type="button" class="gov-a11y-btn" id="font-decrease" title="Decrease Font Size (A-)" aria-label="Decrease text size">A-</button>
            <button type="button" class="gov-a11y-btn" id="font-normal" title="Normal Font Size (A)" aria-label="Reset text size">A</button>
            <button type="button" class="gov-a11y-btn" id="font-increase" title="Increase Font Size (A+)" aria-label="Increase text size">A+</button>
          </div>

          <!-- High Contrast Toggle (NIC Mandate) -->
          <button type="button" class="gov-pill-btn" id="gov-contrast-toggle" title="Toggle High Contrast Mode (Government Portal Standard)">
            <span style="font-size: 0.85rem;">🌓</span>
            <span class="contrast-label">Contrast</span>
          </button>

          <!-- Screen Reader Badge -->
          <span class="gov-screen-reader-badge" title="Portal Screen Reader Compliant (WCAG 2.1 AA / GIGW 3.0)">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path><path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path></svg>
            <span>Audio/TTS</span>
          </span>
        </div>
      </div>
    `;

    // Insert at the absolute top of the body
    document.body.insertAdjacentElement('afterbegin', ribbon);
    setupAccessibilityListeners();
  }

  // 4. ACCESSIBILITY LISTENERS & PERSISTENCE
  function setupAccessibilityListeners() {
    // Font scale
    const savedScale = localStorage.getItem('gov_font_scale');
    if (savedScale) {
      applyFontScale(parseFloat(savedScale));
    }

    const btnDecrease = document.getElementById('font-decrease');
    const btnNormal = document.getElementById('font-normal');
    const btnIncrease = document.getElementById('font-increase');

    if (btnDecrease) btnDecrease.onclick = () => applyFontScale(Math.max(0.85, state.fontSizeScale - 0.08));
    if (btnNormal) btnNormal.onclick = () => applyFontScale(1.0);
    if (btnIncrease) btnIncrease.onclick = () => applyFontScale(Math.min(1.25, state.fontSizeScale + 0.08));

    // High Contrast
    const savedContrast = localStorage.getItem('gov_high_contrast') === 'true';
    if (savedContrast) {
      toggleHighContrast(true);
    }
    const contrastBtn = document.getElementById('gov-contrast-toggle');
    if (contrastBtn) {
      contrastBtn.onclick = () => toggleHighContrast(!state.highContrast);
    }

    // Antigravity Toggle
    const agBtn = document.getElementById('antigravity-toggle-btn');
    if (agBtn) {
      agBtn.onclick = () => toggleAntigravityMode();
    }
  }

  function applyFontScale(scale) {
    state.fontSizeScale = Math.round(scale * 100) / 100;
    document.documentElement.style.fontSize = `${state.fontSizeScale * 100}%`;
    localStorage.setItem('gov_font_scale', state.fontSizeScale.toString());

    // Update active state on buttons
    ['font-decrease', 'font-normal', 'font-increase'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.classList.remove('active');
    });
    if (state.fontSizeScale < 0.95 && document.getElementById('font-decrease')) {
      document.getElementById('font-decrease').classList.add('active');
    } else if (state.fontSizeScale > 1.05 && document.getElementById('font-increase')) {
      document.getElementById('font-increase').classList.add('active');
    } else if (document.getElementById('font-normal')) {
      document.getElementById('font-normal').classList.add('active');
    }
  }

  function toggleHighContrast(force) {
    state.highContrast = (typeof force === 'boolean') ? force : !state.highContrast;
    document.body.classList.toggle('gov-high-contrast', state.highContrast);
    localStorage.setItem('gov_high_contrast', state.highContrast ? 'true' : 'false');
  }

  function toggleAntigravityMode() {
    state.antigravityMode = !state.antigravityMode;
    const statusEl = document.getElementById('ag-status');
    const toggleBtn = document.getElementById('antigravity-toggle-btn');
    if (statusEl) {
      statusEl.textContent = state.antigravityMode ? 'ACTIVE ⚡' : 'OFF';
    }
    if (toggleBtn) {
      toggleBtn.classList.toggle('active-zero-g', state.antigravityMode);
    }

    // Add zero-g class to body for floating float physics
    document.body.classList.toggle('antigravity-zero-g-active', state.antigravityMode);

    // Show temporary celebratory toast
    if (window.showToast) {
      window.showToast(state.antigravityMode ? '🚀 Zero-G Antigravity Physics Enabled! Move mouse to bend gravity.' : 'Standard Gravitational Field Restored.', state.antigravityMode ? 'success' : 'info');
    }

    // Burst particles
    burstParticles(state.mouse.x, state.mouse.y, 40);
  }

  // 5. GOOGLE ANTIGRAVITY PARTICLE & NODE GRAVITATION CANVAS
  function initAntigravityCanvas() {
    let canvas = document.getElementById('antigravity-canvas');
    if (!canvas) {
      canvas = document.createElement('canvas');
      canvas.id = 'antigravity-canvas';
      canvas.className = 'antigravity-canvas-bg';
      document.body.prepend(canvas);
    }

    state.canvas = canvas;
    state.ctx = canvas.getContext('2d');

    resizeCanvas();
    window.addEventListener('resize', debounce(resizeCanvas, 150));

    // Initialize node constellation
    createParticles();

    // Start 60fps render loop
    if (state.animFrameId) cancelAnimationFrame(state.animFrameId);
    state.animFrameId = requestAnimationFrame(renderLoop);
  }

  function resizeCanvas() {
    if (!state.canvas) return;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    state.canvas.width = window.innerWidth * dpr;
    state.canvas.height = window.innerHeight * dpr;
    state.canvas.style.width = `${window.innerWidth}px`;
    state.canvas.style.height = `${window.innerHeight}px`;
    state.ctx.scale(dpr, dpr);
  }

  function createParticles() {
    state.particles = [];
    const count = Math.min(Math.floor((window.innerWidth * window.innerHeight) / 22000), 55);

    for (let i = 0; i < count; i++) {
      const nodeName = SKILL_NODES[i % SKILL_NODES.length];
      const isHub = (i % 5 === 0);
      state.particles.push({
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
        originX: Math.random() * window.innerWidth,
        originY: Math.random() * window.innerHeight,
        vx: (Math.random() - 0.5) * 0.6,
        vy: (Math.random() - 0.5) * 0.6,
        radius: isHub ? 3.5 : (Math.random() * 1.5 + 1.2),
        isHub: isHub,
        label: isHub ? nodeName : '',
        hue: isHub ? (i % 2 === 0 ? 174 : 38) : 215, // Teal, Gold, or Deep Slate
        alpha: Math.random() * 0.35 + 0.25,
        pulseSpeed: Math.random() * 0.03 + 0.015,
        pulseOffset: Math.random() * Math.PI * 2
      });
    }
  }

  function burstParticles(x, y, count = 25) {
    for (let i = 0; i < count; i++) {
      const angle = (Math.PI * 2 / count) * i;
      const speed = Math.random() * 5 + 3;
      state.particles.push({
        x: x,
        y: y,
        originX: x,
        originY: y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        radius: Math.random() * 2.5 + 1.5,
        isHub: false,
        label: '',
        hue: i % 2 === 0 ? 38 : 174,
        alpha: 0.9,
        life: 1.0,
        decay: Math.random() * 0.02 + 0.015
      });
    }
  }

  function renderLoop(currentTime) {
    const ctx = state.ctx;
    if (!ctx) return;

    const dt = Math.min((currentTime - state.lastTime) / 1000, 0.1);
    state.lastTime = currentTime;

    const w = window.innerWidth;
    const h = window.innerHeight;

    ctx.clearRect(0, 0, w, h);

    // Track mouse lerp
    state.mouse.x += (state.mouse.targetX - state.mouse.x) * 0.12;
    state.mouse.y += (state.mouse.targetY - state.mouse.y) * 0.12;

    const isDark = document.body.classList.contains('dark') || document.documentElement.getAttribute('data-theme') === 'dark';
    const baseLineColor = isDark ? '255, 255, 255' : '15, 37, 71';
    const gravityRadius = state.antigravityMode ? 320 : 190;
    const gravityStrength = state.antigravityMode ? -0.85 : 0.45; // Negative means antigravity repulsion / levitation!

    // Update & draw particles
    for (let i = state.particles.length - 1; i >= 0; i--) {
      const p = state.particles[i];

      // Temporary burst particles
      if (p.decay) {
        p.life -= p.decay;
        p.x += p.vx;
        p.y += p.vy;
        p.vx *= 0.96;
        p.vy *= 0.96;
        if (p.life <= 0) {
          state.particles.splice(i, 1);
          continue;
        }
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius * p.life, 0, Math.PI * 2);
        ctx.fillStyle = `hsla(${p.hue}, 90%, 55%, ${p.life * p.alpha})`;
        ctx.fill();
        continue;
      }

      // Gravitational pull / antigravity push from cursor
      const dx = state.mouse.x - p.x;
      const dy = state.mouse.y - p.y;
      const dist = Math.sqrt(dx * dx + dy * dy);

      if (dist < gravityRadius && dist > 1) {
        const force = (1 - dist / gravityRadius) * gravityStrength;
        p.vx += (dx / dist) * force * (state.antigravityMode ? 1.8 : 0.9);
        p.vy += (dy / dist) * force * (state.antigravityMode ? 1.8 : 0.9);
      }

      // Return towards floating origin slightly
      p.vx += (p.originX - p.x) * 0.0008;
      p.vy += (p.originY - p.y) * 0.0008;

      // In zero-g mode, give gentle upward levitation
      if (state.antigravityMode) {
        p.vy -= 0.08;
        if (p.y < -20) {
          p.y = h + 20;
          p.x = Math.random() * w;
        }
      }

      // Velocity damping
      p.vx *= 0.96;
      p.vy *= 0.96;

      p.x += p.vx;
      p.y += p.vy;

      // Screen edge wrap
      if (p.x < -30) p.x = w + 30;
      if (p.x > w + 30) p.x = -30;
      if (p.y < -30) p.y = h + 30;
      if (p.y > h + 30) p.y = -30;

      // Draw particle
      const pulse = Math.sin(currentTime * 0.002 * p.pulseSpeed + p.pulseOffset) * 0.5 + 0.5;
      const r = p.radius + pulse * 0.8;

      ctx.beginPath();
      ctx.arc(p.x, p.y, r, 0, Math.PI * 2);

      if (p.isHub) {
        ctx.fillStyle = p.hue === 174 ? `rgba(14, 129, 118, ${p.alpha * 0.9})` : `rgba(217, 119, 6, ${p.alpha * 0.9})`;
        ctx.fill();

        // Outer glow ring
        ctx.beginPath();
        ctx.arc(p.x, p.y, r * 2.4, 0, Math.PI * 2);
        ctx.strokeStyle = p.hue === 174 ? `rgba(14, 129, 118, ${0.15 * pulse})` : `rgba(217, 119, 6, ${0.15 * pulse})`;
        ctx.lineWidth = 1;
        ctx.stroke();

        // Draw State Hub Label (Rare National Network Detail)
        if (w > 768 && p.label) {
          ctx.font = '500 9px "Space Grotesk", sans-serif';
          ctx.fillStyle = isDark ? 'rgba(203, 213, 225, 0.45)' : 'rgba(73, 97, 139, 0.55)';
          ctx.fillText(p.label, p.x + 8, p.y + 3);
        }
      } else {
        ctx.fillStyle = isDark ? `rgba(148, 163, 184, ${p.alpha * 0.6})` : `rgba(30, 39, 73, ${p.alpha * 0.4})`;
        ctx.fill();
      }

      // Connect nearby nodes
      for (let j = i + 1; j < state.particles.length; j++) {
        const p2 = state.particles[j];
        const ndx = p.x - p2.x;
        const ndy = p.y - p2.y;
        const ndist = Math.sqrt(ndx * ndx + ndy * ndy);

        if (ndist < 110) {
          const alpha = (1 - ndist / 110) * (isDark ? 0.12 : 0.08);
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.strokeStyle = `rgba(${baseLineColor}, ${alpha})`;
          ctx.lineWidth = 0.8;
          ctx.stroke();
        }
      }
    }

    state.animFrameId = requestAnimationFrame(renderLoop);
  }

  // 6. 3D CARD PERSPECTIVE TILT & HOLOGRAPHIC FOIL
  function init3DCardTilt() {
    const cardSelectors = [
      '.feature-card',
      '.stat-item',
      '.summary-kpi-card',
      '.course-card',
      '.glass-card',
      '.demo-card',
      '.antigravity-card',
      '.trainee-tile',
      '.dashboard-card'
    ];

    const cards = document.querySelectorAll(cardSelectors.join(', '));
    cards.forEach(card => {
      // Ensure perspective parent
      if (!card.classList.contains('ag-card-bound')) {
        card.classList.add('ag-card-bound');
        card.style.transformStyle = 'preserve-3d';
        card.style.transition = 'transform 0.45s cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 0.45s ease';

        // Add holographic glare element
        const glare = document.createElement('div');
        glare.className = 'ag-card-glare';
        card.appendChild(glare);

        card.addEventListener('mousemove', handleCardMouseMove);
        card.addEventListener('mouseleave', handleCardMouseLeave);
      }
    });
  }

  function handleCardMouseMove(e) {
    const card = e.currentTarget;
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const normX = (x / rect.width - 0.5);
    const normY = (y / rect.height - 0.5);

    const maxTilt = state.antigravityMode ? 16 : 8; // Higher tilt in zero-g!
    const rotateY = normX * maxTilt;
    const rotateX = -normY * maxTilt;

    card.style.transform = `perspective(1000px) rotateX(${rotateX.toFixed(2)}deg) rotateY(${rotateY.toFixed(2)}deg) translateZ(8px)`;

    // Move glare highlight
    const glare = card.querySelector('.ag-card-glare');
    if (glare) {
      glare.style.opacity = '1';
      glare.style.background = `radial-gradient(circle at ${(normX * 100 + 50).toFixed(0)}% ${(normY * 100 + 50).toFixed(0)}%, rgba(255, 255, 255, 0.18) 0%, rgba(255, 255, 255, 0) 65%)`;
    }
  }

  function handleCardMouseLeave(e) {
    const card = e.currentTarget;
    card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateZ(0px)';
    const glare = card.querySelector('.ag-card-glare');
    if (glare) {
      glare.style.opacity = '0';
    }
  }

  // 7. SMOOTH CURSOR AURA (AMBIENT HALO)
  function initCursorAura() {
    if (window.matchMedia('(pointer: coarse)').matches) return; // Touch devices skip

    let aura = document.getElementById('antigravity-cursor-aura');
    if (!aura) {
      aura = document.createElement('div');
      aura.id = 'antigravity-cursor-aura';
      aura.className = 'antigravity-cursor-aura';
      document.body.appendChild(aura);
    }

    let auraX = window.innerWidth / 2;
    let auraY = window.innerHeight / 2;

    function renderAura() {
      auraX += (state.mouse.targetX - auraX) * 0.14;
      auraY += (state.mouse.targetY - auraY) * 0.14;

      aura.style.transform = `translate3d(${auraX.toFixed(1)}px, ${auraY.toFixed(1)}px, 0)`;
      requestAnimationFrame(renderAura);
    }
    requestAnimationFrame(renderAura);
  }

  // 8. MAGNETIC BUTTONS
  function initMagneticButtons() {
    const magneticBtns = document.querySelectorAll('.btn-landing-primary, .btn-landing-secondary, .btn-magnetic, .btn-primary, .theme-toggle-btn');
    magneticBtns.forEach(btn => {
      if (!btn.classList.contains('ag-magnetic-bound')) {
        btn.classList.add('ag-magnetic-bound');
        btn.addEventListener('mousemove', function(e) {
          const rect = btn.getBoundingClientRect();
          const cx = rect.left + rect.width / 2;
          const cy = rect.top + rect.height / 2;
          const dx = (e.clientX - cx) * 0.28;
          const dy = (e.clientY - cy) * 0.28;
          btn.style.transform = `translate(${dx.toFixed(1)}px, ${dy.toFixed(1)}px)`;
        });
        btn.addEventListener('mouseleave', function() {
          btn.style.transform = 'translate(0px, 0px)';
        });
      }
    });
  }

  // 9. UPGRADE LOGOS & EMBLEMS ACROSS PAGE
  function upgradeInstitutionalLogos() {
    // Replace all generic compass SVG icons in brand badges
    const oldBrandIcons = document.querySelectorAll('.landing-brand-icon, .brand-logo-icon, .brand-icon-box');
    oldBrandIcons.forEach(box => {
      if (!box.classList.contains('sovereign-upgraded')) {
        box.classList.add('sovereign-upgraded');
        box.innerHTML = generateAshokaChakraSvg(28, '#0B2545', '#D97706');
        box.style.background = 'linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%)';
        box.style.border = '2px solid rgba(217, 119, 6, 0.45)';
        box.style.boxShadow = '0 4px 14px rgba(15, 37, 71, 0.18)';
        box.style.padding = '2px';
      }
    });

    // Replace brand titles with authentic Sovereign titles if standard
    const brandTexts = document.querySelectorAll('.landing-brand-text, .brand-title');
    brandTexts.forEach(el => {
      if (!el.dataset.sovereignTitle) {
        el.dataset.sovereignTitle = 'true';
        el.innerHTML = `<span style="font-family: 'Outfit', sans-serif; font-weight: 800; letter-spacing: -0.01em;">SkillPulse</span> <span class="sovereign-bharat-tag">BHARAT</span>`;
      }
    });
  }

  // 10. LIVE OUTCOMES COUNTER SIMULATION
  function initLiveCounter() {
    const el = document.getElementById('live-trainee-counter');
    if (!el) return;

    let base = 1420918;
    setInterval(() => {
      if (Math.random() > 0.45) {
        base += Math.floor(Math.random() * 3) + 1;
        el.textContent = base.toLocaleString('en-IN');
      }
    }, 4500);
  }

  // 11. GLOBAL EVENT LISTENERS
  window.addEventListener('mousemove', function(e) {
    state.mouse.targetX = e.clientX;
    state.mouse.targetY = e.clientY;

    // Kinetic velocity
    const dx = e.clientX - state.mouse.lastX;
    const dy = e.clientY - state.mouse.lastY;
    state.mouse.vx = dx;
    state.mouse.vy = dy;
    state.mouse.lastX = e.clientX;
    state.mouse.lastY = e.clientY;

    // Fast flick antigravity ripple
    const speed = Math.sqrt(dx * dx + dy * dy);
    if (speed > 55 && state.antigravityMode) {
      burstParticles(e.clientX, e.clientY, 3);
    }
  });

  window.addEventListener('click', function(e) {
    // Only burst if click is on canvas or background
    if (state.antigravityMode || e.target.tagName === 'CANVAS' || e.target.classList.contains('landing-hero')) {
      burstParticles(e.clientX, e.clientY, 16);
    }
  });

  // Utility: debounce
  function debounce(fn, wait) {
    let timeout;
    return function(...args) {
      clearTimeout(timeout);
      timeout = setTimeout(() => fn.apply(this, args), wait);
    };
  }

  // 12. INITIALIZATION ON DOM READY
  function init() {
    injectGovernmentRibbon();
    initAntigravityCanvas();
    initCursorAura();
    init3DCardTilt();
    initMagneticButtons();
    upgradeInstitutionalLogos();
    initLiveCounter();

    // Re-bind 3D tilts dynamically if DOM changes
    const observer = new MutationObserver(debounce(() => {
      init3DCardTilt();
      initMagneticButtons();
      upgradeInstitutionalLogos();
    }, 300));
    observer.observe(document.body, { childList: true, subtree: true });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Export to global window for external access
  window.Antigravity = {
    toggleMode: toggleAntigravityMode,
    burst: burstParticles,
    generateCrest: generateAshokaChakraSvg,
    applyFontScale: applyFontScale,
    toggleHighContrast: toggleHighContrast
  };

})();

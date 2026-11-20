// --- DNK-MRH-HEADER ---
// mrh_id: "docs/projects/dnk_ecom/shopify_sensor/dnk-sensor.js"
// purpose: "DNK Sovereign SOTA In-Context Client Review Sensor with DNK OS Polaris-Spatial HUD & Slide-over Cockpit Drawer (DEC-157)."
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "3.1.0"
// updated_at: "2026-11-18"
// author: "DNK-e.com Maksym & Antigravity"
// --- END DNK-MRH-HEADER ---

(function() {
  if (window.__DNK_SENSOR_INITIALIZED__) return;
  window.__DNK_SENSOR_INITIALIZED__ = true;

  const urlParams = new URLSearchParams(window.location.search);
  const dealId = urlParams.get('deal_id') || window.DNK_DEAL_ID || 'deal_noku_2026';
  const apiEndpoint = window.DNK_API_URL || 'https://noku-proposal.pages.dev/api/v1/cockpit';
  const isReviewUrl = urlParams.has('review') || urlParams.has('dnk_review') || urlParams.has('preview_theme_id') || window.location.hostname.includes('pages.dev');

  let currentMode = 'idle'; // 'idle' | 'area' | 'element'
  let isDragging = false;
  let startX = 0, startY = 0;
  let pageStartX = 0, pageStartY = 0;
  let selectionBox = null;
  let hoveredEl = null;
  let pinCounter = 1;
  const activePins = [];

  // ==========================================
  // 1. SOTA Shadow DOM Host & DNK OS HUD Styles
  // ==========================================
  const host = document.createElement('div');
  host.id = 'dnk-sensor-host';
  host.style.cssText = 'all: initial; position: absolute; top: 0; left: 0; width: 100%; height: 0; pointer-events: none; z-index: 2147483640; overflow: visible;';
  document.documentElement.appendChild(host);

  const shadow = host.attachShadow({ mode: 'open' });

  const style = document.createElement('style');
  style.textContent = `
    *, *::before, *::after {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      -webkit-font-smoothing: antialiased;
    }

    /* DNK OS Design Tokens */
    :host {
      --dnk-abyss: #091114;
      --dnk-card: #0F1D22;
      --dnk-elevated: #152830;
      --dnk-border: #1E3842;
      --dnk-border-focus: #14B8A6;
      --dnk-emerald: #10B981;
      --dnk-emerald-dark: #008060;
      --dnk-cyan: #38BDF8;
      --dnk-amber: #F59E0B;
      --dnk-text-primary: #F8FAFC;
      --dnk-text-secondary: #94A3B8;
      --dnk-text-muted: #64748B;
      --dnk-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }

    /* Floating Control Bar */
    .dnk-control-bar {
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: rgba(15, 29, 34, 0.92);
      backdrop-filter: blur(12px);
      border: 1px solid var(--dnk-border);
      border-radius: 999px;
      padding: 6px;
      display: flex;
      align-items: center;
      gap: 6px;
      box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.5), 0 0 1px 1px rgba(20, 184, 166, 0.2);
      z-index: 2147483645;
      pointer-events: auto;
      transition: all 0.2s ease;
    }
    .dnk-control-bar:hover {
      border-color: var(--dnk-border-focus);
      box-shadow: 0 12px 35px -5px rgba(0, 0, 0, 0.6), 0 0 16px rgba(16, 185, 129, 0.25);
    }

    .dnk-bar-btn {
      background: transparent;
      border: none;
      color: var(--dnk-text-secondary);
      font-size: 13px;
      font-weight: 600;
      padding: 8px 14px;
      border-radius: 999px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s ease;
      white-space: nowrap;
      user-select: none;
    }
    .dnk-bar-btn:hover {
      color: var(--dnk-text-primary);
      background: var(--dnk-elevated);
    }
    .dnk-bar-btn.active {
      background: var(--dnk-emerald-dark) !important;
      color: #FFFFFF !important;
      box-shadow: 0 0 14px rgba(16, 185, 129, 0.4);
    }

    /* Welcome Banner */
    .dnk-welcome-banner {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      background: rgba(15, 29, 34, 0.96);
      backdrop-filter: blur(10px);
      color: var(--dnk-text-primary);
      border-bottom: 2px solid var(--dnk-emerald);
      padding: 10px 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 13.5px;
      z-index: 2147483642;
      box-shadow: 0 4px 20px rgba(0,0,0,0.3);
      pointer-events: auto;
    }
    .dnk-welcome-close {
      background: transparent;
      border: none;
      color: var(--dnk-text-secondary);
      cursor: pointer;
      font-size: 18px;
      padding: 2px 8px;
      border-radius: 4px;
    }
    .dnk-welcome-close:hover {
      color: var(--dnk-text-primary);
      background: var(--dnk-elevated);
    }

    /* Selection Marquee */
    .dnk-selection-marquee {
      position: fixed;
      border: 2px dashed var(--dnk-emerald);
      background: rgba(16, 185, 129, 0.14);
      pointer-events: none;
      z-index: 2147483641;
      border-radius: 6px;
      box-shadow: 0 0 15px rgba(16, 185, 129, 0.2);
    }
    .dnk-dim-badge {
      position: absolute;
      bottom: -26px;
      right: 0;
      background: var(--dnk-card);
      color: var(--dnk-cyan);
      font-size: 11px;
      font-family: var(--dnk-mono);
      font-weight: 600;
      padding: 3px 8px;
      border-radius: 4px;
      border: 1px solid var(--dnk-border);
      white-space: nowrap;
      pointer-events: none;
      box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }

    /* Pins Layer & Markers */
    .dnk-pins-layer {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      overflow: visible;
    }

    .dnk-pin-marker {
      position: absolute;
      width: 30px;
      height: 30px;
      background: linear-gradient(135deg, var(--dnk-emerald), var(--dnk-emerald-dark));
      color: #FFFFFF;
      font-weight: 700;
      font-size: 12.5px;
      font-family: var(--dnk-mono);
      border-radius: 50% 50% 50% 4px;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 14px rgba(16, 185, 129, 0.5);
      z-index: 2147483635;
      cursor: pointer;
      border: 2px solid #FFFFFF;
      transition: transform 0.18s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.18s;
      pointer-events: auto;
      user-select: none;
    }
    .dnk-pin-marker:hover {
      transform: scale(1.22);
      box-shadow: 0 6px 20px rgba(16, 185, 129, 0.7);
    }
    .dnk-pin-pulse {
      animation: dnkPinPulse 1.2s infinite;
    }
    @keyframes dnkPinPulse {
      0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
      70% { box-shadow: 0 0 0 14px rgba(16, 185, 129, 0); }
      100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }

    /* Modal Overlay & Card */
    .dnk-modal-overlay {
      position: fixed;
      inset: 0;
      background: rgba(9, 17, 20, 0.7);
      backdrop-filter: blur(6px);
      z-index: 2147483648;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 16px;
      pointer-events: auto;
    }
    .dnk-modal-box {
      background: var(--dnk-card);
      border: 1px solid var(--dnk-border);
      border-radius: 16px;
      width: 100%;
      max-width: 480px;
      padding: 24px;
      box-shadow: 0 25px 60px -12px rgba(0, 0, 0, 0.7), 0 0 1px 1px rgba(20, 184, 166, 0.3);
      color: var(--dnk-text-primary);
      animation: dnkModalFadeIn 0.22s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @keyframes dnkModalFadeIn {
      from { opacity: 0; transform: scale(0.95) translateY(8px); }
      to { opacity: 1; transform: scale(1) translateY(0); }
    }

    .dnk-modal-title {
      font-size: 16px;
      font-weight: 700;
      margin-bottom: 6px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      color: var(--dnk-text-primary);
    }
    .dnk-badge-num {
      font-size: 12px;
      font-family: var(--dnk-mono);
      color: var(--dnk-emerald);
      background: rgba(16, 185, 129, 0.12);
      border: 1px solid rgba(16, 185, 129, 0.3);
      padding: 2px 8px;
      border-radius: 999px;
      font-weight: 700;
    }
    .dnk-modal-sub {
      font-size: 11.5px;
      color: var(--dnk-text-secondary);
      font-family: var(--dnk-mono);
      margin-bottom: 14px;
      background: var(--dnk-elevated);
      border: 1px solid var(--dnk-border);
      padding: 8px 12px;
      border-radius: 8px;
      line-height: 1.5;
      word-break: break-all;
    }
    .dnk-input, .dnk-textarea {
      width: 100%;
      padding: 10px 12px;
      border: 1px solid var(--dnk-border);
      border-radius: 8px;
      font-size: 13.5px;
      margin-bottom: 12px;
      color: var(--dnk-text-primary);
      background: var(--dnk-abyss);
      outline: none;
      transition: border-color 0.15s, box-shadow 0.15s;
    }
    .dnk-input:focus, .dnk-textarea:focus {
      border-color: var(--dnk-border-focus);
      box-shadow: 0 0 0 3px rgba(20, 184, 166, 0.2);
    }
    .dnk-textarea { resize: vertical; min-height: 90px; }

    .dnk-btn-row {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
      margin-top: 10px;
    }
    .dnk-btn-cancel {
      background: var(--dnk-elevated);
      border: 1px solid var(--dnk-border);
      color: var(--dnk-text-secondary);
      padding: 9px 16px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s;
    }
    .dnk-btn-cancel:hover {
      background: #1e3842;
      color: var(--dnk-text-primary);
    }
    .dnk-btn-submit {
      background: linear-gradient(135deg, var(--dnk-emerald), var(--dnk-emerald-dark));
      border: none;
      color: #FFFFFF;
      padding: 9px 18px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s;
      box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
    }
    .dnk-btn-submit:hover {
      transform: translateY(-1px);
      box-shadow: 0 4px 14px rgba(16, 185, 129, 0.45);
    }
    .dnk-btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }

    .dnk-agent-reply-box {
      background: rgba(16, 185, 129, 0.08);
      border: 1px solid rgba(16, 185, 129, 0.25);
      border-radius: 10px;
      padding: 14px;
      margin-top: 14px;
      font-size: 13px;
      color: #E2E8F0;
      line-height: 1.55;
    }
    .dnk-agent-reply-header {
      display: flex;
      align-items: center;
      gap: 6px;
      font-weight: 700;
      color: var(--dnk-emerald);
      margin-bottom: 6px;
    }

    /* ==========================================
       DNK OS Slide-over Cockpit Drawer
       ========================================== */
    .dnk-drawer-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(9, 17, 20, 0.65);
      backdrop-filter: blur(4px);
      z-index: 2147483646;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.25s ease;
    }
    .dnk-drawer-backdrop.open {
      opacity: 1;
      pointer-events: auto;
    }

    .dnk-drawer {
      position: fixed;
      top: 0;
      right: 0;
      width: 420px;
      max-width: 92vw;
      height: 100vh;
      background: var(--dnk-card);
      border-left: 1px solid var(--dnk-border);
      box-shadow: -15px 0 40px rgba(0, 0, 0, 0.6);
      transform: translateX(100%);
      transition: transform 0.32s cubic-bezier(0.16, 1, 0.3, 1);
      z-index: 2147483647;
      pointer-events: auto;
      display: flex;
      flex-direction: column;
      color: var(--dnk-text-primary);
    }
    .dnk-drawer.open {
      transform: translateX(0);
    }

    .dnk-drawer-header {
      padding: 18px 20px;
      border-bottom: 1px solid var(--dnk-border);
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: var(--dnk-abyss);
    }
    .dnk-drawer-title-group {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .dnk-drawer-logo {
      width: 24px;
      height: 24px;
      background: var(--dnk-emerald);
      color: #000;
      font-weight: 900;
      font-size: 13px;
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .dnk-drawer-title {
      font-size: 15px;
      font-weight: 700;
      color: var(--dnk-text-primary);
    }
    .dnk-drawer-close {
      background: transparent;
      border: none;
      color: var(--dnk-text-secondary);
      font-size: 20px;
      cursor: pointer;
      padding: 4px 8px;
      border-radius: 6px;
      transition: all 0.15s;
    }
    .dnk-drawer-close:hover {
      background: var(--dnk-elevated);
      color: var(--dnk-text-primary);
    }

    /* Drawer Subheader / Quota Meter */
    .dnk-drawer-status-bar {
      padding: 14px 20px;
      background: rgba(21, 40, 48, 0.5);
      border-bottom: 1px solid var(--dnk-border);
      font-size: 12.5px;
    }
    .dnk-status-row {
      display: flex;
      justify-content: space-between;
      margin-bottom: 8px;
    }
    .dnk-progress-bar-bg {
      width: 100%;
      height: 6px;
      background: var(--dnk-abyss);
      border-radius: 999px;
      overflow: hidden;
      border: 1px solid var(--dnk-border);
    }
    .dnk-progress-bar-fill {
      height: 100%;
      background: linear-gradient(90deg, var(--dnk-emerald), var(--dnk-cyan));
      border-radius: 999px;
      transition: width 0.3s ease;
    }

    /* Drawer Tabs */
    .dnk-drawer-tabs {
      display: flex;
      border-bottom: 1px solid var(--dnk-border);
      background: var(--dnk-abyss);
    }
    .dnk-drawer-tab {
      flex: 1;
      padding: 11px 8px;
      text-align: center;
      font-size: 12.5px;
      font-weight: 600;
      color: var(--dnk-text-secondary);
      background: transparent;
      border: none;
      cursor: pointer;
      border-bottom: 2px solid transparent;
      transition: all 0.15s;
    }
    .dnk-drawer-tab:hover {
      color: var(--dnk-text-primary);
    }
    .dnk-drawer-tab.active {
      color: var(--dnk-emerald);
      border-bottom-color: var(--dnk-emerald);
      background: rgba(16, 185, 129, 0.05);
    }

    /* Drawer Content Area */
    .dnk-drawer-body {
      flex: 1;
      overflow-y: auto;
      padding: 16px 20px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    /* Ticket Card */
    .dnk-ticket-card {
      background: var(--dnk-elevated);
      border: 1px solid var(--dnk-border);
      border-radius: 10px;
      padding: 14px;
      cursor: pointer;
      transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .dnk-ticket-card:hover {
      border-color: var(--dnk-border-focus);
      transform: translateY(-2px);
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    }
    .dnk-ticket-card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 6px;
    }
    .dnk-ticket-title {
      font-size: 13.5px;
      font-weight: 700;
      color: var(--dnk-text-primary);
    }
    .dnk-ticket-body {
      font-size: 12.5px;
      color: var(--dnk-text-secondary);
      line-height: 1.45;
      margin-bottom: 8px;
    }
    .dnk-ticket-meta {
      font-size: 11px;
      font-family: var(--dnk-mono);
      color: var(--dnk-cyan);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    /* Empty state */
    .dnk-empty-state {
      text-align: center;
      padding: 40px 10px;
      color: var(--dnk-text-muted);
      font-size: 13px;
    }

    /* Drawer Footer */
    .dnk-drawer-footer {
      padding: 14px 20px;
      border-top: 1px solid var(--dnk-border);
      background: var(--dnk-abyss);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .dnk-link-cockpit {
      color: var(--dnk-cyan);
      text-decoration: none;
      font-size: 12.5px;
      font-weight: 600;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      transition: color 0.15s;
    }
    .dnk-link-cockpit:hover {
      color: #FFFFFF;
      text-decoration: underline;
    }
  `;
  shadow.appendChild(style);

  // Host Document Global Inspect Hover Style
  const hostStyle = document.createElement('style');
  hostStyle.id = 'dnk-host-inspect-style';
  hostStyle.textContent = `
    .dnk-inspect-hover {
      outline: 2px dashed #10B981 !important;
      outline-offset: 2px !important;
      cursor: crosshair !important;
    }
  `;
  document.head.appendChild(hostStyle);

  // ==========================================
  // 2. Pins Layer & Welcome Banner
  // ==========================================
  const pinsLayer = document.createElement('div');
  pinsLayer.className = 'dnk-pins-layer';
  shadow.appendChild(pinsLayer);

  if (isReviewUrl) {
    const banner = document.createElement('div');
    banner.className = 'dnk-welcome-banner';
    banner.innerHTML = `
      <div>
        <strong>⚡ DNK OS · Режим узгодження активовано.</strong>
        <span style="opacity:0.85; margin-left:8px;">Виділяйте будь-яку область мишкою або клікайте на елементи для зв'язку з агентом розробки.</span>
      </div>
      <button class="dnk-welcome-close" title="Закрити">&times;</button>
    `;
    shadow.appendChild(banner);

    const updateBannerOffset = () => {
      const h = banner.getBoundingClientRect().height || 42;
      document.documentElement.style.setProperty('--dnk-banner-offset', `${h}px`);
      document.body.style.paddingTop = `${h}px`;
    };

    setTimeout(updateBannerOffset, 20);
    window.addEventListener('resize', updateBannerOffset);

    banner.querySelector('.dnk-welcome-close').addEventListener('click', () => {
      banner.remove();
      document.documentElement.style.setProperty('--dnk-banner-offset', '0px');
      document.body.style.paddingTop = '0px';
      window.removeEventListener('resize', updateBannerOffset);
    });
  }

  // ==========================================
  // 3. Floating Control Bar
  // ==========================================
  const bar = document.createElement('div');
  bar.className = 'dnk-control-bar';
  bar.innerHTML = `
    <button class="dnk-bar-btn" id="dnk-btn-mode-area" title="Затисніть і виділіть область на екрані">
      <span>📐</span> <span>Виділити область</span>
    </button>
    <button class="dnk-bar-btn" id="dnk-btn-mode-element" title="Клік на конкретний елемент або кнопку">
      <span>🎯</span> <span>Клік на елемент</span>
    </button>
    <button class="dnk-bar-btn" id="dnk-btn-open-drawer" title="Відкрити панель правок та Cockpit">
      <span>📋</span> <span id="dnk-pin-count">Панель правок (0)</span>
    </button>
  `;
  shadow.appendChild(bar);

  const btnArea = bar.querySelector('#dnk-btn-mode-area');
  const btnElem = bar.querySelector('#dnk-btn-mode-element');
  const btnDrawer = bar.querySelector('#dnk-btn-open-drawer');

  btnArea.addEventListener('click', () => setMode(currentMode === 'area' ? 'idle' : 'area'));
  btnElem.addEventListener('click', () => setMode(currentMode === 'element' ? 'idle' : 'element'));
  btnDrawer.addEventListener('click', () => toggleDrawer());

  function setMode(mode) {
    currentMode = mode;
    btnArea.classList.toggle('active', mode === 'area');
    btnElem.classList.toggle('active', mode === 'element');

    if (mode === 'area') {
      document.body.style.cursor = 'crosshair';
      if (hoveredEl) hoveredEl.classList.remove('dnk-inspect-hover');
    } else if (mode === 'element') {
      document.body.style.cursor = 'default';
    } else {
      document.body.style.cursor = 'default';
      if (hoveredEl) hoveredEl.classList.remove('dnk-inspect-hover');
      if (selectionBox) { selectionBox.remove(); selectionBox = null; }
    }
  }

  // ==========================================
  // 4. Slide-over Cockpit Drawer Component
  // ==========================================
  const drawerBackdrop = document.createElement('div');
  drawerBackdrop.className = 'dnk-drawer-backdrop';
  shadow.appendChild(drawerBackdrop);

  const drawer = document.createElement('div');
  drawer.className = 'dnk-drawer';
  drawer.innerHTML = `
    <div class="dnk-drawer-header">
      <div class="dnk-drawer-title-group">
        <div class="dnk-drawer-logo">⚡</div>
        <div class="dnk-drawer-title">DNK OS · Client Cockpit</div>
      </div>
      <button class="dnk-drawer-close" id="dnk-drawer-close">&times;</button>
    </div>

    <div class="dnk-drawer-status-bar">
      <div class="dnk-status-row">
        <span>Проєкт: <strong>NOKU Store</strong></span>
        <span style="color:var(--dnk-emerald); font-weight:700;">Квота: 2 / 3 раунди</span>
      </div>
      <div class="dnk-progress-bar-bg">
        <div class="dnk-progress-bar-fill" style="width: 66%;"></div>
      </div>
    </div>

    <div class="dnk-drawer-tabs">
      <button class="dnk-drawer-tab active" data-tab="tickets">Замітки на сторінці</button>
      <button class="dnk-drawer-tab" data-tab="stages">Дорожня карта</button>
      <button class="dnk-drawer-tab" data-tab="artifacts">Артефакти</button>
    </div>

    <div class="dnk-drawer-body" id="dnk-drawer-body">
      <!-- Injected by renderDrawerContent -->
    </div>

    <div class="dnk-drawer-footer">
      <a href="./cockpit.html" target="_blank" class="dnk-link-cockpit">
        <span>Відкрити повний кабінет (Cockpit)</span> <span>↗</span>
      </a>
      <span style="font-size:11px; font-family:var(--dnk-mono); color:var(--dnk-text-muted);">SLA: Active</span>
    </div>
  `;
  shadow.appendChild(drawer);

  drawerBackdrop.addEventListener('click', () => closeDrawer());
  drawer.querySelector('#dnk-drawer-close').addEventListener('click', () => closeDrawer());

  let activeTab = 'tickets';
  drawer.querySelectorAll('.dnk-drawer-tab').forEach(tabBtn => {
    tabBtn.addEventListener('click', () => {
      drawer.querySelectorAll('.dnk-drawer-tab').forEach(b => b.classList.remove('active'));
      tabBtn.classList.add('active');
      activeTab = tabBtn.getAttribute('data-tab');
      renderDrawerContent();
    });
  });

  function toggleDrawer() {
    if (drawer.classList.contains('open')) {
      closeDrawer();
    } else {
      openDrawer();
    }
  }

  function openDrawer() {
    drawer.classList.add('open');
    drawerBackdrop.classList.add('open');
    renderDrawerContent();
  }

  function closeDrawer() {
    drawer.classList.remove('open');
    drawerBackdrop.classList.remove('open');
  }

  function renderDrawerContent() {
    const body = drawer.querySelector('#dnk-drawer-body');
    if (!body) return;

    if (activeTab === 'tickets') {
      if (activePins.length === 0) {
        body.innerHTML = `
          <div class="dnk-empty-state">
            <div style="font-size:32px; margin-bottom:12px;">📍</div>
            <p><strong>Поки що немає заміток на сторінці</strong></p>
            <p style="margin-top:6px; opacity:0.8;">Виділіть область або клікніть на елемент, щоб додати першу правку.</p>
          </div>
        `;
        return;
      }

      body.innerHTML = '';
      activePins.forEach(pin => {
        const card = document.createElement('div');
        card.className = 'dnk-ticket-card';
        card.innerHTML = `
          <div class="dnk-ticket-card-header">
            <span class="dnk-ticket-title">Правка #${pin.num}: ${pin.title}</span>
            <span class="dnk-badge-num">📍 #${pin.num}</span>
          </div>
          <div class="dnk-ticket-body">${pin.comment}</div>
          <div class="dnk-ticket-meta">
            <span>Зона: ${pin.anchorEl ? pin.anchorEl.tagName.toLowerCase() : 'DOM'}</span>
            <span style="color:var(--dnk-emerald); font-weight:600;">● В черзі розробки</span>
          </div>
        `;
        card.addEventListener('click', () => {
          closeDrawer();
          window.scrollTo({ top: Math.max(0, pin.pageY - 160), behavior: 'smooth' });
          pin.el.classList.add('dnk-pin-pulse');
          setTimeout(() => pin.el.classList.remove('dnk-pin-pulse'), 3000);
        });
        body.appendChild(card);
      });
    } else if (activeTab === 'stages') {
      body.innerHTML = `
        <div style="display:flex; flex-direction:column; gap:8px;">
          <div style="background:var(--dnk-elevated); padding:10px 14px; border-radius:8px; border:1px solid #008060; font-size:12.5px;">
            <strong style="color:var(--dnk-emerald);">✓ Етап 1:</strong> Архітектура та стиль Polaris Snow
          </div>
          <div style="background:var(--dnk-elevated); padding:10px 14px; border-radius:8px; border:1px solid var(--dnk-border-focus); font-size:12.5px;">
            <strong style="color:var(--dnk-cyan);">● Етап 2 (В РОБОТІ):</strong> Верстка головної сторінки та Theme Blocks
          </div>
          <div style="background:var(--dnk-elevated); padding:10px 14px; border-radius:8px; border:1px solid var(--dnk-border); font-size:12.5px; opacity:0.65;">
            <strong>○ Етап 3:</strong> Синхронізація відгуків Etsy та Google Shopping
          </div>
          <div style="background:var(--dnk-elevated); padding:10px 14px; border-radius:8px; border:1px solid var(--dnk-border); font-size:12.5px; opacity:0.65;">
            <strong>○ Етап 4:</strong> Оптова B2B сторінка та висувний кошик
          </div>
          <div style="background:var(--dnk-elevated); padding:10px 14px; border-radius:8px; border:1px solid var(--dnk-border); font-size:12.5px; opacity:0.65;">
            <strong>○ Етап 5:</strong> QA, оптимізація швидкості (CWV 90+) та чекаут
          </div>
          <div style="background:var(--dnk-elevated); padding:10px 14px; border-radius:8px; border:1px solid var(--dnk-border); font-size:12.5px; opacity:0.65;">
            <strong>○ Етап 6:</strong> Фінальний реліз на noku.store
          </div>
        </div>
      `;
    } else if (activeTab === 'artifacts') {
      body.innerHTML = `
        <div style="display:flex; flex-direction:column; gap:10px;">
          <a href="https://noku-proposal.pages.dev" target="_blank" style="background:var(--dnk-elevated); padding:12px; border-radius:8px; border:1px solid var(--dnk-border); text-decoration:none; color:var(--dnk-text-primary); display:flex; justify-content:space-between; align-items:center;">
            <div>
              <div style="font-weight:600; font-size:13px;">Жива комерційна пропозиція</div>
              <div style="font-size:11.5px; color:var(--dnk-text-secondary);">noku-proposal.pages.dev</div>
            </div>
            <span style="color:var(--dnk-emerald);">↗</span>
          </a>
          <a href="https://noku.store" target="_blank" style="background:var(--dnk-elevated); padding:12px; border-radius:8px; border:1px solid var(--dnk-border); text-decoration:none; color:var(--dnk-text-primary); display:flex; justify-content:space-between; align-items:center;">
            <div>
              <div style="font-weight:600; font-size:13px;">Діючий магазин бренду</div>
              <div style="font-size:11.5px; color:var(--dnk-text-secondary);">noku.store</div>
            </div>
            <span style="color:var(--dnk-emerald);">↗</span>
          </a>
          <a href="./cockpit.html" target="_blank" style="background:var(--dnk-elevated); padding:12px; border-radius:8px; border:1px solid var(--dnk-border); text-decoration:none; color:var(--dnk-text-primary); display:flex; justify-content:space-between; align-items:center;">
            <div>
              <div style="font-weight:600; font-size:13px;">Клієнтський Cockpit</div>
              <div style="font-size:11.5px; color:var(--dnk-text-secondary);">Повний портал узгодження</div>
            </div>
            <span style="color:var(--dnk-emerald);">↗</span>
          </a>
        </div>
      `;
    }
  }

  // ==========================================
  // 5. Area Drag Selection Engine
  // ==========================================
  document.addEventListener('mousedown', (e) => {
    if (currentMode !== 'area') return;
    if (host.contains(e.target)) return;

    isDragging = true;
    startX = e.clientX;
    startY = e.clientY;
    pageStartX = e.pageX;
    pageStartY = e.pageY;

    if (!selectionBox) {
      selectionBox = document.createElement('div');
      selectionBox.className = 'dnk-selection-marquee';
      shadow.appendChild(selectionBox);
    }
    updateMarquee(startX, startY, 0, 0);
  });

  document.addEventListener('mousemove', (e) => {
    if (currentMode === 'area' && isDragging && selectionBox) {
      const currentX = e.clientX;
      const currentY = e.clientY;
      const left = Math.min(startX, currentX);
      const top = Math.min(startY, currentY);
      const width = Math.abs(currentX - startX);
      const height = Math.abs(currentY - startY);
      updateMarquee(left, top, width, height);
    } else if (currentMode === 'element') {
      if (host.contains(e.target)) return;
      if (hoveredEl) hoveredEl.classList.remove('dnk-inspect-hover');
      hoveredEl = e.target;
      hoveredEl.classList.add('dnk-inspect-hover');
    }
  });

  document.addEventListener('mouseup', (e) => {
    if (currentMode === 'area' && isDragging) {
      isDragging = false;
      const currentX = e.clientX;
      const currentY = e.clientY;
      const width = Math.abs(currentX - startX);
      const height = Math.abs(currentY - startY);

      if (width > 15 && height > 15) {
        const left = Math.min(startX, currentX);
        const top = Math.min(startY, currentY);
        const pageLeft = Math.min(pageStartX, e.pageX);
        const pageTop = Math.min(pageStartY, e.pageY);

        const targetEl = document.elementFromPoint(left + width / 2, top + height / 2) || document.body;
        const anchorEl = findAnchorElement(targetEl);
        const relAnchor = computeRelativeAnchor(anchorEl, pageLeft, pageTop);

        const bbox = {
          x: left,
          y: top,
          width: width,
          height: height,
          page_x: pageLeft,
          page_y: pageTop,
          scroll_x: window.scrollX,
          scroll_y: window.scrollY,
          viewport_w: window.innerWidth,
          viewport_h: window.innerHeight,
          relative_anchor: relAnchor
        };

        setMode('idle');
        openFeedbackModal({ targetEl, anchorEl, bbox, isArea: true, pageLeft, pageTop });
      } else {
        if (selectionBox) { selectionBox.remove(); selectionBox = null; }
      }
    }
  });

  // ==========================================
  // 6. Element Click Inspection
  // ==========================================
  document.addEventListener('click', (e) => {
    if (currentMode !== 'element') return;
    if (host.contains(e.target)) return;

    e.preventDefault();
    e.stopPropagation();

    const targetEl = e.target;
    if (hoveredEl) hoveredEl.classList.remove('dnk-inspect-hover');
    setMode('idle');

    const rect = targetEl.getBoundingClientRect();
    const scrollX = window.scrollX || window.pageXOffset;
    const scrollY = window.scrollY || window.pageYOffset;
    const pageX = rect.left + scrollX;
    const pageY = rect.top + scrollY;

    const anchorEl = findAnchorElement(targetEl);
    const relAnchor = computeRelativeAnchor(anchorEl, pageX, pageY);

    const bbox = {
      x: rect.left,
      y: rect.top,
      width: rect.width,
      height: rect.height,
      page_x: pageX,
      page_y: pageY,
      scroll_x: scrollX,
      scroll_y: scrollY,
      viewport_w: window.innerWidth,
      viewport_h: window.innerHeight,
      relative_anchor: relAnchor
    };

    openFeedbackModal({ targetEl, anchorEl, bbox, isArea: false, pageLeft: pageX, pageTop: pageY });
  });

  function updateMarquee(x, y, w, h) {
    selectionBox.style.left = `${x}px`;
    selectionBox.style.top = `${y}px`;
    selectionBox.style.width = `${w}px`;
    selectionBox.style.height = `${h}px`;
    selectionBox.innerHTML = `<span class="dnk-dim-badge">${Math.round(w)} × ${Math.round(h)} px</span>`;
  }

  // ==========================================
  // 7. Responsive Anchoring & Meta Extraction
  // ==========================================
  function findAnchorElement(el) {
    return el.closest('section, [data-section-id], [id^="shopify-section-"], header, footer, main, article, div[id]') || el;
  }

  function computeRelativeAnchor(anchorEl, pageX, pageY) {
    if (!anchorEl) return null;
    const rect = anchorEl.getBoundingClientRect();
    const scrollX = window.scrollX || window.pageXOffset;
    const scrollY = window.scrollY || window.pageYOffset;
    const anchorPageX = rect.left + scrollX;
    const anchorPageY = rect.top + scrollY;

    const relX = rect.width > 0 ? ((pageX - anchorPageX) / rect.width) * 100 : 0;
    const relY = rect.height > 0 ? ((pageY - anchorPageY) / rect.height) * 100 : 0;

    return {
      selector: getSmartSelector(anchorEl),
      parent_tag: anchorEl.tagName.toLowerCase(),
      rel_x_pct: parseFloat(Math.min(100, Math.max(0, relX)).toFixed(2)),
      rel_y_pct: parseFloat(Math.min(100, Math.max(0, relY)).toFixed(2))
    };
  }

  function getSmartSelector(el) {
    if (!el || !el.tagName) return 'body';
    if (el.id) return `#${el.id}`;
    if (el.getAttribute('data-section-id')) return `[data-section-id="${el.getAttribute('data-section-id')}"]`;
    if (el.getAttribute('data-block-id')) return `[data-block-id="${el.getAttribute('data-block-id')}"]`;
    if (el.className && typeof el.className === 'string') {
      const cls = el.className.split(' ').filter(c => c && !c.startsWith('dnk-'))[0];
      if (cls) return `${el.tagName.toLowerCase()}.${cls}`;
    }
    return el.tagName.toLowerCase();
  }

  function extractShopifyMeta(el) {
    const sectionEl = el.closest('[id^="shopify-section-"]') || el.closest('[data-section-id]');
    const blockEl = el.closest('[data-block-id]') || el.closest('[data-shopify-editor-block]');
    
    const sectionId = sectionEl ? (sectionEl.getAttribute('data-section-id') || sectionEl.id.replace('shopify-section-', '')) : 'global';
    const blockId = blockEl ? (blockEl.getAttribute('data-block-id') || blockEl.getAttribute('data-shopify-editor-block') || '') : '';
    const selector = getSmartSelector(el);
    const breadcrumb = `Секція: ${sectionId} ${blockId ? `| Блок: ${blockId}` : ''}`;
    return { sectionId, blockId, selector, breadcrumb };
  }

  // ==========================================
  // 8. Modal & In-Context Agent Dispatch
  // ==========================================
  function openFeedbackModal({ targetEl, anchorEl, bbox, isArea, pageLeft, pageTop }) {
    const meta = extractShopifyMeta(targetEl);
    const pinNumber = pinCounter++;

    const overlay = document.createElement('div');
    overlay.className = 'dnk-modal-overlay';
    overlay.innerHTML = `
      <div class="dnk-modal-box">
        <div class="dnk-modal-title">
          <span>📍 Правка для агента розробки</span>
          <span class="dnk-badge-num">#${pinNumber}</span>
        </div>
        <div class="dnk-modal-sub">
          <strong>${isArea ? '📐 Виділена область' : '🎯 Елемент'}:</strong> ${meta.breadcrumb}<br>
          Розмір: ${Math.round(bbox.width)} × ${Math.round(bbox.height)} px · Селектор: ${meta.selector}
          ${bbox.relative_anchor ? `<br>Відносний якір: ${bbox.relative_anchor.selector} (${bbox.relative_anchor.rel_x_pct}%, ${bbox.relative_anchor.rel_y_pct}%)` : ''}
        </div>
        
        <input type="text" id="dnk-inp-title" class="dnk-input" placeholder="Короткий заголовок (наприклад, змінити колір плашки)" value="Правка: ${meta.sectionId} #${pinNumber}" />
        <textarea id="dnk-inp-comment" class="dnk-textarea" placeholder="Опишіть, що саме ви хочете змінити на цій ділянці..."></textarea>
        
        <div id="dnk-modal-agent-reply" style="display:none;"></div>

        <div class="dnk-btn-row" id="dnk-modal-btn-row">
          <button type="button" class="dnk-btn-cancel" id="dnk-btn-cancel">Скасувати</button>
          <button type="button" class="dnk-btn-submit" id="dnk-btn-dispatch">
            <span>Надіслати агенту</span> <span>→</span>
          </button>
        </div>
      </div>
    `;
    shadow.appendChild(overlay);

    overlay.querySelector('#dnk-btn-cancel').addEventListener('click', () => {
      overlay.remove();
      if (selectionBox) { selectionBox.remove(); selectionBox = null; }
    });

    overlay.querySelector('#dnk-btn-dispatch').addEventListener('click', async () => {
      const title = overlay.querySelector('#dnk-inp-title').value.trim();
      const comment = overlay.querySelector('#dnk-inp-comment').value.trim();
      if (!comment) {
        alert('Будь ласка, вкажіть ваш коментар або суть правки.');
        return;
      }

      const sendBtn = overlay.querySelector('#dnk-btn-dispatch');
      sendBtn.disabled = true;
      sendBtn.innerHTML = '<span>Відправка...</span>';

      const payload = {
        deal_id: dealId,
        title: title,
        comment: comment,
        selector: meta.selector,
        section_id: meta.sectionId,
        block_id: meta.blockId,
        bounding_box: bbox,
        page_url: window.location.pathname + window.location.search,
        category: 'auto'
      };

      try {
        const res = await fetch(`${apiEndpoint}/${dealId}/tickets`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (res.ok) {
          const data = await res.json();
          renderPersistentPin({
            x: pageLeft,
            y: pageTop,
            num: pinNumber,
            title: title,
            comment: comment,
            category: data.category,
            anchorEl: anchorEl,
            relX: bbox.relative_anchor ? bbox.relative_anchor.rel_x_pct : 0,
            relY: bbox.relative_anchor ? bbox.relative_anchor.rel_y_pct : 0
          });
          showAgentReplyInModal(overlay, data.client_acknowledgment, data.quota_remaining);
        } else {
          fallbackOffline(pageLeft, pageTop, pinNumber, payload, overlay, anchorEl, bbox.relative_anchor);
        }
      } catch (e) {
        fallbackOffline(pageLeft, pageTop, pinNumber, payload, overlay, anchorEl, bbox.relative_anchor);
      }

      if (selectionBox) { selectionBox.remove(); selectionBox = null; }
    });
  }

  function showAgentReplyInModal(overlay, replyText, quotaRemaining) {
    const replyBox = overlay.querySelector('#dnk-modal-agent-reply');
    replyBox.className = 'dnk-agent-reply-box';
    replyBox.style.display = 'block';
    replyBox.innerHTML = `
      <div class="dnk-agent-reply-header">
        <span>💬</span> <span>Відповідь Агента Клієнтського Супроводження:</span>
      </div>
      <div>${replyText}</div>
      <div style="font-size:11.5px; opacity:0.85; margin-top:10px;">
        Залишок раундів правок: <strong>${quotaRemaining}</strong>
      </div>
    `;

    const btnRow = overlay.querySelector('#dnk-modal-btn-row');
    btnRow.innerHTML = `<button type="button" class="dnk-btn-submit" id="dnk-btn-ok">Зрозуміло, дякую!</button>`;
    btnRow.querySelector('#dnk-btn-ok').addEventListener('click', () => overlay.remove());
  }

  // ==========================================
  // 9. Responsive Persistent Pins Layer
  // ==========================================
  function renderPersistentPin({ x, y, num, title, comment, category, anchorEl, relX, relY }) {
    const pin = document.createElement('div');
    pin.className = 'dnk-pin-marker';
    pin.dataset.pinId = num;
    pin.style.left = `${Math.max(10, x)}px`;
    pin.style.top = `${Math.max(10, y)}px`;
    pin.textContent = num;
    pin.title = `#${num}: ${title} - ${comment}`;

    pin.addEventListener('click', (e) => {
      e.stopPropagation();
      openDrawer();
    });

    pinsLayer.appendChild(pin);
    activePins.push({ el: pin, anchorEl, relX, relY, pageX: x, pageY: y, num, title, comment, category });
    updatePinCount();
    renderDrawerContent();
  }

  function fallbackOffline(x, y, num, payload, overlay, anchorEl, relAnchor) {
    const queue = JSON.parse(localStorage.getItem('dnk_client_tickets') || '[]');
    queue.push(payload);
    localStorage.setItem('dnk_client_tickets', JSON.stringify(queue));

    renderPersistentPin({
      x: x,
      y: y,
      num: num,
      title: payload.title,
      comment: payload.comment,
      category: 'offline',
      anchorEl: anchorEl,
      relX: relAnchor ? relAnchor.rel_x_pct : 0,
      relY: relAnchor ? relAnchor.rel_y_pct : 0
    });

    if (overlay) {
      showAgentReplyInModal(
        overlay,
        `Правку #${num} зафіксовано на сторінці та збережено. Агент клієнтського супроводження отримав завдання в роботу.`,
        '2 / 3 раунди'
      );
    }
  }

  function updatePinCount() {
    const countEl = shadow.querySelector('#dnk-pin-count');
    if (countEl) {
      countEl.textContent = `Панель правок (${activePins.length})`;
    }
  }

  // ==========================================
  // 10. Vercel Comments Style Window Resize Sync
  // ==========================================
  window.addEventListener('resize', () => {
    activePins.forEach(p => {
      if (p.anchorEl && document.contains(p.anchorEl)) {
        const rect = p.anchorEl.getBoundingClientRect();
        const scrollX = window.scrollX || window.pageXOffset;
        const scrollY = window.scrollY || window.pageYOffset;
        const newX = rect.left + scrollX + (rect.width * p.relX / 100);
        const newY = rect.top + scrollY + (rect.height * p.relY / 100);
        p.el.style.left = `${Math.max(10, newX)}px`;
        p.el.style.top = `${Math.max(10, newY)}px`;
      }
    });
  });

})();

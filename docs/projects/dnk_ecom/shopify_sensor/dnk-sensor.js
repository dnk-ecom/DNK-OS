// --- DNK-MRH-HEADER ---
// mrh_id: "docs/projects/dnk_ecom/shopify_sensor/dnk-sensor.js"
// purpose: "DNK Sovereign In-Context Client Review Sensor with Area Bounding-Box Selection and Agent Dispatch."
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "2.0.0"
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

  // 1. Inject Styles
  const style = document.createElement('style');
  style.id = 'dnk-sensor-styles';
  style.textContent = `
    .dnk-control-bar {
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: #0F172A;
      border: 1px solid #334155;
      border-radius: 999px;
      padding: 6px;
      display: flex;
      align-items: center;
      gap: 6px;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
      z-index: 2147483640;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .dnk-bar-btn {
      background: transparent;
      border: none;
      color: #94A3B8;
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
    }
    .dnk-bar-btn:hover { color: #FFFFFF; background: #1E293B; }
    .dnk-bar-btn.active {
      background: #008060 !important;
      color: #FFFFFF !important;
    }
    .dnk-welcome-banner {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      background: #0F172A;
      color: #F8FAFC;
      border-bottom: 2px solid #008060;
      padding: 10px 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 13.5px;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      z-index: 2147483630;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .dnk-welcome-close {
      background: transparent;
      border: none;
      color: #94A3B8;
      cursor: pointer;
      font-size: 16px;
      padding: 2px 8px;
    }
    .dnk-selection-marquee {
      position: fixed;
      border: 2px dashed #008060;
      background: rgba(0, 128, 96, 0.12);
      pointer-events: none;
      z-index: 2147483638;
      border-radius: 4px;
    }
    .dnk-dim-badge {
      position: absolute;
      bottom: -22px;
      right: 0;
      background: #0F172A;
      color: #F8FAFC;
      font-size: 10px;
      font-family: monospace;
      padding: 2px 6px;
      border-radius: 3px;
      border: 1px solid #334155;
    }
    .dnk-inspect-hover {
      outline: 2px dashed #008060 !important;
      outline-offset: 2px !important;
      cursor: crosshair !important;
    }
    .dnk-pin-marker {
      position: absolute;
      width: 28px;
      height: 28px;
      background: #008060;
      color: #FFFFFF;
      font-weight: 700;
      font-size: 12px;
      font-family: monospace;
      border-radius: 50% 50% 50% 4px;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 10px rgba(0, 128, 96, 0.4);
      z-index: 2147483635;
      cursor: pointer;
      border: 2px solid #FFFFFF;
      transition: transform 0.15s ease;
    }
    .dnk-pin-marker:hover { transform: scale(1.15); }
    .dnk-modal-overlay {
      position: fixed;
      inset: 0;
      background: rgba(15, 23, 42, 0.45);
      backdrop-filter: blur(4px);
      z-index: 2147483645;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 16px;
    }
    .dnk-modal-box {
      background: #FFFFFF;
      border: 1px solid #E2E8F0;
      border-radius: 12px;
      width: 100%;
      max-width: 480px;
      padding: 24px;
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.15);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      color: #0F172A;
    }
    .dnk-modal-title { font-size: 16px; font-weight: 700; margin-bottom: 4px; }
    .dnk-modal-sub {
      font-size: 11.5px;
      color: #64748B;
      font-family: monospace;
      margin-bottom: 14px;
      background: #F8FAFC;
      border: 1px solid #E2E8F0;
      padding: 6px 10px;
      border-radius: 6px;
      word-break: break-all;
    }
    .dnk-input, .dnk-textarea {
      width: 100%;
      padding: 8px 12px;
      border: 1px solid #CBD5E1;
      border-radius: 6px;
      font-size: 13.5px;
      margin-bottom: 12px;
      font-family: inherit;
      box-sizing: border-box;
      outline: none;
    }
    .dnk-input:focus, .dnk-textarea:focus {
      border-color: #008060;
      box-shadow: 0 0 0 2px rgba(0, 128, 96, 0.15);
    }
    .dnk-textarea { resize: vertical; min-height: 85px; }
    .dnk-btn-row { display: flex; justify-content: flex-end; gap: 10px; margin-top: 8px; }
    .dnk-btn-cancel {
      background: #F1F5F9;
      border: 1px solid #E2E8F0;
      color: #475569;
      padding: 8px 14px;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
    }
    .dnk-btn-submit {
      background: #008060;
      border: none;
      color: #FFFFFF;
      padding: 8px 16px;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    .dnk-btn-submit:hover { background: #006e52; }
    .dnk-agent-reply-box {
      background: #F0FDF4;
      border: 1px solid #BBF7D0;
      border-radius: 8px;
      padding: 14px;
      margin-top: 14px;
      font-size: 13px;
      color: #166534;
      line-height: 1.5;
    }
  `;
  document.head.appendChild(style);

  // 2. Welcome Banner on Preview Links
  if (isReviewUrl) {
    const banner = document.createElement('div');
    banner.className = 'dnk-welcome-banner';
    banner.innerHTML = `
      <div>
        <strong>✨ Режим узгодження проекту активовано.</strong>
        <span style="opacity:0.85; margin-left:8px;">Виділяйте будь-яку область мишкою або клікайте на елементи для правок нашому агенту.</span>
      </div>
      <button class="dnk-welcome-close" title="Закрити">&times;</button>
    `;
    document.body.appendChild(banner);
    banner.querySelector('.dnk-welcome-close').addEventListener('click', () => banner.remove());
  }

  // 3. Floating Control Bar
  const bar = document.createElement('div');
  bar.className = 'dnk-control-bar';
  bar.innerHTML = `
    <button class="dnk-bar-btn" id="dnk-btn-mode-area" title="Затисніть і виділіть область на екрані">
      <span>📐</span> <span>Виділити область</span>
    </button>
    <button class="dnk-bar-btn" id="dnk-btn-mode-element" title="Клік на конкретний елемент або кнопку">
      <span>📌</span> <span>Клік на елемент</span>
    </button>
    <button class="dnk-bar-btn" id="dnk-btn-pins" title="Список розміщених заміток">
      <span>📍</span> <span id="dnk-pin-count">Замітки (0)</span>
    </button>
  `;
  document.body.appendChild(bar);

  const btnArea = bar.querySelector('#dnk-btn-mode-area');
  const btnElem = bar.querySelector('#dnk-btn-mode-element');
  const btnPins = bar.querySelector('#dnk-btn-pins');

  btnArea.addEventListener('click', () => setMode(currentMode === 'area' ? 'idle' : 'area'));
  btnElem.addEventListener('click', () => setMode(currentMode === 'element' ? 'idle' : 'element'));
  btnPins.addEventListener('click', () => togglePins());

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

  // 4. Area Drag Selection Engine
  document.addEventListener('mousedown', (e) => {
    if (currentMode !== 'area') return;
    if (e.target.closest('.dnk-control-bar') || e.target.closest('.dnk-modal-overlay') || e.target.closest('.dnk-welcome-banner')) return;

    isDragging = true;
    startX = e.clientX;
    startY = e.clientY;
    pageStartX = e.pageX;
    pageStartY = e.pageY;

    if (!selectionBox) {
      selectionBox = document.createElement('div');
      selectionBox.className = 'dnk-selection-marquee';
      document.body.appendChild(selectionBox);
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
      if (e.target.closest('.dnk-control-bar') || e.target.closest('.dnk-modal-overlay')) return;
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
          viewport_h: window.innerHeight
        };

        const targetEl = document.elementFromPoint(left + width / 2, top + height / 2) || document.body;
        setMode('idle');
        openFeedbackModal({ targetEl, bbox, isArea: true, pageLeft, pageTop });
      } else {
        if (selectionBox) { selectionBox.remove(); selectionBox = null; }
      }
    }
  });

  // 5. Element Click Inspection
  document.addEventListener('click', (e) => {
    if (currentMode !== 'element') return;
    if (e.target.closest('.dnk-control-bar') || e.target.closest('.dnk-modal-overlay') || e.target.closest('.dnk-welcome-banner')) return;

    e.preventDefault();
    e.stopPropagation();

    const targetEl = e.target;
    if (hoveredEl) hoveredEl.classList.remove('dnk-inspect-hover');
    setMode('idle');

    const rect = targetEl.getBoundingClientRect();
    const bbox = {
      x: rect.left,
      y: rect.top,
      width: rect.width,
      height: rect.height,
      page_x: rect.left + window.scrollX,
      page_y: rect.top + window.scrollY,
      scroll_x: window.scrollX,
      scroll_y: window.scrollY,
      viewport_w: window.innerWidth,
      viewport_h: window.innerHeight
    };

    openFeedbackModal({ targetEl, bbox, isArea: false, pageLeft: bbox.page_x, pageTop: bbox.page_y });
  });

  function updateMarquee(x, y, w, h) {
    selectionBox.style.left = `${x}px`;
    selectionBox.style.top = `${y}px`;
    selectionBox.style.width = `${w}px`;
    selectionBox.style.height = `${h}px`;
    selectionBox.innerHTML = `<span class="dnk-dim-badge">${Math.round(w)} × ${Math.round(h)} px</span>`;
  }

  function extractShopifyMeta(el) {
    const sectionEl = el.closest('[id^="shopify-section-"]') || el.closest('[data-section-id]');
    const blockEl = el.closest('[data-block-id]') || el.closest('[data-shopify-editor-block]');
    
    const sectionId = sectionEl ? (sectionEl.getAttribute('data-section-id') || sectionEl.id.replace('shopify-section-', '')) : 'global';
    const blockId = blockEl ? (blockEl.getAttribute('data-block-id') || blockEl.getAttribute('data-shopify-editor-block') || '') : '';
    
    let selector = el.tagName ? el.tagName.toLowerCase() : 'body';
    if (el.id) selector = `#${el.id}`;
    else if (el.className && typeof el.className === 'string') {
      const cls = el.className.split(' ').filter(c => c && !c.startsWith('dnk-'))[0];
      if (cls) selector = `${el.tagName.toLowerCase()}.${cls}`;
    }

    const breadcrumb = `Секція: ${sectionId} ${blockId ? `| Блок: ${blockId}` : ''}`;
    return { sectionId, blockId, selector, breadcrumb };
  }

  function openFeedbackModal({ targetEl, bbox, isArea, pageLeft, pageTop }) {
    const meta = extractShopifyMeta(targetEl);
    const pinNumber = pinCounter++;

    const overlay = document.createElement('div');
    overlay.className = 'dnk-modal-overlay';
    overlay.innerHTML = `
      <div class="dnk-modal-box">
        <div class="dnk-modal-title">
          <span>📍 Правка для агента супроводження</span>
          <span style="float:right; font-size:12px; font-family:monospace; color:#008060; font-weight:700;">#${pinNumber}</span>
        </div>
        <div class="dnk-modal-sub">
          <strong>${isArea ? '📐 Виділена область' : '📌 Елемент'}:</strong> ${meta.breadcrumb}<br>
          Розмір: ${Math.round(bbox.width)} × ${Math.round(bbox.height)} px · Селектор: ${meta.selector}
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
    document.body.appendChild(overlay);

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
          renderPersistentPin(pageLeft, pageTop, pinNumber, title, comment, data.category);
          showAgentReplyInModal(overlay, data.client_acknowledgment, data.quota_remaining);
        } else {
          fallbackOffline(pageLeft, pageTop, pinNumber, payload, overlay);
        }
      } catch (e) {
        fallbackOffline(pageLeft, pageTop, pinNumber, payload, overlay);
      }

      if (selectionBox) { selectionBox.remove(); selectionBox = null; }
    });
  }

  function showAgentReplyInModal(overlay, replyText, quotaRemaining) {
    const replyBox = overlay.querySelector('#dnk-modal-agent-reply');
    replyBox.className = 'dnk-agent-reply-box';
    replyBox.style.display = 'block';
    replyBox.innerHTML = `
      <strong>💬 Відповідь Агента Клієнтського Супроводження:</strong><br>
      ${replyText}<br><br>
      <span style="font-size:11.5px; opacity:0.85;">Залишок раундів правок: <strong>${quotaRemaining}</strong></span>
    `;

    const btnRow = overlay.querySelector('#dnk-modal-btn-row');
    btnRow.innerHTML = `<button type="button" class="dnk-btn-submit" id="dnk-btn-ok">Зрозуміло, дякую!</button>`;
    btnRow.querySelector('#dnk-btn-ok').addEventListener('click', () => overlay.remove());
  }

  function renderPersistentPin(x, y, num, title, comment, category) {
    const pin = document.createElement('div');
    pin.className = 'dnk-pin-marker';
    pin.style.left = `${Math.max(10, x)}px`;
    pin.style.top = `${Math.max(10, y)}px`;
    pin.textContent = num;
    pin.title = `#${num}: ${title} - ${comment}`;
    pin.addEventListener('click', () => {
      alert(`📍 Правка #${num} (${category || 'in_scope'}):\n\n${title}\n${comment}`);
    });
    document.body.appendChild(pin);

    // Update pin counter button
    const countEl = document.getElementById('dnk-pin-count');
    if (countEl) {
      const currentPins = document.querySelectorAll('.dnk-pin-marker').length;
      countEl.textContent = `Замітки (${currentPins})`;
    }
  }

  function fallbackOffline(x, y, num, payload, overlay) {
    const queue = JSON.parse(localStorage.getItem('dnk_client_tickets') || '[]');
    queue.push(payload);
    localStorage.setItem('dnk_client_tickets', JSON.stringify(queue));
    renderPersistentPin(x, y, num, payload.title, payload.comment, 'offline');
    if (overlay) {
      showAgentReplyInModal(
        overlay,
        `Правку #${num} успішно зафіксовано на сторінці та збережено. Агент клієнтського супроводження отримав завдання в роботу.`,
        '2 / 3 раунди'
      );
    }
  }

  function togglePins() {
    const pins = document.querySelectorAll('.dnk-pin-marker');
    if (pins.length === 0) {
      alert('На цій сторінці ще немає розміщених заміток. Виділіть область або клікніть на елемент, щоб створити першу!');
      return;
    }
    const isHidden = pins[0].style.display === 'none';
    pins.forEach(p => p.style.display = isHidden ? 'flex' : 'none');
  }
})();

/* Quantity breaks V2 extras, loaded by blocks/product_quantity-breaks-v2.liquid after the core script: the popups of
   Product choice, Bundle builder and Free gift "One product of their choice", scratch cards, the live Schedule switch,
   the Next-tier nudge and the tiers the cart nudge reads, discount codes of "Discount code" options, pack variants,
   option-level selling plans and the shrine:qb:* events for apps and pixels. Each widget is driven only through the
   API of <quantity-breaks-v2> (component-quantity-breaks-v2.js). */
(() => {
  if (window.ShrineQBV2Extras) return;
  window.ShrineQBV2Extras = true;

  const report = (error) => console.error('Quantity breaks V2', error);
  const SCRATCH_KEY = 'shrine-qb-scratch';
  const TIERS_KEY = 'shrine-qb-tiers';
  const CODES_KEY = 'shrine-qb-codes';
  const DAY = 864e5;
  // qbv2:change reasons a shopper causes; only these send shrine:qb:select
  const SHOPPER = ['select', 'stepper', 'choice', 'builder', 'gift-choice', 'upsell', 'scratch', 'nudge'];
  // Plan fields main.js looks for besides the form's own (M:1532-1535)
  const PLAN_APPS = '.appstle-active-option [name="selling_plan"], .sls-purchase [name="selling_plan"], skio-plan-picker [name="selling_plan"]';
  const DRAWER_SECTIONS = ['cart-drawer', 'cart-icon-bubble'];
  const CLOSE_ICON = '<svg aria-hidden="true" focusable="false" class="icon icon-close" viewBox="0 0 16 16"><path d="M2 2l12 12M14 2L2 14" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" fill="none"/></svg>';

  const int = (value, fallback = 0) => {
    const number = parseInt(value, 10);
    return Number.isNaN(number) ? fallback : number;
  };
  const same = (a, b) => String(a == null ? '' : a).trim().toLowerCase() === String(b == null ? '' : b).trim().toLowerCase();
  const escapeHtml = (value) => String(value == null ? '' : value).replace(/[&<>"']/g, (char) => `&#${char.charCodeAt(0)};`);
  const fill = (text, values) => String(text || '').replace(/\[([a-z_]+)\]/g, (match, key) => (key in values ? values[key] : match));
  const fire = (element) => element.dispatchEvent(new Event('change', { bubbles: true }));
  const toId = (value) => (/^\d+$/.test(String(value)) ? Number(value) : value);
  const readJson = (element) => {
    try {
      return element ? JSON.parse(element.textContent) : null;
    } catch (error) {
      return null;
    }
  };
  const copy = (value) => JSON.parse(JSON.stringify(value === undefined ? null : value));
  const reducedMotion = () => Boolean(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  const api = () => window.ShrineQBV2;
  const storage = (session) => ({
    get: (key, fallback) => (session ? api().storage.sget(key, fallback) : api().storage.get(key, fallback)),
    set: (key, value) => (session ? api().storage.sset(key, value) : api().storage.set(key, value)),
  });
  const route = (name, fallback) => (window.routes && window.routes[name]) || fallback;
  // Read with GET; write with a JSON POST. Failures resolve to null: a code never blocks the shopper
  const cartRequest = (path, body, keepalive = false) => fetch(path, body === undefined
    ? { headers: { Accept: 'application/json' } }
    : { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify(body), keepalive })
    .then((response) => (response.ok ? response.json() : null))
    .catch(() => null);
  // 2.0.0 carts: one queue for theme cart writes (component-cart.js); keepalive posts stay direct
  const queued = (payload, options) => {
    const requests = window.ShrineCartRequests;
    if (!requests || typeof requests.update !== 'function') return null;
    return requests.update(payload, Object.assign({ source: 'upsells:qb-codes', publish: false }, options))
      .then((result) => (result && result.cart ? Object.assign({}, result.cart, { rendered: Boolean(result.ok && !result.skipped && options.render) }) : null), () => null);
  };
  const codeList = (list) => (Array.isArray(list)
    ? list.map((entry) => ({ code: String((entry && entry.code) || ''), applicable: Boolean(entry) && entry.applicable !== false })).filter((entry) => entry.code)
    : null);
  const hasCode = (list, code) => (list || []).some((entry) => same(entry.code, code));
  // A picker's native selects in option order
  const pickerSelects = (scope) => Array.from(scope.querySelectorAll('.qb-v2-picker'))
    .sort((a, b) => int(a.dataset.optionPosition) - int(b.dataset.optionPosition))
    .map((picker) => picker.querySelector('select'))
    .filter(Boolean);
  const variantImage = (product, variant) => {
    const images = (product && product.images) || {};
    const options = (variant && variant.options) || [];
    const at = options.findIndex((value, index) => images[`${index + 1}|${value}`]);
    return at >= 0 ? images[`${at + 1}|${options[at]}`] : (product && product.image) || '';
  };

  const states = new WeakMap();

  class Extras {
    constructor(qbv2) {
      this.q = qbv2;
      this.controller = new AbortController();
      this.timers = {};
      this.observers = [];
      this.touchedAt = 0;
      this.skipAt = 0;
    }

    // ---------- Lifecycle ----------
    start() {
      const q = this.q;
      this.design = Boolean(q.designMode);
      this.money = q.money || api().money.create(q);
      this.selected = q.getSelected();
      // shrine:qb:select only follows changes a shopper made: their change arrives in the same task as a trusted input
      ['pointerdown', 'click', 'keydown', 'change', 'input'].forEach((type) => this.on(q, type, (event) => {
        if (event.isTrusted) this.touchedAt = Date.now();
      }, { capture: true }));
      this.on(q, 'click', (event) => this.onClick(event));
      this.on(q, 'qbv2:change', (event) => event.target === q && this.onChange(event.detail || {}));
      this.on(q, 'qbv2:before-add', (event) => event.target === q && this.onBeforeAdd(event.detail || {}));
      this.on(q, 'qbv2:added', (event) => event.target === q && this.onAdded(event.detail || {}));
      this.on(q, 'qbv2:active', (event) => event.target === q && this.onActive(event.detail || {}));
      // The skip-cart button redirects to checkout right after the add (M:1847). On window, so it runs before the core's
      // capture listener on document, which starts the add with today's main.js
      this.on(window, 'click', (event) => {
        const button = event.isTrusted && event.target instanceof Element && event.target.closest('[data-skip-cart-button="true"]');
        if (button && (button.id === `SectionAtcBtn-${q.sectionId}` || (q.form && q.form.contains(button)))) this.skipAt = Date.now();
      }, { capture: true });
      this.guard(() => this.initPlans());
      this.guard(() => this.initScratches());
      this.guard(() => this.initSchedule());
      this.guard(() => this.initPacks());
      this.guard(() => this.renderNudges());
      this.guard(() => this.writeTiers());
      this.guard(() => this.initCodes());
    }

    stop() {
      if (this.stopped) return;
      this.stopped = true;
      this.restoreCartUrl();
      this.closeDialog();
      // The next start (the core restarted this widget) builds its own popup with the same id
      if (this.dialog) this.dialog.remove();
      this.controller.abort();
      Object.values(this.timers).forEach(clearTimeout);
      this.observers.forEach((observer) => observer.disconnect());
      if (this.planInput) this.planInput.remove();
      this.togglePackRows(false);
    }

    alive() {
      if (!this.stopped && this.q.isConnected && this.q.ready) return true;
      this.stop();
      return false;
    }

    guard(callback) {
      try {
        return callback();
      } catch (error) {
        return report(error);
      }
    }

    on(target, type, handler, options = {}) {
      if (target) target.addEventListener(type, (event) => this.guard(() => handler(event)), { ...options, signal: this.controller.signal });
    }

    later(name, delay, callback) {
      clearTimeout(this.timers[name]);
      this.timers[name] = setTimeout(() => this.alive() && this.guard(callback), delay);
    }

    // ---------- Events from the core ----------
    onChange({ reason }) {
      if (!this.alive()) return;
      const selected = this.q.getSelected();
      const moved = selected !== this.selected;
      this.selected = selected;
      this.syncPlanInput();
      this.renderNudges();
      this.syncPacks(reason, moved);
      if (reason === 'variant') this.later('tiers', 500, () => this.writeTiers());
      if (moved && !this.design && ['select', 'nudge', 'scratch'].includes(reason)) this.later('code', 600, () => this.queueCodes(selected, false));
      if (SHOPPER.includes(reason) && Date.now() - this.touchedAt < 400) this.later('select', 300, () => this.track('select'));
    }

    onBeforeAdd({ option, lines }) {
      // Another plan field may have appeared since the last check; main.js reads the form right after this event
      if (this.planInput && this.planConflict()) this.blockPlans();
      this.track('add', option, lines);
      this.codeBeforeAdd(option);
    }

    onAdded({ option, lines }) {
      this.track('added', option, lines);
      Promise.resolve(this.codeAfterAdd()).catch(report);
    }

    onActive({ active }) {
      if (!active) this.closeDialog();
      this.togglePackRows(active);
      this.syncPlanInput();
      this.renderNudges();
      this.later('tiers', 500, () => this.writeTiers());
    }

    onClick(event) {
      const target = event.target instanceof Element ? event.target : null;
      let action = target && target.closest('[data-qb-action]');
      // A tap on a button of an option that wasn't selected lands on the option (its body is inert); the core has
      // selected it by now, so the button under the pointer runs as well
      const option = !action && event.detail && target && target.closest('.qb-v2-option');
      if (option) {
        const hit = document.elementFromPoint(event.clientX, event.clientY);
        action = hit && option.contains(hit) && hit.closest('[data-qb-action]');
      }
      if (!action || !this.q.contains(action) || (this.dialog && this.dialog.contains(action))) return;
      const kind = action.dataset.qbAction;
      if (kind === 'choice' || kind === 'builder' || kind === 'gift-choice') {
        const child = action.closest(`[data-qb-child="${kind === 'gift-choice' ? 'gift' : kind}"]`);
        if (child) this.openDialog(kind === 'gift-choice' ? 'gift' : kind, child, action);
      } else if (kind === 'nudge') {
        const nudge = action.closest('[data-qb-child="nudge"]');
        if (nudge && nudge.qbNext) this.q.selectOption(nudge.qbNext, { source: 'nudge' });
      } else if (kind === 'scratch-reveal') {
        const card = action.closest('[data-qb-child="scratch"]');
        if (card && card.qbScratch) this.reveal(card.qbScratch, { focus: true });
      }
    }

    // ---------- Popups: Product choice, Bundle builder, gift choice ----------
    dialogElement() {
      if (this.dialog && this.dialog.isConnected) return this.dialog;
      const q = this.q;
      const id = `qbv2-${q.sectionId}-${q.blockId}-dialog`;
      const dialog = document.createElement('dialog');
      dialog.className = 'qb-v2-dialog';
      dialog.id = id;
      dialog.setAttribute('aria-labelledby', `${id}-title`);
      dialog.innerHTML = `<div class="qb-v2-dialog__header"><h2 class="qb-v2-dialog__title" id="${escapeHtml(id)}-title"></h2><button type="button" class="qb-v2-dialog__close">${CLOSE_ICON}</button></div><div class="qb-v2-dialog__body"></div>`;
      // Inside the widget: its variables and card styles apply; showModal() puts it in the top layer, so animated
      // sections (transform, filter) can't clip it
      q.append(dialog);
      this.on(dialog, 'click', (event) => this.onDialogClick(event));
      this.on(dialog, 'change', (event) => this.onDialogChange(event));
      // A press that starts and ends on the backdrop closes it; a drag out of the panel doesn't
      this.on(dialog, 'pointerdown', (event) => { this.backdropPress = event.target === dialog; });
      // Chrome sends close in the next rendering frame (none in a background tab): Esc's cancel is followed up at once
      this.on(dialog, 'close', () => this.onDialogClose());
      this.on(dialog, 'cancel', () => setTimeout(() => this.guard(() => !dialog.open && this.onDialogClose())));
      this.dialog = dialog;
      return dialog;
    }

    closeDialog() {
      if (this.dialog && this.dialog.open) this.dialog.close();
      this.onDialogClose();
    }

    // Carried gift copies print no product JSON: the template of the gift's original has it
    templateFor(kind, child) {
      if (kind !== 'gift') return child.querySelector('template[data-qb-candidates]');
      const roots = Array.from(this.q.querySelectorAll('[data-qb-child="gift"]')).filter((root) => root.dataset.qbBlock === child.dataset.qbBlock);
      roots.sort((a, b) => Number(b.dataset.qbGiftOrigin === 'self') - Number(a.dataset.qbGiftOrigin === 'self'));
      const withJson = roots.map((root) => root.querySelector('template[data-qb-candidates]')).find((template) => template && template.content.querySelector('script[data-qbv2-product]'));
      return withJson || child.querySelector('template[data-qb-candidates]');
    }

    openDialog(kind, child, opener) {
      const q = this.q;
      const option = child.closest('.qb-v2-option');
      // The body of an option that isn't selected is inert on the storefront; the editor may preview any popup
      if (option && !this.design && !option.classList.contains('is-selected')) return;
      const template = this.templateFor(kind, child);
      if (!template) return;
      const dialog = this.dialogElement();
      if (dialog.open) return;
      dialog.querySelector('.qb-v2-dialog__title').textContent = template.dataset.qbHeading || opener.textContent.trim();
      dialog.querySelector('.qb-v2-dialog__close').setAttribute('aria-label', template.dataset.qbCloseLabel || '');
      const body = dialog.querySelector('.qb-v2-dialog__body');
      body.replaceChildren(template.content.cloneNode(true));
      const old = dialog.querySelector('.qb-v2-dialog__footer');
      if (old) old.remove();
      const ctx = {
        kind,
        child,
        opener,
        compareSource: (option && option.dataset.qbCompareSource) || 'compare_price',
        discount: kind === 'gift' ? { type: 'free', value: 0 } : { type: child.dataset.qbDiscountType || 'none', value: int(child.dataset.qbDiscountValue) },
        cards: Array.from(body.querySelectorAll('[data-qb-candidate]')),
      };
      // What the slot, row or tray holds now: that card is marked and starts on that variant
      let chosen = {};
      if (kind === 'choice') chosen = Object.assign({}, (child.querySelector('[data-qb-choice-slot] [data-qb-item]') || {}).dataset);
      if (kind === 'gift') chosen = Object.assign({}, (child.querySelector('[data-qb-gift-row][data-qb-chosen="true"] [data-qb-item]') || child.querySelector('[data-qb-gift-row] [data-qb-item]') || {}).dataset);
      if (kind === 'builder') {
        ctx.max = Math.max(1, int(child.dataset.qbPicks, 1));
        ctx.repeats = child.dataset.qbAllowRepeats !== 'false';
        ctx.units = [];
        (child._qbPicks || []).forEach((pick) => {
          for (let i = 0; i < Math.max(1, int(pick.quantity, 1)); i += 1) ctx.units.push({ productId: String(pick.productId), variantId: String(pick.variantId), image: pick.image || '' });
        });
        const footer = document.createElement('div');
        footer.className = 'qb-v2-dialog__footer';
        footer.innerHTML = '<span class="qb-v2-dialog__tray" aria-hidden="true"></span><span class="qb-v2-dialog__count" aria-live="polite"></span><button type="button" class="button qb-v2-dialog__done"></button>';
        footer.querySelector('.qb-v2-dialog__done').textContent = template.dataset.qbDoneLabel || '';
        dialog.append(footer);
      }
      ctx.cards.forEach((card) => {
        const product = readJson(card.querySelector('script[data-qbv2-product]')) || (q.products && q.products.get(String(card.dataset.productId))) || null;
        card.qbProduct = product;
        const image = card.querySelector('.qb-v2-cand__media img');
        if (image) card.qbImage = { src: image.getAttribute('src'), srcset: image.getAttribute('srcset'), sizes: image.getAttribute('sizes') };
        card.qbServerVariant = card.dataset.variantId;
        let start = card.dataset.variantId;
        if (kind === 'builder') {
          const mine = ctx.units.filter((unit) => unit.productId === String(card.dataset.productId));
          if (mine.length) start = mine[mine.length - 1].variantId;
        } else if (chosen.productId && String(chosen.productId) === String(card.dataset.productId)) {
          start = chosen.variantId || start;
          card.classList.add('is-picked');
        }
        const variants = (product && product.variants) || [];
        const variant = variants.find((entry) => String(entry.id) === String(start)) || variants.find((entry) => String(entry.id) === String(card.dataset.variantId));
        if (variant) this.setCardVariant(card, ctx, variant);
      });
      if (kind === 'builder') this.renderBuilder(ctx);
      this.ctx = ctx;
      dialog.showModal();
      document.documentElement.classList.add('qb-v2-dialog-open');
    }

    // Runs once per opening, whichever way the popup closed
    onDialogClose() {
      const ctx = this.ctx;
      if (!ctx) return;
      this.ctx = null;
      if (!document.querySelector('.qb-v2-dialog[open]')) document.documentElement.classList.remove('qb-v2-dialog-open');
      // Picks survive closing the popup any way, not only with Done
      if (ctx && ctx.kind === 'builder' && !this.stopped) this.commitBuilder(ctx);
      const dialog = this.dialog;
      if (dialog) {
        dialog.querySelector('.qb-v2-dialog__body').replaceChildren();
        const footer = dialog.querySelector('.qb-v2-dialog__footer');
        if (footer) footer.remove();
      }
      if (ctx && ctx.opener && ctx.opener.isConnected) ctx.opener.focus({ preventScroll: true });
    }

    onDialogClick(event) {
      const dialog = this.dialog;
      const ctx = this.ctx;
      const target = event.target;
      if (target === dialog) {
        if (this.backdropPress) this.closeDialog();
        return;
      }
      if (!ctx || !(target instanceof Element)) return;
      if (target.closest('.qb-v2-dialog__close')) {
        this.closeDialog();
        return;
      }
      if (target.closest('.qb-v2-dialog__done')) {
        this.commitBuilder(ctx);
        this.closeDialog();
        return;
      }
      const card = target.closest('[data-qb-candidate]');
      if (!card) return;
      const step = target.closest('[data-qb-cand-step]');
      if (step && ctx.kind === 'builder') {
        if (!step.disabled) this.stepBuilder(ctx, card, int(step.dataset.qbCandStep));
        return;
      }
      const choose = target.closest('[data-qb-cand-action="choose"]');
      if (!choose || choose.disabled) return;
      const pick = { productId: card.dataset.productId, variantId: card.dataset.variantId };
      const done = ctx.kind === 'gift' ? this.q.setGiftChoice(ctx.child, pick.productId, pick.variantId) : this.q.setChoice(ctx.child, pick);
      if (done !== false) this.closeDialog();
    }

    // A candidate's own picker: the closest variant that keeps the value just picked
    onDialogChange(event) {
      const select = event.target;
      const card = select instanceof Element && select.closest('[data-qb-candidate]');
      const ctx = this.ctx;
      const product = card && card.qbProduct;
      if (!ctx || !product || !select.matches('select')) return;
      const selects = pickerSelects(card);
      const position = selects.indexOf(select);
      const matches = (product.variants || []).filter((variant) => (variant.options || [])[position] === select.value);
      const variant = api().resolveVariant(product, selects.map((entry) => entry.value)) || matches.find((entry) => entry.available !== false) || matches[0];
      if (!variant) return;
      this.setCardVariant(card, ctx, variant);
      if (ctx.kind === 'builder') this.renderBuilder(ctx);
    }

    setCardVariant(card, ctx, variant) {
      const product = card.qbProduct;
      const available = variant.available !== false;
      card.dataset.variantId = String(variant.id);
      card.dataset.available = String(available);
      const selects = pickerSelects(card);
      selects.forEach((select, index) => {
        const value = (variant.options || [])[index];
        if (value !== undefined && select.value !== value) select.value = value;
      });
      this.updateStatuses(selects, product, variant);
      // Card price: the units one pick adds, minus the block's discount (contract 5.4); a gift card shows its value
      const quantity = Math.max(1, int(card.dataset.quantity, 1));
      const line = api().price.extraLine(
        { role: ctx.kind === 'gift' ? 'choice' : ctx.kind, quantity, price: int(variant.price), compare: ctx.kind === 'gift' ? 0 : int(variant.compare_at_price) },
        ctx.discount,
        { rate: this.q.rate, compareSource: ctx.kind === 'gift' ? 'compare_price' : ctx.compareSource },
      );
      const price = card.querySelector('[data-qb-item-price]');
      if (price) price.innerHTML = this.money.html(line.total);
      const compare = card.querySelector('[data-qb-item-compare]');
      if (compare) {
        compare.innerHTML = this.money.html(line.compare);
        compare.classList.toggle('hidden', !(line.compare > line.total));
      }
      // The server image (with its srcset) for the server's variant, the variant's own image otherwise
      const image = card.querySelector('.qb-v2-cand__media img');
      if (image && card.qbImage) {
        const server = String(variant.id) === String(card.qbServerVariant);
        const src = server ? card.qbImage.src : variantImage(product, variant);
        if (src && image.getAttribute('src') !== src) {
          ['srcset', 'sizes'].forEach((name) => (server && card.qbImage[name] ? image.setAttribute(name, card.qbImage[name]) : image.removeAttribute(name)));
          image.src = src;
        }
      }
      const choose = card.querySelector('[data-qb-cand-action="choose"]');
      if (choose) choose.disabled = !available;
    }

    // The server marked values against the default variant only. Same rule as the core's extra pickers: each position
    // against the values before it, so every value of the first position stays reachable
    updateStatuses(selects, product, variant) {
      const hideSoldOut = /hidden/.test(this.q.dataset.qbTSoldoutAttr || '');
      const template = (window.variantStrings && window.variantStrings.unavailable_with_option) || '';
      const chosen = variant.options || [];
      selects.forEach((select, position) => {
        const candidates = ((product && product.variants) || []).filter((entry) => (entry.options || []).slice(0, position).every((value, index) => value === chosen[index]));
        Array.from(select.options).forEach((option) => {
          const matches = candidates.filter((entry) => (entry.options || [])[position] === option.value);
          const missing = !matches.length;
          const soldOut = !missing && matches.every((entry) => entry.available === false);
          option.classList.toggle('non-existent', missing);
          option.classList.toggle('unavailable', soldOut);
          option.disabled = option.hidden = (missing || (soldOut && hideSoldOut)) && option.value !== chosen[position];
          const label = (missing || soldOut) && template ? template.replace('[value]', option.value) : option.value;
          if (option.textContent !== label) option.textContent = label;
        });
      });
    }

    // Builder picks are units: each keeps the variant its card showed when it was added
    stepBuilder(ctx, card, step) {
      const productId = String(card.dataset.productId);
      if (step > 0) {
        const count = ctx.units.filter((unit) => unit.productId === productId).length;
        if (ctx.units.length >= ctx.max || (!ctx.repeats && count > 0) || card.dataset.available === 'false') return;
        const product = card.qbProduct;
        const variant = product && (product.variants || []).find((entry) => String(entry.id) === card.dataset.variantId);
        ctx.units.push({ productId, variantId: card.dataset.variantId, image: (variant && variantImage(product, variant)) || (card.qbImage && card.qbImage.src) || '' });
      } else {
        let index = -1;
        ctx.units.forEach((unit, i) => {
          if (unit.productId === productId && (index < 0 || unit.variantId === card.dataset.variantId)) index = i;
        });
        if (index < 0) return;
        ctx.units.splice(index, 1);
      }
      this.renderBuilder(ctx, card);
    }

    renderBuilder(ctx, focusCard) {
      const total = ctx.units.length;
      const active = document.activeElement;
      ctx.cards.forEach((card) => {
        const count = ctx.units.filter((unit) => unit.productId === String(card.dataset.productId)).length;
        const value = card.querySelector('[data-qb-cand-count]');
        if (value && value.textContent !== String(count)) value.textContent = String(count);
        card.classList.toggle('is-picked', count > 0);
        card.querySelectorAll('[data-qb-cand-step]').forEach((button) => {
          button.disabled = int(button.dataset.qbCandStep) < 0 ? count === 0 : total >= ctx.max || (!ctx.repeats && count > 0) || card.dataset.available === 'false';
        });
      });
      const footer = this.dialog && this.dialog.querySelector('.qb-v2-dialog__footer');
      if (!footer) return;
      footer.querySelector('.qb-v2-dialog__tray').innerHTML = Array.from({ length: ctx.max }, (_, index) => {
        const unit = ctx.units[index];
        return unit ? `<span class="qb-v2-builder__slot is-filled">${unit.image ? `<img src="${escapeHtml(unit.image)}" alt="" width="32" height="32" loading="lazy">` : ''}</span>` : '<span class="qb-v2-builder__slot">?</span>';
      }).join('');
      footer.querySelector('.qb-v2-dialog__count').textContent = `${total} / ${ctx.max}`;
      // A step button that just turned disabled had focus: the next useful control takes it
      if (focusCard && active && active.disabled && focusCard.contains(active)) {
        const other = focusCard.querySelector('[data-qb-cand-step]:not(:disabled)');
        (total >= ctx.max ? footer.querySelector('.qb-v2-dialog__done') : other || footer.querySelector('.qb-v2-dialog__done')).focus();
      }
    }

    commitBuilder(ctx) {
      const picks = [];
      ctx.units.forEach((unit) => {
        const pick = picks.find((entry) => entry.variantId === unit.variantId);
        if (pick) pick.quantity += 1;
        else picks.push({ productId: unit.productId, variantId: unit.variantId, quantity: 1 });
      });
      const key = (list) => JSON.stringify((list || []).map((pick) => [String(pick.variantId), int(pick.quantity, 1)]).sort());
      if (key(picks) !== key(ctx.child._qbPicks)) this.q.setBuilderPicks(ctx.child, picks);
    }

    // ---------- Scratch card ----------
    initScratches() {
      const saved = this.design ? {} : storage(false).get(SCRATCH_KEY, {}) || {};
      this.q.querySelectorAll('.qb-v2-option [data-qb-child="scratch"]').forEach((card) => {
        const optionEl = card.closest('.qb-v2-option');
        const scratch = { card, optionEl, canvas: card.querySelector('canvas'), key: `${this.q.dataset.productId}:${card.dataset.qbBlock || optionEl.dataset.qbV2Option}` };
        card.qbScratch = scratch;
        if (saved[scratch.key]) {
          this.reveal(scratch, { instant: true, store: false, select: false });
          return;
        }
        const point = (event) => {
          const box = card.getBoundingClientRect();
          return { x: event.clientX - box.left, y: event.clientY - box.top };
        };
        this.on(card, 'pointerdown', (event) => {
          if (scratch.revealed || !event.isPrimary || (event.pointerType === 'mouse' && event.button !== 0) || event.target.closest('[data-qb-action]')) return;
          // In the editor one click shows the deal; nothing is stored
          if (this.design) {
            this.reveal(scratch, { store: false });
            return;
          }
          if (!scratch.context) this.paint(scratch);
          try {
            card.setPointerCapture(event.pointerId);
          } catch (error) {
            // Capture only keeps a stroke going outside the card
          }
          scratch.last = point(event);
          scratch.moves = 0;
          this.scratchAt(scratch, scratch.last, scratch.last);
        });
        this.on(card, 'pointermove', (event) => {
          if (!scratch.last || !event.isPrimary) return;
          if (!event.buttons) {
            this.endStroke(scratch);
            return;
          }
          const next = point(event);
          this.scratchAt(scratch, scratch.last, next);
          scratch.last = next;
          scratch.moves += 1;
          if (scratch.moves % 8 === 0 && this.cleared(scratch) >= 0.45) this.reveal(scratch);
        });
        // A vertical swipe pans the page (touch-action: pan-y) and ends the stroke with pointercancel
        ['pointerup', 'pointercancel', 'lostpointercapture'].forEach((type) => this.on(card, type, () => this.endStroke(scratch)));
        // Painted now when the card has a size (observer callbacks wait for a rendering frame), again when it resizes
        this.paint(scratch);
        if (typeof ResizeObserver !== 'function') return;
        const observer = new ResizeObserver(() => this.guard(() => {
          if (!this.alive() || scratch.revealed || scratch.last) return;
          if (`${card.clientWidth}x${card.clientHeight}` !== scratch.size) this.paint(scratch);
        }));
        observer.observe(card);
        scratch.observer = observer;
        this.observers.push(observer);
      });
    }

    // The cover the CSS paints first (from, to, from at 135deg), on a canvas sized in device pixels; the text stays HTML
    paint(scratch) {
      const { card, canvas } = scratch;
      const width = card.clientWidth;
      const height = card.clientHeight;
      if (!canvas || !width || !height) return;
      const ratio = Math.min(window.devicePixelRatio || 1, 3);
      canvas.width = Math.round(width * ratio);
      canvas.height = Math.round(height * ratio);
      const context = canvas.getContext('2d', { willReadFrequently: true });
      if (!context) return;
      context.setTransform(ratio, 0, 0, ratio, 0, 0);
      const style = getComputedStyle(card);
      const from = style.getPropertyValue('--qb-v2-scratch-from').trim() || '#d4af37';
      const to = style.getPropertyValue('--qb-v2-scratch-to').trim() || '#f4e3a1';
      const reach = (width + height) / 4;
      const gradient = context.createLinearGradient(width / 2 - reach, height / 2 - reach, width / 2 + reach, height / 2 + reach);
      gradient.addColorStop(0, from);
      gradient.addColorStop(0.5, to);
      gradient.addColorStop(1, from);
      context.globalCompositeOperation = 'source-over';
      context.fillStyle = gradient;
      context.fillRect(0, 0, width, height);
      context.globalCompositeOperation = 'destination-out';
      context.lineWidth = 44;
      context.lineCap = 'round';
      context.lineJoin = 'round';
      scratch.context = context;
      scratch.size = `${width}x${height}`;
    }

    scratchAt(scratch, from, to) {
      const context = scratch.context;
      if (!context) return;
      context.beginPath();
      if (from === to) {
        context.arc(to.x, to.y, 22, 0, Math.PI * 2);
        context.fill();
        return;
      }
      context.moveTo(from.x, from.y);
      context.lineTo(to.x, to.y);
      context.stroke();
    }

    endStroke(scratch) {
      if (!scratch.last) return;
      scratch.last = null;
      if (!scratch.revealed && this.cleared(scratch) >= 0.45) this.reveal(scratch);
    }

    // Every 64th pixel is enough to estimate how much of the cover is gone
    cleared(scratch) {
      const { canvas, context } = scratch;
      if (!context || !canvas.width) return 0;
      try {
        const pixels = context.getImageData(0, 0, canvas.width, canvas.height).data;
        let total = 0;
        let clear = 0;
        for (let i = 3; i < pixels.length; i += 256) {
          total += 1;
          if (pixels[i] === 0) clear += 1;
        }
        return total ? clear / total : 0;
      } catch (error) {
        return 0;
      }
    }

    reveal(scratch, { instant = false, store = true, select = true, focus = false } = {}) {
      if (scratch.revealed) return;
      scratch.revealed = true;
      scratch.last = null;
      if (scratch.observer) scratch.observer.disconnect();
      // The CSS fades the cover out (badges come back with is-revealed); afterwards it leaves the layout
      scratch.optionEl.classList.add('is-revealed');
      if (instant || reducedMotion()) scratch.card.hidden = true;
      else this.later(`cover-${scratch.key}`, 320, () => { scratch.card.hidden = true; });
      if (store && !this.design) {
        const saved = storage(false).get(SCRATCH_KEY, {}) || {};
        saved[scratch.key] = 1;
        storage(false).set(SCRATCH_KEY, saved);
      }
      this.q.setOptionLocked(scratch.optionEl, false);
      if (select) this.q.selectOption(scratch.optionEl, { source: 'scratch' });
      // The reveal button disappears with the cover: the option's radio takes the focus
      const input = focus && scratch.optionEl.querySelector(':scope > .qb-v2-option__input');
      if (input && !input.disabled) input.focus({ preventScroll: true });
    }

    // ---------- Schedule (the inline script decides at parse time; this follows the clock while the page stays open) ----------
    initSchedule() {
      if (this.design) return;
      this.schedule = this.q.querySelector('[data-qb-child="schedule"]');
      if (!this.schedule) return;
      this.checkSchedule();
      // Timers stop while a computer sleeps
      this.on(document, 'visibilitychange', () => document.visibilityState === 'visible' && this.checkSchedule());
    }

    scheduleTime(value) {
      const match = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})(?::\d{2})?/.exec(value || '');
      if (!match) return null;
      const [year, month, day, hour, minute] = match.slice(1).map(Number);
      if (this.schedule.dataset.qbTimezone === 'fixed') {
        const offset = parseFloat(this.schedule.dataset.qbUtcOffset) || 0;
        return Date.UTC(year, month - 1, day, hour, minute - Math.round(offset * 60));
      }
      return new Date(year, month - 1, day, hour, minute).getTime();
    }

    checkSchedule() {
      if (!this.alive()) return;
      const now = Date.now();
      const start = this.scheduleTime(this.schedule.dataset.qbStart);
      const end = this.scheduleTime(this.schedule.dataset.qbEnd);
      const on = (start === null || now >= start) && (end === null || now < end);
      if (this.q.getAttribute('data-qb-schedule') !== (on ? 'on' : 'off')) this.q.setAttribute('data-qb-schedule', on ? 'on' : 'off');
      if (on) this.q.activate('schedule');
      else this.q.deactivate('schedule');
      const next = [start, end].filter((time) => time !== null && time > now).sort((a, b) => a - b)[0];
      clearTimeout(this.timers.schedule);
      if (next !== undefined) this.timers.schedule = setTimeout(() => this.guard(() => this.checkSchedule()), Math.min(next - now + 50, DAY));
    }

    // ---------- Next-tier nudge ----------
    nextTier() {
      const list = this.q.getOptionsSummary();
      const current = list.find((option) => option.selected);
      if (!current) return null;
      const usable = list.filter((option) => option.available && !option.hidden && !option.dormant && !option.locked);
      const each = (option) => option.saving / Math.max(1, option.units);
      const better = (option) => option.percent > current.percent || (option.percent === current.percent && each(option) > each(current));
      const next = usable.filter((option) => option.units > current.units && better(option)).sort((a, b) => a.units - b.units || b.percent - a.percent)[0] || null;
      const max = Math.max(current.units, ...usable.map((option) => option.units));
      // A bigger option still under its scratch card: no "best deal" claim, and its deal stays hidden
      const covered = list.some((option) => option.locked && !option.hidden && !option.dormant && option.units > current.units);
      return { current, next, covered, progress: Math.min(1, current.units / Math.max(1, max)) };
    }

    renderNudges() {
      const nudges = this.q.querySelectorAll('[data-qb-child="nudge"]');
      if (!nudges.length) return;
      const tier = this.q.active ? this.nextTier() : null;
      nudges.forEach((nudge) => {
        const text = nudge.querySelector('.qb-v2-nudge__text');
        const next = tier && tier.next;
        nudge.qbNext = next ? next.id : null;
        let html = '';
        if (next) {
          html = fill(nudge.dataset.qbText, {
            missing_quantity: next.units - tier.current.units,
            next_title: escapeHtml(next.title),
            next_saving: next.percent > 0 ? `${next.percent}%` : this.money.html(next.saving),
          });
        } else if (tier && !tier.covered) html = nudge.dataset.qbDoneText || '';
        nudge.hidden = !html.trim();
        if (text && html && text.innerHTML !== html) text.innerHTML = html;
        // At the top option the nudge is a status, not a button
        if (text && text.matches('button')) text.disabled = !next;
        if (tier) nudge.style.setProperty('--qb-v2-progress', String(Math.round(tier.progress * 1000) / 1000));
      });
    }

    // Tiers the cart nudge (component-quantity-breaks-v2-nudge.js) offers: quantity deals only, as automatic discounts
    // apply them to any cart; raising a quantity in the cart never adds a code, a pack variant, extras or picks
    // (options still missing picks, with a "From" price, are left out too). A tier's saving is its own discount on q
    // units at the regular price: a compare-at saving shows in the cart line's price already, and a one-time line gets
    // no selling plan
    writeTiers() {
      const q = this.q;
      const meta = (q.main && q.main.meta) || {};
      const handle = q.dataset.productHandle || meta.handle;
      if (!handle) return;
      const variant = this.currentVariant();
      const price = int(variant ? variant.price : q.qb.dataset.basePrice);
      const titles = new Map(q.getOptionsSummary().map((entry) => [entry.id, entry]));
      const seen = new Set();
      const tiers = q.active && price > 0 ? (q.options || [])
        .filter((option) => {
          const entry = titles.get(option.id);
          return entry && !option.hidden && !option.dormant && !option.locked && !entry.hasExtras && !entry.from && !option.pack && option.method !== 'code' && !option.plan;
        })
        .sort((a, b) => a.q - b.q)
        .map((option) => {
          const result = api().price.computeOption({ q: option.q, units: Array.from({ length: option.q }, () => ({ id: '1', price })), discount: option.discount, compareSource: 'price', rate: q.rate });
          return { q: option.q, title: titles.get(option.id).title, p: result.P, s: result.noRate ? 0 : result.S };
        })
        .filter((tier) => tier.s > 0 && !seen.has(tier.q) && seen.add(tier.q)) : [];
      const data = storage(false).get(TIERS_KEY, null);
      const products = data && data.v === 1 && data.products && typeof data.products === 'object' ? data.products : {};
      if (tiers.length) products[handle] = { t: meta.title || '', u: q.dataset.productUrl || meta.url || '', ts: Date.now(), cur: q.dataset.currency || '', tiers };
      else if (handle in products) delete products[handle];
      else return;
      const recent = Object.entries(products).sort((a, b) => ((b[1] && b[1].ts) || 0) - ((a[1] && a[1].ts) || 0)).slice(0, 20);
      storage(false).set(TIERS_KEY, { v: 1, products: Object.fromEntries(recent) });
    }

    // ---------- Pack variants ----------
    packs() {
      return (this.q.options || []).filter((option) => option.pack && option.pack.position > 0);
    }

    currentVariant() {
      const input = this.q.form && this.q.form.querySelector('[name="id"]');
      return input && this.q.main ? this.q.main.variants.get(String(input.value)) || null : null;
    }

    selectable(option) {
      return Boolean(option && option.available && !option.hidden && !option.locked && !option.dormant && !option.input.disabled);
    }

    initPacks() {
      if (!this.packs().length) return;
      this.togglePackRows(this.q.active);
      this.syncPacks('init', true);
    }

    // The pack's row of the Variant picker is hidden: the options choose it
    togglePackRows(on) {
      const picker = document.getElementById(`variant-selects-${this.q.sectionId}`);
      if (!picker) return;
      const rows = picker.querySelectorAll('.product-form__input');
      new Set(this.packs().map((option) => option.pack.position)).forEach((position) => {
        if (rows[position - 1]) rows[position - 1].classList.toggle('qb-v2-hidden-option', Boolean(on));
      });
    }

    syncPacks(reason, moved) {
      const q = this.q;
      const packs = this.packs();
      const variant = packs.length && q.active ? this.currentVariant() : null;
      if (!variant) return;
      const selected = q.getSelected();
      const match = packs.find((option) => same((variant.options || [])[option.pack.position - 1], option.pack.value));
      if (reason === 'variant' || reason === 'init') {
        // The variant decides: a pack variant selects its option; another variant leaves a pack option. At load a pack
        // option selected by default switches the variant instead (below)
        if (match && match !== selected && this.selectable(match)) {
          q.selectOption(match.id, { source: 'pack' });
          return;
        }
        if (reason === 'variant') {
          const first = !match && selected && selected.pack && q.options.find((option) => !option.pack && this.selectable(option));
          if (first) q.selectOption(first.id, { source: 'pack' });
          return;
        }
      } else if (!moved) return;
      if (!selected) return;
      if (selected.pack) {
        if (String(variant.id) !== String(selected.pack.variantId)) this.drive(selected.pack.position, selected.pack.value, selected.pack.variantId);
      } else if (match) {
        // Back to units: the pack's row is hidden, so the shopper couldn't leave the pack variant otherwise
        const at = match.pack.position - 1;
        const unit = Array.from(q.main.variants.values()).find((entry) => (entry.options || []).length && entry.options.every((value, i) => (i === at ? same(value, match.pack.unitValue) : value === variant.options[i])));
        this.drive(match.pack.position, match.pack.unitValue, unit && unit.id);
      }
    }

    // Through the Variant picker, which updates the variant id, URL, media and prices (M:4949-4971); without one, the
    // form's variant id (no section fetch follows)
    drive(position, value, variantId) {
      const q = this.q;
      const picker = document.getElementById(`variant-selects-${q.sectionId}`);
      const row = picker && picker.querySelectorAll('.product-form__input')[position - 1];
      if (row) {
        const type = (row.querySelector('.product-form__input__type') || { dataset: {} }).dataset.type;
        if (type === 'dropdown' || type === 'dropdwon') {
          const select = row.querySelector('.select__select');
          const option = select && Array.from(select.options).find((entry) => same(entry.value, value));
          if (option && select.value !== option.value) {
            select.value = option.value;
            fire(select);
          }
          return;
        }
        const radio = Array.from(row.querySelectorAll('input[type="radio"]')).find((entry) => same(entry.value, value));
        if (radio && !radio.checked) {
          radio.checked = true;
          fire(radio);
        }
        return;
      }
      const input = q.form && q.form.querySelector('[name="id"]');
      if (!input || !variantId || String(input.value) === String(variantId)) return;
      input.value = String(variantId);
      fire(input);
      q.recompute('variant');
    }

    // ---------- Option-level selling plans ----------
    initPlans() {
      const q = this.q;
      if (!(q.options || []).some((option) => option.plan && option.plan.id)) return;
      if (this.planConflict()) {
        this.blockPlans();
        return;
      }
      // Inside <product-form>, so main.js finds it for items[] adds (M:1534); FormData posts it on single-line adds
      const input = document.createElement('input');
      Object.assign(input, { type: 'hidden', name: 'selling_plan', value: '' });
      input.setAttribute('data-qb-v2-plan', '');
      q.form.append(input);
      this.planInput = input;
      const watch = new MutationObserver(() => this.guard(() => {
        if (this.alive() && this.planInput && this.planConflict()) this.blockPlans();
      }));
      const info = document.getElementById(`ProductInfo-${q.sectionId}`);
      [info, info && info.contains(q.form) ? null : q.form].forEach((root) => root && watch.observe(root, { childList: true, subtree: true }));
      this.observers.push(watch);
      this.planWatch = watch;
      this.syncPlanInput();
    }

    // Another plan source (the Subscription widget, an app's picker, any other selling_plan field of this form) wins:
    // main.js takes the first field it finds and single-line adds post every one (M:1785)
    planConflict() {
      const q = this.q;
      const mine = this.planInput;
      if (!q.form || document.getElementById(`SubscriptionWidget-${q.sectionId}`) || document.querySelector(PLAN_APPS)) return true;
      if (Array.from(q.form.elements).some((element) => element.name === 'selling_plan' && element !== mine)) return true;
      const info = document.getElementById(`ProductInfo-${q.sectionId}`);
      return Boolean(info && Array.from(info.querySelectorAll('[name="selling_plan"]')).some((element) => element !== mine));
    }

    blockPlans() {
      if (this.planInput) this.planInput.remove();
      this.planInput = null;
      if (this.planWatch) this.planWatch.disconnect();
      if (this.q.planAllowed !== false) this.q.setPlanAllowed(false);
    }

    syncPlanInput() {
      const input = this.planInput;
      if (!input) return;
      const q = this.q;
      const option = q.getSelected();
      const value = q.active && q.planAllowed && option && option.plan && option.plan.id ? String(option.plan.id) : '';
      if (input.value !== value) input.value = value;
    }

    // ---------- Analytics: DOM events for apps, custom events for pixels ----------
    track(type, option = this.q.getSelected(), lines) {
      const q = this.q;
      if (!option) return;
      const summary = q.getOptionsSummary().find((entry) => entry.id === option.id);
      if (!summary) return;
      const totals = option === q.getSelected() && typeof q.selectedTotals === 'function' ? q.selectedTotals() : { T: summary.total, C: summary.compare };
      const detail = {
        sectionId: q.sectionId,
        productId: toId(q.dataset.productId),
        productHandle: q.dataset.productHandle || '',
        option: { id: summary.id, index: summary.index, title: summary.title, quantity: summary.units, discountType: summary.discountType, discountValue: summary.discountValue, method: summary.method },
        variantIds: Array.from(new Set(q.getCartLines(option).filter((line) => line.role === 'main').map((line) => line.variantId))),
        total: totals.T,
        compare: totals.C,
        currency: q.dataset.currency || '',
      };
      // The core's cart lines are plain data already
      if (type !== 'select') detail.lines = copy(lines || []);
      const payload = copy(detail);
      q.dispatchEvent(new CustomEvent(`shrine:qb:${type}`, { bubbles: true, detail: payload }));
      const analytics = window.Shopify && window.Shopify.analytics;
      if (analytics && typeof analytics.publish === 'function') this.guard(() => analytics.publish(`shrine:qb_${type}`, copy(detail)));
    }

    // ---------- Discount codes ("Discount code" options) ----------
    // Codes V2 added, per cart token: { [token]: [{ code, handle }] } in sessionStorage
    codeRecords() {
      const records = storage(true).get(CODES_KEY, {});
      return records && typeof records === 'object' ? records : {};
    }

    recordCodes(token, update) {
      if (!token) return;
      const records = this.codeRecords();
      const list = update(records[token] || []);
      if (list.length) records[token] = list;
      else delete records[token];
      storage(true).set(CODES_KEY, records);
    }

    redirectPossible() {
      const form = this.q.productForm;
      return !form || !form.cart || form.skipCart === true || Boolean(document.querySelector(`[id="SectionAtcBtn-${this.q.sectionId}"][data-skip-cart-button="true"]`));
    }

    initCodes() {
      if (this.design) return;
      const selected = this.q.getSelected();
      // A later visit cleans up codes V2 left on this cart; a code option selected from the start reads the cart for
      // the redirect paths. Nothing is ever added at load
      if (Object.keys(this.codeRecords()).length || (selected && selected.method === 'code' && selected.code)) this.later('code', 1500, () => this.queueCodes(selected, true));
    }

    // The cart's codes: from cart.js when it lists them, Shopify.actions.getCart(), or an empty update (which changes
    // nothing). Unknown means V2 doesn't touch the codes, so the customer's own codes are never wiped
    async readCodes(cart, write) {
      const listed = codeList(cart && cart.discount_codes);
      if (listed) return listed;
      const actions = window.Shopify && window.Shopify.actions;
      if (actions && typeof actions.getCart === 'function') {
        try {
          const current = await actions.getCart();
          const list = codeList(current && (current.discountCodes || current.discount_codes));
          if (list) return list;
        } catch (error) {
          // Falls through to the empty update
        }
      }
      if (!write) return null;
      const data = await (queued({}, { render: false, standardEvent: null }) || cartRequest(`${route('cart_update_url', '/cart/update')}.js`, {}));
      return codeList(data && data.discount_codes);
    }

    postCodes(codes, { sections = null, keepalive = false, change = null } = {}) {
      // In the queue: V2's own change on the cart's codes of that moment (keeps a code written meanwhile)
      const viaQueue = !keepalive && queued((fresh) => {
        if (!fresh) return null;
        const latest = codeList(fresh.discount_codes);
        let list = codes;
        if (latest && change) {
          list = latest.filter((entry) => entry.applicable || !change.remove.some((code) => same(code, entry.code)));
          if (change.add && !hasCode(list, change.add) && list.length < 5) list = list.concat({ code: change.add, applicable: true });
          if (list.length === latest.length && list.every((entry, i) => entry.code === latest[i].code)) return null;
        }
        return { discount: list.map((entry) => entry.code || entry).join(',') };
      }, { render: Boolean(sections) });
      if (viaQueue) return viaQueue;
      const body = { discount: codes.map((entry) => entry.code || entry).join(',') };
      if (sections) body.sections = sections;
      return cartRequest(`${route('cart_update_url', '/cart/update')}.js`, body, keepalive);
    }

    // On selection: read the cart once; add the code only to a cart that already holds this product (an empty cart
    // would be changed or even created by a selection), and take back codes V2 added that apply to nothing
    async prepareCodes(option, atLoad) {
      this.restoreCartUrl();
      const code = option && option.method === 'code' ? option.code : '';
      const records = this.codeRecords();
      if (!code && !Object.keys(records).length) return;
      const cart = await cartRequest(`${route('cart_url', '/cart')}.js`);
      if (!cart || !this.alive()) return;
      const handles = (cart.items || []).map((item) => item.handle);
      const mine = records[cart.token] || [];
      const removable = mine.filter((entry) => !same(entry.code, code) && !handles.includes(entry.handle));
      const add = code && !atLoad && handles.includes(this.q.dataset.productHandle) && !hasCode(mine, code) ? code : '';
      const exists = cart.item_count > 0 || mine.length > 0;
      const wanted = removable.length || add || (code && cart.item_count > 0 && this.redirectPossible());
      const codes = codeList(cart.discount_codes) || (wanted ? await this.readCodes(cart, exists) : null);
      this.cart = { token: cart.token, count: cart.item_count, codes, at: Date.now() };
      if (!codes || !this.alive()) return;
      // Records of codes no longer on the cart go
      if (mine.some((entry) => !hasCode(codes, entry.code))) this.recordCodes(cart.token, (list) => list.filter((entry) => hasCode(codes, entry.code)));
      let next = codes.filter((entry) => entry.applicable || !removable.some((own) => same(own.code, entry.code)));
      if (add && !hasCode(next, add) && next.length < 5) next = next.concat({ code: add, applicable: true });
      if (next.length === codes.length && next.every((entry, i) => entry.code === codes[i].code)) return;
      const drawer = document.querySelector('cart-drawer');
      const data = await this.postCodes(next, { sections: drawer ? DRAWER_SECTIONS : null, change: { remove: removable.map((entry) => entry.code), add } });
      if (!data) return;
      const result = codeList(data.discount_codes) || next;
      this.cart.codes = result;
      this.recordCodes(data.token || cart.token, (list) => {
        const kept = list.filter((entry) => hasCode(result, entry.code));
        return add && hasCode(result, add) && !hasCode(kept, add) ? kept.concat({ code: add, handle: this.q.dataset.productHandle }) : kept;
      });
      this.renderDrawer(drawer, data);
    }

    renderDrawer(drawer, data) {
      if (data && data.rendered) return;
      if (drawer && data && data.sections && typeof drawer.renderContents === 'function') this.guard(() => drawer.renderContents(data, true));
    }

    // Before the add: drawer and notification carts get the code after the add (the cart exists then and the two
    // writes never race); page cart and skip cart leave the page right after the add (M:1847-1852), so a cart that
    // already holds items gets it now with keepalive and an empty one right after the add
    codeBeforeAdd(option) {
      this.pendingCode = null;
      this.restoreCartUrl();
      const code = option && option.method === 'code' ? option.code : '';
      if (this.design || !code) return;
      const form = this.q.productForm;
      const cart = this.cart;
      if (cart && hasCode(this.codeRecords()[cart.token], code)) return;
      const redirect = !form || !form.cart || form.skipCart === true || Date.now() - this.skipAt < 2000;
      if (!redirect) {
        this.pendingCode = { code, at: Date.now() };
        return;
      }
      if (cart && cart.codes && cart.count > 0) {
        if (hasCode(cart.codes, code) || cart.codes.length >= 5) return;
        this.recordCodes(cart.token, (list) => list.concat({ code, handle: this.q.dataset.productHandle }));
        this.postCodes(cart.codes.concat({ code }), { keepalive: true });
        return;
      }
      // An empty cart holds no codes of its own; unknown codes on a filled cart are never overwritten
      const codes = cart && cart.count === 0 ? cart.codes || [] : null;
      if (!codes) return;
      this.pendingCode = { code, at: Date.now(), redirect: true, codes, token: cart.token };
      if (this.q.patched) return;
      // Today's main.js sends no event before the redirect. To the cart page (M:1851) the shopper goes through Shopify's
      // discount link, which applies the code before the cart renders; to checkout (skip cart, M:1848) only the page's
      // own unload can carry the code, which may arrive after checkout has read the cart (store test)
      if (form && !form.cart && !form.skipCart && Date.now() - this.skipAt >= 2000 && this.cartLink(code, cart.token)) return;
      this.on(window, 'pagehide', () => this.sendPendingCode(), { once: true });
    }

    // On a product page with the page cart, main.js reads routes.cart_url only to redirect (M:1851): the link takes its
    // place until the page is left, the next add or cart read starts, or the widget stops (a failed add stays here)
    cartLink(code, token) {
      const routes = window.routes;
      if (!routes || !routes.cart_url) return false;
      this.cartUrl = this.cartUrl || routes.cart_url;
      routes.cart_url = `/discount/${encodeURIComponent(code)}?redirect=${encodeURIComponent(this.cartUrl)}`;
      this.pendingCode = null;
      this.recordCodes(token, (list) => list.concat({ code, handle: this.q.dataset.productHandle }));
      this.on(window, 'pagehide', () => this.restoreCartUrl(), { once: true });
      return true;
    }

    restoreCartUrl() {
      if (this.cartUrl && window.routes) window.routes.cart_url = this.cartUrl;
      this.cartUrl = null;
    }

    sendPendingCode() {
      const pending = this.pendingCode;
      this.pendingCode = null;
      if (!pending || !pending.redirect || Date.now() - pending.at > 15000 || hasCode(pending.codes, pending.code) || pending.codes.length >= 5) return;
      this.recordCodes(pending.token, (list) => list.concat({ code: pending.code, handle: this.q.dataset.productHandle }));
      this.postCodes(pending.codes.concat({ code: pending.code }), { keepalive: true });
    }

    // After the add the cart exists and holds the product: the selection path adds the code (drawer re-rendered the way the
    // theme's Cart discount block does it, layout/theme.liquid:857-881)
    codeAfterAdd() {
      const pending = this.pendingCode;
      if (!pending || Date.now() - pending.at > 15000) return null;
      if (pending.redirect) return this.sendPendingCode();
      this.pendingCode = null;
      return this.queueCodes({ method: 'code', code: pending.code }, false);
    }

    // One cart read and write at a time: a late selection read and the after-add one never interleave
    queueCodes(option, atLoad) {
      this.codeQueue = (this.codeQueue || Promise.resolve()).then(() => this.alive() && this.prepareCodes(option, atLoad)).catch(report);
      return this.codeQueue;
    }
  }

  const attach = (qbv2) => {
    if (!(qbv2 instanceof HTMLElement) || !qbv2.ready || !qbv2.qb) return;
    const previous = states.get(qbv2);
    if (previous) previous.stop();
    const extras = new Extras(qbv2);
    states.set(qbv2, extras);
    try {
      extras.start();
    } catch (error) {
      report(error);
    }
  };

  // The core usually finishes before this file runs (its init is a microtask), so ready widgets are picked up here;
  // later ones (quick add, editor re-renders) announce themselves with qbv2:ready
  document.addEventListener('qbv2:ready', (event) => attach(event.target));
  const boot = () => api().instances.forEach((qbv2) => qbv2.classList.contains('qb-v2--js') && attach(qbv2));
  if (api()) boot();
  else document.addEventListener('shrine:qbv2:core-ready', boot, { once: true });
})();

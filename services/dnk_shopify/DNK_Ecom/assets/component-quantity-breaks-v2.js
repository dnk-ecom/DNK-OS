/* Quantity breaks V2 (blocks/product_quantity-breaks-v2.liquid), loaded with defer after main.js. The inner
   <quantity-breaks> stays main.js's QuantityBreaks (selection, per-item variants, cart quantity); this adds live prices,
   custom pickers, extra cart lines, add-to-cart hooks and the product price display. Works with and without QB-1a. */
(() => {
  if (customElements.get('quantity-breaks-v2')) return;

  const report = (error) => console.error('Quantity breaks V2', error);
  const NEST_OFF = 'shrine-qb-nest-off';
  const ANNOUNCED = ['unit', 'extra', 'upsell', 'stepper', 'choice', 'builder', 'gift-choice', 'field'];
  const ROLE_ORDER = ['bundle', 'gift', 'upsell', 'wrapper-upsell', 'choice', 'builder', 'unlock'];
  const INTERACTIVE = 'a, button, input, select, textarea, label, [role="button"]';
  const SAVING_TEXT = /\[amount_saved|\[amount\]|\[percentage(_saved)?\]/;
  const CONTROLS = '.qb-v2-dd, .qb-v2-sw [tabindex="0"], select, input';

  const int = (value, fallback = 0) => {
    const number = parseInt(value, 10);
    return Number.isNaN(number) ? fallback : number;
  };
  const toId = (value) => (/^\d+$/.test(String(value)) ? Number(value) : value);
  const same = (a, b) => String(a == null ? '' : a).trim().toLowerCase() === String(b == null ? '' : b).trim().toLowerCase();
  const escapeHtml = (value) => String(value == null ? '' : value).replace(/[&<>"']/g, (char) => `&#${char.charCodeAt(0)};`);
  const textOf = (element) => (element ? element.textContent.replace(/\s+/g, ' ').trim() : '');
  const plain = (html) => {
    const template = document.createElement('template');
    template.innerHTML = html == null ? '' : String(html);
    return textOf(template.content);
  };
  const attempt = (callback, fallback) => {
    try {
      return callback();
    } catch (error) {
      return fallback;
    }
  };
  const readJson = (element) => (element ? attempt(() => JSON.parse(element.textContent), null) : null);
  const fill = (text, values) => String(text || '').replace(/\[([a-z_]+)\]/g, (match, key) => (key in values ? values[key] : match));
  const fire = (element) => element.dispatchEvent(new Event('change', { bubbles: true }));
  const visible = (root) => Array.from(root.querySelectorAll(CONTROLS)).find((element) => element.offsetParent !== null);
  // Renders only changed values; on the init pass an element seen for the first time keeps its server render
  const keyed = (element, key, render, keepFirst) => {
    if (!element || element._qbKey === key) return;
    const first = element._qbKey === undefined;
    element._qbKey = key;
    if (!(first && keepFirst)) render(element);
  };
  const storageArea = (name) => ({
    get: (key, fallback) => attempt(() => {
      const raw = window[name].getItem(key);
      return raw === null ? fallback : JSON.parse(raw);
    }, fallback),
    set: (key, value) => attempt(() => (window[name].setItem(key, JSON.stringify(value)), true), false),
  });
  const local = storageArea('localStorage');
  const session = storageArea('sessionStorage');

  // main.js globals are top-level declarations: reached by their bare names, always guarded. publish() runs
  // subscribers in a plain forEach (M:32-38), so a callback must never throw
  const pubSub = (name, callback) => {
    const events = typeof PUB_SUB_EVENTS === 'object' && PUB_SUB_EVENTS;
    if (!events || !events[name] || typeof subscribe !== 'function') return null;
    return subscribe(events[name], (payload) => {
      try {
        callback(payload);
      } catch (error) {
        report(error);
      }
    });
  };

  // ---------- Price model (contract 5.4): integer cents of the customer's currency ----------
  const base = (price, compare, source) => (source === 'compare_price' && compare > price ? compare : price);
  // Shop-currency amounts in the customer's currency; null while the exchange rate is unknown
  const convert = (amount, rate) => (rate ? Math.round(amount * rate) : null);
  const planPrice = (price, plan) => {
    const value = Number(plan && plan.value) || 0;
    switch (plan && plan.type) {
      case 'percentage':
        return Math.round((price * (100 - value)) / 100);
      case 'fixed_amount':
        return Math.max(0, Math.round(price - value));
      case 'price':
        return Math.max(0, Math.round(value));
      default:
        return price;
    }
  };

  // line: { role, quantity, price, compare, counts }; discount: { type, value }; context: { rate, compareSource }
  const extraLine = (line, discount, context = {}) => {
    const quantity = line.quantity || 0;
    const price = line.price || 0;
    const gross = quantity * price;
    if (line.role === 'gift' || line.role === 'unlock') return { total: 0, compare: line.counts ? gross : 0, disc: gross, noRate: false };
    const type = discount && discount.type;
    const value = Number(discount && discount.value) || 0;
    let disc = 0;
    let noRate = false;
    if (type === 'percentage') disc = Math.round((gross * value) / 100);
    else if (type === 'free') disc = gross;
    else if (type === 'amount_each') {
      const amount = convert(value, context.rate);
      if (amount === null) noRate = true;
      else disc = quantity * Math.min(price, amount);
    }
    return { total: gross - disc, compare: quantity * base(price, line.compare || 0, context.compareSource), disc, noRate };
  };

  /* model: { q, units: [{ id, price, compare }] (one per unit), discount: { type, value, free }, method, compareSource,
     plan, rate, pack: { unitPrice, unitCompare }, extras: [{ role, quantity, price, compare, discount, counts }], from }
     from: the extras hold the cheapest lines of picks still to make, so T is a "From" price: no compare price or saving */
  const computeOption = (model) => {
    const q = Math.max(1, int(model.q, 1));
    const source = model.compareSource;
    const units = model.units || [];
    const discount = model.discount || {};
    // Units grouped into lines by variant: percentages are rounded per line, as Shopify allocates them
    const lines = new Map();
    units.forEach((unit) => {
      if (!lines.has(unit.id)) lines.set(unit.id, { n: 0, p: unit.price, c: unit.compare || 0, pp: planPrice(unit.price, model.plan) });
      lines.get(unit.id).n += 1;
    });
    let B = 0;
    let Cm = 0;
    let regular = 0;
    let D = 0;
    let F = 0;
    let noRate = false;
    lines.forEach((line) => {
      B += line.n * line.pp;
      Cm += line.n * base(line.p, line.c, source);
      regular += line.n * line.p;
    });
    const type = model.method === 'pack' ? 'none' : discount.type || 'none';
    const value = Number(discount.value) || 0;
    if (type === 'percentage') lines.forEach((line) => { D += Math.round((line.n * line.pp * value) / 100); });
    else if (type === 'free_items') {
      F = Math.max(0, Math.min(int(discount.free), units.length - 1));
      units.map((unit) => planPrice(unit.price, model.plan)).sort((a, b) => a - b).slice(0, F).forEach((price) => { D += price; });
    } else if (/^(amount_each|amount_total|set_price)$/.test(type)) {
      const amount = convert(value, model.rate);
      if (amount === null) noRate = true;
      else if (type === 'amount_each') lines.forEach((line) => { D += line.n * Math.min(line.pp, amount); });
      else D = type === 'amount_total' ? Math.min(B, amount) : Math.max(0, B - amount);
    }
    const M = B - D;
    if (model.pack) Cm = q * base(model.pack.unitPrice, model.pack.unitCompare, source);
    let T = M;
    let C = Cm;
    (model.extras || []).forEach((extra) => {
      const line = extraLine(extra, extra.discount, { rate: model.rate, compareSource: source });
      noRate = noRate || line.noRate;
      T += line.total;
      C += line.compare;
    });
    const from = Boolean(model.from);
    if (from) C = T;
    const S = Math.max(0, C - T);
    const hasExtras = T > M || C > Cm;
    // The configured percentage when nothing else changes the saving (2 × 12.97 at 15 % reads 15 %, not 14.99 %)
    const P = from ? 0 : type === 'percentage' && !model.plan && !model.pack && !hasExtras && Cm === regular ? value : C > 0 ? Math.floor((100 * S) / C + 0.05) : 0;
    return { M, Cm, T, C, S, P, F, q, noRate, hasExtras, from, E: Math.round(T / q), CE: Math.round(C / q), units: units.length, paid: units.length - F };
  };

  const resolveVariant = (product, values) =>
    ((product && product.variants) || []).find((variant) => (variant.options || []).every((value, index) => value === values[index])) || null;

  // ---------- Money ----------
  // Format rebuilt from Shopify's own rendering of 123456 cents (e.g. "1.234,56 €") when shop.money_format doesn't match
  const deriveFormat = (sample) => {
    const match = sample && sample.match(/\d[\d.,'\s]*\d/);
    if (!match) return null;
    const number = match[0];
    const decimals = /\D\d\d$/.test(number);
    const marks = number.replace(/\d/g, '');
    const thousands = (decimals ? marks.slice(0, -1) : marks).charAt(0);
    // formatMoney's names: amount or amount_no_decimals, optionally _with_{comma|space|apostrophe}_separator
    const separator = /\s/.test(thousands) ? 'space' : thousands === "'" ? 'apostrophe' : (decimals ? number.charAt(number.length - 3) === ',' : thousands === '.') ? 'comma' : '';
    const at = sample.indexOf(number);
    return `${escapeHtml(sample.slice(0, at))}{{amount${decimals ? '' : '_no_decimals'}${separator && `_with_${separator}_separator`}}}${escapeHtml(sample.slice(at + number.length))}`;
  };

  const createMoney = (element) => {
    const data = element.dataset;
    const formats = { plain: data.moneyFormat || '{{amount}}', currency: data.moneyWithCurrencyFormat || data.moneyFormat || '{{amount}}' };
    const intl = (cents, trim) =>
      attempt(() => {
        const options = { style: 'currency', currency: (window.Shopify && Shopify.currency && Shopify.currency.active) || data.currency };
        if (trim && Math.round(cents) % 100 === 0) options.minimumFractionDigits = options.maximumFractionDigits = 0;
        return new Intl.NumberFormat(document.documentElement.lang || undefined, options).format(cents / 100);
      }, (cents / 100).toFixed(2));
    const raw = (cents, format, trim) => (typeof formatMoney === 'function' ? attempt(() => formatMoney(Math.round(cents), format, trim), intl(cents, trim)) : intl(cents, trim));
    const normal = (value) => String(value || '').replace(/\s+/g, ' ').trim();
    [['plain', data.moneySample], ['currency', data.moneyWithCurrencySample]].forEach(([key, sample]) => {
      if (!sample || typeof formatMoney !== 'function' || normal(plain(raw(123456, formats[key], false))) === normal(sample)) return;
      formats[key] = deriveFormat(sample) || formats[key];
    });
    const trimZeros = element.classList.contains('qb-v2--trim-zeros');
    return {
      format: (cents, { trim = false, withCurrency = false } = {}) => raw(cents, withCurrency ? formats.currency : formats.plain, trim),
      // Prices inside the widget follow its "Show zero decimals" setting
      html: (cents) => raw(cents, formats.plain, trimZeros),
    };
  };

  // ---------- Picker markup ----------
  const hasSwatches = (options) =>
    options.some((option) => option.dataset.swatchColor) || new Set(options.map((option) => option.dataset.swatchImage).filter(Boolean)).size > 1;
  const isUnavailable = (option) => option.disabled || /\b(unavailable|non-existent)\b/.test(option.className);
  const mediaHtml = (option) => {
    const src = option.dataset.image || option.dataset.swatchImage;
    if (src) return `<img src="${escapeHtml(src)}" alt="" aria-hidden="true" width="40" height="40" loading="lazy">`;
    const color = option.dataset.swatchColor;
    return color ? `<span class="qb-v2-swatch" aria-hidden="true" style="--qb-v2-swatch: ${escapeHtml(color)}; width: 100%; height: 100%;"></span>` : '';
  };
  const swatchHtml = (option, swatches, checked) => {
    const image = swatches ? option.dataset.swatchImage || '' : '';
    const color = swatches && !image ? option.dataset.swatchColor || '' : '';
    const pill = !image && !color;
    return `<button type="button" role="radio" class="qb-v2-swatch${pill ? ' qb-v2-swatch--pill' : ''}${isUnavailable(option) ? ' is-unavailable' : ''}" aria-checked="${checked}" aria-label="${escapeHtml(textOf(option))}" tabindex="${checked ? 0 : -1}" data-value="${escapeHtml(option.value)}"${option.disabled ? ' aria-disabled="true"' : ''}${color ? ` style="--qb-v2-swatch: ${escapeHtml(color)}"` : ''}>${image ? `<img src="${escapeHtml(image)}" alt="" loading="lazy">` : pill ? escapeHtml(option.value) : ''}</button>`;
  };
  const quantityBox = (input) => input.closest('.product-form__quantity') || input.closest('quantity-input') || input;

  class QuantityBreaksV2 extends HTMLElement {
    connectedCallback() {
      api.instances.add(this);
      if (this.started) return;
      this.started = true;
      // In quick add the outer element upgrades first: wait for main.js's element
      queueMicrotask(() => customElements.whenDefined('quantity-breaks').then(() => {
        if (this.isConnected && this.started && !this.ready) this.init();
      }).catch(report));
    }

    disconnectedCallback() {
      api.instances.delete(this);
      this.started = false;
      if (this.ready) this.teardown();
    }

    init() {
      this.ready = true;
      try {
        this.setup();
      } catch (error) {
        report(error);
      }
    }

    setup() {
      const data = this.dataset;
      Object.assign(this, { sectionId: data.section, blockId: data.block, cleanups: [], watched: new WeakSet(), reasons: new Set(), version: 0, unitsPending: false });
      this.designMode = data.designMode === 'true' || Boolean(window.Shopify && Shopify.designMode);
      this.qb = this.querySelector('quantity-breaks');
      if (!this.qb) return;
      this.form = document.getElementById(`product-form-${this.sectionId}`);
      this.productForm = this.form && this.form.closest('product-form');
      this.patched = api.isPatched();
      this.fallback = this.querySelector(':scope > .qb-v2-fallback-qty');
      this.linesEl = this.querySelector(':scope > .qb-v2__lines');
      this.listbox = this.querySelector(':scope > .qb-v2__listbox');
      this.widget = document.getElementById(`SubscriptionWidget-${this.sectionId}`);
      this.pickerStyle = (this.className.match(/qb-v2--pickers-([a-z_]+)/) || [])[1] || 'dropdown';
      this.sameForAll = data.variantSelection === 'same_for_all';
      this.rtl = getComputedStyle(this).direction === 'rtl';
      this.money = createMoney(this);
      this.rate = this.readRate();
      this.planAllowed = !this.widget;
      this.onOutside = (event) => {
        if (this.lb && !this.listbox.contains(event.target) && !this.lb.trigger.contains(event.target)) this.closeListbox();
      };
      // Phone toolbars resize the window's height while the page scrolls: only a width change (rotation) closes the list
      this.onResize = () => this.lb && window.innerWidth !== this.lb.width && this.closeListbox();
      this.onQuantityInput = () => this.mirrorQuantity();

      if (this.designMode) this.repairTokens();
      this.products = new Map();
      const list = readJson(this.qb.querySelector('script[type="application/json"]'));
      this.main = {
        meta: readJson(this.querySelector('script[data-qbv2-main]')) || {},
        variants: new Map((Array.isArray(list) ? list : []).map((variant) => [String(variant.id), variant])),
      };
      this.options = Array.from(this.qb.querySelectorAll('.qb-v2-option')).map((element) => this.readOption(element)).filter(Boolean);

      // Stay off: main.js couldn't run the inner element, a second widget in this section, or a closed schedule
      if (!('selectedOffer' in this.qb)) this.reasons.add('error');
      if (document.querySelectorAll(`[id="quantity-breaks-${this.sectionId}"]`).length > 1) this.reasons.add('duplicate');
      else this.repoint();
      if (!this.designMode && data.qbSchedule === 'off') this.reasons.add('schedule');
      this.activateDormant();
      if (this.needsFallback()) this.reasons.add('options');
      this.active = !this.reasons.size;

      this.qb.updatePrices = this.qb.updatePdpPrices = false;
      if (!this.widgetUpdatesPrices()) this.savePdp(document);
      this.restoreFormState();
      this.querySelectorAll('[data-qb-child="upsell"]').forEach((upsell) => this.initUpsell(upsell));
      this.options.forEach((option) => option.stepper && this.setStep(option, int(option.input.value, option.q)));
      if (this.active) this.applyDefaults(this.options);
      this.assertFormVariants();
      this.listen();
      this.setSelected(this.checkedOption());
      this.options.forEach((option) => option.body && this.enhancePickers(option.body));
      this.querySelectorAll(':scope > .qb-v2__slot').forEach((slot) => this.enhancePickers(slot));
      this.applyActive();
      this.initPass = true;
      this.run('init');
      this.initPass = false;
      this.loadComplementary();
      this.classList.add('qb-v2--js');
      this.dispatch('qbv2:ready', { qbv2: this });
    }

    teardown() {
      this.ready = false;
      this.closeListbox();
      (this.cleanups || []).forEach((cleanup) => this.guard(cleanup));
      this.cleanups = [];
      [this.pendingTimer, this.announceTimer, this.fieldTimer].forEach(clearTimeout);
      if (!this.qb) return;
      this.unregisterRequired();
      this.watchQuantity(null);
      if (this.form) {
        this.form.querySelectorAll('[data-qb-v2-prop], [data-qb-v2-plan]').forEach((input) => input.remove());
        this.form.classList.remove('qb-v2-hide-bin');
      }
      this.restoreOtherQuantities();
      this.togglePicker(false);
    }

    guard(callback) {
      try {
        return callback();
      } catch (error) {
        return report(error);
      }
    }

    dispatch(name, detail) {
      this.dispatchEvent(new CustomEvent(name, { bubbles: true, detail }));
    }

    // ---------- State ----------
    // Extra product JSON by id, read on first use: from the page (carried gift copies have none, the original has), or
    // from a candidates <template> for a product chosen in a popup. A miss is remembered as null
    product(id) {
      const key = String(id);
      if (!this.products.has(key)) {
        const selector = `script[data-qbv2-product="${CSS.escape(key)}"]`;
        const template = Array.from(this.querySelectorAll('template[data-qb-candidates]')).find((entry) => entry.content.querySelector(selector));
        this.products.set(key, readJson(this.querySelector(selector) || (template && template.content.querySelector(selector))));
      }
      return this.products.get(key);
    }

    readOption(element) {
      const data = element.dataset;
      const input = element.querySelector(':scope > .qb-v2-option__input');
      const label = element.querySelector(':scope > .qb-v2-card');
      if (!input || !label) return null;
      const option = element._qbv2 || { el: element, touched: false, expanded: false };
      element._qbv2 = option;
      const q = Math.max(1, int(data.qbQ, 1));
      const stepInput = label.querySelector('.qb-v2-stepper__input');
      Object.assign(option, {
        input,
        label,
        q,
        body: element.querySelector(':scope > .qb-v2-option__body'),
        id: data.qbV2Option,
        index: int(data.qbIndex) || int(String(input.dataset.input).replace('input_', '')),
        dormant: element.hasAttribute('data-qb-dormant'),
        hidden: data.qbHidden === 'true',
        scratch: data.qbScratch === 'true',
        discount: { type: data.qbDiscountType || 'none', value: int(data.qbDiscountValue), free: int(data.qbFree) },
        method: data.qbMethod || 'automatic',
        code: data.qbCode || '',
        compareSource: data.qbCompareSource || 'compare_price',
        plan: data.qbPlanId ? { id: data.qbPlanId, type: data.qbPlanType, value: Number(data.qbPlanValue) || 0 } : null,
        galleryKey: data.qbGalleryMedia || '',
        defaultOptions: data.qbDefaultOptions || '',
        unitEls: Array.from(label.querySelectorAll('.qb-v2-unit')),
        stepper: data.qbStepper === 'true' ? { min: q, step: Math.max(1, int(stepInput && stepInput.step, 1)) } : null,
      });
      option.hasPickers = option.unitEls.length > 0;
      if (option.locked === undefined) option.locked = option.scratch;
      if (option.units === undefined) option.units = int(data.qbUnits, int(input.value, q));
      this.readAvailability(option);
      return option;
    }

    readAvailability(option) {
      const data = option.el.dataset;
      option.available = data.qbAvailable === 'true';
      option.reason = data.qbUnavailableReason || '';
      option.pack = option.method === 'pack' && data.qbPackVariant ? { value: data.qbPack || '', variantId: data.qbPackVariant, position: int(data.qbPackPosition), unitValue: data.qbUnitValue || '' } : null;
      if (!option.stepper) return;
      option.stepper.max = Math.max(option.q, int(data.qbStepperMax, option.q));
      const stepInput = option.label.querySelector('.qb-v2-stepper__input');
      if (stepInput) stepInput.max = String(option.stepper.max);
    }

    stateOf(element) {
      return element && element._qbv2 && this.options.includes(element._qbv2) ? element._qbv2 : null;
    }

    resolveOption(value) {
      if (!value) return null;
      if (value.el && this.options.includes(value)) return value;
      if (value instanceof Element) return this.stateOf(value.closest('.qb-v2-option'));
      return this.options.find((option) => option.id === String(value) || option.index === Number(value)) || null;
    }

    checkedOption() {
      const input = this.qb.querySelector('.qb-v2-option > input[name="quantity"]:checked');
      return input ? this.stateOf(input.closest('.qb-v2-option')) : null;
    }

    isSelectable(option) {
      return Boolean(option && option.available && !option.hidden && !option.locked && !option.dormant);
    }

    // Default rule of contract 5.2.3
    defaultOption() {
      const selectable = this.options.filter((option) => this.isSelectable(option));
      return selectable.find((option) => option.el.dataset.qbDefault === 'true') || selectable.find((option) => option.el.dataset.qbMustChoose !== 'true') || selectable[0] || null;
    }

    // No option can be bought while the variant can: only the plain quantity field meets its rules (or stock). A
    // scratch-locked option counts: it becomes selectable when revealed
    needsFallback() {
      if (this.options.some((option) => option.available && !option.hidden && !option.dormant)) return false;
      const variant = this.variant(this.currentId());
      return !(variant ? variant.available === false : this.options.some((option) => option.reason === 'soldout'));
    }

    // Shop-currency amounts need the exchange rate in another currency; null while it is unknown (M:3227-3236)
    readRate() {
      const { currency, shopCurrency } = this.dataset;
      if (!currency || !shopCurrency || currency === shopCurrency) return 1;
      return typeof _qbGetPresentmentRate === 'function' ? attempt(() => _qbGetPresentmentRate(shopCurrency), null) : null;
    }

    currentId() {
      const input = this.form && this.form.querySelector('[name="id"]');
      return String((input && input.value) || this.dataset.variantId || '');
    }

    variant(id) {
      return this.main.variants.get(String(id)) || null;
    }

    findVariant(test) {
      for (const variant of this.main.variants.values()) if (test(variant.options || [])) return variant;
      return null;
    }

    // One unit's variant: the form's variant, or its single-unit sibling while the page is on a pack variant (5.3.3)
    baseVariant(option) {
      const id = this.currentId();
      const current = this.variant(id) || { id, price: int(this.qb.dataset.basePrice), compare_at_price: 0, available: true, options: [] };
      if (option && option.pack) return current;
      const pack = this.options.find((entry) => entry.pack && same((current.options || [])[entry.pack.position - 1], entry.pack.value));
      return (pack && this.packSibling(current, pack.pack)) || current;
    }

    packSibling(variant, pack) {
      const at = pack.position - 1;
      return this.findVariant((options) => options.length > 0 && options.every((value, i) => (i === at ? same(value, pack.unitValue) : value === (variant.options || [])[i])));
    }

    unitVariants(option) {
      const current = this.baseVariant(option);
      if (option.pack) return [this.variant(option.pack.variantId) || current];
      if (option.hasPickers) return option.unitEls.map((unit) => this.variant(unit.dataset.selectedId) || current);
      return Array.from({ length: Math.max(1, option.units) }, () => current);
    }

    optionQuantity(option) {
      return option.stepper ? option.units : option.q;
    }

    planFor(option, withWidget = true) {
      if (this.planAllowed && option.plan && option.plan.type) return option.plan;
      return withWidget && this.qb.subDiscountType ? { type: this.qb.subDiscountType, value: this.qb.subDiscount } : null;
    }

    nestAllowed() {
      return this.patched && this.dataset.qbNest !== 'false' && !session.get(NEST_OFF, null);
    }

    widgetUpdatesPrices() {
      return Boolean(this.widget && this.widget.dataset.updatePrices === 'true');
    }

    // ---------- Extras ----------
    // Everything an option adds besides its units, in cart order; withWrapper adds the wrapper's upsells and
    // unlockable gifts (those follow the selected option)
    collect(option, withWrapper) {
      const entries = [];
      const children = option && option.body ? Array.from(option.body.querySelectorAll('[data-qb-child]')) : [];
      if (withWrapper) children.push(...this.querySelectorAll(':scope > .qb-v2__slot :is([data-qb-child="upsell"], [data-qb-child="unlock"])'));
      children.forEach((child) => {
        const kind = child.dataset.qbChild;
        const add = (role, item, added, gift, quantity) => item && entries.push(this.entry(role, item, child, quantity, added, gift));
        if (kind === 'bundle') child.querySelectorAll('[data-qb-item][data-role="bundle"]').forEach((item) => add('bundle', item, true));
        else if (kind === 'gift' && (child.dataset.qbGiftType || 'product') === 'product') {
          const rows = [...child.querySelectorAll('[data-qb-gift-row]')];
          const chosen = child.dataset.qbSelection === 'one' && (rows.find((row) => row.dataset.qbChosen === 'true') || rows[0]);
          rows.forEach((row) => add('gift', row.querySelector('[data-qb-item]'), !chosen || row === chosen, { row, text: row.querySelector('.qb-v2-gift__text') }));
        } else if (kind === 'upsell' && child.dataset.productId) {
          const input = child.querySelector('.qb-v2-upsell__input');
          add(child.closest('.qb-v2-option') ? 'upsell' : 'wrapper-upsell', child, Boolean(input && input.checked && !input.disabled), null, child.dataset.qbQuantityMode === 'match' && option ? this.optionQuantity(option) : 1);
        } else if (kind === 'choice') add('choice', child.querySelector('[data-qb-choice-slot] [data-qb-item]'), true);
        else if (kind === 'builder') (child._qbPicks || []).forEach((pick) => entries.push(this.entry('builder', null, child, pick.quantity, true, null, pick)));
        // Unlocked once the selected option has enough units (a pack counts as the one unit in the cart)
        else if (kind === 'unlock' && option) add('unlock', child.querySelector('[data-qb-item]'), option.units >= int(child.dataset.qbUnlockQuantity, 1), { row: child, text: child.querySelector('.qb-v2-unlock__text--open') });
      });
      return entries.sort((a, b) => ROLE_ORDER.indexOf(a.role) - ROLE_ORDER.indexOf(b.role));
    }

    // One extra line. Gift rows and unlockable gifts (gift = { row, text }) are left out while sold out; builder picks
    // have no element of their own (pick = { productId, variantId })
    entry(role, element, child, quantity, added, gift, pick) {
      const source = pick || element.dataset;
      const json = this.product(source.productId);
      const variant = json && (json.variants || []).find((entry) => String(entry.id) === String(source.variantId));
      const available = variant ? variant.available !== false : !element || element.dataset.available !== 'false';
      return {
        role, child, json, variant, available,
        el: element,
        productId: source.productId,
        variantId: source.variantId,
        quantity: quantity || int(element.dataset.quantity, int(child.dataset.qbQuantity, 1)),
        price: variant ? int(variant.price) : 0,
        compare: variant ? int(variant.compare_at_price) : 0,
        discount: { type: child.dataset.qbDiscountType || 'none', value: int(child.dataset.qbDiscountValue) },
        title: json ? json.title : textOf(element && element.querySelector('.qb-v2-item__title')),
        counts: Boolean(gift) && child.dataset.qbCountsValue === 'true',
        unlocked: added,
        added: added && (!gift || available),
        row: gift && gift.row,
        text: gift ? textOf(gift.text) : '',
      };
    }

    // Gift rule requirement: the quantity of the option that offers the gift (1 for a pack: one unit in the cart)
    giftRequirement(child) {
      const origin = Array.from(this.qb.querySelectorAll('[data-qb-child="gift"][data-qb-gift-origin="self"]')).find((gift) => gift.dataset.qbBlock === child.dataset.qbBlock) || child;
      const option = this.stateOf(origin.closest('.qb-v2-option'));
      return !option || option.pack ? 1 : option.q;
    }

    /* Picks the customer still has to make (an empty "Customer chooses" slot, a Bundle builder that isn't full): their
       cheapest lines, which make the option's total a "From" price (null when nothing is open). Cheapest = the lowest
       price among the available variants a popup card offers (its picker's, else its own), the first card on a tie
       (Liquid ranks the same: data-qb-low-prices). A builder fills up with the cheapest product (its other ones without
       repeats), merged with a pick of the same variant, and its lines replace its picks' (done), so each discount
       applies per line */
    completion(option, entries) {
      const lines = [];
      const done = new Set();
      // Must-choose children with candidates: Product choice "Customer chooses" and Bundle builder (not Personalisation)
      (option.body ? option.body.querySelectorAll('[data-qb-must-choose="true"]') : []).forEach((child) => {
        const role = child.dataset.qbChild;
        const builder = role === 'builder';
        const template = child.querySelector('template[data-qb-candidates]');
        const own = entries.filter((entry) => entry.child === child && entry.added);
        const left = builder ? int(child.dataset.qbPicks, 1) - own.reduce((sum, entry) => sum + entry.quantity, 0) : 1 - own.length;
        if (left < 1 || !template) return;
        const once = builder && child.dataset.qbAllowRepeats === 'false';
        const cheapest = [];
        template.content.querySelectorAll('[data-qb-candidate]').forEach((card) => {
          const { productId, variantId } = card.dataset;
          const json = this.product(productId);
          // A card without a picker (Show variant picker off, over 100 variants) offers only its own variant
          const picker = card.querySelector('.qb-v2-cand__picker');
          const variant = ((json && json.variants) || []).filter((entry) => entry.available !== false && (picker || String(entry.id) === variantId)).sort((a, b) => a.price - b.price)[0];
          if (variant && !(once && own.some((entry) => entry.productId === productId))) cheapest.push({ productId, variantId: String(variant.id), price: variant.price });
        });
        const add = cheapest.sort((a, b) => a.price - b.price).slice(0, once ? left : 1);
        if (add.length < (once ? left : 1)) return;
        add.forEach((pick) => {
          const quantity = !builder ? int(child.dataset.qbQuantity, 1) : once ? 1 : left;
          const same = own.find((entry) => String(entry.variantId) === pick.variantId);
          if (same) same.quantity += quantity;
          else own.push(this.entry(role, null, child, quantity, true, null, pick));
        });
        done.add(child);
        lines.push(...own);
      });
      return done.size ? { lines, done } : null;
    }

    modelFor(option, withWidget = true) {
      const entries = this.collect(option, false);
      const open = this.completion(option, entries);
      const model = {
        q: this.optionQuantity(option),
        units: this.unitVariants(option).map((variant) => ({ id: String(variant.id), price: int(variant.price), compare: int(variant.compare_at_price) })),
        discount: option.discount,
        method: option.pack ? 'pack' : option.method,
        compareSource: option.compareSource,
        plan: this.planFor(option, withWidget),
        rate: this.rate,
        extras: entries.filter((entry) => entry.added && !(open && open.done.has(entry.child))).concat(open ? open.lines : [])
          .map((entry) => ({ role: entry.role, quantity: entry.quantity, price: entry.price, compare: entry.compare, discount: entry.discount, counts: entry.counts })),
        from: Boolean(open),
      };
      if (option.pack) {
        const current = this.baseVariant(option);
        const unit = this.packSibling(this.variant(option.pack.variantId) || current, option.pack) || current;
        model.pack = { unitPrice: int(unit.price), unitCompare: int(unit.compare_at_price) };
      }
      return model;
    }

    computeOption(option) {
      const state = this.resolveOption(option);
      if (!state) return null;
      if (!state.result || state.resultVersion !== this.version) {
        state.result = computeOption(this.modelFor(state));
        state.resultVersion = this.version;
      }
      return state.result;
    }

    mainProperties(option) {
      const properties = {};
      if (!option) return properties;
      if (this.collect(option, false).some((entry) => entry.added && ['bundle', 'choice', 'builder'].includes(entry.role))) properties._qb_bundle = this.plainTitle(option);
      if (option.body) {
        option.body.querySelectorAll('[data-qb-child="field"]').forEach((field) => {
          const input = field.querySelector('input');
          const name = (field.dataset.qbFieldName || '').trim();
          if (name && input && input.value.trim()) properties[name] = input.value.trim();
        });
      }
      return properties;
    }

    getCartLines(option = this.selected, { includeMain = true } = {}) {
      const state = this.resolveOption(option);
      if (!state) return [];
      const { meta } = this.main;
      const title = this.plainTitle(state);
      const nest = this.nestAllowed();
      const lines = [];
      if (includeMain) {
        const properties = this.mainProperties(state);
        this.unitVariants(state).forEach((variant) => {
          const id = toId(variant.id);
          const line = lines.find((entry) => entry.variantId === id);
          if (line) line.quantity += 1;
          else lines.push({ variantId: id, quantity: 1, role: 'main', productId: meta.id, handle: meta.handle, title: meta.title, properties, parent: null });
        });
      }
      this.collect(state, true).forEach((entry) => {
        if (!entry.added) return;
        const role = entry.role === 'wrapper-upsell' ? 'upsell' : entry.role;
        const key = { gift: '_qb_gift', unlock: '_qb_gift', upsell: '_qb_upsell' }[role] || '_qb_bundle';
        lines.push({
          role,
          variantId: toId(entry.variantId),
          quantity: entry.quantity,
          productId: entry.json ? entry.json.id : toId(entry.productId),
          handle: entry.json ? entry.json.handle : '',
          title: entry.title,
          properties: { [key]: key === '_qb_gift' ? entry.text || title : title },
          parent: nest && ['gift', 'unlock', 'upsell'].includes(role) ? 'main' : null,
          requirement: role === 'gift' ? this.giftRequirement(entry.child) : role === 'unlock' ? int(entry.child.dataset.qbUnlockQuantity, 1) : undefined,
        });
      });
      return lines;
    }

    plainTitle(option) {
      if (!option) return '';
      return textOf(option.label.querySelector('.qb-v2-card__title')) || textOf(this.querySelector(':scope > .qb-v2__heading')) || `${this.optionQuantity(option)}×`;
    }

    planName(option) {
      return this.planAllowed && option.plan ? textOf(option.label.querySelector('[data-qb-plan-name]')).split(' · ').pop() : '';
    }

    // ---------- Pipeline ----------
    recompute(reason = 'api') {
      if (!this.ready || !this.qb) return;
      this.version += 1;
      if (this.queued) return;
      this.queued = reason;
      queueMicrotask(() => this.flush());
    }

    flush() {
      const reason = this.queued;
      this.queued = null;
      if (reason) this.run(reason);
    }

    run(reason) {
      if (!this.ready || !this.qb) return;
      try {
        const keep = this.initPass;
        this.options.forEach((option) => {
          option.result = computeOption(this.modelFor(option));
          option.resultVersion = this.version;
        });
        this.options.forEach((option) => this.renderOption(option, keep));
        const totals = this.selectedTotals();
        const source = this.selected ? this.selected.compareSource : 'compare_price';
        this.collect(this.selected, true).forEach((entry) => {
          if (entry.role === 'wrapper-upsell') this.renderEntry(entry, keep && entry.quantity === 1 && !entry.child.hasAttribute('data-qb-pending'), source);
          else if (entry.role === 'unlock') this.renderEntry(entry, keep);
        });
        this.renderSavings(totals);
        this.writeOfferPrices();
        this.syncLines();
        this.syncBin();
        this.syncRequired();
        this.writePdp(totals);
        this.assertFormVariants();
        if (!keep) this.announce(reason, totals);
      } catch (error) {
        report(error);
      }
      this.dispatch('qbv2:change', { qbv2: this, option: this.selected, reason });
    }

    // A price that is a "From" price (on) gets the theme's own words (products.product.price.from_price_html, from the
    // wrapper), as Liquid prints them: in spans, on whichever side of the price the translation puts them
    fromPrice(html, on) {
      if (!on) return html;
      const [before, after = ''] = (this.dataset.qbFromLabel || '[price]').split('[price]');
      const words = (text) => (text.trim() ? `<span class="qb-v2-from">${text}</span>` : '');
      return words(before) + html + words(after);
    }

    keywords(result, option) {
      const money = (cents) => this.money.html(cents);
      const saved = money(result.S);
      const percent = `${result.P}%`;
      // Servings per item (wrapper setting): the price of one serving of one item
      const servings = parseInt(this.dataset.qbServings, 10) || 0;
      return {
        price_per_serving: servings > 0 && result.E > 0 ? this.fromPrice(money(Math.floor(result.E / servings)), result.from) : '',
        quantity: result.q,
        title: escapeHtml(this.main.meta.title || ''),
        price: this.fromPrice(money(result.T), result.from),
        compare_price: money(result.C),
        price_each: this.fromPrice(money(result.E), result.from),
        compare_price_each: money(result.CE),
        amount_saved: saved,
        amount: saved,
        amount_saved_rounded: money(Math.round(result.S / 100) * 100),
        percentage_saved: percent,
        percentage: percent,
        free_quantity: result.F,
        paid_quantity: result.paid,
        plan_name: escapeHtml(option ? this.planName(option) : ''),
      };
    }

    // Liquid printed T|C|S|P on every text (data-qb-v, "|f" for a "From" price): equal values keep the server render,
    // so nothing flashes
    renderText(element, result, values, force) {
      const text = element.dataset.qbText;
      if (text === undefined) return;
      const key = `${result.T}|${result.C}|${result.S}|${result.P}${result.from ? '|f' : ''}`;
      const extra = `${values.quantity}|${values.plan_name}|${result.noRate}`;
      // Liquid can't know the wrapper's Servings per item: texts with [price_per_serving] are filled here once at least
      const serving = !element._qbServed && text.includes('[price_per_serving]');
      if (force || serving || element.dataset.qbV !== key || (element._qbExtra !== undefined && element._qbExtra !== extra)) {
        element.innerHTML = fill(text, values);
        element.dataset.qbV = key;
        element._qbServed = true;
      }
      element._qbExtra = extra;
      // The class marks saving texts without keywords too (the option's savings line)
      if (SAVING_TEXT.test(text) || element.classList.contains('qb-v2-text--saving')) element.hidden = !(result.S > 0) || result.noRate;
    }

    renderOption(option, keep) {
      const result = option.result;
      const pending = option.el.classList.contains('qb-v2-pending');
      const kept = keep && !pending;
      const values = this.keywords(result, option);
      option.el.toggleAttribute('data-qb-from', result.from);
      option.el.querySelectorAll('.qb-v2-text[data-qb-ctx="option"]').forEach((element) => element.closest('[data-qb-child]') || this.renderText(element, result, values, pending));
      option.label.querySelectorAll('[data-qb-compare-text]').forEach((element) => element.classList.toggle('hidden', !(result.C > result.T)));
      option.label.querySelectorAll('.qb-v2-card__plan').forEach((element) => element.classList.toggle('hidden', !this.planAllowed));
      const each = option.label.querySelector('[data-qb-each]');
      if (each) {
        // Paid extras (a ticked add-on, a chosen item) are in T, so T / q would misstate the price per item
        each.classList.toggle('hidden', (Boolean(option.stepper) && option.units === 1) || result.T > result.M);
        keyed(each.querySelector('.qb-v2-card__each-amount'), result.E, (element) => { element.innerHTML = this.money.html(result.E); }, kept);
      }
      if (option.body) {
        option.body.querySelectorAll('[data-qb-item-main]').forEach((tile) => {
          keyed(tile.querySelector('.qb-v2-item__price'), result.M, (element) => { element.innerHTML = this.money.html(result.M); }, kept);
          const compare = tile.querySelector('.qb-v2-item__compare');
          keyed(compare, `${result.M}|${result.Cm}`, (element) => { element.innerHTML = result.Cm > result.M ? this.money.html(result.Cm) : ''; }, kept);
          if (compare) compare.classList.toggle('hidden', !(result.Cm > result.M));
        });
      }
      // The server prints upsells for one unit ("Same as option quantity" ones need the option's quantity) and item
      // compare prices from the compare-at price (children can't read the option's compare source)
      const entries = this.collect(option, false);
      entries.forEach((entry) => this.renderEntry(entry, kept && !entry.child.hasAttribute('data-qb-pending') && (entry.role !== 'upsell' || entry.quantity === 1), option.compareSource));
      // What the option adds, for screen readers (other options' bodies are inert): store and merchant text only
      const contents = option.label.querySelector('[id$="-contents"]');
      const text = entries.filter((entry) => entry.added).map((entry) => (entry.role === 'gift' ? entry.text : `${entry.quantity > 1 ? `${entry.quantity}× ` : ''}${entry.title}`))
        .filter(Boolean).map((part) => (/[.!?]$/.test(part) ? part : `${part}.`)).join(' ');
      if (contents && contents.textContent !== text) contents.textContent = text;
      if (pending) option.el.classList.remove('qb-v2-pending');
    }

    // Prices and texts of one extra product. The server render can only use the compare-at price for item compare
    // prices, so "Compare price based on: Regular price" always re-renders them
    renderEntry(entry, keep, compareSource = 'compare_price') {
      if (!entry.el) return;
      const money = (cents) => this.money.html(cents);
      const id = entry.variantId;
      if (entry.role === 'gift' || entry.role === 'unlock') {
        const value = entry.quantity * entry.price;
        const values = { title: escapeHtml(entry.title), quantity: entry.quantity, value: money(value) };
        if (entry.role === 'unlock') {
          values.unlock_quantity = entry.child.dataset.qbUnlockQuantity;
          entry.child.classList.toggle('is-locked', !entry.unlocked);
        }
        keyed(entry.row.querySelector('[data-qb-gift-value], .qb-v2-unlock__value'), `${id}|${value}`, (element) => { element.innerHTML = money(value); }, keep);
        entry.row.querySelectorAll(':is(.qb-v2-gift__text, .qb-v2-unlock__text) .qb-v2-text').forEach((element) => {
          keyed(element, `${id}|${value}|${entry.title}`, (target) => { target.innerHTML = fill(target.dataset.qbText, values); }, keep);
        });
        return;
      }
      const line = extraLine({ role: entry.role, quantity: entry.quantity, price: entry.price, compare: entry.compare }, entry.discount, { rate: this.rate, compareSource });
      keep = keep && compareSource === 'compare_price';
      const key = `${id}|${entry.quantity}|${line.total}|${line.compare}`;
      keyed(entry.el.querySelector('[data-qb-item-price]'), key, (element) => { element.innerHTML = money(line.total); }, keep);
      const compare = entry.el.querySelector('[data-qb-item-compare]');
      keyed(compare, key, (element) => { element.innerHTML = money(line.compare); }, keep);
      if (compare) compare.classList.toggle('hidden', !(line.compare > line.total));
      if (!entry.role.endsWith('upsell')) return;
      const saving = Math.max(0, line.compare - line.total);
      const percent = `${line.compare > 0 ? Math.floor((100 * saving) / line.compare + 0.05) : 0}%`;
      const values = { title: escapeHtml(entry.title), quantity: entry.quantity, price: money(line.total), compare_price: money(line.compare), amount_saved: money(saving), amount: money(saving), percentage_saved: percent, percentage: percent };
      entry.el.querySelectorAll('.qb-v2-text[data-qb-ctx="upsell"]').forEach((element) => {
        keyed(element, key, (target) => { target.innerHTML = fill(target.dataset.qbText, values); }, keep);
        if (SAVING_TEXT.test(element.dataset.qbText || '')) element.hidden = !(saving > 0) || line.noRate;
      });
    }

    // The selected option plus its ticked wrapper-level add-ons and unlocked gifts: savings line, product price, Add to
    // cart price
    selectedTotals() {
      const option = this.selected;
      if (!option || !option.result) return { T: 0, C: 0, S: 0, P: 0, q: 1, noRate: false };
      let { T, C } = option.result;
      const { from } = option.result;
      let extra = false;
      this.collect(option, true).forEach((entry) => {
        if (!entry.added || !['wrapper-upsell', 'unlock'].includes(entry.role)) return;
        const line = extraLine({ role: entry.role, quantity: entry.quantity, price: entry.price, compare: entry.compare, counts: entry.counts }, entry.discount, { rate: this.rate, compareSource: option.compareSource });
        T += line.total;
        C += line.compare;
        extra = extra || line.total > 0 || line.compare > 0;
      });
      // A "From" price has no compare price or saving yet, add-ons included
      if (from) C = T;
      const S = Math.max(0, C - T);
      return { T, C, S, P: extra && !from ? (C > 0 ? Math.floor((100 * S) / C + 0.05) : 0) : option.result.P, q: option.result.q, noRate: option.result.noRate, from };
    }

    renderSavings(totals) {
      const savings = this.querySelector(':scope > .qb-v2__savings');
      if (!savings || !this.selected) return;
      const pending = savings.classList.contains('qb-v2-pending');
      const values = this.keywords({ ...totals, E: 0, CE: 0, F: 0, paid: 0 }, null);
      savings.querySelectorAll('.qb-v2-text').forEach((element) => this.renderText(element, totals, values, pending));
      savings.classList.remove('qb-v2-pending');
    }

    announce(reason, totals) {
      const region = this.querySelector(':scope > [data-qb-announce]');
      if (!region || !ANNOUNCED.includes(reason) || !this.selected) return;
      clearTimeout(this.announceTimer);
      this.announceTimer = setTimeout(() => {
        region.textContent = `${this.plainTitle(this.selected)} ${plain(this.fromPrice(this.money.html(totals.T), totals.from))}`;
      }, 400);
    }

    // ---------- main.js state ----------
    // handleSelectChange gives formVariants to whichever option's unit changed (M:3424-3430): the selected one wins
    assertFormVariants() {
      if (!this.active || this.unitsPending || !this.qb) return;
      const option = this.checkedOption() || this.selected;
      if (option) this.qb.formVariants = this.qb.hasVariants ? (this.qb.selectedVariants && this.qb.selectedVariants[`input_${option.index}`]) || [] : [];
    }

    // The widget's own texts read offerPrices (M:3693-3698) and only re-render from main.js's handlers
    writeOfferPrices() {
      const offers = this.qb.offerPrices;
      if (!offers) return;
      this.options.forEach((option) => {
        if (option.dormant || !option.result) return;
        const main = this.qb.subDiscountType ? computeOption(this.modelFor(option, false)).M : option.result.M;
        offers[`offer_${option.index}`] = { price: main, compare_price: option.result.Cm };
      });
      const widget = this.widget;
      if (widget && widget.displayedPrices !== 'unit' && typeof widget.renderSubTexts === 'function') this.guard(() => widget.renderSubTexts());
    }

    // ---------- Selection ----------
    selectOption(value, { source = 'api' } = {}) {
      const option = this.resolveOption(value);
      if (!option || !this.active || !this.isSelectable(option) || option.input.disabled) return false;
      if (option.input.checked && this.selected === option) return true;
      this.check(option, source);
      return true;
    }

    // main.js's own listener on the radio runs first (handleChange reads the radio, M:3499-3515)
    check(option, source) {
      this.source = source;
      try {
        option.input.checked = true;
        fire(option.input);
      } finally {
        this.source = null;
      }
    }

    onRadioChange(option) {
      const source = this.source || 'user';
      this.setSelected(option);
      this.recompute(source === 'user' || source === 'api' ? 'select' : source);
      if (['user', 'api', 'nudge', 'scratch'].includes(source)) this.showGalleryImage(option);
    }

    setSelected(option) {
      this.selected = option || null;
      this.options.forEach((entry) => {
        entry.el.classList.toggle('is-selected', entry === this.selected);
        // Bodies of other options are inert on the storefront, so a click there reaches the option (6.6.1). Under a
        // scratch cover only the cover can be reached (its controls would take focus unseen)
        if (entry.body && !this.designMode) {
          entry.body.toggleAttribute('inert', entry !== this.selected && !entry.locked);
          for (const child of entry.body.children) child.toggleAttribute('inert', !!entry.locked && !child.matches('.qb-v2-scratch'));
        }
      });
      if (this.lb && this.qb.contains(this.lb.trigger) && !(option && option.el.contains(this.lb.trigger))) this.closeListbox();
      if (option) this.enhancePickers(option.el);
    }

    // MediaGallery.setActiveMedia scrolls to the image on Stacked and 1 column layouts (media-gallery.js:57-64)
    showGalleryImage(option) {
      if (!option.galleryKey) return;
      document.querySelectorAll(`[id^="MediaGallery-${this.sectionId}"]`).forEach((gallery) => {
        if (typeof gallery.setActiveMedia !== 'function') return;
        const scrolls = !gallery.querySelector('[id^="GalleryThumbnails"]') || ['stacked', 'single_column'].includes(gallery.dataset.desktopLayout);
        const top = window.scrollY;
        this.guard(() => gallery.setActiveMedia(option.galleryKey, true));
        if (scrolls) setTimeout(() => requestAnimationFrame(() => window.scrollTo({ top, behavior: 'instant' })));
      });
    }

    syncRadios() {
      this.options.forEach((option) => {
        option.input.disabled = !(this.active && this.isSelectable(option));
      });
    }

    // ---------- Listeners ----------
    listen() {
      const on = (target, type, handler, options) => {
        if (!target) return;
        target.addEventListener(type, handler, options);
        this.cleanups.push(() => target.removeEventListener(type, handler, options));
      };
      ['change', 'click', 'keydown', 'input'].forEach((type) => on(this, type, (event) => event.target instanceof Element && this.guard(() => this[`on${type[0].toUpperCase()}${type.slice(1)}`](event))));
      on(this.listbox, 'mousedown', (event) => event.preventDefault());
      // The theme's modals (quick add) close on Escape's keyup: an Escape that closed a V2 list (onTriggerKey) or popup
      // (its cancel event, which doesn't bubble) ends here; the next keydown clears the flag
      on(this, 'cancel', () => { this.escaped = true; }, true);
      on(this, 'keyup', (event) => event.key === 'Escape' && this.escaped && event.stopPropagation());
      on(this.form, 'change', (event) => event.target && event.target.name === 'id' && this.guard(() => this.onIdChange()));
      ['click', 'change'].forEach((type) => on(this.widget, type, () => this.guard(() => this.onWidget())));
      const unsubscribers = [pubSub('variantChange', (payload) => this.onVariantChange(payload))];
      if (this.patched) {
        on(document, 'product-form:before-add', (event) => this.onBeforeAdd(event));
        on(document, 'product-form:added', (event) => this.guard(() => this.onAdded(event)));
        on(document, 'product-form:error', (event) => this.guard(() => this.onAddError(event)));
      } else {
        // Capture phase: runs before ProductForm on every path (drawer, notification, page cart, skip cart)
        on(document, 'submit', (event) => this.onSubmitCapture(event), true);
        on(document, 'click', (event) => this.onClickCapture(event), true);
        unsubscribers.push(pubSub('cartUpdate', (payload) => this.onCartUpdate(payload)));
      }
      unsubscribers.forEach((unsubscribe) => unsubscribe && this.cleanups.push(unsubscribe));
      if (this.designMode) on(document, 'shopify:block:select', (event) => this.guard(() => this.onBlockSelect(event)));

      this.unitObserver = new MutationObserver((records) => this.guard(() => this.onUnitMutations(records)));
      this.selectObserver = new MutationObserver((records) => this.guard(() => {
        new Set(records.map((record) => (record.target.nodeType === 1 ? record.target : record.target.parentElement).closest('.qb-v2-picker'))).forEach((picker) => this.syncPicker(picker));
      }));
      const observers = [this.unitObserver, this.selectObserver];
      this.options.forEach((option) => {
        if (!option.dormant) option.unitEls.forEach((unit) => this.unitObserver.observe(unit, { attributes: true, attributeFilter: ['data-selected-id'] }));
      });
      this.querySelectorAll('.qb-v2-picker select').forEach((select) => this.watchSelect(select));
      if (this.designMode) {
        // An option or child the editor re-rendered alone (wrapper-level ones sit in the slots) still holds the wrapper's
        // tokens: repair and start again
        const editor = new MutationObserver((records) => {
          if (this.restarting || !records.some((record) => Array.from(record.addedNodes).some((node) => node.nodeType === 1 && node.outerHTML.includes('__QB_')))) return;
          this.restarting = true;
          queueMicrotask(() => {
            this.restarting = false;
            if (!this.isConnected || !this.ready) return;
            this.teardown();
            this.init();
          });
        });
        // The options and slots in depth; the wrapper's own children only (the setup panel redraws often)
        editor.observe(this, { childList: true });
        [this.qb, ...this.querySelectorAll(':scope > .qb-v2__slot')].forEach((target) => editor.observe(target, { childList: true, subtree: true }));
        observers.push(editor);
      }
      this.cleanups.push(() => observers.forEach((observer) => observer.disconnect()));
    }

    // main.js rewrites option texts, classes and whole lists (M:3975-3996, M:5199-5203): the custom UI follows
    watchSelect(select) {
      if (!this.selectObserver || this.watched.has(select)) return;
      this.watched.add(select);
      this.selectObserver.observe(select, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ['class', 'disabled', 'hidden', 'selected'] });
    }

    onChange(event) {
      const target = event.target;
      const option = this.stateOf(target.closest('.qb-v2-option'));
      if (target.matches('.qb-v2-option > .qb-v2-option__input')) {
        if (option && target.checked) this.onRadioChange(option);
      } else if (target.matches('.qb-v2-unit select')) {
        if (option && event.isTrusted) option.touched = true;
        this.syncPicker(target.closest('.qb-v2-picker'));
        this.recompute('unit');
      } else if (target.matches('.qb-v2-xselect')) {
        this.onExtraSelect(target);
      } else if (target.matches('.qb-v2-upsell__input')) {
        this.recompute('upsell');
      } else if (target.matches('.qb-v2-stepper__input')) {
        if (option && option.stepper) this.setStep(option, int(target.value, option.units), true);
      } else if (target === this.quantityField) {
        this.mirrorQuantity();
      }
    }

    onInput(event) {
      if (event.target.matches('[data-qb-child="field"] input')) {
        clearTimeout(this.fieldTimer);
        this.fieldTimer = setTimeout(() => this.recompute('field'), 150);
      } else if (event.target === this.quantityField) {
        this.mirrorQuantity();
      }
    }

    onClick(event) {
      const target = event.target;
      const step = target.closest('[data-qb-step]');
      const toggle = target.closest('.qb-v2-units__toggle');
      const trigger = target.closest('.qb-v2-dd');
      const swatch = target.closest('.qb-v2-sw [role="radio"]');
      const row = this.lb && target.closest('[role="option"]');
      if (step) {
        const option = this.stateOf(step.closest('.qb-v2-option'));
        if (option && option.stepper) this.setStep(option, option.units + int(step.dataset.qbStep) * option.stepper.step, true);
      } else if (toggle) this.expandUnits(toggle);
      else if (trigger) {
        if (this.lb && this.lb.trigger === trigger) this.closeListbox();
        else this.openListbox(trigger);
      } else if (swatch) this.pickSwatch(swatch);
      else if (row && this.listbox.contains(row)) this.commitListbox(this.lb.items.findIndex((item) => item.el === row), true);
      else {
        const element = target.closest('.qb-v2-option');
        const option = element && this.qb.contains(element) ? this.stateOf(element) : null;
        if (!option || option === this.selected || target.closest(INTERACTIVE) || (this.designMode && target.closest('[data-qb-child]'))) return;
        this.selectOption(option, { source: 'user' });
      }
    }

    onKeydown(event) {
      this.escaped = false;
      if (event.target.matches('.qb-v2-dd')) this.onTriggerKey(event, event.target);
      else if (event.target.matches('.qb-v2-sw [role="radio"]')) this.onSwatchKey(event, event.target);
    }

    // The widget's boxes fire no change (M:3579-3608) and force main.js's price pushes back on (M:3553-3554)
    onWidget() {
      this.qb.updatePrices = this.qb.updatePdpPrices = false;
      this.recompute('subscription');
    }

    onBlockSelect(event) {
      const option = event.target instanceof Element ? this.stateOf(event.target.closest('.qb-v2-option')) : null;
      if (!option || !this.contains(option.el)) return;
      const selectable = this.isSelectable(option);
      this.options.forEach((entry) => entry.el.classList.toggle('is-previewed', entry === option && !selectable));
      if (selectable) this.selectOption(option, { source: 'editor' });
    }

    // ---------- Units, stepper, defaults ----------
    onUnitMutations(records) {
      new Set(records.map((record) => record.target)).forEach((unit) => {
        unit.querySelectorAll('.qb-v2-picker').forEach((picker) => this.syncPicker(picker));
        const option = this.stateOf(unit.closest('.qb-v2-option'));
        if (option && this.sameForAll && !option.expanded && option.unitEls[0] === unit) this.mirrorUnits(option);
      });
      this.recompute('unit');
    }

    // All selects of a unit first, then one change: main.js reads every select of the unit (M:3399) and would
    // otherwise resolve half-set combinations
    setUnitValues(unit, values) {
      const selects = Array.from(unit.querySelectorAll('select'));
      const wanted = selects.map((select, index) => (values[index] ? values[index] : select.value));
      const variant = this.findVariant((options) => options.every((value, index) => wanted[index] === undefined || same(value, wanted[index])));
      let last = null;
      selects.forEach((select, index) => {
        const option = Array.from(select.options).find((entry) => same(entry.value, variant ? variant.options[index] : wanted[index]) && (variant || !entry.disabled));
        if (option && select.value !== option.value) {
          select.value = option.value;
          last = select;
        }
      });
      if (!last) return;
      fire(last);
      this.assertFormVariants();
    }

    applyDefaults(options) {
      const qb = this.qb;
      const prevent = qb.preventGalleryScroll;
      qb.preventGalleryScroll = true;
      try {
        options.forEach((option) => {
          const items = option.defaultOptions.split(',').map((item) => item.split('/').map((value) => value.trim())).filter((item) => item.some(Boolean));
          if (option.dormant || !option.hasPickers || !items.length) return;
          const collapsed = this.sameForAll && !option.expanded;
          option.unitEls.forEach((unit, index) => this.setUnitValues(unit, items[collapsed ? 0 : Math.min(index, items.length - 1)]));
        });
      } finally {
        qb.preventGalleryScroll = prevent;
      }
      this.assertFormVariants();
    }

    // "One picker for all items": while collapsed, the other units follow the first one
    mirrorUnits(option) {
      const variant = this.variant(option.unitEls[0].dataset.selectedId);
      if (!variant) return;
      option.unitEls.slice(1).forEach((unit) => unit.dataset.selectedId !== String(variant.id) && this.setUnitValues(unit, variant.options || []));
      this.assertFormVariants();
    }

    expandUnits(toggle) {
      const units = toggle.closest('.qb-v2-units');
      const option = this.stateOf(toggle.closest('.qb-v2-option'));
      if (!units || !option) return;
      option.expanded = true;
      units.classList.add('is-expanded');
      toggle.setAttribute('aria-expanded', 'true');
      toggle.hidden = true;
      this.enhancePickers(units);
      const control = option.unitEls[1] && visible(option.unitEls[1]);
      if (control) control.focus({ preventScroll: true });
    }

    setStep(option, value, fromShopper = false) {
      const { min, max, step } = option.stepper;
      let units = Math.max(min, Math.min(max, int(value, min)));
      units = min + Math.floor((units - min) / step) * step;
      const input = option.label.querySelector('.qb-v2-stepper__input');
      if (input && input.value !== String(units)) input.value = String(units);
      option.label.querySelectorAll('[data-qb-step]').forEach((button) => {
        button.disabled = int(button.dataset.qbStep) < 0 ? units <= min : units + step > max;
      });
      if (units === option.units && option.input.value === String(units)) return;
      option.units = units;
      option.input.value = option.label.dataset.quantity = String(units);
      // main.js reads the quantity from the radio's change (M:3500), also when a new variant's stock lowered the maximum
      if (option.input.checked && this.active) this.check(option, 'stepper');
      if (fromShopper) this.recompute('stepper');
    }

    // ---------- Pickers (the native select stays the source of truth) ----------
    enhancePickers(root) {
      if (root) root.querySelectorAll('.qb-v2-picker').forEach((picker) => this.syncPicker(picker, true));
    }

    pickerMode(picker, select) {
      if (this.pickerStyle !== 'mixed') return { buttons: 'swatches', image_dropdown: 'image' }[this.pickerStyle] || 'native';
      if (!picker.dataset.qbMode) {
        const shown = Array.from(select.options).filter((option) => !option.hidden);
        picker.dataset.qbMode = hasSwatches(shown) || shown.length <= 5 ? 'swatches' : 'dropdown';
      }
      return picker.dataset.qbMode === 'swatches' ? 'swatches' : 'image';
    }

    syncPicker(picker, first = false) {
      const select = picker && !picker.closest('.qb-v2-dialog, template') && picker.querySelector('select');
      if (!select) return;
      this.watchSelect(select);
      const mode = this.pickerMode(picker, select);
      if (mode === 'image') this.syncTrigger(picker, select, first);
      else if (mode === 'swatches') this.syncSwatches(picker, select);
    }

    syncTrigger(picker, select, first) {
      const trigger = picker.querySelector('.qb-v2-dd');
      if (!trigger) return;
      const option = select.options[select.selectedIndex];
      const valueEl = trigger.querySelector('.qb-v2-dd__value');
      const text = option ? textOf(option) : '';
      if (valueEl && valueEl.textContent !== text) valueEl.textContent = text;
      const value = option ? option.value : '';
      // The server printed the image of the selected value
      if (trigger._qbValue === value || (first && trigger._qbValue === undefined)) {
        trigger._qbValue = value;
        return;
      }
      trigger._qbValue = value;
      const media = trigger.querySelector('.qb-v2-dd__image');
      if (media) media.innerHTML = option ? mediaHtml(option) : '';
    }

    syncSwatches(picker, select) {
      const wrap = picker.querySelector('.qb-v2-sw');
      if (!wrap) return;
      const options = Array.from(select.options).filter((option) => !option.hidden);
      const swatches = hasSwatches(options);
      const html = options.map((option) => swatchHtml(option, swatches, option.value === select.value)).join('');
      if (wrap._qbHtml === html) return;
      const focused = wrap.contains(document.activeElement);
      wrap._qbHtml = wrap.innerHTML = html;
      if (!wrap.querySelector('[tabindex="0"]') && wrap.firstElementChild) wrap.firstElementChild.tabIndex = 0;
      if (focused && wrap.querySelector('[tabindex="0"]')) wrap.querySelector('[tabindex="0"]').focus({ preventScroll: true });
    }

    commitValue(select, value) {
      if (select.value !== value) {
        select.value = value;
        const unit = select.closest('.qb-v2-unit');
        const option = unit && this.stateOf(unit.closest('.qb-v2-option'));
        if (option) option.touched = true;
        fire(select);
        if (unit) this.assertFormVariants();
      }
      this.syncPicker(select.closest('.qb-v2-picker'));
    }

    pickSwatch(button) {
      const select = button.closest('.qb-v2-picker').querySelector('select');
      if (select && button.getAttribute('aria-disabled') !== 'true') this.commitValue(select, button.dataset.value);
    }

    // APG radio group: arrows move and select, wrapping; disabled values are skipped
    onSwatchKey(event, button) {
      let direction = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[event.key];
      if (!direction) return;
      if (this.rtl && (event.key === 'ArrowLeft' || event.key === 'ArrowRight')) direction = -direction;
      event.preventDefault();
      const buttons = Array.from(button.parentElement.querySelectorAll('[role="radio"]')).filter((entry) => entry === button || entry.getAttribute('aria-disabled') !== 'true');
      const next = buttons[(buttons.indexOf(button) + direction + buttons.length) % buttons.length];
      if (next !== button) this.pickSwatch(next);
    }

    // Image dropdown: APG select-only combobox over one shared listbox; focus stays on the trigger. The listbox is
    // absolute inside the widget, never fixed (animated sections)
    openListbox(trigger, at) {
      const listbox = this.listbox;
      const select = listbox && trigger.closest('.qb-v2-picker').querySelector('select');
      if (!select) return;
      this.closeListbox();
      if (!listbox.id) listbox.id = `qbv2-${this.sectionId}-${this.blockId}-listbox`;
      const items = Array.from(select.options).filter((option) => !option.hidden).map((option) => ({ option }));
      listbox.innerHTML = items.map(({ option }, index) => `<div role="option" id="${listbox.id}-opt-${index}" aria-selected="${option.selected}"${option.disabled ? ' aria-disabled="true"' : ''}${isUnavailable(option) ? ' class="is-unavailable"' : ''}>${mediaHtml(option)}<span>${escapeHtml(textOf(option))}</span></div>`).join('');
      Array.from(listbox.children).forEach((element, index) => { items[index].el = element; });
      // Named like its trigger without the value: the option name, after the item number for a unit ("#2 Color")
      listbox.setAttribute('aria-labelledby', trigger.getAttribute('aria-labelledby').replace(/ \S+$/, ''));
      this.lb = { trigger, select, items, active: -1, buffer: '', width: window.innerWidth };
      listbox.hidden = false;
      const host = this.getBoundingClientRect();
      const rect = trigger.getBoundingClientRect();
      listbox.style.minWidth = `${Math.round(rect.width)}px`;
      const below = window.innerHeight - rect.bottom;
      const top = below < 280 && rect.top > below ? rect.top - listbox.offsetHeight - 4 : rect.bottom + 4;
      listbox.style.top = `${Math.round(top - host.top - this.clientTop)}px`;
      listbox.style.left = this.rtl ? 'auto' : `${Math.round(rect.left - host.left - this.clientLeft)}px`;
      listbox.style.right = this.rtl ? `${Math.round(host.right - rect.right - this.clientLeft)}px` : 'auto';
      trigger.setAttribute('aria-expanded', 'true');
      const current = items.findIndex((item) => item.option.selected);
      this.moveListbox(at === 'first' ? 0 : at === 'last' ? items.length - 1 : Math.max(0, current));
      document.addEventListener('pointerdown', this.onOutside, true);
      window.addEventListener('resize', this.onResize);
    }

    moveListbox(index) {
      const lb = this.lb;
      if (!lb || !lb.items.length) return;
      if (lb.items[lb.active]) lb.items[lb.active].el.classList.remove('is-active');
      lb.active = Math.max(0, Math.min(lb.items.length - 1, index));
      const element = lb.items[lb.active].el;
      element.classList.add('is-active');
      lb.trigger.setAttribute('aria-activedescendant', element.id);
      const box = this.listbox;
      if (element.offsetTop < box.scrollTop) box.scrollTop = element.offsetTop;
      else if (element.offsetTop + element.offsetHeight > box.scrollTop + box.clientHeight) box.scrollTop = element.offsetTop + element.offsetHeight - box.clientHeight;
    }

    closeListbox() {
      const lb = this.lb;
      if (!lb) return;
      this.lb = null;
      clearTimeout(lb.timer);
      this.listbox.hidden = true;
      this.listbox.innerHTML = '';
      lb.trigger.setAttribute('aria-expanded', 'false');
      lb.trigger.removeAttribute('aria-activedescendant');
      document.removeEventListener('pointerdown', this.onOutside, true);
      window.removeEventListener('resize', this.onResize);
    }

    // Disabled values can be active but not chosen
    commitListbox(index, refocus) {
      const item = this.lb && this.lb.items[index];
      if (!item || item.option.disabled) return false;
      const { trigger, select } = this.lb;
      this.closeListbox();
      this.commitValue(select, item.option.value);
      if (refocus) trigger.focus({ preventScroll: true });
      return true;
    }

    typeahead(char) {
      const lb = this.lb;
      clearTimeout(lb.timer);
      lb.buffer += char.toLowerCase();
      lb.timer = setTimeout(() => { lb.buffer = ''; }, 500);
      const start = Math.max(0, lb.buffer.length === 1 ? lb.active + 1 : lb.active);
      for (let i = 0; i < lb.items.length; i += 1) {
        const index = (start + i) % lb.items.length;
        if (textOf(lb.items[index].option).toLowerCase().startsWith(lb.buffer)) return this.moveListbox(index);
      }
      return undefined;
    }

    onTriggerKey(event, trigger) {
      const { key } = event;
      const printable = key.length === 1 && key !== ' ' && !event.ctrlKey && !event.metaKey && !event.altKey;
      const lb = this.lb && this.lb.trigger === trigger ? this.lb : null;
      if (!lb) {
        if (!printable && !['ArrowDown', 'ArrowUp', 'Enter', ' ', 'Home', 'End'].includes(key)) return;
        event.preventDefault();
        this.openListbox(trigger, { Home: 'first', End: 'last' }[key]);
        if (printable && this.lb) this.typeahead(key);
        return;
      }
      if (key === 'Tab') {
        if (!this.commitListbox(lb.active, false)) this.closeListbox();
        return;
      }
      const moves = { ArrowDown: lb.active + 1, ArrowUp: lb.active - 1, Home: 0, End: lb.items.length - 1, PageDown: lb.active + 10, PageUp: lb.active - 10 };
      if (!printable && !(key in moves) && !['Enter', ' ', 'Escape'].includes(key)) return;
      event.preventDefault();
      if ((key === 'ArrowUp' && event.altKey) || key === 'Enter' || key === ' ') this.commitListbox(lb.active, false);
      else if (key === 'Escape') {
        this.closeListbox();
        this.escaped = true;
      } else if (key in moves) this.moveListbox(moves[key]);
      else this.typeahead(key);
    }

    // ---------- Extra products ----------
    pickerSelects(scope) {
      return Array.from(scope.querySelectorAll('.qb-v2-picker'))
        .sort((a, b) => int(a.dataset.optionPosition) - int(b.dataset.optionPosition))
        .map((picker) => picker.querySelector('select'))
        .filter(Boolean);
    }

    onExtraSelect(select) {
      const item = select.closest('[data-qb-item], [data-qb-child="upsell"]');
      const json = item && this.product(item.dataset.productId);
      if (!json) return;
      const selects = this.pickerSelects(item);
      const position = selects.indexOf(select);
      // No variant with these values: keep the value just picked and take the closest variant that has it
      const candidates = (json.variants || []).filter((entry) => (entry.options || [])[position] === select.value);
      const variant = resolveVariant(json, selects.map((entry) => entry.value)) || candidates.find((entry) => entry.available !== false) || candidates[0];
      if (!variant) return;
      this.setItemVariant(item, json, variant);
      // A gift keeps its variant in the original row and in its copies in bigger options
      const gift = item.closest('[data-qb-child="gift"]');
      if (gift) {
        this.querySelectorAll('[data-qb-child="gift"]').forEach((root) => {
          if (root.dataset.qbBlock !== gift.dataset.qbBlock) return;
          root.querySelectorAll('[data-qb-item]').forEach((other) => other !== item && other.dataset.productId === item.dataset.productId && this.setItemVariant(other, json, variant));
        });
      }
      this.recompute('extra');
    }

    setItemVariant(item, json, variant) {
      item.dataset.variantId = String(variant.id);
      item.dataset.available = String(variant.available !== false);
      const selects = this.pickerSelects(item);
      selects.forEach((select, index) => {
        const value = (variant.options || [])[index];
        if (value !== undefined && select.value !== value) select.value = value;
      });
      this.updateExtraStatuses(selects, json, variant);
      const status = item.querySelector('.qb-v2-item__status');
      if (status) status.hidden = variant.available !== false;
      const image = item.querySelector('img[data-qb-item-img]');
      if (image && image.dataset.qbItemImg !== 'fixed') {
        const images = json.images || {};
        const options = variant.options || [];
        const position = options.findIndex((value, index) => images[`${index + 1}|${value}`]);
        const src = position >= 0 ? images[`${position + 1}|${options[position]}`] : json.image;
        if (src && image.getAttribute('src') !== src) {
          image.removeAttribute('srcset');
          image.removeAttribute('sizes');
          image.src = src;
        }
      }
      selects.forEach((select) => this.syncPicker(select.closest('.qb-v2-picker')));
    }

    // Value statuses as main.js writes them for units (M:3962-3998): each position against the values before it, so
    // every value of the first position stays reachable
    updateExtraStatuses(selects, json, variant) {
      const hideSoldOut = /hidden/.test(this.dataset.qbTSoldoutAttr || '');
      const template = (window.variantStrings && window.variantStrings.unavailable_with_option) || '';
      const chosen = variant.options || [];
      selects.forEach((select, position) => {
        const candidates = (json.variants || []).filter((entry) => (entry.options || []).slice(0, position).every((value, index) => value === chosen[index]));
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

    // Pre-ticked add-ons get their state from here, never from a checked attribute (main.js reads input[checked], M:3262)
    initUpsell(upsell) {
      const input = upsell.querySelector('.qb-v2-upsell__input');
      if (input) input.checked = upsell.dataset.qbDefaultChecked === 'true' && !input.disabled && upsell.dataset.available !== 'false';
    }

    // "Complementary products" upsells: the section rendered with Search & Discovery's recommendations holds the row
    // (the pattern of blocks/product_complementary.liquid). Nothing found: the upsell stays hidden
    loadComplementary() {
      const roots = Array.from(this.querySelectorAll('[data-qb-child="upsell"][data-qb-reco-url]:not([data-qb-reco-loaded])'));
      if (!roots.length) return;
      const idle = window.requestIdleCallback || ((callback) => setTimeout(callback, 1500));
      idle(() => roots.forEach((root) => this.loadRecommendation(root).catch(report)));
    }

    async loadRecommendation(root) {
      root.dataset.qbRecoLoaded = 'false';
      const original = this.sectionId.replace(/^quickadd-/, '');
      // Quick add prefixed the section id in the URL (quick-add.js:106-112); the section only renders under its own id
      const response = await fetch(root.dataset.qbRecoUrl.replace('section_id=quickadd-', 'section_id='));
      const doc = new DOMParser().parseFromString(await response.text(), 'text/html');
      // The row's content, with the product attributes on its holder
      const row = doc.querySelector(`[data-qbv2-reco="${CSS.escape(root.dataset.qbBlock || '')}"][data-product-id]`);
      if (!row || !root.isConnected) return;
      const setup = Array.from(root.querySelectorAll(':scope > script[data-qbv2-setup]'));
      // In quick add the rest of the modal carries quickadd- ids; the fetched row must too, or its label would point at
      // the page's own checkbox
      root.innerHTML = this.sectionId === original ? row.innerHTML : row.innerHTML.split(original).join(this.sectionId);
      root.append(...setup);
      ['productId', 'variantId', 'available'].forEach((key) => { root.dataset[key] = row.dataset[key] || ''; });
      if (!root.querySelector('.qb-v2-upsell__input')) return;
      root.dataset.qbRecoLoaded = 'true';
      root.hidden = false;
      this.initUpsell(root);
      this.enhancePickers(root);
      // A ticked add-on whose variant is sold out blocks Add to cart like any other extra (6.6.15)
      this.registerRequired();
      this.recompute('upsell');
    }

    // A candidate card of a child's <template data-qb-candidates> and its product JSON (carried gift copies have
    // templates without JSON; product() finds it in the original's)
    candidate(roots, productId) {
      let card = null;
      roots.some((root) => {
        const template = root.querySelector('template[data-qb-candidates]');
        card = template && template.content.querySelector(`[data-qb-candidate][data-product-id="${CSS.escape(String(productId))}"]`);
        return Boolean(card);
      });
      const json = card && this.product(productId);
      if (!json) return null;
      const variants = json.variants || [];
      return { card, json, pick: (id) => variants.find((variant) => String(variant.id) === String(id || card.dataset.variantId)) || variants.find((variant) => variant.available !== false) || variants[0] };
    }

    // "One product of their choice": the chosen gift row takes a candidate's product, in every copy of the gift
    setGiftChoice(childEl, productId, variantId) {
      const root = childEl && childEl.closest && childEl.closest('[data-qb-child="gift"]');
      if (!root) return false;
      const roots = Array.from(this.querySelectorAll('[data-qb-child="gift"]')).filter((gift) => gift.dataset.qbBlock === root.dataset.qbBlock);
      const found = this.candidate(roots, productId);
      const variant = found && found.pick(variantId);
      if (!variant) return false;
      roots.forEach((gift) => {
        const row = gift.querySelector('[data-qb-gift-row][data-qb-chosen="true"]') || gift.querySelector('[data-qb-gift-row]');
        const item = row && row.querySelector('[data-qb-item]');
        if (item) this.swapItem(item, found.card, found.json, variant);
      });
      this.recompute('gift-choice');
      return true;
    }

    // Product choice ("Customer chooses" starts empty): the slot shows the chosen candidate and its Change button
    setChoice(childEl, { productId, variantId } = {}) {
      const root = childEl && childEl.closest && childEl.closest('[data-qb-child="choice"]');
      const slot = root && root.querySelector('[data-qb-choice-slot]');
      const found = slot && this.candidate([root], productId);
      const variant = found && found.pick(variantId);
      if (!variant) return false;
      let item = slot.querySelector('[data-qb-item]');
      if (!item) {
        // The empty placeholder becomes an item row; its title id stays (the button is described by it). Prices and
        // picker follow the block's Show price / Show variant picker, which the candidate cards already reflect
        const empty = slot.querySelector('.qb-v2-item');
        const title = empty && empty.querySelector('.qb-v2-item__title');
        const quantity = Math.max(1, int(root.dataset.qbQuantity, 1));
        item = document.createElement('div');
        item.className = 'qb-v2-item qb-v2-item--row';
        item.setAttribute('data-qb-item', '');
        Object.assign(item.dataset, { role: 'choice', quantity: String(quantity) });
        item.innerHTML = `<div class="qb-v2-item__media"></div><div class="qb-v2-item__info"><span class="qb-v2-item__title" id="${escapeHtml(title ? title.id : '')}">${quantity > 1 ? `<span class="qb-v2-item__qty">${quantity}×</span> ` : ''}</span>${found.card.querySelector('[data-qb-item-price]') ? '<span class="qb-v2-item__prices"><span class="qb-v2-item__price" data-qb-item-price></span> <s class="qb-v2-item__compare hidden" data-qb-item-compare></s></span>' : ''}<span class="qb-v2-item__status" hidden>${escapeHtml(this.dataset.soldoutLabel || '')}</span></div>`;
        if (empty) empty.replaceWith(item);
        else slot.prepend(item);
      }
      this.swapItem(item, found.card, found.json, variant);
      root.classList.remove('qb-v2-choice--empty');
      this.choiceLabel(root, root.dataset.qbChangeLabel);
      this.recompute('choice');
      return true;
    }

    clearChoice(childEl) {
      const root = childEl && childEl.closest && childEl.closest('[data-qb-child="choice"]');
      const item = root && root.querySelector('[data-qb-choice-slot] [data-qb-item]');
      if (!item) return false;
      const title = item.querySelector('.qb-v2-item__title');
      const empty = document.createElement('div');
      empty.className = 'qb-v2-item qb-v2-item--row qb-v2-item--empty';
      // The empty title only keeps its id (the button says the label and is described by the block's title)
      empty.innerHTML = `<span class="qb-v2-item__placeholder" aria-hidden="true">?</span><span class="qb-v2-item__title" id="${escapeHtml(title ? title.id : '')}"></span>`;
      item.replaceWith(empty);
      root.classList.add('qb-v2-choice--empty');
      this.choiceLabel(root, root.dataset.qbEmptyLabel);
      this.recompute('choice');
      return true;
    }

    choiceLabel(root, label) {
      const button = root.querySelector('[data-qb-choice-slot] [data-qb-action="choice"]');
      if (button && label) button.textContent = label;
    }

    // Bundle builder: picks [{ productId, variantId, quantity }] fill the tray and become cart lines. At most
    // data-qb-picks units; each product once unless repeats are allowed
    setBuilderPicks(childEl, picks) {
      const root = childEl && childEl.closest && childEl.closest('[data-qb-child="builder"]');
      if (!root) return false;
      const max = Math.max(1, int(root.dataset.qbPicks, 1));
      const repeats = root.dataset.qbAllowRepeats !== 'false';
      const chosen = [];
      let left = max;
      (Array.isArray(picks) ? picks : []).forEach((pick) => {
        const found = pick && left > 0 && this.candidate([root], pick.productId);
        const variant = found && found.pick(pick.variantId);
        if (!variant || (!repeats && chosen.some((entry) => entry.productId === String(found.json.id)))) return;
        const quantity = Math.min(left, repeats ? Math.max(1, int(pick.quantity, 1)) : 1);
        const image = found.card.querySelector('.qb-v2-cand__media img');
        const same = chosen.find((entry) => entry.variantId === String(variant.id));
        left -= quantity;
        if (same) same.quantity += quantity;
        else chosen.push({ productId: String(found.json.id), variantId: String(variant.id), quantity, title: found.json.title || '', image: (image && image.getAttribute('src')) || found.json.image || '' });
      });
      root._qbPicks = chosen;
      const units = [];
      chosen.forEach((pick) => units.push(...Array(pick.quantity).fill(pick)));
      const tray = root.querySelector('[data-qb-builder-tray]');
      if (tray) {
        tray.innerHTML = Array.from({ length: max }, (_, index) => {
          const pick = units[index];
          // A product without an image shows its initial
          if (!pick) return '<span class="qb-v2-builder__slot" aria-hidden="true">?</span>';
          return `<span class="qb-v2-builder__slot is-filled" aria-hidden="true" title="${escapeHtml(pick.title)}">${pick.image ? `<img src="${escapeHtml(pick.image)}" alt="" width="40" height="40" loading="lazy">` : escapeHtml(pick.title.charAt(0))}</span>`;
        }).join('');
      }
      root.querySelectorAll('.qb-v2-builder__title .qb-v2-text').forEach((element) => {
        element.innerHTML = fill(element.dataset.qbText, { picks: max, chosen: units.length });
      });
      this.recompute('builder');
      return true;
    }

    // Fills an item row from a candidate card: image (unless the merchant's own), title, the card's picker (cards carry
    // one only when the block shows pickers) with its ids moved to this row's prefix, variant
    swapItem(item, card, json, variant) {
      item.dataset.productId = String(json.id);
      const media = item.querySelector('.qb-v2-item__media');
      const current = media && media.querySelector('img[data-qb-item-img]');
      const source = card.querySelector('.qb-v2-cand__media img');
      if (media && !(current && current.dataset.qbItemImg === 'fixed')) {
        // Without an image the cell keeps a placeholder: an empty div is hidden by the theme and the row would shift
        const image = source ? source.cloneNode(true) : document.createElement('span');
        if (source) image.setAttribute('data-qb-item-img', '');
        image.className = source ? 'qb-v2-item__img' : 'qb-v2-item__img qb-v2-item__img--placeholder';
        media.replaceChildren(image);
      }
      const title = item.querySelector('.qb-v2-item__title');
      if (title) {
        const quantity = title.querySelector('.qb-v2-item__qty');
        title.replaceChildren(...(quantity ? [quantity, ' '] : []), json.title || '');
      }
      const prefix = title && title.id ? title.id.replace(/-title$/, '') : '';
      const candidateTitle = card.querySelector('[id$="-title"]');
      const from = candidateTitle ? candidateTitle.id.replace(/-title$/, '') : '';
      const oldPicker = item.querySelector('.qb-v2-item__picker');
      if (oldPicker) oldPicker.remove();
      const pickers = card.querySelectorAll('.qb-v2-cand__picker .qb-v2-picker');
      if (pickers.length && prefix && from) {
        const box = document.createElement('div');
        box.className = 'qb-v2-item__picker';
        pickers.forEach((picker) => box.append(picker.cloneNode(true)));
        // Pickers reference their own ids in id and aria-labelledby; aria-controls (the shared listbox) stays
        box.querySelectorAll('*').forEach((element) => ['id', 'aria-labelledby'].forEach((name) => {
          const value = element.getAttribute(name);
          if (value) element.setAttribute(name, value.split(from).join(prefix));
        }));
        const status = item.querySelector('.qb-v2-item__status');
        (status ? status.parentElement : item).insertBefore(box, status);
      }
      this.setItemVariant(item, json, variant);
      this.enhancePickers(item);
    }

    // ---------- Cart lines ----------
    syncLines() {
      const lines = this.active && this.selected ? this.getCartLines(this.selected, { includeMain: false }) : [];
      const key = JSON.stringify([this.patched, lines.map((line) => [line.variantId, line.quantity, line.role, line.properties, line.parent])]);
      if (this.linesEl && key !== this.linesKey) {
        this.linesKey = key;
        const spans = [];
        lines.forEach((line) => {
          // Today's main.js adds every element once and merges equal variants (M:1409-1428); QB-1a reads one element per
          // line with its quantity, properties and parent
          for (let i = 0; i < (this.patched ? 1 : line.quantity); i += 1) {
            const span = document.createElement('span');
            span.className = `product-info-upsell-${this.sectionId}`;
            Object.assign(span.dataset, { selected: 'true', id: String(line.variantId), qbLine: line.role });
            if (this.patched) Object.assign(span.dataset, { quantity: String(line.quantity), properties: JSON.stringify(line.properties) }, line.parent ? { parent: line.parent } : {});
            spans.push(span);
          }
        });
        this.linesEl.replaceChildren(...spans);
      }
      // Main-line properties go into the form; main.js reads every properties[] input of ProductInfo, disabled or not
      // (M:1541-1549), so inputs that don't apply are removed
      if (!this.form) return;
      const properties = this.active && this.selected ? this.mainProperties(this.selected) : {};
      const inputs = Array.from(this.form.querySelectorAll('input[data-qb-v2-prop]'));
      inputs.forEach((input) => input.dataset.qbV2Prop in properties || input.remove());
      Object.keys(properties).forEach((name) => {
        let input = inputs.find((entry) => entry.dataset.qbV2Prop === name && entry.isConnected);
        if (!input) {
          input = Object.assign(document.createElement('input'), { type: 'hidden', name: `properties[${name}]` });
          input.dataset.qbV2Prop = name;
          this.form.append(input);
        }
        if (input.value !== properties[name]) input.value = properties[name];
      });
    }

    // Buy it now posts only the variant and the quantity: hidden whenever the selected option needs more
    syncBin() {
      const option = this.selected;
      if (!this.form) return;
      const current = this.currentId();
      const hide = Boolean(this.active && option && (
        this.getCartLines(option).some((line) => line.role !== 'main' || String(line.variantId) !== current) ||
        option.method === 'code' || (this.planAllowed && option.plan) || !this.isComplete(option) || Object.keys(this.mainProperties(option)).length
      ));
      this.form.classList.toggle('qb-v2-hide-bin', hide);
    }

    // ---------- Add to cart state of incomplete options ----------
    addButton() {
      return this.form && this.form.querySelector('[name="add"]');
    }

    // This widget's buttons only: quick add renders the main-product section (quick-add.js:26)
    atcButtons() {
      const buttons = new Set(this.form ? this.form.querySelectorAll('[name="add"], [id^="SectionAtcBtn-"]') : []);
      const sticky = document.getElementById(`sticky-atc-${this.sectionId}`);
      if (sticky && sticky.querySelector('.main-product-atc')) buttons.add(sticky.querySelector('.main-product-atc'));
      document.querySelectorAll(`.featured-product-atc-${this.sectionId}`).forEach((button) => buttons.add(button));
      return buttons;
    }

    canBeIncomplete() {
      return Boolean(this.qb.querySelector('.qb-v2-option__body :is([data-qb-must-choose="true"], [data-qb-item], [data-qb-child="upsell"])') || this.querySelector(':scope > .qb-v2__slot [data-qb-child="upsell"]'));
    }

    mustChooseOpen(option) {
      if (!option || !option.body) return [];
      return Array.from(option.body.querySelectorAll('[data-qb-must-choose="true"]')).filter((child) => {
        const kind = child.dataset.qbChild;
        const input = child.querySelector('input');
        if (kind === 'choice') return !child.querySelector('[data-qb-choice-slot] [data-qb-item]');
        if (kind === 'builder') return (child._qbPicks || []).reduce((sum, pick) => sum + (pick.quantity || 0), 0) < int(child.dataset.qbPicks, 1);
        return kind === 'field' && !(input && input.value.trim());
      });
    }

    soldOutExtras(option) {
      return option ? this.collect(option, true).filter((entry) => entry.added && !entry.available && entry.role !== 'gift') : [];
    }

    isComplete(option) {
      return !option || (!this.mustChooseOpen(option).length && !this.soldOutExtras(option).length);
    }

    incompleteMessage(option) {
      const open = this.mustChooseOpen(option)[0];
      if (open) return open.dataset.qbRequiredMessage || '';
      return this.soldOutExtras(option).length ? this.dataset.soldoutLabel || '' : '';
    }

    // Shares the Custom product field counters (M:4843, M:4882-4885), always read-modify-write. Buttons are only touched
    // when this widget changes the outcome, never while ProductForm disables them during an add
    registerRequired() {
      const button = this.addButton();
      if (this.requiredOn || !this.active || !button || !this.canBeIncomplete()) return;
      this.requiredOn = true;
      this.validCounted = this.isComplete(this.selected);
      this.count(button, 'requiredFields', 1);
      if (this.validCounted) this.count(button, 'validFields', 1);
      else this.applyButtonRule();
    }

    unregisterRequired() {
      if (!this.requiredOn) return;
      const button = this.addButton();
      const counted = this.validCounted;
      this.requiredOn = this.validCounted = false;
      if (button) {
        this.count(button, 'requiredFields', -1);
        if (counted) this.count(button, 'validFields', -1);
      }
      if (!counted) this.applyButtonRule();
    }

    count(button, name, step) {
      button.dataset[name] = String(int(button.dataset[name]) + step);
    }

    syncRequired() {
      if (!this.requiredOn) return;
      const complete = this.isComplete(this.selected);
      const button = this.addButton();
      if (button && complete !== this.validCounted) {
        this.validCounted = complete;
        this.count(button, 'validFields', complete ? 1 : -1);
        this.applyButtonRule();
      } else if ((complete ? '' : this.incompleteMessage(this.selected)) !== this.shownMessage) {
        this.applyButtonRule(true);
      }
    }

    // Same rule as CustomProductField.validateValue (M:4888-4911), for this widget's buttons
    applyButtonRule(messageOnly) {
      const button = this.addButton();
      if (!button) return;
      const valid = int(button.dataset.validFields) === int(button.dataset.requiredFields);
      if (!messageOnly) this.atcButtons().forEach((entry) => entry.toggleAttribute('disabled', !valid || button.dataset.unavailable === 'true'));
      const message = this.requiredOn && !this.validCounted ? this.incompleteMessage(this.selected) : '';
      this.shownMessage = message;
      const sticky = document.getElementById(`sticky-atc-${this.sectionId}`);
      [[button, 'main-atc'], [sticky, 'sticky-atc']].forEach(([root, prefix]) => {
        const error = root && root.querySelector(`.${prefix}__error`);
        const label = root && root.querySelector(`.${prefix}__label`);
        if (!error || !label) return;
        if (message) {
          // A Custom product field may own this element too: its message comes back afterwards
          if (error._qbPrevious === undefined) error._qbPrevious = error.innerHTML;
          error.textContent = message;
          error.style.display = '';
          label.style.display = 'none';
        } else if (error._qbPrevious !== undefined) {
          error.innerHTML = error._qbPrevious;
          error._qbPrevious = undefined;
          if (valid) {
            error.style.display = 'none';
            label.style.display = '';
          }
        }
      });
    }

    // ---------- Product page price display ----------
    // Server HTML for restores, from the page at init or from the fetched variant section (quick add: un-prefixed ids)
    savePdp(root) {
      const sid = root === document ? this.sectionId : this.sectionId.replace(/^quickadd-/, '');
      const read = (id) => (root.getElementById(id) ? root.getElementById(id).innerHTML : null);
      this.pdp = { price: read(`price-${sid}`), sticky: read(`sticky-atc-separate-price-${sid}`), spans: Array.from(root.querySelectorAll(`.main-atc-price-span-${sid}`), (span) => span.innerHTML) };
    }

    writePdp(totals) {
      const mode = this.dataset.priceDisplay || 'button';
      const result = this.active && this.selected && this.selected.result;
      // With the widget's price updates on, off and button modes show one unit (plan price while subscribing), as the
      // widget does without quantity breaks (M:3626-3629)
      const units = this.widgetUpdatesPrices() && this.unitValues();
      // An option still missing picks shows "From" its cheapest total here too (no compare price), as on its card
      if (result && mode === 'each') this.writeMain(result.E, result.CE, result.from);
      else if (result && mode === 'total') this.writeMain(totals.T, totals.C, totals.from);
      else if (units) this.writeMain(...units);
      else this.restore('main');
      if (result && mode !== 'off') this.writeSpans(totals.T, totals.from);
      else if (units) this.writeSpans(units[0]);
      else this.restore('spans');
    }

    unitValues() {
      const widget = this.widget;
      const price = int(widget.dataset.basePrice, int(this.baseVariant(null).price));
      const current = widget.isSubSelected && typeof widget.applySubTo === 'function' ? int(this.guard(() => widget.applySubTo(price)), price) : price;
      return [current, int(widget.dataset.baseComparePrice, price)];
    }

    writeMain(price, compare, from) {
      const holder = document.getElementById(`price-${this.sectionId}`);
      const withCurrency = this.dataset.currencyCodeEnabled === 'true';
      const set = (element, html) => element && element.innerHTML !== html && (element.innerHTML = html);
      document.querySelectorAll(`.price-${this.sectionId}`).forEach((element) => {
        // money_with_currency only inside #price (snippets/price.liquid:37-41); the sticky price hides the code
        const format = (cents) => this.money.format(cents, { withCurrency: withCurrency && Boolean(holder && holder.contains(element)) });
        const current = this.fromPrice(format(price), from);
        element.classList.toggle('price--on-sale', compare > price);
        set(element.querySelector('.price__regular .price-item--regular'), current);
        set(element.querySelector('.price__sale .price-item--sale'), current);
        if (!(compare > price)) return;
        set(element.querySelector('.price__sale .price-item--regular'), format(compare));
        set(element.querySelector('.badge__percentage-saved'), String(Math.floor((100 * (compare - price)) / compare + 0.05)));
        set(element.querySelector('.badge__money-saved'), this.money.format(compare - price, { trim: true }));
      });
      this.mainDirty = true;
    }

    writeSpans(price, from) {
      const html = this.fromPrice(this.money.format(price), from);
      document.querySelectorAll(`.main-atc-price-span-${this.sectionId}`).forEach((span) => span.innerHTML !== html && (span.innerHTML = html));
      this.spansDirty = true;
    }

    restore(what) {
      if (!this.pdp) return;
      if (what === 'main' && this.mainDirty) {
        this.mainDirty = false;
        [[`price-${this.sectionId}`, this.pdp.price], [`sticky-atc-separate-price-${this.sectionId}`, this.pdp.sticky]].forEach(([id, html]) => {
          const element = document.getElementById(id);
          if (element && html !== null) element.innerHTML = html;
        });
      } else if (what === 'spans' && this.spansDirty) {
        this.spansDirty = false;
        document.querySelectorAll(`.main-atc-price-span-${this.sectionId}`).forEach((span, index) => {
          if (this.pdp.spans[index] !== undefined) span.innerHTML = this.pdp.spans[index];
        });
      }
    }

    // ---------- Other quantity fields, fallback field, activation ----------
    otherQuantities() {
      return this.form ? Array.from(this.form.elements).filter((element) => element.name === 'quantity' && element.tagName === 'INPUT' && !this.contains(element)) : [];
    }

    // Disabled fields aren't posted by new FormData(form) (M:1785), so they can't override the option's quantity
    disableOtherQuantities() {
      this.otherQuantities().forEach((input) => {
        if (input.disabled) return;
        input.disabled = true;
        input.dataset.qbV2Disabled = 'true';
        quantityBox(input).classList.add('qb-v2-hidden-qty');
      });
    }

    restoreOtherQuantities() {
      this.otherQuantities().forEach((input) => {
        if (input.dataset.qbV2Disabled !== 'true') return;
        input.disabled = false;
        delete input.dataset.qbV2Disabled;
        quantityBox(input).classList.remove('qb-v2-hidden-qty');
      });
    }

    setFallback(show) {
      if (!this.fallback) return;
      this.fallback.hidden = !show;
      const input = this.fallback.querySelector('input[name="quantity"]');
      if (input) input.disabled = !show;
    }

    togglePicker(on) {
      const picker = this.dataset.showProductPicker === 'false' && document.getElementById(`variant-selects-${this.sectionId}`);
      if (picker) picker.classList.toggle('qb-v2-hidden-picker', on);
    }

    // While off, main.js's items[] path still reads quantityBreaks.selectedQuantity first (M:1489-1495)
    watchQuantity(field) {
      const swap = (target, add) => target && !this.contains(target) && ['input', 'change'].forEach((type) => target[add ? 'addEventListener' : 'removeEventListener'](type, this.onQuantityInput));
      if (this.quantityField !== field) {
        swap(this.quantityField, false);
        swap(field, true);
      }
      this.quantityField = field || null;
    }

    mirrorQuantity() {
      if (!this.active && this.quantityField) this.qb.selectedQuantity = Math.max(1, int(this.quantityField.value, 1));
    }

    applyActive() {
      if (this.active) {
        this.qb.dataset.qbV2Active = 'true';
        this.classList.remove('qb-v2--off', 'qb-v2--inactive');
        this.watchQuantity(null);
        this.setFallback(false);
        this.disableOtherQuantities();
        this.qb.querySelectorAll('[data-qb-schedule-disabled]').forEach((input) => input.removeAttribute('data-qb-schedule-disabled'));
        this.syncRadios();
        this.togglePicker(true);
        this.registerRequired();
        return;
      }
      delete this.qb.dataset.qbV2Active;
      this.closeListbox();
      this.syncRadios();
      this.qb.formVariants = [];
      this.syncLines();
      if (this.form) this.form.querySelectorAll('[data-qb-v2-plan]').forEach((input) => { input.value = ''; });
      this.restoreOtherQuantities();
      // The fallback field only when the form has no other quantity field (the Schedule script may have shown it early)
      const others = this.otherQuantities().filter((input) => !input.disabled);
      this.setFallback(!others.length);
      this.watchQuantity(others[0] || (this.fallback && this.fallback.querySelector('input[name="quantity"]')) || null);
      this.mirrorQuantity();
      this.writePdp(this.selectedTotals());
      if (this.form) this.form.classList.remove('qb-v2-hide-bin');
      this.togglePicker(false);
      this.unregisterRequired();
      this.classList.add(this.designMode ? 'qb-v2--inactive' : 'qb-v2--off');
    }

    deactivate(reason = 'api') {
      if (!this.ready || !this.qb || (reason === 'schedule' && this.designMode)) return;
      this.reasons.add(reason);
      if (!this.active) return;
      const checked = this.checkedOption();
      if (checked) this.remembered = checked.id;
      this.active = false;
      this.applyActive();
      this.dispatch('qbv2:active', { qbv2: this, active: false, reasons: Array.from(this.reasons) });
    }

    activate(reason = 'api') {
      if (!this.ready || !this.qb) return;
      this.reasons.delete(reason);
      if (this.active || this.reasons.size) return;
      this.active = true;
      this.applyActive();
      // The Schedule script unchecked the default at parse time and marked it (4.8.9)
      const was = this.qb.querySelector('input[data-qb-was-checked]');
      this.qb.querySelectorAll('[data-qb-was-checked]').forEach((input) => input.removeAttribute('data-qb-was-checked'));
      let target = was ? this.stateOf(was.closest('.qb-v2-option')) : this.resolveOption(this.remembered);
      if (!this.isSelectable(target)) target = this.defaultOption();
      if (target) this.check(target, 'active');
      this.assertFormVariants();
      this.recompute('active');
      this.dispatch('qbv2:active', { qbv2: this, active: true, reasons: [] });
    }

    // ---------- Init helpers ----------
    // Options 5-8: main.js with QB-1a runs them (refresh()), today's main.js would throw on a fifth offer (M:3338)
    activateDormant() {
      const dormant = this.options.filter((option) => option.dormant);
      if (!dormant.length) return;
      if (!this.patched) {
        dormant.forEach((option) => {
          if (!this.designMode) option.el.hidden = true;
          else {
            option.el.classList.add('qb-v2-option--needs-update');
            option.el.toggleAttribute('inert', true);
          }
        });
        return;
      }
      dormant.forEach((option) => {
        Object.assign(option, { dormant: false, activated: true });
        option.input.name = 'quantity';
        option.input.removeAttribute('data-qb-dormant-input');
        option.label.classList.add('quantity-break');
        option.label.classList.remove('qb-v2-card--dormant');
        option.el.removeAttribute('data-qb-dormant');
        option.input.disabled = !(!this.reasons.size && this.isSelectable(option));
      });
      this.guard(() => this.qb.refresh());
      const checked = this.checkedOption();
      const first = this.options.find((option) => option.el.dataset.qbDefault === 'true' && this.isSelectable(option));
      const target = !checked ? this.defaultOption() : first && first.activated && checked.el.dataset.qbDefault !== 'true' ? first : null;
      if (target && !this.reasons.size) {
        target.input.checked = true;
        fire(target.input);
      }
    }

    // Firefox may restore the radio and the selects after a reload, while main.js read the server state (M:3262)
    restoreFormState() {
      const checked = this.checkedOption();
      if (checked && !this.reasons.size && checked.index !== this.qb.selectedOffer) fire(checked.input);
      this.options.forEach((option) => {
        if (option.dormant) return;
        option.unitEls.forEach((unit) => {
          const options = (this.variant(unit.dataset.selectedId) || {}).options;
          const selects = Array.from(unit.querySelectorAll('select'));
          if (!options || selects.every((select, index) => options[index] === undefined || select.value === options[index])) return;
          // The selected option keeps what the shopper had (main.js re-reads its selects); others go back to their variant
          if (option.input.checked) fire(selects[selects.length - 1]);
          else selects.forEach((select, index) => options[index] !== undefined && (select.value = options[index]));
        });
      });
      // Extra pickers go back to their item's variant
      this.querySelectorAll('[data-qb-item], [data-qb-child="upsell"]').forEach((item) => {
        const json = this.product(item.dataset.productId);
        const variant = json && (json.variants || []).find((entry) => String(entry.id) === String(item.dataset.variantId));
        const values = (variant && variant.options) || [];
        if (this.pickerSelects(item).some((select, index) => values[index] !== undefined && select.value !== values[index])) this.setItemVariant(item, json, variant);
      });
    }

    // main.js caches <quantity-breaks> at construction (M:1355, M:4936, M:3528): after an editor re-render of this
    // block alone they would point at the removed element
    repoint() {
      const qb = this.qb;
      [[this.productForm, 'quantityBreaks'], [document.getElementById(`variant-selects-${this.sectionId}`), 'QuantityBreaks'], [this.widget, 'quantityBreaks']].forEach(([owner, key]) => {
        if (!owner || !(key in owner) || owner[key] === qb || (owner[key] && owner[key].isConnected)) return;
        owner[key] = qb;
        if (owner === this.productForm) owner.quantityBreakUpsells = qb.querySelectorAll('quantity-break-upsells');
      });
    }

    // Theme editor: an option or child rendered without the wrapper still holds the wrapper's __QB_*__ tokens (6.6.20).
    // Those elements are new (nothing is bound to them yet), so they are rebuilt from their corrected HTML
    repairTokens() {
      const { qb, dataset: data } = this;
      const options = [...qb.querySelectorAll('.qb-v2-option')];
      const raw = (element) => element.outerHTML.includes('__QB_');
      const targets = [];
      options.forEach((root) => (String(root.dataset.qbIndex).includes('__QB_') ? targets.push([root, root]) : root.querySelectorAll(':scope > .qb-v2-option__body > *').forEach((child) => raw(child) && targets.push([child, root]))));
      this.querySelectorAll(':scope > .qb-v2__slot > *, :scope > [data-qb-child]').forEach((child) => raw(child) && targets.push([child, null]));
      if (!targets.length) return;
      const checked = qb.querySelector('.qb-v2-option > input:checked');
      const keep = checked && checked.parentElement.dataset.qbV2Option;
      targets.forEach(([element, root]) => {
        // Options are numbered in DOM order; slots and wrapper-level children get 0
        const k = options.indexOf(root) + 1;
        const q = root ? Math.max(1, int(root.dataset.qbQ, 1)) : 1;
        const dormant = k > (this.patched ? 8 : 4);
        const tokens = {
          N: String(k),
          NAME: dormant ? 'qb_v2_dormant' : 'quantity',
          CARD_CLASS: dormant ? 'qb-v2-card--dormant' : 'quantity-break',
          LEVEL: root ? 'option' : 'wrapper',
          Q: q,
          QX: q > 1 ? `${q}× ` : '',
          OPTION_ID: root ? root.dataset.qbV2Option : '',
          EACH_LABEL: escapeHtml(data.qbTEachLabel),
          PER_ITEM: escapeHtml(data.qbTPerItem),
          IMG_SIZES: data.qbTImgSizes,
          WRAPPER_ID: data.qbTWrapperId || this.blockId,
          // Attribute tokens: the parser lower-cased them into attribute names
          dormant: dormant ? 'data-qb-dormant' : '',
          dormant_input: dormant ? 'disabled data-qb-dormant-input' : '',
          soldout_attr: data.qbTSoldoutAttr,
        };
        element.outerHTML = element.outerHTML.replace(/__QB_([A-Z_]+?)__|__qb_([a-z_]+?)__(?:="")?/g, (match, upper, lower) => tokens[upper || lower] || '');
      });
      // The removed __qb_checked__ attribute was the default selection; every option is priced and rendered again
      const fresh = [...qb.querySelectorAll('.qb-v2-option')];
      const target = fresh.find((root) => root.dataset.qbV2Option === keep) || fresh.find((root) => root.dataset.qbDefault === 'true' && root.dataset.qbAvailable === 'true') || fresh.find((root) => root.dataset.qbAvailable === 'true');
      const input = target && target.querySelector(':scope > .qb-v2-option__input');
      if (input && input.name === 'quantity' && !input.disabled) input.checked = true;
      fresh.forEach((root) => root.classList.add('qb-v2-pending'));
      if (this.patched) this.guard(() => qb.refresh());
      else console.warn('Quantity breaks V2: refresh the preview.');
    }

    // ---------- Variant change ----------
    // VariantSelects writes [name=id] at once (M:5020-5026) but resets the units only after its section fetch: until
    // then formVariants stays empty, so an add posts [name=id] × quantity instead of the old variant's units
    onIdChange() {
      clearTimeout(this.pendingTimer);
      // Without the Variant picker no section fetch follows (a script set the id, e.g. a pack option)
      if (document.getElementById(`variant-selects-${this.sectionId}`)) {
        this.unitsPending = true;
        this.qb.formVariants = [];
        this.pendingTimer = setTimeout(() => {
          this.unitsPending = false;
          this.assertFormVariants();
        }, 10000);
      }
      this.recompute('variant');
    }

    onVariantChange({ data } = {}) {
      const idInput = data && data.variant && this.form && this.form.querySelector('[name="id"]');
      // Quick add publishes under the page's section id (M:5126): only this form's variant counts
      if (!idInput || String(idInput.value) !== String(data.variant.id)) return;
      this.main.variants.set(String(data.variant.id), { ...this.variant(data.variant.id), ...data.variant });
      const source = data.html && data.html.querySelector(`quantity-breaks-v2[data-block="${CSS.escape(this.blockId)}"]`);
      if (source) {
        const list = readJson(source.querySelector('quantity-breaks script[type="application/json"]'));
        if (Array.isArray(list)) list.forEach((variant) => this.main.variants.set(String(variant.id), variant));
        source.querySelectorAll('.qb-v2-option').forEach((fresh) => {
          const option = this.options.find((entry) => entry.id === fresh.dataset.qbV2Option);
          if (!option) return;
          ['qbAvailable', 'qbUnavailableReason', 'qbStepperMax', 'qbPackVariant', 'qbPackPosition', 'qbUnitValue'].forEach((key) => {
            if (fresh.dataset[key] !== undefined) option.el.dataset[key] = fresh.dataset[key];
          });
          const status = option.label.querySelector('.qb-v2-card__status');
          const freshStatus = fresh.querySelector('.qb-v2-card__status');
          if (status && freshStatus) {
            status.innerHTML = freshStatus.innerHTML;
            status.hidden = freshStatus.hidden;
          }
          this.readAvailability(option);
          if (option.stepper) this.setStep(option, option.units);
        });
        if (!this.widgetUpdatesPrices()) this.savePdp(data.html);
      }
      // main.js has reset every unit to the new variant and emptied formVariants (M:5196-5204)
      clearTimeout(this.pendingTimer);
      this.unitsPending = false;
      this.syncRadios();
      if (this.active) this.applyDefaults(this.options.filter((option) => !option.touched));
      this.assertFormVariants();
      this.querySelectorAll('.qb-v2-picker').forEach((picker) => this.syncPicker(picker));
      const checked = this.checkedOption();
      const next = this.options.find((option) => this.isSelectable(option));
      if (this.active && !this.isSelectable(checked) && next) this.selectOption(next, { source: 'variant' });
      // A variant whose quantity rules no option meets renders only the plain field (no widget in the fetched section)
      if ((data.html && !source) || this.needsFallback()) this.deactivate('options');
      else this.activate('options');
      this.recompute('variant');
    }

    // ---------- Add to cart ----------
    prepareAdd(path) {
      if (!this.ready || !this.qb || !this.active) return true;
      this.flush();
      const option = this.checkedOption();
      if (!option || !this.isSelectable(option)) return false;
      if (!this.isComplete(option)) {
        this.guard(() => {
          this.syncRequired();
          // The first open slot, empty field or sold-out item's picker (a builder pick has only the builder's button)
          const open = this.mustChooseOpen(option)[0];
          const sold = this.soldOutExtras(option)[0];
          const target = open ? open.querySelector('[data-qb-action], input') : sold && (visible(sold.el || sold.child) || sold.child.querySelector('[data-qb-action]'));
          if (target) target.focus();
        });
        return false;
      }
      // A V2 error never blocks an ordinary add
      try {
        this.syncLines();
        const lines = this.getCartLines(option);
        this.writeGiftRules(lines);
        let cancelled = false;
        let message = '';
        this.dispatch('qbv2:before-add', { qbv2: this, option, lines, path, cancel: (text) => { cancelled = true; message = text || ''; } });
        if (cancelled) {
          if (message && this.productForm && this.productForm.handleErrorMessage) this.productForm.handleErrorMessage(message);
          return false;
        }
        this.lastBeforeAdd = { at: Date.now(), option, lines, variantIds: lines.filter((line) => line.role === 'main').map((line) => String(line.variantId)), nested: Boolean(this.linesEl && this.linesEl.querySelector('[data-parent]')) };
      } catch (error) {
        report(error);
      }
      return true;
    }

    // Cart-side gift removal (M:91-166) needs one rule per gift before the add; it parses localStorage unguarded (M:4073)
    writeGiftRules(lines) {
      if (typeof updateGiftGoalInStorage !== 'function') return;
      lines.forEach((line) => {
        if (line.role !== 'gift' && line.role !== 'unlock') return;
        this.guard(() => updateGiftGoalInStorage({
          giftHandle: line.handle,
          giftVariantId: line.variantId,
          unlockType: 'product_quantity',
          unlockRequirement: String(line.requirement || 1),
          unlockTarget: this.dataset.productHandle,
          lineMarker: '_qb_gift',
        }));
      });
    }

    onBeforeAdd(event) {
      if ((event.detail || {}).sectionId === this.sectionId && !this.prepareAdd('patched')) event.preventDefault();
    }

    onSubmitCapture(event) {
      // getAttribute: the form's <input name="id"> shadows form.id
      if (!(event.target instanceof HTMLFormElement) || event.target.getAttribute('id') !== `product-form-${this.sectionId}`) return;
      this.blockAdd(event, this.productForm, 'submit');
    }

    // The sticky and secondary buttons call the main form's handleSubmit directly (layout/theme.liquid:618-626)
    onClickCapture(event) {
      const button = event.target instanceof Element && event.target.closest('[id^="SectionAtcBtn-"]');
      const main = document.querySelector('product-form[data-main="true"]');
      if (button && !button.disabled && main && main.dataset.section === this.sectionId) this.blockAdd(event, main, 'click');
    }

    blockAdd(event, form, path) {
      // ProductForm returns at once while an add is running (M:1377)
      if (form && form.submitButton && form.submitButton.getAttribute('aria-disabled') === 'true') return;
      if (this.prepareAdd(path)) return;
      event.preventDefault();
      event.stopImmediatePropagation();
    }

    onAdded(event) {
      const detail = event.detail || {};
      const last = this.lastBeforeAdd;
      if (detail.sectionId !== this.sectionId || !last) return;
      this.lastBeforeAdd = null;
      this.dispatch('qbv2:added', { qbv2: this, option: last.option, lines: last.lines, response: detail.response });
    }

    // Shopify refuses nested lines in some stores (Script Editor, bundle parents): later adds go without parents
    onAddError(event) {
      if ((event.detail || {}).sectionId !== this.sectionId) return;
      if (this.lastBeforeAdd && this.lastBeforeAdd.nested) {
        session.set(NEST_OFF, 1);
        this.linesKey = null;
        this.syncLines();
      }
      this.lastBeforeAdd = null;
    }

    // Today's main.js: the first cart update from a product form with this add's main variant, within 15 s, once
    onCartUpdate({ source, cartData } = {}) {
      const last = this.lastBeforeAdd;
      if (source !== 'product-form' || !last || !cartData || Date.now() - last.at > 15000) return;
      const ids = (Array.isArray(cartData.items) ? cartData.items.map((item) => item.variant_id) : [cartData.variant_id]).map(String);
      if (!last.variantIds.some((id) => ids.includes(id))) return;
      this.lastBeforeAdd = null;
      this.dispatch('qbv2:added', { qbv2: this, option: last.option, lines: last.lines, response: cartData });
    }

    // ---------- Public API ----------
    getSelected() {
      return this.selected;
    }

    // The wrapper-level children (upsells, unlockable gifts and nudges sit in the slots; the Schedule after the field)
    get wrapperChildren() {
      const of = (kind) => [...this.querySelectorAll(`:scope > .qb-v2__slot [data-qb-child="${kind}"]`)];
      return { upsells: of('upsell'), unlocks: of('unlock'), nudges: of('nudge'), schedule: this.querySelector(':scope > [data-qb-child="schedule"]') };
    }

    getOptionsSummary() {
      return this.options.map((option) => {
        const result = this.computeOption(option);
        return {
          id: option.id,
          index: option.index,
          title: this.plainTitle(option),
          q: option.q,
          units: option.pack ? option.q : result.units,
          available: option.available,
          hidden: option.hidden,
          dormant: option.dormant,
          locked: option.locked,
          selected: option === this.selected,
          total: result.T,
          compare: result.C,
          saving: result.S,
          percent: result.P,
          discountType: option.discount.type,
          discountValue: option.discount.value,
          method: option.pack ? 'pack' : option.method,
          code: option.code,
          hasExtras: result.hasExtras,
          from: result.from,
        };
      });
    }

    // Scratch card: the option stays locked (radio disabled, its body still interactive) until it is revealed
    setOptionLocked(optionEl, locked) {
      const option = this.resolveOption(optionEl);
      if (!option) return false;
      option.locked = Boolean(locked);
      this.syncRadios();
      this.setSelected(this.selected);
      const fallback = option.locked && option === this.selected && this.active && this.defaultOption();
      if (fallback) this.check(fallback, 'scratch');
      this.recompute('scratch');
      return true;
    }

    // Option-level selling plans step aside for the Subscription widget and subscription apps (B5 decides, 6.7.9)
    setPlanAllowed(allowed) {
      this.planAllowed = Boolean(allowed);
      this.recompute('plan');
    }
  }

  const api = {
    version: '2.0.0',
    instances: new Set(),
    isPatched: () => Boolean(customElements.get('quantity-breaks') && customElements.get('quantity-breaks').qbApi >= 1),
    price: { computeOption, extraLine, planPrice },
    money: { create: createMoney },
    resolveVariant,
    storage: { get: local.get, set: local.set, sget: session.get, sset: session.set },
    plain,
  };
  window.ShrineQBV2 = api;
  customElements.define('quantity-breaks-v2', QuantityBreaksV2);
  document.dispatchEvent(new CustomEvent('shrine:qbv2:core-ready'));
})();

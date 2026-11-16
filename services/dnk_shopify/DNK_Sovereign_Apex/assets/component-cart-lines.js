/* Shrine PRO cart lines (02-lines §8). Writes go through ShrineCartRequests only; without it controls stay disabled. */
(() => {
  'use strict';
  if (window.ShrineSubscriptions) return;
  const d = document;
  const w = window;
  const qs = (s, r) => (r || d).querySelector(s);
  const qsa = (s, r) => Array.from((r || d).querySelectorAll(s));
  const att = (f, x) => { try { return f(); } catch (e) { return x; } };
  const core = () => w.ShrineCart || null;
  const req = () => w.ShrineCartRequests || null;
  const t = (k, v) => att(() => core().t(k, v), k);
  const kw = (s, m) => att(() => core().keywords(s, m), s);
  const say = (s, o) => s && att(() => core().announce(s, o));
  const toast = (o) => att(() => core().toast.show(o));
  const fire = (n, detail) => att(() => d.dispatchEvent(new CustomEvent(n, { detail })));
  const pub = (n, x) => att(() => w.Shopify.analytics.publish(n, x));
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const esc = (v) => (w.CSS && CSS.escape ? CSS.escape(String(v)) : String(v).replace(/["\\\][]/g, '\\$&'));
  const num = (v) => (v === null || v === undefined || v === '' || !isFinite(+v) ? null : +v);
  const planOf = (it) => att(() => num(it.selling_plan_allocation.selling_plan.id), null);
  const props = (el) => {
    if (!el || !el.hasAttribute('data-properties')) return undefined;
    const p = att(() => JSON.parse(el.getAttribute('data-properties')));
    return p === undefined ? p : p && typeof p === 'object' && !Array.isArray(p) ? p : {};
  };
  const shown = (el) => !!(el && el.getClientRects().length && !el.closest('[hidden]'));
  const rootOf = (s) => (s === 'drawer' ? qs('cart-drawer') : s === 'page' ? qs('cart-items') : s === 'page-v2' ? qs('cart-page') : null);
  const ctxOf = (s) => (s === 'drawer' ? 'dialog' : 'cart');
  const flag = (row, f) => (' ' + ((row && row.dataset.lineFlags) || '') + ' ').indexOf(' ' + f + ' ') > -1;
  const msgOf = (res) => (res && res.error && res.error.code === 'cart' && res.error.message) || (w.cartStrings && cartStrings.error) || '';
  const define = (n, c) => customElements.get(n) || customElements.define(n, c);
  const usable = (b, host) => !!b && host.contains(b) && !b.disabled && b.getAttribute('aria-disabled') !== 'true';

  // L6
  const isEligibleDom = (h) => {
    if (!h) return true;
    if (qs('cart-drawer-gift[data-handle="' + esc(h) + '"], cart-drawer-upsell[data-toggle="true"][data-handle="' + esc(h) + '"]')) return false;
    const g = att(() => JSON.parse(w.localStorage.getItem('shrine_gift_goals')));
    return !(g && typeof g === 'object' && Object.keys(g).some((k) => g[k] && g[k].gift_handle === h));
  };

  // L7
  const switched = (res, vid, plan) => {
    if (!res) return false;
    if (res.ok) return true;
    const e = res.error;
    return !!(e && e.code === 'mismatch' && !e.reverted && res.cart && Array.isArray(res.cart.items) && res.cart.items.some((i) => num(i.variant_id) === vid && planOf(i) === plan));
  };

  const firstButton = (root) => qsa('[data-upgrade-button]', root).find((b) => !b.disabled && shown(b)) || null;
  // sel: the control the shopper used (the frequency select keeps focus after a plan change)
  const focusTarget = (root, res, sel) => {
    if (!root || !res || !res.key) return null;
    const k = '[data-sub-control][data-line-key="' + esc(res.key) + '"] ';
    const el = (sel && qs(k + sel, root)) || qs(k + '[data-sub-focus]', root);
    return (el && !el.disabled && shown(el) && el) || firstButton(root) || qs('.cart-item[data-line-key="' + esc(res.key) + '"] .cart-item__name', root);
  };

  const errTarget = (surface, key, vid, plan) => {
    const scope = rootOf(surface) || d;
    const row = (key && qs('.cart-item[data-line-key="' + esc(key) + '"]', scope)) || (vid && qsa('.cart-item[data-variant-id="' + vid + '"]', scope).find((r) => num(r.dataset.sellingPlan) === plan));
    return (row && qs('.cart-item__error-text', row)) || d.getElementById({ page: 'cart-errors', 'page-v2': 'CartPage-CartErrors' }[surface] || 'CartDrawer-CartErrors') || qs('#CartDrawer-CartErrors, #cart-errors, #CartPage-CartErrors');
  };

  const resetSelects = (el) =>
    qsa('select', el).forEach((s) => {
      const o = qsa('option', s).find((x) => x.defaultSelected);
      if (o) s.value = o.value;
    });
  const busyUi = (control, row, plan) => {
    const undo = [];
    const set = (el, a, v) => {
      const b = el.getAttribute(a);
      el.setAttribute(a, v);
      undo.push(() => (b === null ? el.removeAttribute(a) : el.setAttribute(a, b)));
    };
    const cls = (el, c, on) => {
      el.classList.toggle(c, on);
      undo.push(() => el.classList.toggle(c, !on));
    };
    set(control, 'aria-busy', 'true');
    qsa('[data-sub-toggle], select, [data-upgrade-button]', control).forEach((el) => set(el, 'aria-disabled', 'true'));
    qsa('[data-upgrade-button]', control).forEach((b) => {
      cls(b, 'loading', true);
      qsa('.loading-overlay__spinner', b).forEach((s) => cls(s, 'hidden', false));
    });
    if (row && control.tagName === 'CART-SUBSCRIPTION-TOGGLE') qsa('.loading-overlay.hidden', row).forEach((o) => cls(o, 'hidden', false));
    const tg = qs('[data-sub-toggle]', control);
    const ta = tg && (tg.hasAttribute('aria-pressed') ? 'aria-pressed' : 'aria-checked');
    const before = tg && tg.getAttribute(ta);
    if (tg) tg.setAttribute(ta, String(plan !== null));
    return {
      busy: () => undo.reverse().forEach((f) => att(f)),
      state: () => {
        if (tg) tg.setAttribute(ta, before);
        resetSelects(control);
      },
    };
  };

  const subEvent = (detail) => {
    fire('shrine:cart:subscription', detail);
    pub('shrine:cart_subscription', detail);
  };
  const currencyOf = (cart) => (cart && cart.currency) || att(() => core().config.currency || core().config.shopCurrency) || null;
  const info = (el) => {
    const x = el.dataset;
    return { key: x.lineKey || undefined, vid: num(x.variantId), pid: num(x.productId), current: num(x.currentPlan), plan: num(x.planId), title: x.title || '', saving: num(x.saving) || 0, quantity: num(x.quantity) || 1 };
  };
  const detail = (i, action, source, surface, plan, quantity, cart, key) => ({
    action, source, surface, key: key || i.key || null, variantId: i.vid, productId: i.pid, sellingPlanId: plan,
    previousSellingPlanId: i.current || null, quantity, savingCents: i.saving, currency: currencyOf(cart),
  });
  const skipped = { ok: false, skipped: true, status: 0, cart: null, sections: null, error: null };

  const apply = (control, sellingPlanId, opts) => {
    const r = req();
    if (!control || !r || control.dataset.busy) return Promise.resolve(skipped);
    control.dataset.busy = '1';
    const i = info(control);
    const plan = num(sellingPlanId);
    const surface = control.dataset.surface || 'drawer';
    const row = control.closest('.cart-item');
    const pr = props(control) === undefined ? props(row) : props(control);
    const ui = busyUi(control, row, plan);
    say(t('lines_updating'), { busy: true });
    const input = row && qs('.quantity__input', row);
    // L8
    return (input && input.value !== input.defaultValue ? wait(350) : Promise.resolve())
      .then(() =>
        r.change({ key: i.key, variantId: i.vid, sellingPlanId: i.current, properties: pr, free: false }, { sellingPlan: plan }, {
          source: 'lines:subscribe',
          standardEvent: 'update',
          context: ctxOf(surface),
          expect: { variantId: i.vid, sellingPlanId: plan },
          focus: (root, res) => (res && res.key ? focusTarget(rootOf(surface) || root, res, opts && opts.focusSel) : null),
        })
      )
      .catch(() => null)
      .then((res) => {
        const ok = switched(res, i.vid, plan);
        if (control.isConnected) {
          ui.busy();
          if (!ok) ui.state();
          delete control.dataset.busy;
        }
        if (ok) {
          const line = res.line && res.cart && Array.isArray(res.cart.items) ? res.cart.items[res.line - 1] : null;
          const action = plan === null ? 'unsubscribe' : i.current ? 'change_plan' : 'subscribe';
          subEvent(detail(i, action, (opts && opts.source) || 'toggle', surface, plan, line ? line.quantity : i.quantity, res.cart, res.key));
          say(t(action === 'subscribe' ? 'lines_subscribed' : action === 'unsubscribe' ? 'lines_one_time' : 'lines_plan_changed', { product: i.title }));
        } else if (!(res && res.skipped)) {
          const m = msgOf(res);
          const el = errTarget(surface, i.key, i.vid, i.current);
          if (el && m) el.textContent = m;
          say(m, { politeness: 'assertive' });
        }
        return res;
      });
  };

  const applyMany = (control, items) => {
    const r = req();
    const none = { ok: false, done: [], failed: [], cart: null, skipped: true };
    if (!control || !r || control.dataset.busy) return Promise.resolve(none);
    const list = (items || qsa('[data-upgrade-item]', control)).filter((el) => isEligibleDom(el.dataset.handle)).map((el) => Object.assign(info(el), { pr: props(el) }));
    if (!list.length) return Promise.resolve(none);
    control.dataset.busy = '1';
    const surface = control.dataset.surface || 'drawer';
    const ui = busyUi(control, null, 0);
    say(t('lines_updating'), { busy: true });
    return r
      .batch(list.map((s) => ({ ref: { key: s.key, variantId: s.vid, sellingPlanId: null, properties: s.pr, free: false }, sellingPlan: s.plan })), {
        source: 'lines:subscribe-all',
        standardEvent: 'update',
        context: ctxOf(surface),
        focus: (root) => {
          const s = rootOf(surface) || root;
          return s && (firstButton(s) || qs('.cart-item--subscribed [data-sub-focus]', s) || qs('.cart-item__name', s));
        },
      })
      .catch(() => null)
      .then((res) => {
        res = res || { ok: false, done: [], failed: [], cart: null };
        const done = (res.done || []).map((ref) => ref && (ref.key || ref.variantId));
        const ok = (s) => done.indexOf(s.key || s.vid) > -1;
        list.filter(ok).forEach((s) => subEvent(detail(s, 'subscribe', 'upgrade', surface, s.plan, s.quantity, res.cart)));
        const missed = list.filter((s) => !ok(s));
        if (missed.length) toast({ text: t('lines_upgrade_partial', { titles: missed.map((s) => s.title).join(', ') }), timeout: 8000, surface: surface === 'drawer' ? 'drawer' : 'page' });
        else if (done.length) say(t('lines_subscribed', { product: list.map((s) => s.title).join(', ') }));
        if (control.isConnected) {
          ui.busy();
          if (!done.length) ui.state();
          delete control.dataset.busy;
        }
        return res;
      });
  };

  w.ShrineSubscriptions = { version: 1, isEligibleDom, apply, applyMany };

  const enableToggle = (el) => {
    if (el.hasAttribute('data-sub-sample') || el.hidden || !req()) return;
    qsa('[data-sub-toggle], [data-sub-select], [data-sub-plan]', el).forEach((c) => (c.disabled = false));
  };
  class SubToggle extends HTMLElement {
    connectedCallback() {
      if (this.hasAttribute('data-sub-sample')) return;
      if (!isEligibleDom(this.dataset.handle)) {
        this.hidden = true;
        this.dataset.hiddenReason = 'gift';
        return;
      }
      enableToggle(this);
      if (this._b) return;
      this._b = 1;
      // main.js reads every bubbling change as a quantity change
      this.addEventListener('change', (e) => {
        e.stopPropagation();
        const s = e.target;
        if (s.matches && s.matches('[data-sub-select]')) apply(this, s.value || null, { source: 'toggle' });
        else if (s.matches && s.matches('[data-sub-plan]')) apply(this, s.value, { source: 'toggle', focusSel: '[data-sub-plan]' });
      });
      this.addEventListener('click', (e) => {
        const b = e.target.closest && e.target.closest('[data-sub-toggle]');
        if (!usable(b, this)) return;
        e.preventDefault();
        if (b.getAttribute('aria-checked') !== 'true' && b.getAttribute('aria-pressed') !== 'true') apply(this, this.dataset.planId, { source: 'toggle' });
        else if (this.dataset.status === 'subscribed') apply(this, null, { source: 'toggle' });
      });
    }
  }
  define('cart-subscription-toggle', SubToggle);

  // [data-preserve] restores the select after renders: plan and texts follow it
  const syncOffer = (o) => {
    const s = qs('[data-upgrade-plan]', o);
    const opt = s && s.options[s.selectedIndex];
    if (!opt || o.dataset.planId === s.value) return;
    o.dataset.planId = s.value;
    o.dataset.saving = opt.dataset.saving || '0';
    const h = qs('[data-upgrade-heading]', o);
    const l = qs('[data-upgrade-label]', o);
    if (h) h.innerHTML = opt.dataset.heading || '';
    if (l) l.innerHTML = opt.dataset.button || '';
  };
  const enableUpgrade = (u) => req() && !u.hidden && qsa('[data-upgrade-offer]:not([hidden]) [data-upgrade-button], [data-upgrade-offer]:not([hidden]) [data-upgrade-plan]', u).forEach((c) => (c.disabled = false));
  class SubUpgrade extends HTMLElement {
    connectedCallback() {
      if (qs('[data-upgrade-sample]', this)) return;
      const hide = (els) => {
        this.hidden = true;
        this.dataset.hiddenReason = 'gift';
        this.dataset.hiddenTitles = els.map((el) => el.dataset.title).join(', ');
      };
      if (this.dataset.offer === 'all') {
        const card = qs('[data-upgrade-offer]', this);
        const items = qsa('[data-upgrade-item]', this);
        const keep = items.filter((el) => isEligibleDom(el.dataset.handle));
        if (!card || !keep.length) return hide(items);
        if (keep.length < items.length) {
          items.forEach((el) => keep.indexOf(el) < 0 && el.remove());
          const sum = (k) => keep.reduce((a, el) => a + (num(el.dataset[k]) || 0), 0);
          const total = sum('saving');
          const price = sum('linePrice');
          const map = { amount_saved: att(() => core().money.format(total, { trailingZeros: false }), ''), percentage_saved: (price ? Math.floor((total * 100) / price) : 0) + '%', count: keep.length, plan_name: '', title: '' };
          const h = qs('[data-upgrade-heading]', card);
          const l = qs('[data-upgrade-label]', card);
          card.dataset.saving = total;
          if (h) h.innerHTML = kw(this.dataset.headingTemplate, map);
          if (l) l.textContent = kw(this.dataset.buttonTemplate, map);
        }
      } else {
        const offers = qsa('[data-upgrade-offer]', this);
        const first = offers.find((o) => isEligibleDom(o.dataset.handle));
        offers.forEach((o) => (o.hidden = o !== first));
        if (!first) return hide(offers);
      }
      enableUpgrade(this);
      if (this._b) return;
      this._b = 1;
      this.addEventListener('change', (e) => {
        e.stopPropagation();
        const o = e.target.matches && e.target.matches('[data-upgrade-plan]') && e.target.closest('[data-upgrade-offer]');
        if (o) syncOffer(o);
      });
      this.addEventListener('click', (e) => {
        const b = e.target.closest && e.target.closest('[data-upgrade-button]');
        const o = usable(b, this) && b.closest('[data-upgrade-offer]');
        if (!o) return;
        e.preventDefault();
        syncOffer(o);
        if (o.hasAttribute('data-sub-all')) applyMany(o);
        else apply(o, o.dataset.planId, { source: 'upgrade' });
      });
    }
  }
  define('cart-subscription-upgrade', SubUpgrade);

  // skeleton 3b.2
  const liveItems = () => qs('[data-cart-root] [data-cart-items]');
  const notFound = () => ({ ok: false, status: 0, cart: null, sections: null, error: { code: 'not_found', message: 'not_found' } });
  // add-on lines (main.js checkForClear, E15-aware): cart-hidden and reward gift lines, and lines of an add-on switch or a
  // gift (main.js engines, V2's add-on cards); with E15 a Rewards bar gift counts only its own gift line
  const giftOff = (g) => !(att(() => core().has('rewardGiftLines')) && g.dataset.lineMarker === '_reward_gift');
  const isAddon = () => {
    const h = qsa('cart-drawer-upsell[data-toggle="true"], cart-drawer-gift, cart-upsell-item[data-ups-kind="toggle"]:not([data-ups-per-item="true"])').filter(giftOff).map((el) => el.dataset.handle);
    return (el) => flag(el, 'cart-hidden') || flag(el, 'reward-gift') || h.indexOf(el.dataset.handle) > -1;
  };
  class PageItems extends HTMLElement {
    connectedCallback() {
      if (att(() => core().has('cartRoot')) && !qs('cart-drawer') && typeof initShrineGiftsCheck === 'function') att(() => initShrineGiftsCheck());
      if (this._b) return;
      this._b = 1;
      let timer = 0;
      this.addEventListener('change', (e) => {
        const i = e.target;
        if (!i.matches || !i.matches('.quantity__input')) return;
        // the line typed in, by key: a render inside the debounce can move it or detach this list (QB-1c E18 in main.js)
        const old = i.closest('.cart-item');
        const key = old && old.dataset.lineKey;
        clearTimeout(timer);
        timer = setTimeout(() => {
          const host = (!this.isConnected && liveItems()) || this;
          const row = key && qs('.cart-item[data-line-key="' + esc(key) + '"]', host);
          // gone (a new key, or removed): the core looks it up by what it was
          host.updateQuantity(row ? row.dataset.index : key ? 0 : i.dataset.index, i.value, att(() => d.activeElement.getAttribute('name')), key && !row ? old : null);
        }, 300);
      });
      this.addEventListener('click', (e) => {
        const b = e.target.closest && e.target.closest('[data-line-remove]');
        const row = b && b.closest('.cart-item');
        if (!row || !this.contains(b)) return;
        e.preventDefault();
        this.updateQuantity(row.dataset.index, 0);
      });
    }

    // a detached instance hands over to the live one
    other() {
      const el = !this.isConnected && liveItems();
      return el && el !== this ? el : null;
    }

    updateQuantity(line, quantity, name, old) {
      if (!this.isConnected) {
        const el = this.other();
        return el ? el.updateQuantity(line, quantity, name, old) : Promise.resolve(notFound());
      }
      const root = this.closest('[data-cart-root]');
      const checks = root && root.giftChecks;
      return this.write(line, quantity, name, old)
        .catch(() => notFound())
        .then((res) => {
          // A34: only without a cart drawer
          if (!qs('cart-drawer')) {
            fire('cartQuantityUpdated', { handle: 'handle' });
            att(() => typeof checkShrineGifts === 'function' && checkShrineGifts());
            // not when the root's render of this write already validated (a second fix would post a removed key: 400)
            if (!root || root.giftChecks === checks) att(() => typeof validateCartGifts === 'function' && validateCartGifts());
          }
          return res;
        });
    }

    async write(line, quantity, name, old) {
      const r = req();
      const row = old || qs('#CartPage-Item-' + line, this);
      if (!r || !row) return notFound();
      const q = parseInt(quantity, 10);
      const focus = (root, res) => this.focusAfter(res, line, name);
      const rest = qsa('.cart-item', this).filter((el) => el !== row);
      if (q === 0 && rest.every(isAddon())) {
        // only add-ons would remain: clear (main.js checkForClear)
        if (pending && pending.key === row.dataset.lineKey) pending.addons = pageAddons(rest);
        return r.clear({ source: 'lines:page-clear', standardEvent: 'remove', context: 'cart', focus });
      }
      this.enableLoading(line);
      const input = qs('.quantity__input', row);
      const res = await r.change(
        { key: row.dataset.lineKey, variantId: num(row.dataset.variantId), sellingPlanId: num(row.dataset.sellingPlan), properties: props(row), free: flag(row, 'free') },
        { quantity: q },
        { source: 'lines:page-quantity', standardEvent: q === 0 ? 'remove' : 'update', context: 'cart', focus }
      );
      if (res.ok) {
        const got = res.line && res.cart ? att(() => res.cart.items[res.line - 1].quantity) : null;
        if (q > 0 && got != null && got !== q) this.updateLiveRegions(res.line, ((w.cartStrings && cartStrings.quantityError) || '').replace('[quantity]', got));
      } else {
        this.disableLoading(line);
        if (input) input.value = input.getAttribute('value');
        // a removal whose line is already gone (a second click) is done; an error shows on its own line (by key)
        const e = !(q === 0 && res.error && res.error.code === 'not_found') && qs('.cart-item[data-line-key="' + esc(row.dataset.lineKey) + '"] .cart-item__error-text', (!this.isConnected && liveItems()) || this);
        if (e) e.textContent = msgOf(res);
      }
      return res;
    }

    focusAfter(res, line, name) {
      const page = qs('cart-page');
      const root = page || d;
      if ((res && res.cart && res.cart.item_count === 0) || !qs('.cart-item', root)) return page && d.getElementById('CartPage-EmptyHeading-' + page.dataset.sectionId);
      const same = res && res.key && qs('.cart-item[data-line-key="' + esc(res.key) + '"]', root);
      return (same && ((name && qs('[name="' + name + '"]', same)) || qs('.cart-item__name', same))) || qs('#CartPage-Item-' + line + ' .cart-item__name', root) || qs('#CartPage-Item-' + (line - 1) + ' .cart-item__name', root);
    }

    enableLoading(line) { this.loading(line, false); }

    disableLoading(line) { this.loading(line, true); }

    loading(line, hide) {
      const el = this.other();
      if (el) return el.loading(line, hide);
      qsa('#CartPage-Item-' + line + ' .loading-overlay', this).forEach((o) => o.classList.toggle('hidden', hide));
    }

    updateLiveRegions(line, message) {
      const el = this.other();
      if (el) return el.updateLiveRegions(line, message);
      const e = qs('#CartPage-LineItemError-' + line + ' .cart-item__error-text', this);
      if (e) e.textContent = message || '';
    }

    getSectionsToRender() {
      const p = this.closest('cart-page') || qs('cart-page');
      return p && p.getSectionsToRender ? p.getSectionsToRender() : [];
    }
  }
  define('cart-page-items', PageItems);

  // L14
  const products = new Map();
  const productJson = async (h) => {
    const k = 'shrine-cart-product:' + h;
    const c = products.get(h) || att(() => JSON.parse(w.sessionStorage.getItem(k)));
    if (c && Date.now() - c.t < 60000) return c.p;
    const r = await fetch(att(() => Shopify.routes.root, '/') + 'products/' + encodeURIComponent(h) + '.js', { headers: { Accept: 'application/json' } });
    if (!r.ok) throw new Error(String(r.status));
    const x = { t: Date.now(), p: await r.json() };
    products.set(h, x);
    att(() => w.sessionStorage.setItem(k, JSON.stringify(x)));
    return x.p;
  };
  class LineVariant extends HTMLElement {
    connectedCallback() {
      if (req()) qsa('select', this).forEach((s) => (s.disabled = false));
      if (this._b) return;
      this._b = 1;
      this.addEventListener('change', (e) => {
        e.stopPropagation();
        this.pick();
      });
    }

    reset(m) {
      resetSelects(this);
      const e = m && qs('.cart-item__error-text', this.closest('.cart-item') || this);
      if (e) e.textContent = m;
    }

    async pick() {
      const r = req();
      const row = this.closest('.cart-item');
      if (!r || !row || this.busy) return;
      const wanted = qsa('select', this).sort((a, b) => a.dataset.optionIndex - b.dataset.optionIndex).map((s) => s.value);
      const old = num(this.dataset.variantId);
      this.busy = 1;
      try {
        const p = await productJson(this.dataset.handle).catch(() => null);
        const v = p && (p.variants || []).find((x) => (x.options || []).every((o, i) => o === wanted[i]));
        if (v && v.id === old) return;
        if (!v || !v.available) return this.reset(this.dataset.unavailable);
        const plan = num(row.dataset.sellingPlan);
        if (plan && !(v.selling_plan_allocations || []).some((a) => num(a.selling_plan_id) === plan)) return this.reset(t('lines_plan_unavailable'));
        const surface = row.closest('cart-page-items') ? 'page-v2' : 'drawer';
        const pr = props(row);
        const item = { id: v.id, quantity: num(row.dataset.quantity) || 1 };
        if (pr && Object.keys(pr).length) item.properties = pr;
        if (plan) item.selling_plan = plan;
        const a = await r.add([item], { source: 'lines:variant', render: false, publish: false, standardEvent: 'add', context: ctxOf(surface) });
        if (!a.ok) return this.reset(msgOf(a));
        const rm = await r.change({ key: row.dataset.lineKey, variantId: old, sellingPlanId: plan, properties: pr, free: false }, { quantity: 0 }, {
          source: 'lines:variant',
          standardEvent: 'remove',
          context: ctxOf(surface),
          focus: (root) => qs('.cart-item[data-variant-id="' + v.id + '"] cart-line-variant select', rootOf(surface) || root),
        });
        if (!rm || !rm.ok) {
          // the old line stayed: show the cart as it is (both variants) and say why on the old line
          await att(() => r.render(null, { source: 'lines:variant', publish: true }));
          const e = qs('.cart-item[data-variant-id="' + old + '"] .cart-item__error-text', rootOf(surface) || d);
          if (e) e.textContent = msgOf(rm);
        }
      } finally {
        this.busy = 0;
      }
    }
  }
  define('cart-line-variant', LineVariant);

  // undo, save for later (8.7, 8.8)
  let pending = null;
  let kind = null;
  let wasSaved = false;
  const SKIP = ['free', 'gift-card', 'bundle', 'nested', 'parent', 'qb', 'reward-gift', 'cart-hidden'];
  const record = (row, host) => {
    if (!row || SKIP.some((f) => flag(row, f))) return;
    pending = {
      key: row.dataset.lineKey, variantId: num(row.dataset.variantId), quantity: num(row.dataset.quantity) || 1, sellingPlanId: num(row.dataset.sellingPlan),
      properties: props(row), propsJson: row.getAttribute('data-properties'), title: row.dataset.title || '', handle: row.dataset.handle,
      surface: host.matches('cart-page-items') ? 'page-v2' : 'drawer', kind: kind || 'remove', undoText: host.dataset.undoText,
      undo: host.hasAttribute('data-undo-text'), addons: [], wasSaved, at: Date.now(),
    };
  };
  // add-ons a clear removed come back with the undo (gifts come back on their own)
  const drawerAddons = () =>
    qsa('cart-drawer cart-drawer-upsell[data-toggle="true"][data-selected="true"]')
      .filter((el) => el.dataset.id && qs('cart-drawer .cart-item--product-' + esc(el.dataset.handle)))
      .map((el) => ({ id: num(el.dataset.id), quantity: 1, selling_plan: att(() => qs('[name="selling_plan"]', el).value) || undefined }));
  const pageAddons = (rows) =>
    rows
      .filter((el) => !flag(el, 'free') && !flag(el, 'reward-gift') && !flag(el, 'qb') && !qsa('cart-drawer-gift[data-handle="' + esc(el.dataset.handle) + '"]').some(giftOff))
      .map((el) => {
        const o = { id: num(el.dataset.variantId), quantity: num(el.dataset.quantity) || 1 };
        const pr = props(el);
        if (pr && Object.keys(pr).length) o.properties = pr;
        if (el.dataset.sellingPlan) o.selling_plan = num(el.dataset.sellingPlan);
        return o;
      });
  const hostOf = (el) => el.closest('cart-drawer-items, cart-page-items');
  d.addEventListener(
    'click',
    (e) => {
      const b = e.target.closest && e.target.closest('cart-remove-button, [data-line-remove]');
      const host = b && hostOf(b);
      if (!host || (!host.hasAttribute('data-undo-text') && kind !== 'save')) return;
      record(b.closest('.cart-item'), host);
      if (pending && b.clearCart === true) pending.addons = drawerAddons();
    },
    true
  );
  d.addEventListener(
    'change',
    (e) => {
      const i = e.target;
      const host = i.matches && i.matches('.quantity__input') && num(i.value) === 0 && hostOf(i);
      if (host && host.hasAttribute('data-undo-text')) record(i.closest('.cart-item'), host);
    },
    true
  );
  d.addEventListener('click', (e) => {
    const b = e.target.closest && e.target.closest('button[data-save-later]');
    const row = b && b.closest('.cart-item');
    const rm = row && qs('cart-remove-button button, [data-line-remove]', row);
    if (!rm) return;
    e.preventDefault();
    kind = 'save';
    wasSaved = !!att(() => ShrineWishlist.has(row.dataset.handle));
    try {
      rm.click(); // recorded by the capture listener
    } finally {
      kind = null;
      wasSaved = false;
    }
  });

  const undo = async (p) => {
    const r = req();
    if (!r) return;
    att(() => ShrineCartUpsells.skipNextFill());
    const item = { id: p.variantId, quantity: p.quantity };
    if (p.properties && Object.keys(p.properties).length) item.properties = p.properties;
    if (p.sellingPlanId) item.selling_plan = p.sellingPlanId;
    const res = await r.add([item].concat(p.addons || []), {
      source: 'lines:undo',
      standardEvent: 'add',
      context: ctxOf(p.surface),
      focus: (root) => qs('.cart-item[data-variant-id="' + p.variantId + '"] .cart-item__name', rootOf(p.surface) || root),
    });
    const ok = !!(res && res.ok);
    if (ok && p.kind === 'save' && !p.wasSaved) att(() => ShrineWishlist.remove(p.handle));
    fire('shrine:cart:undo', { ok, variantId: p.variantId, quantity: p.quantity });
    if (ok) say(t('lines_restored', { product: p.title }));
    else toast({ text: msgOf(res), surface: p.surface === 'drawer' ? 'drawer' : 'page' });
  };
  const setVariant = (h, id) => {
    if (att(() => typeof ShrineWishlist.setVariant === 'function')) return ShrineWishlist.setVariant(h, id);
    const m = att(() => JSON.parse(w.localStorage.getItem('shrine-wishlist-variants')) || {}, {});
    m[h] = id;
    att(() => w.localStorage.setItem('shrine-wishlist-variants', JSON.stringify(m)));
  };
  const confirmRemoval = () => {
    const p = pending;
    if (!p) return;
    if (Date.now() - p.at > 10000) return (pending = null);
    const there = qsa('.cart-item').some(
      (el) => el.dataset.lineKey === p.key || (num(el.dataset.variantId) === p.variantId && num(el.dataset.sellingPlan) === p.sellingPlanId && el.getAttribute('data-properties') === p.propsJson)
    );
    if (there) return;
    pending = null;
    const surface = p.surface === 'drawer' ? 'drawer' : 'page';
    const back = { label: t('lines_undo'), onClick: () => undo(p) };
    if (p.kind === 'save') {
      att(() => ShrineWishlist.add(p.handle));
      att(() => setVariant(p.handle, p.variantId));
      const x = { handle: p.handle, variantId: p.variantId, quantity: p.quantity, surface: p.surface };
      fire('shrine:cart:save-for-later', x);
      pub('shrine:cart_save_for_later', x);
      const cfg = att(() => JSON.parse(d.getElementById('shrine-wishlist-config').textContent), null) || {};
      toast({ text: t('lines_saved_for_later', { product: p.title }), action: p.undo ? back : cfg.url ? { label: cfg.view, onClick: () => location.assign(cfg.url) } : null, timeout: 5000, surface });
    } else if (p.undo) toast({ text: kw(p.undoText, { title: p.title }), action: back, timeout: 5000, surface });
  };

  // 8.9
  const groups = (root) =>
    qsa('.cart-group', root).forEach((g) => {
      const rows = qsa('.cart-item', g);
      g.hidden = !!rows.length && rows.every((el) => getComputedStyle(el).display === 'none');
    });
  const seen = {};
  const sig = (el) => el.dataset.variantId + '|' + (el.dataset.sellingPlan || '');
  const motion = (surface, root, first) => {
    const rows = qsa('.cart-item', root);
    const before = seen[surface];
    seen[surface] = rows.map(sig);
    if (first || !before || att(() => matchMedia('(prefers-reduced-motion: reduce)').matches)) return;
    rows.forEach((el) => {
      if (before.indexOf(sig(el)) > -1) return;
      el.classList.add('cart-line--enter');
      el.addEventListener('animationend', () => el.classList.remove('cart-line--enter'), { once: true });
    });
  };

  // M1b (skeleton A6); render(null) is one GET ?sections= with the real ids
  let m1b = 0;
  const rerenderPage = () => {
    if (m1b) return (m1b = 2);
    m1b = 1;
    Promise.resolve(att(() => req().whenIdle(), true))
      .then(() => req().render(null, { surfaces: ['page'], publish: false, source: 'lines:m1b' }))
      .catch((e) => att(() => console.warn('[cart lines] cart page refresh failed', e)))
      .then(() => {
        const again = m1b === 2;
        m1b = 0;
        if (again) rerenderPage();
      });
  };
  const initM1b = () => {
    const host = qs('cart-items[data-section-id]');
    if (!host || host._shrineM1b) return;
    host._shrineM1b = true;
    // only the default-settings render replaces the host's children
    new MutationObserver(() => {
      const inner = d.getElementById('main-cart-items');
      const real = host.dataset.sectionId;
      if (!inner || !real || inner.dataset.id === real) return;
      inner.dataset.id = real;
      rerenderPage();
    }).observe(host, { childList: true });
  };

  const onRender = (info) => {
    const root = (info && info.root) || d;
    if (!root.querySelectorAll) return;
    qsa('cart-subscription-toggle', root).forEach(enableToggle);
    qsa('[data-upgrade-offer]', root).forEach(syncOffer);
    qsa('cart-subscription-upgrade', root).forEach(enableUpgrade);
    groups(root);
    if (info && info.surface && info.surface !== 'page') motion(info.surface, root);
    confirmRemoval();
    initM1b();
  };

  const init = () => {
    const c = core();
    initM1b();
    att(() => c.onRender(onRender));
    if (w.Shopify && Shopify.designMode) {
      // A37
      const a = att(() => c.config.assets.lines) || {};
      const src = a.editor || (a.js && a.js.replace('component-cart-lines.js', 'component-cart-lines-editor.js'));
      if (src && !qs('script[src="' + src + '"]')) d.head.appendChild(Object.assign(d.createElement('script'), { src, async: true }));
    }
    qsa('cart-subscription-toggle').forEach(enableToggle);
    qsa('cart-subscription-upgrade').forEach(enableUpgrade);
    ['drawer', 'page-v2'].forEach((s) => rootOf(s) && motion(s, rootOf(s), true));
    groups(d);
    att(() => c.provide('lines', { version: 1, subscriptions: w.ShrineSubscriptions }));
  };
  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', init);
  else init();
})();

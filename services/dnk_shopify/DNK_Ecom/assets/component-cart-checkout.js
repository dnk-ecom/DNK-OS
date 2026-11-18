/* Cart checkout (footer area), loaded from data-cart-feature="checkout" markers; the cart page sections link it.
   window.ShrineCheckoutGate blocks every cart checkout button (button[name="checkout"], [data-checkout-button]) of a
   form while a Terms checkbox or a required Cart field of that form is unfulfilled: capture phase, so the button's own
   onclick (the spinner) never runs; it can lock express buttons behind a shield. Elements: cart-note-counter,
   cart-field. The opt-in parts (cart-totals-goal, cart-gift-card, cart-shipping-estimator) are in
   component-cart-checkout-extras.js, loaded when one of their hosts is on the page; the editor checks are in
   component-cart-checkout-editor.js (design mode only). Every main.js and core name is optional. */
(() => {
  if (window.ShrineCartCheckout) return;
  const C = (window.ShrineCartCheckout = { version: 1 });
  const w = window;
  const d = document;
  const SRC = d.currentScript && d.currentScript.src;
  const BUTTONS = 'button[name="checkout"], [data-checkout-button]';
  const NEAR = ['CartDrawer-Checkout', 'CartPage-Checkout', 'checkout']; // buttons that sit next to their fields
  const SHIELD = 'cart-checkout__express-shield';
  const LOCKED = 'cart-checkout__express--locked';
  const controls = new Set();
  const forms = new Set();

  const t = (key, vars, fallback) => {
    const c = w.ShrineCart;
    const s = c && c.t ? c.t(key, vars) : '';
    return s && s !== key ? s : fallback.replace(/\[(\w+)\]/g, (m, n) => (vars && vars[n] != null ? vars[n] : m));
  };
  const formOf = (el) => el.getAttribute('form') || (el.form && el.form.id) || el.dataset.checkoutForm || '';
  const rootOf = (el) => el.closest('cart-drawer, cart-page, #main-cart-footer') || d.body;
  const blocks = (c) => {
    try { return !!c.isBlocking(); } catch (e) { return false; }
  };
  const live = (test) => [...controls].filter((c) => c.element.isConnected && test(c))
    .sort((a, b) => (a.element.compareDocumentPosition(b.element) & 4 ? -1 : 1));
  const blocking = (form) => live((c) => c.form === form && blocks(c));
  const notify = (list, button) => list.forEach((c, i) => {
    try { c.onBlocked(button, !i); } catch (e) {}   // the first one reveals its field
  });
  const reveal = (el, button) => {
    if (!el) return;
    const near = !!button && (NEAR.includes(button.id) || button.classList.contains(SHIELD));
    if (!near && el.scrollIntoView) {   // compact bar, Cart page V2's bar, a submit without a button
      const reduce = w.matchMedia && w.matchMedia('(prefers-reduced-motion: reduce)').matches;
      el.scrollIntoView({ block: 'center', behavior: reduce ? 'auto' : 'smooth' });
    }
    el.focus(near ? undefined : { preventScroll: true });
  };
  // the dimmed look: 1.9.0's .disabled class (opacity and cursor only; clicks still arrive)
  const dim = (form) => {
    const on = live((c) => c.form === form && c.disablesButton && blocks(c)).length > 0;
    d.querySelectorAll(BUTTONS).forEach((b) => {
      if (formOf(b) !== form || (!on && !b.hasAttribute('data-gate-dimmed'))) return;
      b.classList.toggle('disabled', on);
      b.toggleAttribute('data-gate-dimmed', on);
    });
  };
  // express lock: wallet buttons sit in a closed shadow DOM, so a locked box gets inert children and a shield button
  const lock = (box, control) => {
    let shield = [...box.children].find((x) => x.classList.contains(SHIELD));
    box.classList.add(LOCKED);
    [...box.children].forEach((x) => { if (x !== shield) x.inert = true; });
    if (!shield) {
      shield = box.appendChild(Object.assign(d.createElement('button'), { type: 'button', className: SHIELD, innerHTML: '<span class="visually-hidden"></span>' }));
      shield.addEventListener('click', (e) => {
        e.preventDefault();
        const root = rootOf(box);
        notify(live((c) => c.gatesExpress && rootOf(c.element) === root && blocks(c)), shield);
      });
    }
    shield.firstElementChild.textContent = control.kind === 'terms'
      ? t('checkout_terms_express_locked', null, 'Accept the terms to use express checkout')
      : t('checkout_field_express_locked', { label: control.label || '' }, 'Fill in [label] to use express checkout');
  };
  const unlock = (box) => {
    box.classList.remove(LOCKED);
    [...box.children].forEach((x) => (x.classList.contains(SHIELD) ? x.remove() : (x.inert = false)));
  };
  const refreshExpress = () => {
    const roots = new Map();   // root -> its first blocking control that gates express checkout
    live((c) => c.gatesExpress && blocks(c)).forEach((c) => roots.get(rootOf(c.element)) || roots.set(rootOf(c.element), c));
    d.querySelectorAll('.' + LOCKED).forEach((box) => roots.get(rootOf(box)) || unlock(box));
    roots.forEach((c, root) => root.querySelectorAll('.cart__dynamic-checkout-buttons').forEach((box) => lock(box, c)));
  };
  const refresh = (form) => {
    dim(form);
    refreshExpress();
  };
  const refreshAll = () => {
    forms.forEach(dim);
    refreshExpress();
  };
  const register = (control) => {
    if (!control || !control.element) return () => {};
    controls.add(control);
    forms.add(control.form);
    refresh(control.form);
    return () => {
      controls.delete(control);
      refresh(control.form);
    };
  };
  const stop = (e, button, form) => {
    const list = blocking(form);
    if (!list.length) return;
    e.preventDefault();
    e.stopImmediatePropagation();
    notify(list, button);
  };
  // capture phase: before the button's onclick and the browser's validation; keyboard activation and implicit
  // submission (Enter in a cart input) arrive as clicks on the button
  d.addEventListener('click', (e) => {
    const b = e.target.closest && e.target.closest(BUTTONS);
    if (b) stop(e, b, formOf(b));
  }, true);
  d.addEventListener('submit', (e) => {
    const f = e.target;
    if (f && f.id && (!e.submitter || e.submitter.matches(BUTTONS))) stop(e, e.submitter || null, f.id);
  }, true);
  w.ShrineCheckoutGate = { register, blocking, refresh, refreshAll, reveal };
  d.dispatchEvent(new CustomEvent('shrine:checkout-gate:ready'));

  // ---------- helpers
  const define = (name, cls) => customElements.get(name) || customElements.define(name, cls);
  const store = (key, value) => {
    try {
      if (value === undefined) return sessionStorage.getItem(key);
      if (value === null) sessionStorage.removeItem(key);
      else sessionStorage.setItem(key, value);
    } catch (e) {}
    return null;
  };
  C.util = { t, store, define };   // shared with component-cart-checkout-extras.js

  // ---------- cart-note-counter: "12/200" under a note or a Cart field with a character limit (maxlength limits)
  define('cart-note-counter', class extends HTMLElement {
    connectedCallback() {
      const input = (this.input = d.getElementById(this.dataset.for));
      if (!input) return;
      this.update = () => {
        const max = +this.dataset.max || 0;
        this.textContent = input.value.length + '/' + max;
        this.classList.toggle('cart-field__counter--limit', max > 0 && input.value.length >= max);
      };
      input.addEventListener('input', this.update);
      this.update();
      requestAnimationFrame(this.update);   // after a render restored a typed value
    }

    disconnectedCallback() {
      if (this.input) this.input.removeEventListener('input', this.update);
    }
  });

  // ---------- cart-field: a cart attribute. It posts with the checkout form and is saved while the customer types;
  // the draft (sessionStorage) survives re-renders until the cart holds it.
  define('cart-field', class extends HTMLElement {
    connectedCallback() {
      const x = this.dataset;
      this.key = 'shrine-cart-field:' + x.attribute;
      this.controls = [...this.querySelectorAll('input, textarea, select')];
      this.error = this.querySelector('.cart-field__error');
      if (!this.wired) {
        this.wired = true;
        const text = x.type === 'text' || x.type === 'textarea';
        if (x.type === 'date') this.setupDate();
        this.addEventListener('input', () => text && this.edited(600));
        this.addEventListener('change', (e) => {
          e.stopPropagation();
          if (text) return;
          const problem = this.checkDate();
          this.edited(0);
          if (problem) this.showError(problem);
        });
        this.addEventListener('keydown', (e) => {
          // implicit submission would start checkout (the form's default button is Checkout): save instead
          if (e.key === 'Enter' && e.target.matches('input[type="text"], input[type="date"]')) {
            e.preventDefault();
            this.schedule(0);
          }
        });
        const draft = store(this.key);
        if (draft != null && draft !== this.value()) this.setValue(draft);
      }
      // save() runs after a render's [data-preserve] restore (E12, or the core's right after this callback) and
      // compares what the field shows with what the cart holds: nothing to do in the common case
      this.schedule(0);
      if (x.required === 'true' && !this.unregister) {
        const label = this.querySelector('.cart-field__label');
        this.unregister = register({
          form: x.form,
          kind: 'field',
          element: this,
          gatesExpress: x.gateExpress === 'true',
          label: label ? label.textContent.trim() : '',
          isBlocking: () => this.value() === '' || !this.controls.every((c) => c.validity.valid),
          onBlocked: (button, focus) => {
            this.showError(x.requiredMessage || '');
            if (focus) reveal(this.controls[0], button);
          },
        });
      }
    }

    disconnectedCallback() {
      clearTimeout(this.timer);   // the draft stays: the new instance saves it
      if (this.unregister) this.unregister();
      this.unregister = null;
    }

    edited(ms) {
      store(this.key, this.value());
      this.clearError();
      this.schedule(ms);
      if (this.unregister) refresh(this.dataset.form);
    }

    schedule(ms) {
      clearTimeout(this.timer);
      this.timer = setTimeout(() => this.save(), ms);
    }

    value() {
      const type = this.dataset.type;
      const c = this.controls;
      if (type === 'checkbox' || type === 'pills') {
        const on = c.find((x) => x.checked);
        return on ? on.value : '';
      }
      const v = c[0] ? c[0].value : '';
      return type === 'text' ? v.trim() : v;
    }

    setValue(v) {
      const type = this.dataset.type;
      this.controls.forEach((c) => {
        if (type === 'checkbox') c.checked = v !== '';
        else if (type === 'pills') c.checked = c.value === v;
        else c.value = v;
      });
    }

    async save() {
      const v = this.value();
      const x = this.dataset;
      const R = w.ShrineCartRequests;
      if (v !== (x.saved || '')) {
        if (!R || !R.update) return;   // it still posts with the checkout form
        // an attribute changes no line or total: no render, no publish (product pages would re-fetch their section)
        const r = await R.update({ attributes: { [x.attribute]: v } }, { source: 'footer:cart-field', render: false, publish: false });
        if (!r || !r.ok) return this.isConnected && this.showError((w.cartStrings && w.cartStrings.error) || '');
        x.saved = v;
      }
      if (store(this.key) === v) store(this.key, null);
    }

    setupDate() {
      const c = this.controls[0];
      const x = this.dataset;
      const days = (x.daysToSkip || '').split(',');
      const dates = (x.datesToSkip || '').split(',').map((s) => s.split('-').map(Number).join('-'));
      const names = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
      const pad = (n) => String(n).padStart(2, '0');
      const skipped = (day) => days.includes(names[day.getDay()]) || dates.includes(day.getMonth() + 1 + '-' + day.getDate());
      const min = new Date();
      min.setHours(12, 0, 0, 0);
      min.setDate(min.getDate() + (+x.earliest || 0));
      for (let i = 0; i < 366 && skipped(min); i++) min.setDate(min.getDate() + 1);
      c.min = min.getFullYear() + '-' + pad(min.getMonth() + 1) + '-' + pad(min.getDate());
      this.unavailable = (v) => v < c.min || skipped(new Date(v + 'T12:00:00'));
    }

    checkDate() {
      const c = this.controls[0];
      if (!this.unavailable) return '';
      const problem = c.value && this.unavailable(c.value) ? t('checkout_field_date_unavailable', null, "This date isn't available. Choose another one.") : '';
      c.setCustomValidity(problem);
      if (problem) c.value = '';
      return problem;
    }

    showError(text) {
      const e = this.error;
      if (!e) return;
      e.hidden = false;
      e.textContent = '';
      clearTimeout(this.errorTimer);
      this.errorTimer = setTimeout(() => (e.textContent = text), 30);   // new text in an alert region is announced
      this.controls.forEach((c) => c.setAttribute('aria-invalid', 'true'));
    }

    clearError() {
      clearTimeout(this.errorTimer);
      if (this.error) {
        this.error.hidden = true;
        this.error.textContent = '';
      }
      this.controls.forEach((c) => c.removeAttribute('aria-invalid'));
    }
  });

  // ---------- the opt-in parts (a store-currency free shipping goal in another currency, gift cards, the Shipping
  // estimator) are in component-cart-checkout-extras.js: their hosts print its URL (data-checkout-extras), and it loads
  // once, as soon as the first one is on the page
  const extras = () => {
    const host = !C.extras && !C.extrasLoading && d.querySelector('[data-checkout-extras]');
    if (!host) return;
    C.extrasLoading = true;
    d.head.appendChild(Object.assign(d.createElement('script'), { src: host.dataset.checkoutExtras, async: true }));
  };

  // ---------- hooks into the core (component-cart.js), when it is there; the editor checks load in design mode only
  let hooked = false;
  const hook = () => {
    const cart = w.ShrineCart;
    if (hooked || !cart) return;
    hooked = true;
    if (cart.onRender) cart.onRender(() => {
      refreshAll();
      extras();
    });
    C.api = { gate: w.ShrineCheckoutGate };   // giftCards ({ add, remove }) come with the extras file
    if (C.extras) C.api.giftCards = C.extras.giftCards;
    if (cart.provide) cart.provide('checkout', C.api);
    const a = cart.config && cart.config.assets && cart.config.assets.checkout;
    const editor = (a && a.editor) || (SRC && SRC.replace('component-cart-checkout.js', 'component-cart-checkout-editor.js'));
    if (w.Shopify && w.Shopify.designMode && editor && editor !== SRC && !d.querySelector('script[src="' + editor + '"]')) {
      d.head.appendChild(Object.assign(d.createElement('script'), { src: editor, async: true }));
    }
  };
  hook();
  if (!hooked) d.addEventListener('DOMContentLoaded', hook, { once: true });
  extras();
})();

/* Shrine cart extras (loader key "extras"): sheet swipe, cart icon animation, after-add message, floating cart button,
   rotating cart announcements, and the standard updateCart handler body */
(() => {
  if (window.ShrineCartExtras) return;
  const SC = window.ShrineCart;
  if (!SC) return;
  window.ShrineCartExtras = { version: 1 };
  const d = document;
  const w = window;
  const qs = (s, r) => (r || d).querySelector(s);
  const on = (t, n, f, o) => t && t.addEventListener(n, f, o);
  const reduced = () => !!(w.matchMedia && w.matchMedia('(prefers-reduced-motion: reduce)').matches);
  const mobile = () => !!(w.matchMedia && w.matchMedia('(max-width: 749px)').matches);
  const drawer = () => qs('cart-drawer');
  const isOpen = () => {
    const dr = drawer();
    return !!(dr && dr.classList.contains('active'));
  };
  const headerLink = () => {
    const b = qs('#cart-icon-bubble');
    return b && b.tagName === 'DIV' ? b.closest('.header__icon--cart') : b;
  };

  // #region standard updateCart handler (moved from the core, 01 §8.22)
  const handleUpdate = (defaultHandler, payload, options, core) =>
    core.enqueue(
      async () => {
        const before = drawer();
        const result = await defaultHandler();
        const out = Object.assign({}, result, { detail: Object.assign({}, (result && result.detail) || {}, { handledBy: 'shrine' }) });
        if (before && drawer() !== before) {
          console.warn('[Shrine cart] Shopify replaced the cart drawer during updateCart; reloading so the theme scripts reconnect');
          setTimeout(() => location.reload(), 0);
          return out;
        }
        let done = [];
        try {
          done = await core.render(null, { source: 'core:standard-action' });
        } catch (e) {}
        try {
          const cart = await core.getCart();
          if (cart) core.publishCart(cart, 'core:standard-action', done);
          core.fire('shrine:cart:updated', { ok: !(result && result.userErrors && result.userErrors.length), action: 'update', source: 'core:standard-action', cart, error: null });
        } catch (e) {}
        return out;
      },
      { label: 'core:standard-action' }
    );
  // #endregion

  // #region bottom sheet swipe
  let drag = null;
  const sheetOn = (dr) => dr && dr.classList.contains('cart-drawer--mobile-bottom') && mobile();
  on(d, 'pointerdown', (e) => {
    const dr = e.target.closest && e.target.closest('cart-drawer');
    if (!sheetOn(dr) || !e.isPrimary || e.button !== 0 || !e.target.closest('.cart-sheet__handle, .drawer__header')) return;
    const inner = qs('.drawer__inner', dr);
    if (inner) drag = { dr, inner, y: e.clientY, t: Date.now(), id: e.pointerId, dy: 0, on: false };
  });
  on(d, 'pointermove', (e) => {
    if (!drag || e.pointerId !== drag.id) return;
    drag.dy = Math.max(0, e.clientY - drag.y);
    if (!drag.on && drag.dy > 8) {
      drag.on = true;
      drag.inner.classList.add('is-dragging');
      try {
        drag.inner.setPointerCapture(e.pointerId);
      } catch (x) {}
    }
    if (drag.on && !reduced()) drag.inner.style.translate = '0 ' + drag.dy + 'px';
  });
  const release = (e) => {
    if (!drag || e.pointerId !== drag.id) return;
    const g = drag;
    drag = null;
    if (!g.on) return;
    g.inner.classList.remove('is-dragging');
    const v = g.dy / Math.max(1, Date.now() - g.t);
    if (g.dy > g.inner.offsetHeight / 3 || (v > 0.6 && g.dy > 40)) {
      g.dr.close();
      setTimeout(() => (g.inner.style.translate = ''), 350);
    } else g.inner.style.translate = '';
  };
  on(d, 'pointerup', release);
  on(d, 'pointercancel', release);
  // #endregion

  // #region cart icon animation
  const animate = (kind) => {
    if (reduced()) return;
    [headerLink(), qs('.cart-floating-button__link')].forEach((el) => {
      if (!el) return;
      el.classList.remove('cart-icon--bump', 'cart-icon--shake');
      void el.offsetWidth;
      el.classList.add('cart-icon--' + kind);
      setTimeout(() => el.classList.remove('cart-icon--' + kind), 900);
    });
  };
  const bubbleCount = () => {
    const b = qs('#cart-icon-bubble .cart-count-bubble');
    if (!b) return 0;
    const n = qs('span[aria-hidden="true"]', b);
    return n ? parseInt(n.textContent, 10) || 0 : 100;
  };
  const bubble = qs('#cart-icon-bubble');
  const kind = SC.config.iconAnimation;
  if (bubble && (kind === 'bump' || kind === 'shake')) {
    let count = bubbleCount();
    new MutationObserver(() => {
      const n = bubbleCount();
      if (n > count) animate(kind);
      count = n;
    }).observe(bubble, { childList: true });
  }
  // #endregion

  // #region after-add message
  on(d, 'product-form:added', (e) => {
    const dr = qs('cart-drawer[data-after-add="stay"]');
    const form = e.target;
    if (!dr || !SC.has('afterAdd') || !form || !form.closest) return;
    if ((form.dataset && form.dataset.isCartUpsell === 'true') || form.closest('cart-drawer, [data-cart-root]')) return;
    const show = () =>
      SC.toast.show({
        text: SC.t('core_item_added'),
        action: { label: SC.t('core_view_cart'), onClick: (button) => dr.open(headerLink() || button) },
        timeout: 6000,
        surface: 'page',
      });
    if (!form.closest('quick-add-modal')) return show();
    let shown = false;
    const once = () => {
      if (shown) return;
      shown = true;
      show();
    };
    d.body.addEventListener('modalClosed', once, { once: true });
    setTimeout(once, 1200);
  });
  // #endregion

  // #region floating cart button
  if (w.customElements && !customElements.get('cart-floating-button')) {
    customElements.define(
      'cart-floating-button',
      class extends HTMLElement {
        connectedCallback() {
          if (this.ready) return;
          this.ready = true;
          const link = qs('.cart-floating-button__link', this);
          if (!link) return;
          const icon = qs('.header__icon--cart svg.icon-cart');
          const box = qs('.cart-floating-button__icon', this);
          if (icon && box) box.replaceChildren(icon.cloneNode(true));
          on(link, 'click', (e) => {
            const dr = drawer();
            if (!dr || typeof dr.open !== 'function') return;
            e.preventDefault();
            dr.open(link);
          });
          on(link, 'keydown', (e) => {
            if (link.getAttribute('role') !== 'button' || (e.code !== 'Space' && e.key !== ' ')) return;
            e.preventDefault();
            link.click();
          });
          const head = headerLink();
          if (this.dataset.afterScroll === 'true' && head && w.IntersectionObserver) {
            this.io = new IntersectionObserver((en) => this.classList.toggle('is-hidden', en[en.length - 1].isIntersecting));
            this.io.observe(head);
          } else this.classList.remove('is-hidden');
          const count = qs('.cart-floating-button__count', this);
          const copy = () => {
            const b = qs('#cart-icon-bubble .cart-count-bubble');
            if (!count) return;
            if (!b) {
              count.hidden = true;
              return;
            }
            count.hidden = false;
            const num = qs('span[aria-hidden="true"]', b);
            const label = qs('.visually-hidden', b);
            count.innerHTML = '<span aria-hidden="true"></span><span class="visually-hidden"></span>';
            count.firstChild.textContent = num ? num.textContent : '';
            count.lastChild.textContent = label ? label.textContent : '';
          };
          const bub = qs('#cart-icon-bubble');
          if (bub) {
            this.mo = new MutationObserver(copy);
            this.mo.observe(bub, { childList: true });
          } else {
            this.onUpdated = (ev) => {
              const n = ev.detail && ev.detail.cart && ev.detail.cart.item_count;
              if (count && n != null) {
                count.hidden = !n;
                count.firstChild && (count.firstChild.textContent = n < 100 ? n : '');
              }
            };
            on(d, 'shrine:cart:updated', this.onUpdated);
          }
          const sync = (v) => link.hasAttribute('aria-expanded') && link.setAttribute('aria-expanded', String(v));
          this.offs = [SC.onOpen(() => sync(true)), SC.onClose(() => sync(false))];
        }
        disconnectedCallback() {
          if (this.io) this.io.disconnect();
          if (this.mo) this.mo.disconnect();
          if (this.onUpdated) d.removeEventListener('shrine:cart:updated', this.onUpdated);
          (this.offs || []).forEach((f) => f());
          this.ready = false;
        }
      }
    );
  }
  // #endregion

  // #region cart announcement
  const announcements = new Map();
  if (w.customElements && !customElements.get('cart-announcement')) {
    customElements.define(
      'cart-announcement',
      class extends HTMLElement {
        connectedCallback() {
          const msgs = Array.from(this.querySelectorAll('.cart-announcement__message'));
          if (msgs.length < 2 || this.timer) return;
          const id = this.dataset.blockId || '';
          const st = announcements.get(id) || { i: 0, paused: false };
          announcements.set(id, st);
          const show = (i) => {
            st.i = ((i % msgs.length) + msgs.length) % msgs.length;
            msgs.forEach((m, j) => {
              m.classList.toggle('is-active', j === st.i);
              m.hidden = j !== st.i;
            });
          };
          const btn = qs('.cart-announcement__toggle', this);
          const label = () => {
            if (!btn) return;
            btn.setAttribute('aria-label', st.paused ? btn.dataset.labelPlay : btn.dataset.labelPause);
            const [pause, play] = [qs('.cart-announcement__icon-pause', btn), qs('.cart-announcement__icon-play', btn)];
            if (pause) pause.toggleAttribute('hidden', st.paused);
            if (play) play.toggleAttribute('hidden', !st.paused);
          };
          if (!this.bound) {
            // listeners once per element (a moved element reconnects without new markup)
            this.bound = true;
            on(btn, 'click', () => {
              st.paused = !st.paused;
              label();
            });
            on(this, 'mouseenter', () => (this.held = true));
            on(this, 'mouseleave', () => (this.held = false));
            on(this, 'focusin', () => (this.held = true));
            on(this, 'focusout', (e) => (this.held = this.contains(e.relatedTarget)));
          }
          show(st.i);
          label();
          this.timer = setInterval(() => {
            const dr = this.closest('cart-drawer');
            if (st.paused || this.held || (dr && !dr.classList.contains('active'))) return;
            show(st.i + 1);
          }, Math.max(2, parseFloat(this.dataset.speed) || 5) * 1000);
        }
        disconnectedCallback() {
          clearInterval(this.timer);
          this.timer = 0;
        }
      }
    );
  }
  // #endregion

  SC.provide('extras', { version: 1, handleUpdate, isOpen });
})();

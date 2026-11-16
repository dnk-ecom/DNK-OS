/* Shrine PRO 2.0.0 cart pages: <cart-page> (Cart page V2 root), <cart-saved-products>, Empty cart helpers.
   Classic script, safe to run twice; main.js names are guarded, so it works on every main.js build. */
(() => {
  if (window.ShrineCartPage) return;
  const d = document;
  const w = window;
  const att = (f, x) => {
    try {
      return f();
    } catch (e) {
      return x;
    }
  };
  const log = (f) => {
    try {
      f();
    } catch (e) {
      console.error(e);
    }
  };
  const core = () => w.ShrineCart || null;
  const dm = () => !!(w.Shopify && w.Shopify.designMode);
  const cartUrl = () => (w.routes && w.routes.cart_url) || att(() => core().config.routes.cart) || '/cart';
  const rootUrl = () => att(() => w.Shopify.routes.root) || '/';
  const parse = (html) => new DOMParser().parseFromString(html, 'text/html');
  const liveDrawer = () => {
    const el = d.querySelector('cart-drawer');
    return el && typeof el.renderContents === 'function' ? el : null;
  };
  const list = (k) => {
    const v = att(() => JSON.parse(w.localStorage.getItem(k)));
    return Array.isArray(v) ? v.filter((x) => typeof x === 'string' && x) : [];
  };
  const getSections = (ids) =>
    fetch(cartUrl() + '?sections=' + encodeURIComponent(ids.join(',')), { cache: 'no-store' }).then((r) => {
      if (!r.ok) throw new Error('Cart page V2: sections ' + r.status);
      return r.json();
    });
  const emit = (o) => att(() => core().emitRender(o));
  const setPad = (px) => (d.documentElement.style.scrollPaddingBottom = px ? px + 'px' : '');
  const pubsub = (cb) => (typeof subscribe === 'function' && typeof PUB_SUB_EVENTS === 'object' ? subscribe(PUB_SUB_EVENTS.cartUpdate, (e) => att(() => cb(e || {}))) : null);

  class CartPage extends HTMLElement {
    connectedCallback() {
      if (this.offs) return;
      const c = core();
      const r = w.ShrineCartRequests;
      const show = (e) => e.persisted && this.scheduleRefresh(0, false);
      this.sectionId = this.dataset.sectionId;
      if (this.enginesOn === undefined) this.enginesOn = !!att(() => c.has('cartRoot')) && !d.querySelector('cart-drawer');
      if (this.enginesOn && !this.enginesInit) this.initEngines();
      this.bindBar();
      w.addEventListener('pageshow', show);
      this.offs = [
        att(() => r.registerSurface(this.surface())),
        pubsub((e) => this.onCartUpdate(e)),
        att(() => c.onRender((e) => att(() => this.onDrawerRender(e || {})))),
        () => w.removeEventListener('pageshow', show),
      ];
      emit({ surface: 'page-v2', root: this, source: 'connect', announce: false });
    }

    disconnectedCallback() {
      (this.offs || []).forEach((f) => typeof f === 'function' && att(f));
      this.offs = null;
      if (this.io) this.io.disconnect();
      clearTimeout(this.timer);
      setPad(0);
    }

    surface() {
      return {
        id: 'page-v2',
        isPresent: () => this.isConnected,
        sections: () => [this.sectionId, 'cart-icon-bubble'],
        render: (state, opts) => {
          if (!this.renderOwn(state, opts || {})) throw new Error('Cart page V2: no contents in the section');
        },
      };
    }

    getSectionsToRender() {
      const s = [{ id: this.sectionId }, { id: 'cart-icon-bubble' }];
      if (liveDrawer()) s.push({ id: 'cart-drawer' });
      return s;
    }

    // main.js's entry (QB-1c E13)
    async renderContents(state) {
      clearTimeout(this.timer);
      this.announceNext = false;
      const ids = this.getSectionsToRender().map((s) => s.id);
      const ok = (s) => s && ids.every((id) => typeof s[id] === 'string');
      if (!ok(state && state.sections)) {
        const fresh = await getSections(ids).catch(() => null);
        if (!ok(fresh)) return location.reload();
        state = Object.assign({}, state, { sections: fresh });
      }
      const dr = liveDrawer();
      if (dr) {
        this.forwarding = Date.now();
        log(() => dr.renderContents(state, true));
        dr.classList.toggle('is-empty', !!dr.querySelector('#CartDrawer .drawer__inner-empty'));
      }
      if (!this.renderOwn(state, { source: 'renderContents' })) location.reload();
    }

    setActiveElement(el) {
      this.activeElement = el;
    }

    onCartUpdate(e) {
      if ((att(() => e.shrine.surfaces) || []).indexOf('page-v2') < 0) this.scheduleRefresh();
    }

    onDrawerRender(e) {
      if (e.surface !== 'drawer' || /^[a-z]+:/.test(e.source || '')) return;
      const own = this.forwarding && Date.now() - this.forwarding < 1000; // this page's own forward
      this.forwarding = 0;
      if (!own) this.scheduleRefresh();
    }

    scheduleRefresh(delay = 120, announce = true) {
      this.announceNext = this.announceNext || announce;
      clearTimeout(this.timer);
      this.timer = setTimeout(() => this.refresh(), delay);
    }

    refresh() {
      if (this.refreshing) return (this.dirty = true), this.refreshing;
      const announce = !!this.announceNext;
      this.announceNext = false;
      this.refreshing = (async () => {
        await att(() => w.ShrineCartRequests.whenIdle({ timeout: 10000 }));
        const sections = await getSections(liveDrawer() ? [this.sectionId] : [this.sectionId, 'cart-icon-bubble']);
        if (this.isConnected && !this.renderOwn({ sections }, { source: 'refresh', announce })) location.reload();
      })()
        .catch((e) => console.warn(e))
        .finally(() => {
          this.refreshing = null;
          if (this.dirty) (this.dirty = false), this.scheduleRefresh(0);
        });
      return this.refreshing;
    }

    renderOwn(state, opts) {
      const html = att(() => state.sections[this.sectionId]);
      const fresh = typeof html === 'string' && parse(html).querySelector('cart-page');
      const next = fresh && fresh.querySelector('[data-cart-page-contents]');
      const box = this.querySelector('[data-cart-page-contents]');
      if (!next || !box) return false;
      const a = d.activeElement;
      const inside = !!a && a !== box && box.contains(a);
      const sel = inside && att(() => (typeof a.selectionStart === 'number' ? [a.selectionStart, a.selectionEnd] : 0));
      const keep = {};
      box.querySelectorAll('[data-preserve][id]').forEach((el) => {
        keep[el.id] = { open: el.open, checked: el.checked, value: el.type === 'file' ? undefined : el.value, scrollLeft: el.scrollLeft };
      });
      if (this.enginesOn && typeof fixParsedHtml === 'function') log(() => fixParsedHtml(box, next));
      box.innerHTML = next.innerHTML;
      this.classList.toggle('is-empty', fresh.classList.contains('is-empty'));
      const bubble = att(() => state.sections['cart-icon-bubble']);
      const icon = d.getElementById('cart-icon-bubble');
      const src = !liveDrawer() && icon && typeof bubble === 'string' && parse(bubble).querySelector('.shopify-section');
      if (src) icon.innerHTML = src.innerHTML;
      Object.keys(keep).forEach((id) => {
        const el = d.getElementById(id);
        const s = keep[id];
        if (el && this.contains(el)) ['open', 'checked', 'value', 'scrollLeft'].forEach((p) => s[p] !== undefined && p in el && el[p] !== s[p] && att(() => (el[p] = s[p])));
      });
      if (inside) {
        const t = a.id && d.getElementById(a.id);
        if (t && this.contains(t)) {
          att(() => t.focus({ preventScroll: true }));
          if (sel) att(() => t.setSelectionRange(sel[0], sel[1]));
        } else if (!opts.focus) {
          const h = d.getElementById('CartPage-Heading-' + this.sectionId) || d.getElementById('CartPage-EmptyHeading-' + this.sectionId);
          if (h) att(() => h.focus({ preventScroll: true }));
        }
      }
      this.bindBar();
      if (this.enginesOn) this.syncGifts();
      emit({ surface: 'page-v2', root: this, source: opts.source, announce: opts.announce !== false });
      return true;
    }

    // QB-1c E13, no drawer: main.js runs this root's gifts
    initEngines() {
      this.enginesInit = true;
      customElements.whenDefined('cart-page-items').then(() => {
        if (this.isConnected && this.querySelector('cart-page-items') && typeof initToggleUpsells === 'function') log(() => initToggleUpsells(this));
      });
    }

    syncGifts() {
      const due = [...this.querySelectorAll('cart-drawer-gift')].filter((g) => att(() => g.getUpdateRequired()));
      const rm = due.find((g) => g.dataset.selected === 'false');
      const add = due.find((g) => g.dataset.selected === 'true');
      log(() => (rm ? rm.removeFromCart() : add && add.addToCart()));
      this.giftChecks = (this.giftChecks || 0) + 1; // cart-page-items then skips its own validate (one per write)
      att(() => validateCartGifts());
    }

    // mobile bar: shown while the Summary's checkout is out of view
    bindBar() {
      if (this.io) this.io.disconnect();
      this.io = null;
      const bar = this.querySelector('[data-cart-page-bar]');
      if (!bar) return setPad(0);
      const target = this.querySelector('.cart-page__summary [name="checkout"]');
      const show = (v) => {
        if (!v && bar.contains(d.activeElement)) return;
        bar.classList.toggle('is-visible', v);
        bar.inert = !v;
        setPad(v ? bar.offsetHeight : 0);
      };
      if (!target || !w.IntersectionObserver) return show(true);
      this.io = new IntersectionObserver((es) => show(!es[es.length - 1].isIntersecting), { rootMargin: '0px 0px -10% 0px' });
      this.io.observe(target);
    }
  }

  // Saved products: cards from sections/cart-saved-card, cached 10 minutes per market
  const memory = new Map();
  const inflight = new Map();
  const keyOf = (h, v) => [rootUrl(), att(() => w.Shopify.currency.active) || '', att(() => w.Shopify.country) || '', h, v || ''].join('|');
  const cached = (h, v) => {
    const k = keyOf(h, v);
    const s = memory.get(k) || att(() => JSON.parse(w.sessionStorage.getItem('shrine-cart-saved:' + k)));
    if (!s || !(s.html || s.missing) || !(Date.now() - s.t < 600000)) return null;
    memory.set(k, s);
    return s;
  };
  const fetchCard = (h, v) => {
    const k = keyOf(h, v);
    if (!inflight.has(k)) {
      const url = rootUrl() + 'products/' + encodeURIComponent(h) + '?section_id=cart-saved-card' + (v ? '&variant=' + encodeURIComponent(v) : '');
      const p = fetch(url, { cache: 'no-store' })
        .then((r) => (r.status === 404 ? { missing: true } : r.ok ? r.text() : null))
        .then((x) => {
          if (typeof x !== 'string') return x;
          const tpl = d.createElement('template');
          tpl.innerHTML = x;
          const card = tpl.content.querySelector('[data-saved-card]');
          return card ? { html: card.outerHTML } : null;
        })
        .catch(() => null)
        .then((res) => {
          inflight.delete(k);
          if (res) {
            res.t = Date.now();
            memory.set(k, res);
            att(() => w.sessionStorage.setItem('shrine-cart-saved:' + k, JSON.stringify(res)));
          }
          return res;
        });
      inflight.set(k, p);
    }
    return inflight.get(k);
  };

  let pending = null;
  const onSubmit = function (e) {
    const c = e.target.closest && e.target.closest('[data-saved-card]');
    if (c) pending = { t: Date.now(), handle: c.dataset.handle, variantId: +c.dataset.variantId, productId: +c.dataset.productId, blockId: this.dataset.blockId };
  };
  const emitSaved = () => {
    const p = pending;
    pending = null;
    if (!p) return;
    const detail = { action: 'add', source: 'saved_products', blockId: p.blockId, handle: p.handle, productId: p.productId, variantId: p.variantId };
    d.dispatchEvent(new CustomEvent('shrine:cart:upsell', { detail }));
    att(() => w.Shopify.analytics.publish('shrine:cart_upsell', detail));
  };
  d.addEventListener('product-form:added', (e) => pending && e.target.closest && e.target.closest('[data-saved-card]') && emitSaved());
  const bridge = () => {
    if (bridge.done) return;
    bridge.done = !!pubsub((e) => {
      if (e.source !== 'product-form' || !pending || Date.now() - pending.t > 10000) return;
      const c = e.cartData || {};
      const vid = c.variant_id || att(() => c.items[0].variant_id);
      if (!vid || +vid === pending.variantId) emitSaved();
    });
  };

  class CartSavedProducts extends HTMLElement {
    connectedCallback() {
      if (this.offs) return;
      this.offs = [];
      this.run = (this.run || 0) + 1;
      this.recent = this.dataset.source !== 'wishlist';
      this.limit = Math.min(12, Math.max(1, parseInt(this.dataset.limit, 10) || 4));
      this.list = this.querySelector('[data-saved-list]');
      if (!this.list) return;
      if (this.recent) att(() => w.localStorage.setItem('shrine-recently-viewed-on', '1'));
      if (this.dataset.wishlistOff === 'true') return this.finish([], []);
      const reload = () => this.load(true);
      const onStorage = (e) => /^shrine-(wishlist|recently-viewed)$/.test(e.key || '') && reload();
      d.addEventListener('shrine:wishlist:change', reload);
      w.addEventListener('storage', onStorage);
      this.addEventListener('submit', onSubmit, true);
      this.offs.push(() => {
        d.removeEventListener('shrine:wishlist:change', reload);
        w.removeEventListener('storage', onStorage);
        this.removeEventListener('submit', onSubmit, true);
      });
      bridge();
      this.load(false);
    }

    disconnectedCallback() {
      (this.offs || []).forEach((f) => f());
      this.offs = null;
      this.stopWait();
      this.run++;
    }

    handles() {
      const raw = this.recent ? list('shrine-recently-viewed') : att(() => w.ShrineWishlist.all()) || list('shrine-wishlist');
      const skip = (this.dataset.cartHandles || '').split(',');
      const m = /\/products\/([^/?#]+)/.exec(location.pathname);
      if (m) skip.push(att(() => decodeURIComponent(m[1])) || m[1]);
      return raw.filter((h, i) => typeof h === 'string' && h && skip.indexOf(h) < 0 && raw.indexOf(h) === i).slice(0, this.limit);
    }

    load(force) {
      const run = ++this.run;
      const hs = this.handles();
      const map = this.recent ? {} : att(() => JSON.parse(w.localStorage.getItem('shrine-wishlist-variants'))) || {};
      const vs = hs.map((h) => (typeof map === 'object' && map[h]) || null);
      const ready = hs.map((h, i) => cached(h, vs[i]));
      let started = false;
      const start = () => {
        if (started) return;
        started = true;
        this.stopWait();
        Promise.all(hs.map((h, i) => ready[i] || fetchCard(h, vs[i]))).then((r) => run === this.run && this.isConnected && this.finish(r, hs));
      };
      this.stopWait();
      if (ready.every(Boolean)) return this.finish(ready, hs);
      const dr = this.closest('cart-drawer');
      // a closed drawer sits edge to edge with the viewport, which IntersectionObserver counts as intersecting: wait for open
      if (dr && !force && !dr.classList.contains('active')) return (this.offOpen = att(() => core().onOpen(start))) || start();
      if (dr || force || !w.IntersectionObserver) return start();
      // the root is hidden: watch its parent
      this.io = new IntersectionObserver((es) => es.some((e) => e.isIntersecting) && start(), { rootMargin: '200px' });
      this.io.observe(this.parentElement || this);
    }

    stopWait() {
      if (this.io) this.io.disconnect();
      if (typeof this.offOpen === 'function') att(this.offOpen);
      this.io = this.offOpen = null;
    }

    finish(results, hs) {
      const frag = d.createDocumentFragment();
      const gone = [];
      const style = this.dataset.addStyle;
      const text = this.dataset.addLabel;
      let count = 0;
      results.forEach((r, i) => {
        if (r && r.missing) return gone.push(hs[i]);
        const tpl = d.createElement('template');
        tpl.innerHTML = (r && r.html) || '';
        const li = tpl.content.firstElementChild;
        if (!li) return;
        if (text) li.querySelectorAll('[data-saved-add-label]').forEach((el) => (el.textContent = text));
        const btn = li.querySelector('[data-saved-add]');
        if (btn && (style === 'outline' || style === 'pill')) btn.classList.add('button--secondary');
        if (btn && style === 'pill') btn.classList.add('cart-add--pill');
        frag.appendChild(li);
        count++;
      });
      this.list.querySelectorAll(count || !dm() ? '[data-saved-card], [data-saved-sample]' : '[data-saved-card]').forEach((el) => el.remove());
      this.list.appendChild(frag);
      this.hidden = !count && !dm();
      if (this.recent && gone.length) att(() => w.localStorage.setItem('shrine-recently-viewed', JSON.stringify(list('shrine-recently-viewed').filter((h) => gone.indexOf(h) < 0))));
      if (!dm()) return;
      const n = att(() => core().notices);
      if (count) att(() => n.clear('pages-saved-sample'));
      else
        att(() =>
          n.set('pages-saved-sample', {
            level: 'info',
            title: 'Saved products',
            text: 'this browser has no ' + (this.recent ? 'recently viewed' : 'saved') + ' products yet, so samples are shown.',
            blockId: this.dataset.blockId,
          })
        );
    }
  }

  // Empty drawer, after an add from its blocks: focus into the filled drawer; a failed add keeps is-empty
  // (main.js's ProductForm removes it after every add)
  let emptyAddAt = 0;
  let emptyMO = null;
  d.addEventListener(
    'submit',
    (e) => {
      const dr = e.target.closest && e.target.closest('cart-drawer');
      if (!dr || !e.target.closest('.cart-empty')) return;
      emptyAddAt = Date.now();
      if (emptyMO) emptyMO.disconnect();
      emptyMO = new MutationObserver(() => {
        if (!dr.querySelector('#CartDrawer .drawer__inner-empty') || Date.now() - emptyAddAt > 15000) emptyMO.disconnect();
        else if (!dr.classList.contains('is-empty')) dr.classList.add('is-empty');
      });
      emptyMO.observe(dr, { attributes: true, attributeFilter: ['class'] });
    },
    true
  );
  const onEmptyRender = (e) => {
    if (!e || e.surface !== 'drawer' || !emptyAddAt) return;
    const dr = d.querySelector('cart-drawer');
    if (Date.now() - emptyAddAt > 10000) emptyAddAt = 0;
    if (!emptyAddAt || !dr || dr.querySelector('#CartDrawer .drawer__inner-empty')) return;
    emptyAddAt = 0;
    const box = d.getElementById('CartDrawer');
    const inner = dr.querySelector('#CartDrawer .drawer__inner');
    if (!dr.classList.contains('active') || !box || !inner) return;
    try {
      core().trapFocus(box, inner);
    } catch (x) {
      inner.focus();
    }
  };

  const api = {
    version: 1,
    refresh: (el) => (el ? [el] : [...d.querySelectorAll('cart-page')]).forEach((p) => att(() => p.scheduleRefresh(0))),
    savedCache: {
      clear() {
        memory.clear();
        inflight.clear();
        att(() => Object.keys(w.sessionStorage).forEach((k) => !k.indexOf('shrine-cart-saved:') && w.sessionStorage.removeItem(k)));
      },
    },
  };
  window.ShrineCartPage = api;
  let wired = false;
  const wire = () => {
    bridge();
    const c = core();
    if (wired || !c || typeof c.onRender !== 'function') return;
    wired = true;
    att(() => c.onRender(onEmptyRender));
    att(() => c.provide('page', api));
  };
  wire();
  if (!wired) {
    d.addEventListener('DOMContentLoaded', wire, { once: true });
    w.addEventListener('load', wire, { once: true });
  }
  if (!customElements.get('cart-page')) customElements.define('cart-page', CartPage);
  if (!customElements.get('cart-saved-products')) customElements.define('cart-saved-products', CartSavedProducts);
})();

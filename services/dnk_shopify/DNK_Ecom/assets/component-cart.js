/* Shrine cart core: window.ShrineCart, window.ShrineCartRequests, loader, announcer, toast, footer fit */
(() => {
  if (window.ShrineCart && window.ShrineCart.version) return;
  const d = document;
  const w = window;
  const qs = (s, r) => (r || d).querySelector(s);
  const qsa = (s, r) => Array.from((r || d).querySelectorAll(s));
  const on = (t, n, f, o) => t && t.addEventListener(n, f, o);
  const att = (f, x) => {
    try {
      return f();
    } catch (e) {
      return x;
    }
  };
  const fire = (n, detail, t) => att(() => (t || d).dispatchEvent(new CustomEvent(n, { bubbles: true, detail })));
  const err = (e) => console.error(e);
  const safe = (f) => {
    try {
      return f();
    } catch (e) {
      err(e);
    }
  };
  const msg = (e) => String((e && e.message) || e);
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const cfgEl = qs('#shrine-cart-config');
  const config = (cfgEl && att(() => JSON.parse(cfgEl.textContent))) || {};
  const designMode = !!(config.designMode || (w.Shopify && w.Shopify.designMode));
  const E = () => w.ShrineCartEngine || {};
  const has = (f) => !!E()[f];
  const gid = (id) => 'gid://shopify/ProductVariant/' + id;
  const present = (s) => att(() => s.isPresent(), false);
  const openNow = () => !!att(() => qs('cart-drawer').classList.contains('active'));
  let lastCart = null;

  // #region hooks, strings
  const hooks = { open: [], close: [], render: [] };
  const hook = (n) => (cb) => {
    hooks[n].push(cb);
    return () => (hooks[n] = hooks[n].filter((f) => f !== cb));
  };
  const call = (n, a) => hooks[n].slice().forEach((f) => safe(() => f(a)));
  const rep = (s, k, v) => s.split('[' + k + ']').join(v);
  const t = (key, vars) => {
    let s = (config.strings || {})[key];
    if (typeof s !== 'string') return key;
    for (const k in vars || {}) {
      if (vars[k] == null) continue;
      const v = String(vars[k]);
      s = rep(s, k, v).replace(new RegExp('\\{\\{\\s*' + k + '\\s*\\}\\}', 'g'), () => v);
    }
    return s;
  };
  const keywords = (text, map) => {
    let s = text == null ? '' : String(text);
    for (const k in map || {}) if (Object.prototype.hasOwnProperty.call(map, k) && map[k] != null) s = rep(s, k, String(map[k]));
    return s;
  };
  // #endregion

  // #region loader
  const KEYS = ['lines', 'checkout', 'rewards', 'upsells', 'page', 'extras', 'editor'];
  const loaded = {};
  const provided = {};
  const waits = {};
  const failed = {};
  const sel = (u) => String(u).replace(/["\\]/g, '\\$&');
  const settle = (key, api) => (waits[key] || []).splice(0).forEach((r) => r(api));
  const load = (key, cssOnly) => {
    const a = (config.assets || {})[key];
    if (!a || KEYS.indexOf(key) < 0 || (key === 'editor' && !designMode)) return;
    const st = loaded[key] || (loaded[key] = {});
    if (a.css && !st.css) {
      st.css = 1;
      if (!qs('link[rel="stylesheet"][href="' + sel(a.css) + '"]')) d.head.appendChild(Object.assign(d.createElement('link'), { rel: 'stylesheet', href: a.css }));
    }
    if (cssOnly || !a.js || st.js) return;
    st.js = 1;
    if (qs('script[src="' + sel(a.js) + '"]')) return;
    const s = Object.assign(d.createElement('script'), { src: a.js, async: true });
    s.onerror = () => {
      failed[key] = 1;
      settle(key, null);
    };
    d.head.appendChild(s);
  };
  // an empty drawer hides its header, Body and Footer: their files load with the first add (a product form's submit) or
  // the render after it, not on every page view (all = also those)
  const hiddenEmpty = (el) => !!(el.closest('cart-drawer.is-empty') && el.closest('.drawer__header, .cart-drawer__body, .drawer__footer'));
  const scan = (root, all) => {
    if (!root || !root.querySelectorAll) return;
    const els = qsa('[data-cart-feature]', root);
    if (root.matches && root.matches('[data-cart-feature]')) els.unshift(root);
    els.forEach(
      (el) =>
        (all || !hiddenEmpty(el)) &&
        el
          .getAttribute('data-cart-feature')
          .split(/\s+/)
          .forEach((k) => k && load(k.replace(/:css$/, ''), /:css$/.test(k)))
    );
  };
  on(d, 'submit', (e) => att(() => e.target.closest('product-form') && scan(qs('cart-drawer'), 1)), true);
  const requireKey = (key) =>
    key in provided || failed[key]
      ? Promise.resolve(key in provided ? provided[key] : null)
      : new Promise((res) => {
          (waits[key] = waits[key] || []).push(res);
          load(key);
          setTimeout(() => res(key in provided ? provided[key] : null), 10000);
        });
  const provide = (key, api) => {
    provided[key] = api;
    settle(key, api);
  };
  // #endregion

  // #region announcer
  const aq = [];
  let aTimer = 0;
  let aFirst = 0;
  // sentences, not a run-on: a period between texts that don't end in one
  const join = (list) => list.reduce((s, x) => (s && x ? s + (/[.!?…。！？:]$/.test(s) ? ' ' : '. ') + x : s || x), '');
  const flushAnnounce = () => {
    const open = openNow();
    let items = aq.splice(0).filter((x) => !x.slot || (x.slot === 'render:drawer') === open);
    // a busy text ("Updating…") flushed with its result is dropped
    if (items.some((x) => !x.busy)) items = items.filter((x) => !x.busy);
    aFirst = 0;
    const text = join(items.map((x) => x.text));
    const reg = (o) => qs(o ? 'cart-drawer [data-cart-announcer="drawer"]' : '[data-cart-announcer="page"]');
    const r = reg(open) || reg(!open);
    if (!text || !r) return;
    r.setAttribute('aria-live', items.some((x) => x.p === 'assertive') ? 'assertive' : 'polite');
    r.textContent = '';
    setTimeout(() => (r.textContent = text), 150);
  };
  const queueText = (x) => {
    if (x.slot) {
      const i = aq.findIndex((y) => y.slot === x.slot);
      if (i > -1) aq.splice(i, 1);
    }
    if (x.text && (x.slot || !aq.some((y) => !y.slot && y.text === x.text))) aq.push(x);
    if (!aq.length) return;
    const now = Date.now();
    aFirst = aFirst || now;
    clearTimeout(aTimer);
    aTimer = setTimeout(flushAnnounce, Math.max(0, Math.min(500, aFirst + 1000 - now)));
  };
  const announce = (text, o) => queueText({ text: String(text == null ? '' : text).trim(), p: (o && o.politeness) || 'polite', busy: !!(o && o.busy) });
  const announceRender = (surface, root) => {
    if (!root || !root.querySelectorAll) return;
    const els = qsa('[data-cart-announce]', root);
    if (root.matches && root.matches('[data-cart-announce]')) els.unshift(root);
    const text = join(els.map((el) => el.getAttribute('data-cart-announce').trim()));
    queueText({ slot: 'render:' + (surface || 'page'), text });
  };
  // #endregion

  // #region focus, toast
  const reduced = () => !!(w.matchMedia && w.matchMedia('(prefers-reduced-motion: reduce)').matches);
  const focusIn = (c, el) => {
    const x = el || c;
    if (!att(() => (typeof trapFocus === 'function' ? trapFocus(c, x) : x.focus(), 1))) att(() => x.focus());
  };
  let toastPos = null;
  const button = (cls, label) => Object.assign(d.createElement('button'), { type: 'button', className: cls, textContent: label || '' });
  const toast = {
    show(o) {
      o = o || {};
      const dr = qs('cart-drawer');
      const inDrawer = o.surface !== 'page' && openNow();
      const box = (inDrawer && qs('[data-cart-toast-region="drawer"]', dr)) || qs('[data-cart-toast-region="page"]');
      if (!box) return { close() {} };
      const inner = inDrawer && qs('.drawer__inner', dr);
      if (box.shrineToast) box.shrineToast.close('replaced');
      const el = Object.assign(d.createElement('div'), { className: 'cart-toast' });
      el.setAttribute('data-cart-toast', '');
      el.appendChild(Object.assign(d.createElement('p'), { className: 'cart-toast__text', textContent: o.text || '' }));
      const act = o.action && o.action.label ? el.appendChild(button('cart-toast__action', o.action.label)) : null;
      const x = el.appendChild(button('cart-toast__close'));
      x.setAttribute('aria-label', t('core_close'));
      x.innerHTML = '<svg aria-hidden="true" focusable="false" viewBox="0 0 24 24" width="16" height="16"><path d="M6 6l12 12M18 6 6 18" stroke="currentColor" stroke-width="2" fill="none"/></svg>';
      let left = o.timeout == null ? 6000 : Number(o.timeout) || 0;
      let start = 0;
      let timer = 0;
      let running = false;
      let hov = false;
      let foc = false;
      let done = false;
      const pos = () => {
        if (!inner || !inner.isConnected) return;
        const r = inner.getBoundingClientRect();
        const gap = 1.2 * (parseFloat(getComputedStyle(d.documentElement).fontSize) || 10);
        const bar = qs(':scope > cart-compact-bar', inner);
        const foot = qs(':scope > .drawer__footer', inner);
        let top = r.bottom;
        if (bar && !bar.hidden && !bar.classList.contains('is-hidden')) top = bar.getBoundingClientRect().top;
        else if (foot) top = Math.min(r.bottom, Math.max(r.top, foot.getBoundingClientRect().top));
        box.style.setProperty('--cart-toast-left', r.left + gap + 'px');
        box.style.setProperty('--cart-toast-width', Math.max(0, r.width - 2 * gap) + 'px');
        box.style.setProperty('--cart-toast-bottom', Math.max(gap, w.innerHeight - top + gap / 2) + 'px');
      };
      const api = {
        close(reason) {
          if (done) return;
          done = true;
          clearTimeout(timer);
          if (box.shrineToast === api) box.shrineToast = null;
          if (toastPos === pos) toastPos = null;
          const hadFocus = el.contains(d.activeElement);
          const fin = () => {
            el.remove();
            if (inDrawer && openNow()) {
              const trap = dr.classList.contains('is-empty') ? qs('.drawer__inner-empty', dr) : qs('#CartDrawer', dr);
              const a = d.activeElement;
              if (trap) focusIn(trap, hadFocus || !a || !trap.contains(a) ? inner || trap : a);
            }
            safe(() => o.onClose && o.onClose(reason || 'close'));
          };
          el.classList.add('is-leaving');
          if (reduced()) fin();
          else setTimeout(fin, 150);
        },
      };
      const tick = () => {
        if ((hov || foc) && running) {
          clearTimeout(timer);
          left -= Date.now() - start;
          running = false;
        } else if (!hov && !foc && !running && left > 0) {
          start = Date.now();
          running = true;
          timer = setTimeout(() => api.close('timeout'), left);
        }
      };
      const flag = (n, f) => on(el, n, (e) => {
        if (f(e) !== false) tick();
      });
      flag('mouseenter', () => (hov = true));
      flag('mouseleave', () => {
        hov = false;
      });
      flag('focusin', () => (foc = true));
      flag('focusout', (e) => (el.contains(e.relatedTarget) ? false : (foc = false, true)));
      on(el, 'keyup', (e) => {
        if (e.key !== 'Escape' && e.code !== 'Escape') return;
        e.stopPropagation();
        api.close('close');
      });
      on(act, 'click', () => {
        safe(() => o.action.onClick && o.action.onClick(act));
        api.close('action');
      });
      on(x, 'click', () => api.close('close'));
      box.appendChild(el);
      box.shrineToast = api;
      if (inDrawer) {
        pos();
        toastPos = pos;
        const a = d.activeElement;
        focusIn(dr, a && dr.contains(a) ? a : inner);
      }
      announce((o.text || '') + (act ? '. ' + o.action.label : ''));
      tick();
      return api;
    },
  };
  // #endregion

  // #region money
  let fmts = null;
  const plain = (s) => String(s == null ? '' : s).replace(/<[^>]*>/g, '').replace(/\s+/g, ' ').trim();
  const derive = (sample) => {
    const m = sample && sample.match(/\d[\d.,'\s]*\d/);
    if (!m) return null;
    const n = m[0];
    const dec = /\D\d\d$/.test(n);
    const marks = n.replace(/\d/g, '');
    const th = (dec ? marks.slice(0, -1) : marks).charAt(0);
    const sep = /\s/.test(th) ? 'space' : th === "'" ? 'apostrophe' : (dec ? n.charAt(n.length - 3) === ',' : th === '.') ? 'comma' : '';
    return sample.replace(n, '{{amount' + (dec ? '' : '_no_decimals') + (sep ? '_with_' + sep + '_separator' : '') + '}}');
  };
  const moneyInit = () => {
    fmts = { p: config.moneyFormat || '{{amount}}', c: config.moneyWithCurrencyFormat || config.moneyFormat || '{{amount}}' };
    if (typeof formatMoney !== 'function') return;
    [
      ['p', config.moneySample],
      ['c', config.moneyWithCurrencySample],
    ].forEach(([k, s]) => {
      if (s && !att(() => plain(formatMoney(123456, fmts[k])) === plain(s), false)) fmts[k] = derive(plain(s)) || fmts[k];
    });
  };
  const money = {
    format(cents, o) {
      o = o || {};
      if (!fmts) moneyInit();
      const trim = o.trailingZeros === false;
      const cur = o.currency;
      const c = Number(cents) || 0;
      const own = (!cur || cur === config.currency) && typeof formatMoney === 'function' ? att(() => plain(formatMoney(Math.round(c), o.withCurrency ? fmts.c : fmts.p, trim))) : null;
      if (own != null) return own;
      return att(() => {
        const opt = { style: 'currency', currency: cur || config.currency || 'USD' };
        if (trim && Math.round(c) % 100 === 0) opt.minimumFractionDigits = opt.maximumFractionDigits = 0;
        return new Intl.NumberFormat(d.documentElement.lang || config.locale || undefined, opt).format(c / 100);
      }, (c / 100).toFixed(2));
    },
    rate(shop) {
      const c = (w.Shopify && w.Shopify.currency) || {};
      const rate = parseFloat(c.rate);
      return !c.active || !rate || rate === 1 || c.active === (shop || config.shopCurrency) ? null : { active: c.active, rate };
    },
  };
  // #endregion

  // #region queue, line lock
  let chain = Promise.resolve();
  let pending = 0;
  let reloadPending = false;
  const mainBusy = () =>
    !!qs('.cart__items--disabled') ||
    qsa('product-form [type="submit"][aria-disabled="true"]').some((b) => {
      const m = qs('.sold-out-message', b);
      return !m || m.classList.contains('hidden');
    });
  const isBusy = () => pending > 0 || mainBusy() || !!att(() => E().queue.isBusy());
  const waitFor = (fn, ms) =>
    new Promise((res) => {
      const end = Date.now() + ms;
      const tick = () => (att(fn, false) ? res(true) : Date.now() >= end ? res(false) : setTimeout(tick, 50));
      tick();
    });
  const begin = () => ++pending === 1 && fire('shrine:cart:busy', { busy: true });
  const end = () => {
    if (--pending > 0) return;
    pending = 0;
    fire('shrine:cart:busy', { busy: false });
    if (reloadPending) location.reload();
  };
  const engineQueue = () => (has('lineKeys') && E().queue && E().queue.enqueue ? E().queue : null);
  const enqueue = (task, o) => {
    const run = async () => {
      if (!has('lineKeys') && !(await waitFor(() => !mainBusy(), 10000))) console.warn('[Shrine cart] main.js stayed busy for 10 s; continuing', (o && o.label) || '');
      return task();
    };
    begin();
    const q = engineQueue();
    let p;
    if (q) p = Promise.resolve(q.enqueue(run));
    else {
      p = chain.then(run, run);
      chain = p.catch(() => {});
    }
    p.then(end, end);
    return p;
  };
  const whenIdle = (o) => waitFor(() => !isBusy(), (o && o.timeout) || 10000).then((ok) => (ok || console.warn('[Shrine cart] cart stayed busy; continuing'), ok));
  const LOCK = 'data-cart-locked';
  const lock = () => {
    if (has('lineKeys')) return () => {};
    qsa('cart-drawer-items, cart-items, cart-page-items').forEach((el) => el.setAttribute(LOCK, ''));
    return () => qsa('[' + LOCK + ']').forEach((el) => el.removeAttribute(LOCK));
  };
  const guard = (e) => {
    if (e.target && e.target.closest && e.target.closest('[' + LOCK + ']')) {
      e.preventDefault();
      e.stopImmediatePropagation();
    }
  };
  on(d, 'click', guard, true);
  on(d, 'change', guard, true);
  // #endregion

  // #region requests
  const route = (name) =>
    (config.routes || {})[name] ||
    (w.routes || {})[name + '_url'] ||
    ((w.Shopify && w.Shopify.routes && w.Shopify.routes.root) || '/') + (name === 'cart' ? 'cart' : name.replace('_', '/'));
  const split = (j) => {
    const cart = Object.assign({}, j);
    const sections = cart.sections || null;
    delete cart.sections;
    return { cart, sections };
  };
  const getCart = async () => {
    try {
      const r = await fetch(route('cart') + '.js', { cache: 'no-store', headers: { Accept: 'application/json' } });
      const j = r.ok ? await r.json() : null;
      if (j && Array.isArray(j.items)) lastCart = j;
      return j;
    } catch (e) {
      return null;
    }
  };
  const getSections = async (ids) => {
    if (!ids.length) return {};
    try {
      const r = await fetch(route('cart') + '?sections=' + ids.map(encodeURIComponent).join(','));
      return r.ok ? await r.json() : null;
    } catch (e) {
      return null;
    }
  };
  const failure = (code, message, status) => ({ ok: false, status: status || 0, cart: null, sections: null, error: { code, message: message || code } });
  const post = async (name, body, sections) => {
    const payload = Object.assign({}, body);
    if (sections && sections.length) Object.assign(payload, { sections, sections_url: location.pathname });
    let r;
    try {
      r = await fetch(route(name) + '.js', { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify(payload) });
    } catch (e) {
      return failure('network', msg(e));
    }
    const j = await r.json().catch(() => null);
    const st = j && typeof j.status === 'number' ? j.status : r.status;
    if (st >= 400 || (j && j.errors && !Array.isArray(j.items))) {
      return failure(r.ok || r.status === 422 ? 'cart' : 'http', (j && (j.description || j.message || (typeof j.errors === 'string' && j.errors))) || String(st), st);
    }
    return j ? { ok: true, status: r.status, json: j } : failure('http', String(r.status), r.status);
  };
  const planOf = (it) => att(() => String(it.selling_plan_allocation.selling_plan.id), null);
  const normPlan = (v) => (v === null || v === undefined || v === '' ? null : String(v));
  const planParam = (v) => (v !== null && /^\d+$/.test(v) ? Number(v) : v);
  const propsKey = (p) => JSON.stringify(Object.keys(p || {}).sort().map((k) => [k, String(p[k])]));
  const resolve = (ref, cart) => {
    const items = (cart && cart.items) || [];
    if (!ref) return null;
    let i = ref.key ? items.findIndex((it) => it.key === ref.key) : -1;
    if (i < 0 && ref.variantId != null) {
      const c = [];
      items.forEach((it, j) => {
        if (
          String(it.variant_id) === String(ref.variantId) &&
          (ref.sellingPlanId === undefined || planOf(it) === normPlan(ref.sellingPlanId)) &&
          (ref.properties === undefined || propsKey(it.properties) === propsKey(ref.properties)) &&
          (ref.free === undefined || (Number(it.final_line_price) === 0) === !!ref.free)
        )
          c.push(j);
      });
      i = ref.properties !== undefined || c.length === 1 ? (c.length ? c[0] : -1) : -1;
    }
    return i < 0 ? null : { line: i + 1, key: items[i].key, item: items[i] };
  };
  // #endregion

  // #region standard events
  let sePromise = null;
  const loadSE = () =>
    sePromise ||
    (sePromise = (async () => {
      let m = w.StandardEvents || null;
      if (!m && config.standardEventsUrl) {
        m = await import(config.standardEventsUrl).catch(() => null);
        if (m && !w.StandardEvents) w.StandardEvents = m;
      }
      att(() => m && m.createViewEventElement && !customElements.get('s-view-event') && customElements.define('s-view-event', m.createViewEventElement()));
      return m;
    })());
  const seRecord = (cls, init, el) => {
    const rec = { known: false, out: null, fire: null };
    Promise.race([loadSE(), sleep(3000)]).then((m) => {
      const C = m && m[cls];
      if (!C || typeof C.createPromise !== 'function') return;
      att(() => {
        const cp = C.createPromise() || {};
        const promise = cp.promise || cp;
        if (promise.catch) promise.catch(() => {});
        const target = el && el.isConnected ? el : d;
        const conv = (cart) => att(() => (cart && C.createCartFromAjaxResponse ? C.createCartFromAjaxResponse(cart) : cart || null), cart || null);
        target.dispatchEvent(new C(Object.assign({}, init, { promise })));
        rec.fire = (o) =>
          att(() => {
            if (o.network) {
              if (m.CartErrorEvent) target.dispatchEvent(new m.CartErrorEvent({ error: o.network, code: 'SERVICE_UNAVAILABLE' }));
              if (cp.reject) cp.reject(new Error(o.network));
            } else if (cp.resolve) cp.resolve(o.decline ? { cart: conv(o.cart || lastCart), userErrors: [{ code: 'INVALID', field: ['lines'], message: o.decline }] } : { cart: conv(o.cart) });
          });
        if (rec.known) rec.fire(rec.out);
      });
    });
    rec.settle = (o) => {
      if (rec.known) return;
      rec.known = true;
      rec.out = o || {};
      if (rec.fire) rec.fire(rec.out);
    };
    return rec;
  };
  const outcome = (res) => {
    const e = res && res.error;
    if (e && e.code === 'network') return { network: e.message || 'network' };
    return e && e.code !== 'mismatch' && e.code !== 'sections' ? { decline: e.message || e.code } : { cart: res && res.cart };
  };
  const eventRoot = (context) => {
    const dr = qs('cart-drawer');
    const page = qs('cart-page') || qs('cart-items');
    if (context) return [(context === 'dialog' ? dr : page) || d, context];
    if (dr && openNow()) return [dr, 'dialog'];
    return page ? [page, 'cart'] : [dr || d, dr ? 'dialog' : 'cart'];
  };
  // #endregion

  // #region writes
  const publishCart = (cart, source, list) =>
    safe(() => typeof publish === 'function' && typeof PUB_SUB_EVENTS !== 'undefined' && publish(PUB_SUB_EVENTS.cartUpdate, { source: 'cart-items', cartData: cart, shrine: { source, surfaces: list || [] } }));
  let warned = false;
  const sourceOf = (opts) => {
    if (!opts.source && !warned) console.warn('[Shrine cart] ShrineCartRequests write without opts.source');
    warned = warned || !opts.source;
    return opts.source || 'unknown';
  };
  const makeCtx = (opts) => {
    const all = opts.render === false ? [] : sectionIds();
    const ctx = { sections: all.slice(0, 5), extra: all.slice(5), evs: [] };
    ctx.event = (action, extra, cls) => {
      if (opts.standardEvent === null || (!cls && ctx.evs.length)) return;
      const [el, context] = eventRoot(opts.context);
      ctx.evs.push(seRecord(cls || 'CartLinesUpdateEvent', Object.assign({ action: cls ? 'update' : opts.standardEvent || action, context }, extra), el));
    };
    return ctx;
  };
  const finishWrite = async (ctx, opts, source, state) => {
    const need = ctx.sections.concat(ctx.extra);
    const secs = Object.assign({}, state.sections || {});
    const missing = need.filter((id) => secs[id] == null);
    if (missing.length) Object.assign(secs, (await getSections(missing)) || {});
    state.sections = secs;
    if (need.some((id) => secs[id] == null)) {
      reloadPending = true;
      return null;
    }
    return render({ sections: secs, cart: state.cart }, { source, focus: opts.focus, fromWrite: true, result: state.result || state }).catch((e) => (err(e), []));
  };
  const closeWrite = (ctx, opts, source, action, res, list) => {
    ctx.evs.forEach((ev) => att(() => ev.settle(outcome(res))));
    if (res.cart && opts.publish !== false) publishCart(res.cart, source, list);
    fire('shrine:cart:updated', { ok: !!res.ok, action, source, cart: res.cart || null, error: res.error || null });
  };
  const write = (action, opts, fn) => {
    opts = opts || {};
    const source = sourceOf(opts);
    loadSE();
    return enqueue(async () => {
      const ctx = makeCtx(opts);
      let res = null;
      let list = [];
      try {
        res = (await fn(ctx).catch((e) => failure('network', msg(e)))) || failure('network', 'no result');
        if (res.skipped) return res;
        if (res.cart && Array.isArray(res.cart.items)) lastCart = res.cart;
        if ((res.cart || res.sections) && opts.render !== false) {
          const state = { sections: res.sections, cart: res.cart, result: res };
          list = (await finishWrite(ctx, opts, source, state)) || [];
          res.sections = state.sections;
          if (!list.length && reloadPending) res.error = res.error || { code: 'sections', message: 'sections' };
        }
        return res;
      } finally {
        if (res && !res.skipped) closeWrite(ctx, opts, source, action, res, list);
      }
    }, { label: source }).catch((e) => failure('network', msg(e)));
  };
  const verifyPlan = async (t, body, cart, before, target) => {
    const item = cart.items[body.line - 1];
    const same = item && String(item.variant_id) === String(t.item.variant_id) && propsKey(item.properties) === propsKey(t.item.properties);
    if (same && planOf(item) === target) return { cart };
    const prev = !same && item && planOf(item) === target && ((before && before.items) || []).find((it) => String(it.variant_id) === String(item.variant_id) && propsKey(it.properties) === propsKey(item.properties));
    // the POST landed on another line: give it back its plan, and its quantity (already on the plan: only the quantity)
    if (prev && (planOf(prev) !== target || Number(prev.quantity) !== Number(item.quantity))) {
      const r2 = await post('cart_change', { line: body.line, quantity: prev.quantity, selling_plan: planParam(planOf(prev)) }, null);
      return r2.error ? { cart, error: { code: 'mismatch', reverted: false, message: 'line moved' } } : { cart: split(r2.json).cart, corrected: true, error: { code: 'mismatch', reverted: true, message: 'line moved' } };
    }
    return { cart, error: { code: 'mismatch', message: 'plan not applied' } };
  };
  // One change.js request for a line: quantity steps post the key, plan steps resolve the line against `base` (else a fresh GET)
  const changeLine = async (ref, s, sections, base, onBody) => {
    const plan = 'sellingPlan' in s;
    const target = plan ? normPlan(s.sellingPlan) : undefined;
    let t = null;
    let body;
    if (!plan && ref.key) body = { id: ref.key, quantity: Number(s.quantity) };
    else {
      base = base || (await getCart());
      t = resolve(ref, base);
      if (!t) return failure('not_found');
      body = plan ? { line: t.line, quantity: s.quantity != null ? Number(s.quantity) : t.item.quantity, selling_plan: planParam(target) } : { id: t.key, quantity: Number(s.quantity) };
    }
    if (onBody) onBody(body, t);
    let r = await post('cart_change', body, sections);
    if (!plan && r.status === 400) {
      const t2 = resolve(ref, await getCart());
      if (!t2) return failure('not_found');
      body.id = t2.key;
      r = await post('cart_change', body, sections);
    }
    if (r.error) return r;
    const out = Object.assign({ ok: true, status: r.status, t, body, plan, target, error: null }, split(r.json));
    if (plan) {
      const v = await verifyPlan(t, body, out.cart, base, target);
      Object.assign(out, { cart: v.cart, error: v.error || null, ok: !v.error });
      if (v.corrected) out.sections = null;
    }
    return out;
  };
  const change = (ref, changes, opts) =>
    write('change', opts, async (ctx) => {
      ref = ref || {};
      changes = changes || {};
      opts = opts || {};
      const release = 'sellingPlan' in changes ? lock() : null;
      try {
        const x = await changeLine(ref, changes, ctx.sections, null, (body, t) => ctx.event(body.quantity === 0 && !('selling_plan' in body) ? 'remove' : 'update', { lines: [{ id: body.id || t.key, quantity: body.quantity }] }));
        if (!x.cart) return x;
        const props = ref.properties !== undefined ? ref.properties : x.t ? x.t.item.properties : undefined;
        const near = { variantId: ref.variantId != null ? ref.variantId : x.t && x.t.item.variant_id, properties: props, sellingPlanId: x.plan ? x.target : ref.sellingPlanId };
        const after = x.plan ? resolve(near, x.cart) : resolve({ key: x.body.id }, x.cart) || (x.body.quantity > 0 ? resolve(near, x.cart) : null);
        const exp = opts.expect;
        const item = after && after.item;
        if (
          !x.error &&
          exp &&
          (exp.quantity === 0
            ? !!item
            : !item || (exp.variantId != null && String(item.variant_id) !== String(exp.variantId)) || (exp.sellingPlanId !== undefined && planOf(item) !== normPlan(exp.sellingPlanId)) || (exp.quantity != null && item.quantity !== Number(exp.quantity)))
        )
          x.error = { code: 'mismatch', message: 'unexpected result' };
        return { ok: !x.error, status: x.status, cart: x.cart, sections: x.sections, line: after ? after.line : undefined, key: after ? after.key : undefined, error: x.error };
      } finally {
        if (release) release();
      }
    });
  const update = (payload, opts) =>
    write('update', opts, async (ctx) => {
      let p = payload;
      if (typeof p === 'function') {
        const cart = await getCart();
        p = p(cart);
        if (p == null) return { ok: true, skipped: true, status: 0, cart, sections: null, error: null };
      }
      const body = {};
      ['updates', 'attributes', 'note', 'discount'].forEach((k) => p && p[k] !== undefined && (body[k] = p[k]));
      const u = body.updates;
      if (u && !Array.isArray(u)) ctx.event('update', { lines: Object.keys(u).map((k) => (k.indexOf(':') > -1 ? { id: k, quantity: Number(u[k]) } : { merchandiseId: gid(k), quantity: Number(u[k]) })) });
      if ('note' in body) ctx.event(0, { note: body.note }, 'CartNoteUpdateEvent');
      if ('attributes' in body) ctx.event(0, { attributes: body.attributes }, 'CartAttributesUpdateEvent');
      if ('discount' in body) ctx.event(0, { discountCodes: String(body.discount || '').split(',').filter(Boolean) }, 'CartDiscountUpdateEvent');
      const r = await post('cart_update', body, ctx.sections);
      return r.error ? r : Object.assign({ ok: true, status: r.status, error: null }, split(r.json));
    });
  const add = (items, opts) =>
    write('add', opts, async (ctx) => {
      const list = (items || []).map((i) => {
        const o = { id: i.id, quantity: Number(i.quantity) || 1 };
        if (i.properties !== undefined) o.properties = i.properties;
        if (i.selling_plan != null) o.selling_plan = i.selling_plan;
        if (i.parent_id != null) o.parent_id = i.parent_id;
        return o;
      });
      ctx.event('add', { lines: list.map((i) => ({ merchandiseId: gid(i.id), quantity: i.quantity })) });
      const r = await post('cart_add', { items: list }, ctx.sections);
      return r.error ? r : { ok: true, status: r.status, cart: await getCart(), sections: r.json.sections || null, error: null };
    });
  const clear = (opts) =>
    write('clear', opts, async (ctx) => {
      ctx.event('remove', { lines: ((lastCart && lastCart.items) || []).map((i) => ({ id: i.key, quantity: 0 })) });
      const r = await post('cart_clear', {}, ctx.sections);
      return r.error ? r : Object.assign({ ok: true, status: r.status, error: null }, split(r.json));
    });
  const batch = async (steps, opts) => {
    opts = opts || {};
    steps = steps || [];
    const source = sourceOf(opts);
    loadSE();
    const ctx = makeCtx(opts);
    const st = { done: [], failed: [], cart: null, sections: null, fin: false };
    let list = [];
    att(() => ctx.event('update', { lines: steps.map((s) => (s.ref && s.ref.key ? { id: s.ref.key, quantity: Number(s.quantity) } : { merchandiseId: gid(s.ref && s.ref.variantId), quantity: Number(s.quantity) })) }));
    const step = async (i, fresh) => {
      const s = steps[i] || {};
      const ref = s.ref || {};
      const x = await changeLine(ref, s, i === steps.length - 1 ? ctx.sections : null, fresh ? null : st.cart);
      if (x.cart) Object.assign(st, { cart: x.cart, sections: x.sections });
      if (x.error) st.failed.push({ ref, error: x.error });
      else st.done.push(ref);
      return !x.error;
    };
    const finish = async () => {
      st.fin = true;
      if (opts.render === false) return;
      if (!st.cart) st.cart = await getCart();
      const state = { sections: st.failed.length ? null : st.sections, cart: st.cart, result: { ok: !st.failed.length, done: st.done, failed: st.failed, cart: st.cart } };
      list = (await finishWrite(ctx, opts, source, state)) || [];
    };
    begin();
    try {
      const q = engineQueue();
      if (q) {
        for (let i = 0; i < steps.length; i++) {
          const ok = await q.enqueue(async () => {
            const res = await step(i, true);
            if (res && i === steps.length - 1) await finish();
            return res;
          });
          if (!ok) break;
        }
        if (!st.fin) await q.enqueue(finish);
      } else {
        await enqueue(async () => {
          const release = lock();
          try {
            for (let i = 0; i < steps.length && (await step(i, false)); i++);
            await finish();
          } finally {
            release();
          }
        }, { label: source });
      }
    } catch (e) {
      err(e);
      if (!st.failed.length) st.failed.push({ ref: null, error: { code: 'network', message: msg(e) } });
      // earlier steps may have changed the cart: render what it is now (never throws)
      if (!st.fin && st.done.length) await att(() => (engineQueue() || { enqueue })['enqueue'](finish).catch(err), null);
    } finally {
      const fail = st.failed[0] && st.failed[0].error;
      closeWrite(ctx, opts, source, 'batch', { ok: !fail, cart: st.cart, error: fail || null }, list);
      end();
    }
    return { ok: !st.failed.length, done: st.done, failed: st.failed, cart: st.cart || (await getCart()) };
  };
  // #endregion

  // #region surfaces and render
  const surfaces = [];
  const registerSurface = (s) => {
    if (!s || !s.id) return () => {};
    const i = surfaces.findIndex((x) => x.id === s.id);
    surfaces.splice(i > -1 ? i : surfaces.length, i > -1 ? 1 : 0, s);
    return () => surfaces.indexOf(s) > -1 && surfaces.splice(surfaces.indexOf(s), 1);
  };
  const idsOf = (list) => [...new Set([].concat(...list.map((s) => s.sections() || [])))];
  const sectionIds = () => idsOf(surfaces.filter(present));
  const rootOf = (id) => (id === 'drawer' ? qs('cart-drawer') : id === 'page' ? qs('cart-items') : qs('[data-cart-surface="' + id + '"]'));
  let renderSource = null;
  const render = async (state, o) => {
    o = o || {};
    let list = surfaces.filter((s) => present(s) && (!o.surfaces || o.surfaces.indexOf(s.id) > -1));
    let secs;
    if (!state) state = { sections: (secs = (await getSections(idsOf(list))) || {}), cart: null };
    else {
      secs = Object.assign({}, state.sections || {});
      list = list.filter((s) => (s.sections() || []).every((id) => id in secs));
      const nul = idsOf(list).filter((id) => secs[id] == null);
      if (nul.length) Object.assign(secs, (await getSections(nul)) || {});
    }
    const done = [];
    for (const s of list) {
      if ((s.sections() || []).some((id) => secs[id] == null)) continue;
      renderSource = o.source || null;
      try {
        await s.render({ sections: secs, cart: state.cart || null }, { source: o.source, rendered: done.slice() });
        done.push(s.id);
      } catch (e) {
        err(e);
      }
      if (s.id === 'drawer') flush('drawer');
      setTimeout(() => (renderSource = null), 0);
    }
    const el = done.length && o.focus && safe(() => o.focus(rootOf(done[0]), o.result));
    if (el && el.focus) {
      const dr = qs('cart-drawer');
      if (dr && dr.contains(el)) focusIn(dr, el);
      else att(() => el.focus());
    }
    if (o.publish) publishCart(state.cart || lastCart, o.source, done);
    if (o.fromWrite && !done.length && qs('cart-drawer, cart-items, cart-page')) location.reload();
    return done;
  };
  registerSurface({
    id: 'drawer',
    isPresent: () => !!att(() => typeof qs('cart-drawer').renderContents === 'function'),
    sections: () => ['cart-drawer', 'cart-icon-bubble'],
    render(state) {
      const el = qs('cart-drawer');
      el.renderContents({ sections: state.sections }, true);
      el.classList.toggle('is-empty', !!qs('#CartDrawer .drawer__inner-empty'));
    },
  });
  const pageList = () => {
    const ci = qs('cart-items');
    const mi = d.getElementById('main-cart-items');
    const mf = d.getElementById('main-cart-footer');
    const l = [
      ['main-cart-items', (ci && ci.dataset.sectionId) || (mi && mi.dataset.id), '.js-contents'],
      ['cart-icon-bubble', 'cart-icon-bubble', '.shopify-section'],
      ['cart-live-region-text', 'cart-live-region-text', '.shopify-section'],
      ['main-cart-footer', mf && mf.dataset.id, '.js-contents'],
    ];
    return l.filter((x) => x[1]);
  };
  registerSurface({
    id: 'page',
    isPresent: () => !!att(() => typeof qs('cart-items').getSectionInnerHTML === 'function' && d.getElementById('main-cart-items')),
    sections: () => pageList().map((x) => x[1]),
    render(state, o) {
      const ci = qs('cart-items');
      pageList().forEach(([id, sec, s]) => {
        const wr = d.getElementById(id);
        const html = wr && !(id === 'cart-icon-bubble' && (o.rendered || []).indexOf('drawer') > -1) ? att(() => ci.getSectionInnerHTML(state.sections[sec], s), null) : null;
        if (html != null) (qs(s, wr) || wr).innerHTML = html;
      });
      const recs = [];
      pageObs.forEach((m) => recs.push(...m.takeRecords()));
      preserve(recs);
      const n = state.cart && state.cart.item_count;
      if (n != null) [ci, d.getElementById('main-cart-footer'), qs('cart-drawer')].forEach((el) => el && el.classList.toggle('is-empty', n === 0));
      if (!qs('cart-drawer')) {
        safe(() => typeof checkShrineGifts === 'function' && typeof shouldCheckShrineGifts !== 'undefined' && shouldCheckShrineGifts && checkShrineGifts(true));
        safe(() => typeof validateCartGifts === 'function' && validateCartGifts(true));
      }
      observePage();
      emitRender({ surface: 'page', root: d.getElementById('main-cart-items'), source: o.source });
    },
  });
  // #endregion

  // #region render hooks
  const emitRender = (o) => {
    o = o || {};
    const root = o.root;
    if (root) att(() => qsa('details[data-preserve] > summary[aria-expanded]', root).forEach((s) => s.setAttribute('aria-expanded', String(s.parentElement.open))));
    scan(root);
    call('render', { surface: o.surface, root, source: o.source });
    if (designMode && provided.editor && provided.editor.run) safe(() => provided.editor.run({ surface: o.surface, root }));
    if (o.announce !== false) announceRender(o.surface, root);
  };
  const scrolls = {};
  on(d, 'scroll', (e) => att(() => e.target.matches('[data-preserve][id]') && (scrolls[e.target.id] = e.target.scrollLeft)), true);
  const eachPreserved = (n, fn) => {
    if (!n || n.nodeType !== 1) return;
    if (n.matches('[data-preserve][id]')) fn(n);
    qsa('[data-preserve][id]', n).forEach(fn);
  };
  const preserve = (recs) => {
    const old = {};
    recs.forEach((r) => r.removedNodes.forEach((n) => eachPreserved(n, (el) => (old[el.id] = { open: el.hasAttribute('open'), checked: el.checked, value: el.value, sl: scrolls[el.id] || el.scrollLeft }))));
    if (!Object.keys(old).length) return;
    recs.forEach((r) =>
      r.addedNodes.forEach((n) =>
        eachPreserved(n, (el) => {
          const s = old[el.id];
          if (!s) return;
          if (el.tagName === 'DETAILS') el.toggleAttribute('open', s.open);
          else if (el.type === 'checkbox' || el.type === 'radio') el.checked = !!s.checked;
          else if (s.value !== undefined && el.type !== 'file' && 'value' in el) el.value = s.value;
          if (s.sl) requestAnimationFrame(() => (el.scrollLeft = s.sl));
        })
      )
    );
  };
  const pend = {};
  const flush = (surface) => {
    const p = pend[surface];
    if (!p) return;
    clearTimeout(p.timer);
    delete pend[surface];
    if (surface === 'drawer') {
      attachInner();
      fitAttach();
      fitUpdate();
      if (toastPos) toastPos();
    } else observePage();
    emitRender({ surface, root: d.getElementById(surface === 'drawer' ? 'CartDrawer' : 'main-cart-items'), source: p.source });
  };
  const mark = (surface, src) => {
    const p = pend[surface];
    if (!p) pend[surface] = { source: renderSource || src || 'observer', timer: setTimeout(() => flush(surface), 0) };
    else if (!renderSource && src && p.source === 'observer') p.source = src;
  };
  const swap = (surface, recs) => {
    if (surface === 'page' || !has('preserveState')) preserve(recs);
    mark(surface);
  };
  const observe = (el, fn, opt) => {
    const m = new MutationObserver(fn);
    m.observe(el, opt || { childList: true });
    return m;
  };
  let pageObs = [];
  const observePage = () => {
    pageObs.forEach((m) => m.disconnect());
    pageObs = qsa('#main-cart-items .js-contents, #main-cart-footer .js-contents, cart-items').map((el) => observe(el, (r) => swap('page', r)));
  };
  // #endregion

  // #region drawer: open, close, aria, inert, fit
  let drawerEl = null;
  let drawerObs = [];
  let innerObs = null;
  let isOpen = false;
  let cartLink = null;
  let inerted = [];
  const attachInner = () => {
    if (innerObs) innerObs.disconnect();
    const inner = drawerEl && qs('.drawer__inner', drawerEl);
    innerObs = inner ? observe(inner, (r) => swap('drawer', r)) : null;
  };
  const setInert = (v) => {
    if (designMode || !drawerEl || !v === !inerted.length) return;
    if (v) {
      inerted = Array.from(d.body.children).filter((c) => !(c.contains(drawerEl) || c.inert || /^(SCRIPT|STYLE|LINK|TEMPLATE|NOSCRIPT)$/.test(c.tagName) || c.matches('[data-cart-toast-region], [data-cart-announcer]')));
      inerted.forEach((c) => (c.inert = true));
      return;
    }
    inerted.forEach((c) => (c.inert = false));
    inerted = [];
    const a = d.activeElement;
    const back = drawerEl.activeElement || cartLink;
    if ((!a || a === d.body || !a.isConnected || (!drawerEl.classList.contains('active') && drawerEl.contains(a))) && back && back.focus) back.focus();
  };
  const setExpanded = (v) => cartLink && cartLink.setAttribute('aria-expanded', String(v));
  const opened = () => {
    isOpen = true;
    setExpanded(true);
    setInert(true);
    fit.schedule();
    loadSE().then(() => att(() => qs('#CartDrawer s-view-event').dispatchViewEvent()));
    call('open', {});
  };
  const closed = () => {
    isOpen = false;
    setInert(false);
    setExpanded(false);
    att(() => qs('[data-cart-toast-region="drawer"]').shrineToast.close('close'));
    call('close', {});
  };
  on(d, 'shrine:cart:open', () => !isOpen && opened());
  on(d, 'shrine:cart:close', () => isOpen && closed());
  on(d, 'shrine:cart:rendered', (e) => mark((e.detail || {}).surface === 'page' ? 'page' : 'drawer', (e.detail || {}).source));
  const fit = {
    schedule() {
      clearTimeout(fit.t);
      fit.t = setTimeout(fitUpdate, 30);
    },
  };
  let fitRO = null;
  let fitIO = null;
  const parts = () => {
    const inner = drawerEl && qs('.drawer__inner', drawerEl);
    return [inner, inner && qs(':scope > .drawer__footer', inner), inner && qs(':scope > cart-compact-bar', inner)];
  };
  const fitAttach = () => {
    if (!drawerEl || !drawerEl.hasAttribute('data-keep-checkout')) return;
    if (!fitRO && w.ResizeObserver) fitRO = new ResizeObserver(() => fit.schedule());
    if (fitRO) {
      fitRO.disconnect();
      parts()
        .slice(0, 2)
        .forEach((el) => el && fitRO.observe(el));
    }
    fit.schedule();
  };
  const fitUpdate = () => {
    const dr = drawerEl;
    if (!dr || !dr.hasAttribute('data-keep-checkout')) return;
    const [inner, foot, bar] = parts();
    if (fitIO) fitIO.disconnect();
    if (!foot || dr.classList.contains('is-empty')) {
      delete dr.dataset.cartFit;
      if (bar) bar.hidden = true;
      return;
    }
    const sheet = dr.classList.contains('cart-drawer--mobile-bottom') && w.matchMedia('(max-width: 749px)').matches;
    const ref = sheet ? parseFloat(getComputedStyle(inner).maxHeight) || w.innerHeight * 0.9 : inner.clientHeight;
    const mode = foot.offsetHeight > ref * 0.5 ? 'scroll' : 'pinned';
    dr.dataset.cartFit = mode;
    if (!bar) return;
    bar.hidden = mode === 'pinned';
    if (bar.hidden) return;
    const h = bar.offsetHeight;
    dr.style.setProperty('--cart-compact-bar-height', h + 'px');
    const btn = qs('#CartDrawer-Checkout, [name="checkout"]', foot);
    bar.classList.remove('is-hidden');
    if (!btn || !w.IntersectionObserver) return;
    fitIO = new IntersectionObserver(
      (en) => {
        const e = en[en.length - 1];
        bar.classList.toggle('is-hidden', e.isIntersecting && e.intersectionRatio >= 0.99);
        if (toastPos) toastPos();
      },
      { root: inner, rootMargin: '0px 0px -' + h + 'px 0px', threshold: [0, 0.99, 1] }
    );
    fitIO.observe(btn);
  };
  const initDrawer = (el) => {
    if (!el) return;
    drawerEl = el;
    drawerObs.forEach((m) => m.disconnect());
    const cd = qs('#CartDrawer', el);
    drawerObs = [
      observe(el, () => {
        const a = el.classList.contains('active');
        if (!has('events') && a !== isOpen) a ? opened() : closed();
      }, { attributes: true, attributeFilter: ['class'] }),
    ];
    if (cd) drawerObs.push(observe(cd, (r) => swap('drawer', r)));
    attachInner();
    let link = qs('#cart-icon-bubble');
    if (link && link.tagName === 'DIV') link = link.closest('.header__icon--cart');
    cartLink = link;
    if (link && el.id) link.setAttribute('aria-controls', el.id);
    isOpen = false;
    if (el.classList.contains('active')) opened();
    else setExpanded(false);
    if (!el.shrineCore) {
      el.shrineCore = 1;
      const lift = (e, ok) => ok && !(e.target.closest && e.target.closest('[data-cart-toast]')) && setInert(false);
      on(el, 'keyup', (e) => lift(e, e.key === 'Escape' || e.code === 'Escape'), true);
      on(el, 'click', (e) => lift(e, e.target.closest && e.target.closest('#CartDrawer-Overlay, .drawer__close')), true);
    }
    fitAttach();
  };
  if (w.customElements && !customElements.get('cart-compact-bar')) {
    customElements.define(
      'cart-compact-bar',
      class extends HTMLElement {
        connectedCallback() {
          if (this.shrineBound) return;
          this.shrineBound = 1;
          on(this, 'click', (e) => {
            const btn = e.target.closest && e.target.closest('.cart-compact-bar__checkout');
            if (!btn || e.defaultPrevented || (btn.form && !btn.form.checkValidity())) return;
            const sp = qs('.loading-overlay__spinner', btn);
            const show = (v) => {
              btn.classList.toggle('loading', v);
              if (sp) sp.classList.toggle('hidden', !v);
            };
            show(true);
            setTimeout(() => location.pathname.indexOf('/checkout') < 0 && show(false), 8000);
          });
        }
      }
    );
  }
  // #endregion

  // #region product-form bridge, standard actions
  const pfRecords = new Map();
  on(d, 'product-form:before-add', (e) => {
    const pf = e.target;
    if (has('standardEvents') || !pf || !pf.querySelector) return;
    Promise.resolve().then(() => {
      if (e.defaultPrevented) return;
      const lines = [];
      const items = {};
      let id = null;
      let qty = null;
      att(() => {
        for (const [k, v] of new FormData(qs('form', pf) || pf)) {
          const m = /^items\[(\d+)\]\[(id|quantity)\]$/.exec(k);
          if (m) (items[m[1]] = items[m[1]] || {})[m[2]] = v;
          else if (k === 'id') id = v;
          else if (k === 'quantity') qty = v;
        }
      });
      Object.keys(items)
        .sort((a, b) => a - b)
        .forEach((k) => items[k].id && lines.push({ merchandiseId: gid(items[k].id), quantity: Number(items[k].quantity) || 1 }));
      if (!lines.length && id) lines.push({ merchandiseId: gid(id), quantity: Number(qty) || 1 });
      const context = pf.closest('cart-drawer') ? 'dialog' : pf.closest('[data-cart-root], cart-items') ? 'cart' : 'product';
      const old = pfRecords.get(pf);
      if (old) old.end();
      const rec = seRecord('CartLinesUpdateEvent', { action: 'add', context, lines }, pf);
      const ent = {
        end: (o) => {
          clearTimeout(ent.timer);
          if (pfRecords.get(pf) === ent) pfRecords.delete(pf);
          if (o) rec.settle(o);
          else getCart().then((cart) => rec.settle({ cart }));
        },
      };
      ent.timer = setTimeout(() => ent.end(), 10000);
      pfRecords.set(pf, ent);
    });
  });
  on(d, 'product-form:added', (e) => att(() => pfRecords.get(e.target).end()));
  on(d, 'product-form:error', (e) => {
    const ent = pfRecords.get(e.target);
    const x = e.detail || {};
    if (ent) ent.end(x.error && !x.response ? { network: x.error.message || x.error.name || 'network' } : { decline: (x.response && (x.response.description || x.response.message)) || 'error', cart: lastCart });
  });
  const actions = {
    eventTarget: () => qs('cart-drawer') || qs('cart-page, cart-items') || null,
    handleUpdate: (def, payload, options) =>
      requireKey('extras').then((x) => (x && x.handleUpdate ? x.handleUpdate(def, payload, options, { enqueue, render, getCart, publishCart, fire }) : def())),
  };
  // #endregion

  // #region public API, init
  const editorRender = () => att(() => provided.editor.renderNotices());
  const notices = {
    list: new Map(),
    set(code, o) {
      if (designMode && code) notices.list.set(code, Object.assign({ code }, o));
      editorRender();
    },
    clear(code) {
      notices.list.delete(code);
      editorRender();
    },
  };
  const editor = {
    checks: new Map(),
    registerCheck: (name, fn) => designMode && name && typeof fn === 'function' && editor.checks.set(name, fn),
    checkDiscounts: (lines, o) => requireKey('editor').then((api) => (api && api.checkDiscounts ? api.checkDiscounts(lines, o) : { lines: [], currency: null, warnings: [], errors: ['unavailable'] })),
  };
  const SC = (w.ShrineCart = {
    version: 1,
    config,
    t,
    has,
    require: requireKey,
    provide,
    onOpen: hook('open'),
    onClose: hook('close'),
    onRender: hook('render'),
    emitRender,
    root: (el) => (el && el.closest ? el.closest('.cart-root') : null),
    surface: (el) => att(() => SC.root(el).getAttribute('data-cart-surface'), null),
    announce,
    toast,
    money,
    keywords,
    trapFocus: focusIn,
    actions,
    notices,
    editor,
  });
  w.ShrineCartRequests = {
    version: 1,
    isBusy,
    whenIdle,
    enqueue,
    getCart,
    resolve,
    change,
    update,
    add,
    clear,
    batch,
    sections: sectionIds,
    render: (state, o) => render(state, o).catch((e) => (err(e), [])),
    registerSurface,
  };
  let inited = false;
  const init = () => {
    if (inited) return;
    inited = true;
    scan(d);
    moneyInit();
    initDrawer(qs('cart-drawer'));
    observePage();
    if (qsa('s-view-event').some((el) => !el.closest('#CartDrawer'))) loadSE();
    on(w, 'resize', () => {
      fit.schedule();
      if (toastPos) toastPos();
    });
    const reinit = () => {
      const el = qs('cart-drawer');
      if (el && el !== drawerEl) initDrawer(el);
    };
    const sec = d.getElementById('shopify-section-cart-drawer');
    if (sec) observe(sec, reinit);
    if (designMode) {
      on(d, 'shopify:section:load', () => {
        reinit();
        observePage();
        scan(d);
      });
    }
  };
  if (d.readyState === 'complete') init();
  else {
    on(d, 'DOMContentLoaded', init);
    on(w, 'load', init);
  }
  // #endregion
})();

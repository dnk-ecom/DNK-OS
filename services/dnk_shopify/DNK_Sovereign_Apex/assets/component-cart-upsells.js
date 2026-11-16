/* Shrine PRO - cart upsells (loader key "upsells"). main.js drives the drawer's engine cards; this file keeps their
   switches showing the cart (T2), ARIA and recovery, and runs T14, recommendations, order, V2 prices and focus.
   Theme cards, price bands, per-item add-ons and cart attributes: component-cart-upsells-cards.js, loaded on demand. */
(() => {
  if (window.ShrineCartUpsells) return;
  const d = document;
  const w = window;
  const TOGGLE = 'cart-drawer-upsell[data-toggle="true"]';
  const THEME_TOGGLE = 'cart-upsell-item[data-ups-kind="toggle"]';
  const DECL = 'shrine-cart-upsells-declined';
  const RECS = 'shrine-cart-recs:';
  const CARDS = 'cart-upsell-item, [data-ups-bands], [data-ups-attribute]';
  const core = () => w.ShrineCart || {};
  const qsa = (s, r) => [...(r || d).querySelectorAll(s)];
  const own = (r, s) => (r.matches && r.matches(s) ? [r] : []).concat(qsa(s, r));
  const num = (v) => Number(v) || 0;
  const intents = new Map();
  const recent = {};
  const filled = new WeakMap();
  const watched = new WeakSet();
  const loading = {};
  let skipUntil = 0;
  let mem = null;

  // ---------------------------------------------------------------- cart facts, storage
  const rootOf = (el) => (el && el.closest ? el.closest('cart-drawer, .cart-root, [data-cart-root]') : null);
  const roots = () => [...new Set(qsa('cart-drawer, .cart-root'))];
  const handleOf = (l) => (/(?:^|\s)cart-item--product-(\S+)/.exec(l.className || '') || [])[1] || '';
  const inCart = (root, h) => !!(h && root && root.querySelector('.cart-item--product-' + h));
  const isFilled = (root) => {
    const addons = new Set(qsa(TOGGLE + ', cart-drawer-gift, ' + THEME_TOGGLE, root).map((el) => el.dataset.handle));
    return qsa('.cart-item', root).some((l) => !/(^|\s)(cart-hidden|reward-gift|qb-gift)(\s|$)/.test(l.dataset.lineFlags || '') && !addons.has(handleOf(l)));
  };
  // Quantity "Match …" add-ons (theme cards): the cart's quantity of every other product, or of the chosen ones, counted
  // from the printed lines. Other add-ons never count, so two matched add-ons can't raise each other. Lines without
  // these attributes (older cart markup): the count the card printed.
  const matchTarget = (c, root) => {
    const lines = qsa('.cart-item[data-line-key][data-product-id]', root);
    if (!lines.length) return num(c.dataset.upsTarget);
    const only = c.dataset.upsMatchProducts;
    const addons = new Set(qsa('[data-ups-kind="toggle"][data-handle], cart-drawer-gift[data-handle]', root).map((el) => el.dataset.handle));
    return lines.reduce((n, l) => {
      const f = l.dataset.lineFlags || '';
      if (/(^|\s)(free|gift-card|qb-gift|reward-gift)(\s|$)/.test(f) || l.dataset.productId === c.dataset.productId) return n;
      if (only) return only.indexOf(',' + l.dataset.productId + ',') > -1 ? n + num(l.dataset.quantity) : n;
      return /(^|\s)(cart-hidden|nested)(\s|$)/.test(f) || addons.has(l.dataset.handle) ? n : n + num(l.dataset.quantity);
    }, 0);
  };
  // the quantity an add-on goes in with: a matched one the count (at least 1 when it comes with the cart's first
  // product), a quantity selector its value, else 1
  const startQuantity = (c, root, first) => {
    if (c.dataset.upsPerItem) return first ? Math.max(1, matchTarget(c, root)) : matchTarget(c, root);
    const i = c.dataset.upsQtyMode === 'selector' && c.querySelector('[data-ups-quantity]');
    return i ? Math.max(1, Math.round(num(i.value)) || 1) : 1;
  };
  const inert = (c) => !!c.closest('[data-ups-placeholder]') || c.classList.contains('cart-upsell--soldout');
  const store = (k, v) => {
    try {
      if (v === undefined) return JSON.parse(sessionStorage.getItem(k) || 'null');
      if (v) sessionStorage.setItem(k, JSON.stringify(v));
      else sessionStorage.removeItem(k);
    } catch (e) {}
    return null;
  };
  const declines = () => {
    const l = store(DECL);
    return Array.isArray(l) ? l : [];
  };
  const decline = (h, on) => {
    const l = declines().filter((x) => x !== h);
    store(DECL, on ? l.concat(h) : l.length ? l : null);
  };

  // ---------------------------------------------------------------- switch state, prices
  const aria = (c) => {
    const ctl = c.querySelector('[data-ups-part="control"][aria-checked]');
    const on = c.dataset.selected === 'true' ? 'true' : 'false';
    if (ctl && ctl.getAttribute('aria-checked') !== on) ctl.setAttribute('aria-checked', on);
    if (c.matches('cart-upsell-item')) return;
    if (!c.classList.contains('cart-upsell--soldout') && c.querySelector('.upsell-toggle-btn[disabled]')) c.setAttribute('aria-busy', 'true');
    else c.removeAttribute('aria-busy');
  };
  const setSel = (c, on) => {
    const v = on ? 'true' : 'false';
    if (c.dataset.selected !== v) c.dataset.selected = v;
    aria(c);
  };
  const money = (x) => (core().money ? core().money.format(x) : (x / 100).toFixed(2));
  // presentment units per store unit (1 = same currency); 0 = unknown
  const rate = (shop) => {
    const r = core().money ? core().money.rate(shop) : null;
    if (r && r.rate > 0) return r.rate;
    const cur = w.Shopify && w.Shopify.currency;
    return !cur || !cur.active ? 0 : cur.active === shop ? 1 : num(cur.rate);
  };
  const variants = (c) => {
    const s = c.querySelector('script[data-ups-variants]') || c.querySelector('script[type="application/json"]');
    try {
      const l = JSON.parse((s && s.textContent) || '[]');
      return Array.isArray(l) ? l : [];
    } catch (e) {
      return [];
    }
  };
  // a variant's price, compare price and savings, with the card's display-only offer
  const paint = (c, v) => {
    const o = (c.dataset.upsOffer || '1:0').split(':');
    const price = Math.round(num(v.price) * Number(o[0]) - num(o[1]));
    const cmp = Math.max(num(v.compare_at_price), num(v.price));
    const reg = c.querySelector('.upsell__price .regular-price');
    const cp = c.querySelector('.upsell__price .compare-price');
    if (reg) reg.textContent = money(price);
    if (cp) {
      cp.textContent = money(cmp);
      cp.classList.toggle('hidden', !(cmp > price));
    }
    c.dataset.upsPrice = price;
    const sv = c.querySelector('.cart-upsell__savings');
    const host = c.closest('[data-ups-savings-text]');
    const save = num(v.compare_at_price) - num(v.price);
    if (!sv || !host) return;
    sv.hidden = !(save > 0);
    if (save > 0) sv.textContent = host.dataset.upsSavingsText.replace('[amount]', money(save)).replace('[percentage]', Math.round((save * 100) / num(v.compare_at_price)) + '%');
  };
  // V2 engine cards: fixParsedHtml copied the shopper's variant back into a fresh render
  const resync = (scope) =>
    own(scope, 'cart-drawer-upsell[data-ups-initial-id]').forEach((c) => {
      const v = c.dataset.id !== c.dataset.upsInitialId && variants(c).find((x) => String(x.id) === c.dataset.id);
      if (v) paint(c, v);
    });

  // ---------------------------------------------------------------- T14: subtotal rules in another currency
  const reveal = (scope) =>
    own(scope, '[data-ups-placeholder="pending"]').forEach((wrap) => {
      const r = rate(wrap.dataset.upsShopCurrency);
      const limit = num(wrap.dataset.upsThreshold) * r;
      const total = num(wrap.dataset.upsCartTotal);
      if (!r || !(wrap.dataset.upsCondition === 'subtotal_less_than' ? total < limit : total > limit)) return;
      wrap.hidden = false;
      wrap.removeAttribute('data-ups-placeholder');
      qsa('[data-ups-uid]', wrap).forEach((c) => {
        if (inert(c)) return;
        const st = c.previousElementSibling;
        if (st && st.matches('style[data-ups-hide-lines]')) st.media = 'all';
        if (c.dataset.upsSelShown) setSel(c, c.dataset.upsSelShown === 'true');
      });
    });

  // ---------------------------------------------------------------- free-shipping order, one at a time (never in a mounted slider)
  const order = (host, scope) => {
    if (host.dataset.upsOrder !== 'gap' || scope.querySelector('.splide.is-initialized')) return;
    const G = w.ShrineCartGoals;
    const k = host.dataset.goalKind;
    const cents = num(host.dataset.goalCents);
    const r = rate(host.dataset.goalCurrency);
    const g = G && G.toPresentment ? G.toPresentment({ kind: k, cents, currency: host.dataset.goalCurrency }) : k === 'local' ? cents : k === 'shop' && r ? Math.round(cents * r) : null;
    const need = g == null ? 0 : g - num(host.dataset.upsGoalTotal);
    const rank = (p) => (p >= need ? p : 1e12 - p);
    if (need > 0)
      qsa('[data-ups-kind="add"]', scope)
        .map((c, i) => ({ el: c.closest('.splide__slide') || c, p: num(c.dataset.upsPrice), i }))
        .sort((a, b) => rank(a.p) - rank(b.p) || a.i - b.i)
        .forEach((x) => x.el.parentNode.appendChild(x.el));
    if (host.dataset.upsOne === 'true') qsa('[data-ups-kind="add"]', scope).slice(1).forEach((c) => (c.closest('.splide__slide') || c).remove());
  };

  // ---------------------------------------------------------------- recommendations (05 §7.4)
  const trim = (host, frag) => {
    const hs = host.dataset.upsCartHandles || '';
    const cards = () => qsa('[data-ups-uid]', frag);
    cards().forEach((c) => hs.indexOf(',' + c.dataset.handle + ',') > -1 && (c.closest('.splide__slide') || c).remove());
    order(host, frag);
    cards().slice(host.dataset.upsOne === 'true' ? 1 : num(host.dataset.upsLimit) || 10).forEach((c) => (c.closest('.splide__slide') || c).remove());
    return cards().length;
  };
  const put = (host, frag) => {
    const n = trim(host, frag);
    if (!n) return false;
    host.querySelector('[data-ups-list]').replaceChildren(frag);
    host.dataset.upsRecsState = 'done';
    if (host.dataset.upsV === '1') {
      const st = host.dataset.upsStacking;
      host.classList.toggle('upsells-container--stacked-columns', n > 1 && st === 'column');
      host.classList.toggle('side-margins-negative', n > 1 && st === 'slider');
      host.dataset.count = n;
      host.style.setProperty('--item-count', n > 3 ? (n % 2 === 0 && n % 3 ? 2 : 3) : n);
    }
    return true;
  };
  // nothing to show: hidden ("empty" also gives the theme editor its notice, component-cart-upsells-editor.js)
  const fallback = (host) => {
    const t = host.querySelector('template[data-ups-fallback]');
    if (t && put(host, t.content.cloneNode(true))) return;
    host.hidden = true;
    host.dataset.upsRecsState = 'empty';
  };
  const insert = (host, html) => {
    const t = d.createElement('template');
    t.innerHTML = html || '';
    if (!put(host, t.content)) fallback(host);
  };
  // at most 10 cached urls: the oldest go
  const cache = (key, val) => {
    try {
      const old = Object.keys(sessionStorage).filter((k) => !k.indexOf(RECS) && k !== key);
      old.sort((a, b) => (store(a) || {}).t - (store(b) || {}).t).slice(0, Math.max(0, old.length - 9)).forEach((k) => store(k, null));
    } catch (e) {}
    store(key, val);
  };
  const loadRecommendations = (host) => {
    if (!host || !host.isConnected || host.dataset.upsRecsState || host.closest('[data-ups-placeholder="condition"]')) return;
    if (!host.dataset.upsSeed) return fallback(host);
    const url = host.dataset.upsRecsUrl + '?section_id=' + encodeURIComponent(host.dataset.upsSection) + '&product_id=' + host.dataset.upsSeed + '&limit=10&intent=' + host.dataset.upsIntent;
    const key = RECS + url;
    const cur = host.dataset.upsCurrency;
    const hit = store(key);
    const show = (map) => host.isConnected && (map[host.id] ? insert(host, map[host.id].html) : fallback(host));
    if (hit && hit.v === 1 && hit.cur === cur && Date.now() - hit.t < 18e5) return show(hit.map);
    host.dataset.upsRecsState = 'loading';
    (loading[url] =
      loading[url] ||
      fetch(url)
        .then((r) => (r.ok ? r.text() : Promise.reject(r.status)))
        .then((text) => {
          const map = {};
          qsa('[data-ups-recs-host][id]', new DOMParser().parseFromString(text, 'text/html')).forEach((el) => {
            const l = el.querySelector('[data-ups-list]');
            map[el.id] = { html: l ? l.innerHTML : '' };
          });
          cache(key, { v: 1, t: Date.now(), cur, map });
          delete loading[url];
          return map;
        }))
      .then(show, () => {
        delete loading[url];
        if (host.isConnected) fallback(host);
      });
  };

  // ---------------------------------------------------------------- add-ons for the first product (T2)
  // engineOnly: the fill once the first product is in. It takes main.js's switches and the theme add-ons with a Quantity
  // mode (main.js's product add only brings its own switches); those only from the drawer, or from a page cart when
  // there is no drawer, so the drawer and Cart page V2 on /cart never both send it. Without it: every Selected by
  // default add-on.
  const collect = (root, engineOnly) => {
    const out = [];
    const seen = new Set();
    const dec = declines();
    const themed = !engineOnly || root.matches('cart-drawer') || !d.querySelector('cart-drawer');
    qsa(TOGGLE + '[data-selected="true"]' + (themed ? ', ' + THEME_TOGGLE + '[data-ups-preselected="true"]' + (engineOnly ? '[data-ups-qty-mode]' : '') : ''), root).forEach((c) => {
      const h = c.dataset.handle;
      const id = num(c.dataset.id);
      if (!h || !id || inert(c) || dec.includes(h) || inCart(root, h) || seen.has(id)) return;
      const item = { id, quantity: c.matches(TOGGLE) ? 1 : startQuantity(c, root, !engineOnly) };
      if (!item.quantity) return;
      seen.add(id);
      const p = (c.querySelector('input[name="selling_plan"]') || {}).value || c.dataset.upsSellingPlan;
      if (p) item.selling_plan = Number(p) || p;
      out.push({ c, item });
    });
    return out;
  };
  const pendingAddonItems = (root) => collect(root || d.querySelector('cart-drawer') || d).map((e) => e.item);
  const skipNextFill = () => {
    skipUntil = Date.now() + 1e4;
  };
  const sendFill = (root, list) => {
    const r = w.ShrineCartRequests;
    const sig = 'fill:' + list.map((e) => e.item.id).sort().join(',');
    if (!r || (recent[sig] && Date.now() - recent[sig] < 8e3)) return;
    recent[sig] = Date.now();
    r.add(list.map((e) => e.item), { source: 'upsells:preselected', standardEvent: 'add', context: root.matches('cart-drawer') ? 'dialog' : 'cart' }).then((res) => {
      if (res && res.ok) return list.forEach((e) => emit('add', snap(e.c, 'toggle')));
      // not added (e.g. sold out meanwhile): the switch shows the cart again, so no later add includes it
      list.forEach((e) => {
        const c = root.querySelector(TOGGLE + '[data-handle="' + e.c.dataset.handle + '"]');
        if (c && !inCart(root, c.dataset.handle)) recover(c, (res && res.error && res.error.message) || '');
      });
    });
  };

  // ---------------------------------------------------------------- events, errors
  const snap = (c, source) => {
    const b = c.closest('[data-ups-block]');
    return { source, blockId: b ? b.dataset.upsBlock : null, handle: c.dataset.handle || null, productId: num(c.dataset.productId) || null, variantId: num(c.dataset.id) || null };
  };
  const emit = (action, data) => {
    const detail = Object.assign({ action }, data);
    d.dispatchEvent(new CustomEvent('shrine:cart:upsell', { detail }));
    try {
      w.Shopify.analytics.publish('shrine:cart_upsell', detail);
    } catch (e) {}
  };
  const sourceOf = (c) => {
    if (c.closest('.drawer__inner-empty, .cart-empty')) return 'empty_cart';
    const b = c.closest('[data-ups-source-name]');
    return (b && b.dataset.upsSourceName) || 'upsells';
  };
  const slot = (c) => c.querySelector('[data-ups-error-slot]');
  const clearError = (c) => {
    const s = slot(c);
    if (s && !s.hidden) {
      s.textContent = '';
      s.hidden = true;
    }
  };
  const showError = (c, text) => {
    const s = slot(c);
    const b = c.closest('[data-ups-error]');
    const m = text || (b && b.dataset.upsError) || '';
    if (!s || !m) return;
    s.textContent = '';
    s.hidden = false;
    // the alert region exists before its text arrives, so screen readers announce it
    setTimeout(() => (s.textContent = m), 50);
  };
  const recover = (c, message) => {
    if (!c.classList.contains('cart-upsell--soldout')) qsa('.upsell-toggle-btn[disabled], .select__select[disabled]', c).forEach((el) => el.removeAttribute('disabled'));
    if (c.dataset.toggle === 'true') setSel(c, inCart(rootOf(c) || d, c.dataset.handle));
    intents.delete(c.dataset.upsUid);
    if (message !== null) showError(c, message);
  };

  // ---------------------------------------------------------------- focus after renders (05 §8.7)
  const focusTarget = (root) => {
    const m = mem;
    mem = null;
    if (!m || !root || Date.now() - m.at > 8e3) return null;
    const ok = (el) => el && !el.closest('[hidden]') && !el.disabled;
    const card = root.querySelector('[data-ups-uid="' + m.uid + '"]');
    let el = card && card.querySelector('[data-ups-part="' + m.part + '"]');
    if (ok(el)) return el;
    const b = root.querySelector('[data-ups-block="' + m.block + '"]');
    el = b && qsa('[data-ups-part="control"]', b).find(ok);
    if (el || !b) return el || null;
    el = b.querySelector('.cart-upsells__title');
    if (el) el.setAttribute('tabindex', '-1');
    return el;
  };

  // ---------------------------------------------------------------- one pass per render
  let cardsFile = 0;
  const syncRoot = (root) => {
    if (!root || !root.querySelectorAll) return;
    reveal(root);
    qsa(TOGGLE, root).forEach((c) => inert(c) && setSel(c, inCart(root, c.dataset.handle)));
    const f = isFilled(root);
    // An empty drawer loads this file with the first add, so its first look may already be at the filled cart: on a
    // page that loaded with an empty cart, a root seen for the first time was empty before.
    const before = filled.has(root) ? filled.get(root) : core().config && core().config.itemCount === 0 ? false : undefined;
    filled.set(root, f);
    let fill = null;
    if (f) {
      if (before === false) {
        if (Date.now() < skipUntil) {
          skipUntil = 0;
          qsa(TOGGLE + '[data-ups-preselected="true"], ' + THEME_TOGGLE + '[data-ups-preselected="true"]', root).forEach((c) => !inert(c) && !inCart(root, c.dataset.handle) && setSel(c, false));
        } else fill = collect(root, true);
      }
      if (declines().length) store(DECL, null);
    } else {
      const dec = declines();
      if (dec.length) qsa(TOGGLE + ', ' + THEME_TOGGLE, root).forEach((c) => dec.includes(c.dataset.handle) && !inCart(root, c.dataset.handle) && setSel(c, false));
    }
    qsa(TOGGLE, root).forEach(aria);
    qsa('[data-ups-recs-host]', root).forEach(loadRecommendations);
    resync(root);
    const a = d.activeElement;
    if (mem && (!a || a === d.body || a.matches('.drawer__inner, .cart-item__name'))) {
      const el = focusTarget(root);
      const dr = el && el.closest('cart-drawer');
      if (dr && core().trapFocus) core().trapFocus(dr, el);
      else if (el) el.focus({ preventScroll: true });
    }
    intents.forEach((it, uid) => {
      if (Date.now() - it.at > 1e4) intents.delete(uid);
      else if ((it.action === 'add') === inCart(d.querySelector('cart-drawer') || d, it.data.handle)) {
        intents.delete(uid);
        emit(it.action, it.data);
      }
    });
    if (fill && fill.length) return sendFill(root, fill);
    if (api.auto) return api.auto(root);
    // theme cards, price bands, cart attributes: their file loads the first time a cart prints them
    const src = core().config && core().config.assets && core().config.assets.upsells;
    if (!cardsFile && src && root.querySelector(CARDS)) {
      cardsFile = 1;
      d.head.appendChild(Object.assign(d.createElement('script'), { src: src.cards || String(src.js).replace('component-cart-upsells.js', 'component-cart-upsells-cards.js'), async: true }));
    }
  };
  const sync = (root) => (root ? syncRoot(root) : roots().forEach(syncRoot));

  // V2 root: before its slider mounts, other-currency rules, recommendations, the free-shipping order, prices
  class CartUpsells extends HTMLElement {
    connectedCallback() {
      reveal(this);
      const l = this.querySelector('[data-ups-list]');
      if (this.hasAttribute('data-ups-recs-host')) loadRecommendations(this);
      else if (l) order(this, l);
      resync(this);
    }
  }
  if (!customElements.get('cart-upsells')) customElements.define('cart-upsells', CartUpsells);

  // ---------------------------------------------------------------- listeners
  d.addEventListener(
    'click',
    (e) => {
      const t = e.target;
      const c = t instanceof Element && t.closest('cart-drawer-upsell');
      if (!c || /^(select|option)$/i.test(t.nodeName)) return;
      if (c.dataset.toggle === 'true') {
        const hit = t.closest('.upsell-toggle-btn');
        if (!hit || !c.contains(hit) || hit.hasAttribute('disabled')) return;
        clearError(c);
        const root = rootOf(c);
        const was = c.dataset.selected === 'true';
        if (root && c.dataset.handle && !isFilled(root)) decline(c.dataset.handle, was);
        intents.set(c.dataset.upsUid, { action: was ? 'remove' : 'add', at: Date.now(), data: snap(c, 'toggle') });
        setTimeout(() => {
          const b = c.isConnected && c.querySelector('.upsell-toggle-btn');
          if (b && b.hasAttribute('disabled')) recover(c, null);
        }, 1e4);
      } else if (t.closest('.upsell__add-btn')) {
        clearError(c);
        intents.set(c.dataset.upsUid, { action: 'add', at: Date.now(), data: snap(c, sourceOf(c)) });
      }
    },
    true
  );
  d.addEventListener(
    'focusin',
    (e) => {
      const c = e.target.closest && e.target.closest('[data-ups-uid]');
      if (!c) return;
      const p = e.target.closest('[data-ups-part]');
      const b = c.closest('[data-ups-block]');
      mem = { uid: c.dataset.upsUid, part: p ? p.dataset.upsPart : 'control', block: b && b.dataset.upsBlock, at: Date.now() };
    },
    true
  );
  // V2 engine pickers: main.js updated data-id (V2 cards never print data-update-prices)
  d.addEventListener('change', (e) => {
    const c = e.target.closest && e.target.closest('cart-drawer-upsell[data-ups-initial-id]');
    const v = c && variants(c).find((x) => String(x.id) === c.dataset.id);
    if (v) paint(c, v);
  });
  d.addEventListener('product-form:error', (e) => {
    const c = e.target.closest && e.target.closest('cart-drawer-upsell');
    const x = e.detail || {};
    const text = (x.response && (x.response.description || x.response.message)) || (x.error && x.error.message) || '';
    if (c) recover(c, typeof text === 'string' ? text : '');
  });
  d.addEventListener('product-form:added', (e) => {
    const c = e.target.closest && e.target.closest('cart-drawer-upsell');
    if (!c || c.dataset.toggle === 'true') return;
    intents.delete(c.dataset.upsUid);
    emit('add', snap(c, sourceOf(c)));
  });
  const watch = () =>
    qsa('cart-drawer').forEach((dr) => {
      if (watched.has(dr)) return;
      watched.add(dr);
      new MutationObserver((recs) => new Set(recs.map((r) => r.target.closest && r.target.closest(TOGGLE)).filter(Boolean)).forEach(aria)).observe(dr, {
        subtree: true,
        attributes: true,
        attributeFilter: ['data-selected', 'disabled'],
      });
    });
  const init = () => {
    watch();
    roots().forEach(syncRoot);
    // the state is kept per cart root (<cart-drawer>, <cart-page>, …), whichever element inside it the hook reports
    if (core().onRender)
      core().onRender((info) => {
        const root = info && info.root && info.root.closest ? rootOf(info.root) || info.root : null;
        watch();
        if (root) syncRoot(root);
        else roots().forEach(syncRoot);
      });
    const ed = w.Shopify && w.Shopify.designMode && core().config && core().config.assets && core().config.assets.upsells && core().config.assets.upsells.editor;
    if (ed && ![...d.scripts].some((s) => s.src === new URL(ed, location.href).href)) d.head.appendChild(Object.assign(d.createElement('script'), { src: ed, async: true }));
  };

  // `_` is for component-cart-upsells-cards.js only (same release, same owner)
  const api = { version: 1, pendingAddonItems, skipNextFill, loadRecommendations, sync, focusTarget };
  api._ = { qsa, num, rootOf, inCart, isFilled, inert, setSel, decline, variants, paint, rate, emit, snap, sourceOf, clearError, showError, recent, TOGGLE, matchTarget, startQuantity };
  w.ShrineCartUpsells = api;
  const start = () => {
    if (core().provide) core().provide('upsells', api);
    init();
  };
  // the core's loader injects this file after the core; a deferred tag that runs first waits for it
  if (d.readyState === 'loading' || (!w.ShrineCart && d.readyState !== 'complete')) d.addEventListener('DOMContentLoaded', start, { once: true });
  else start();
})();

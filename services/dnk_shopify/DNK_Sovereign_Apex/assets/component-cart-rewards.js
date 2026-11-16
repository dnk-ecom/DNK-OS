/* Shrine PRO cart rewards: ShrineCartGoals, Rewards bar, gift picker, free-shipping-goal, Free gift helpers (04-rewards §7).
   Standalone-safe: every ShrineCart, ShrineCartRequests, ShrineCartEngine and main.js name is optional. */
(() => {
  if (window.ShrineCartGoals) return;
  const w = window, d = document, core = () => w.ShrineCart || {};
  const has = (f) => (core().has ? !!core().has(f) : !!(w.ShrineCartEngine || {})[f]);
  const config = () => core().config || {};
  const present = (v) => v != null && String(v).trim() !== '';
  const rep = (s, k, v) => String(s).split(k).join(v);
  const num = (v) => parseFloat(v) || 0;
  const $ = (s, r) => (r || d).querySelector(s);
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => '&#' + c.charCodeAt(0) + ';');
  const cur = () => (w.Shopify && w.Shopify.currency) || {};
  const list = (v) => (!v ? [] : Array.isArray(v) ? v : String(v).split(',')).map((s) => String(s).trim()).filter(Boolean);
  // after the cart core: deferred scripts run in page order, so a block's own script can run before the core's
  const later = (fn) => {
    let done = core().version || d.readyState === 'complete' ? fn() : 0;
    const go = () => done++ || fn();
    if (done === 0) [d, w].forEach((t, i) => t.addEventListener(i ? 'load' : 'DOMContentLoaded', go, { once: true }));
  };
  const EN = {
    rewards_gift_removed: 'Free gift removed',
    rewards_gift_chosen: '{{ title }} chosen as your free gift',
    rewards_unlocked: 'Unlocked: {{ reward }}',
    rewards_relocked: 'Locked again: {{ reward }}',
    rewards_relock_shipping: 'Subscribing removes free shipping',
    rewards_relock_discount: 'Subscribing removes your discount',
    rewards_relock_gift: 'Subscribing removes your free gift',
    rewards_relock_many: 'Subscribing removes some rewards',
  };
  const t = (k, vars) => {
    let s = core().t ? core().t(k, vars) : k;
    if (s === k) for (const n in ((s = EN[k] || k), vars)) s = rep(s, '{{ ' + n + ' }}', vars[n]);
    return s;
  };
  const kw = (s, map) => {
    if (core().keywords) return core().keywords(s, map);
    for (const k in map) s = rep(s || '', '[' + k + ']', map[k]);
    return s;
  };

  // goals: the JS twin of the cart-free-shipping-goal / cart-goal-total snippets (skeleton §3b.4)
  const G = (w.ShrineCartGoals = {
    version: 1,
    parse(src) {
      const p = !src ? 0 : src.nodeType === 1 ? ['kind', 'cents', 'currency'].map((n) => src.getAttribute('data-goal-' + n)) : typeof src === 'string' ? src.trim().split('|') : [src.kind, src.cents, src.currency];
      return !p || p.length < 2 || ['none', 'local', 'shop', 'items'].indexOf(p[0]) < 0 ? null : { kind: p[0], cents: num(p[1]), currency: p[2] || '' };
    },
    rate(shop) {
      const m = core().money, a = cur().active, r = num(cur().rate);
      if (m && m.rate) return (m.rate(shop) || {}).rate || null;
      return !a || r <= 0 || r === 1 || a === (shop || config().shopCurrency) ? null : r;
    },
    toPresentment(src) {
      const g = G.parse(src), a = cur().active || config().currency, r = num(cur().rate);
      if (!g || g.kind === 'none') return null;
      return g.kind !== 'shop' || (a && (!g.currency || a === g.currency)) ? g.cents : a && r > 0 ? Math.round(g.cents * r) : null;
    },
    countedTotal(cart, o) {
      o = o || {};
      const hidden = list(o.hiddenHandles), skip = list(o.skipHandles), sh = o.skipHidden !== false;
      let out = 0, items = 0, plan = false;
      if (sh) d.querySelectorAll('.cart-item[data-line-flags~="cart-hidden"]').forEach((el) => hidden.push(el.dataset.handle));
      ((cart && cart.items) || []).forEach((it) => {
        const p = it.properties || {};
        plan = plan || !!it.selling_plan_allocation;
        if (present(p._reward_gift) || (sh && hidden.indexOf(it.handle) > -1) || (o.skipGifts !== false && (present(p._qb_gift) || it.final_line_price === 0)) ||
          (o.skipGiftCards !== false && it.gift_card) || (o.skipUnshipped === true && it.requires_shipping === false) || skip.indexOf(it.handle) > -1) out += num(it.final_line_price);
        else items += num(it.quantity);
      });
      return { total: Math.max(0, num(cart && cart.total_price) - out), items, hasPlan: plan };
    },
    status(src, total, items) {
      const g = G.toPresentment(src), n = items === undefined ? 1 : num(items);
      total = num(total);
      return g === null ? null : { goalCents: g, remainingCents: Math.max(0, g - total), reached: n > 0 && total >= g, percent: g > 0 ? Math.min(100, (total * 100) / g) : 100 };
    },
    format(cents, o) {
      const tz = !!(o && o.trailingZeros), code = (o && o.currency) || cur().active || config().currency || 'USD', f = { style: 'currency', currency: code };
      if (core().money) return core().money.format(cents, { trailingZeros: tz, currency: o && o.currency });
      if (!tz && Math.round(cents) % 100 === 0) f.minimumFractionDigits = f.maximumFractionDigits = 0;
      try {
        return new Intl.NumberFormat(d.documentElement.lang || undefined, f).format(num(cents) / 100);
      } catch (e) {
        return (num(cents) / 100).toFixed(2) + ' ' + code;
      }
    },
  });
  const fmt = (c) => G.format(c);
  const define = (n, connected, extra) => {
    if (!w.customElements || customElements.get(n)) return;
    const C = class extends HTMLElement {};
    Object.assign(C.prototype, extra, {
      connectedCallback() {
        try {
          connected.call(this);
        } catch (e) {
          console.error(e);
        }
      },
    });
    customElements.define(n, C);
  };

  // Free gift text in other currencies (the inline sync, earlier in tree order, set the gift's data-selected)
  define('cart-gift-status', function () {
    const gift = this.closest('cart-drawer-gift, .cart-drawer-gift'), x = this.dataset, q = x.quantity === 'true', r = G.rate(x.shopCurrency);
    const on = !!gift && gift.dataset.selected === 'true', text = (on ? x.unlockedText : x.lockedText) || '', h = this.closest('.cart-drawer-gift__progress');
    const left = Math.max(0, num(x.goalCents) * (q ? 1 : r) - num(x.totalCents)), lock = gift && $('.cart-drawer-gift__image__locked', gift);
    if (!q && !r) return;
    this.innerHTML = rep(text, '[amount]', q ? Math.round(left) : '<span>' + fmt(Math.round(left)) + '</span>');
    if (h) h.hidden = !present(text);
    if (lock) lock.hidden = on;
  });

  // gifts on stores without a cart drawer are live only with main.js's cart root support (QB-1c E13)
  const gate = (el, host) => {
    if (!has('cartRoot')) return el.classList.add('is-gifts-off');
    host.hidden = false;
    host.removeAttribute('data-rw-engine-wait');
  };
  define('cart-rewards-gate', function () {
    if (this.parentElement) gate(this.parentElement, this.parentElement);
  });

  // Rewards bar (§7.4)
  const FILL = {}, ONE = [];
  let FOCUS = null;
  const seen = (map) => {
    try {
      if (!map) return JSON.parse(sessionStorage.getItem('shrine-cart-rewards')) || {};
      sessionStorage.setItem('shrine-cart-rewards', JSON.stringify(map));
    } catch (e) {
      return {};
    }
  };
  const emit = (detail) => {
    try {
      d.dispatchEvent(new CustomEvent('shrine:cart:reward', { bubbles: true, detail }));
      w.Shopify.analytics.publish('shrine:cart_reward', detail);
    } catch (e) {}
  };
  define(
    'cart-rewards-bar',
    function () {
      const bar = this, x = bar.dataset, total = num(x.total), items = num(x.items), msg = $('.cart-rewards__message', bar), fill = $('.cart-rewards__fill', bar);
      if (x.preview === 'sample') return;
      const steps = [...bar.querySelectorAll('.cart-rewards__steps > [data-rw-id]')].map((el) => {
        const s = el.dataset, ship = s.rwType === 'shipping';
        return { el, id: s.rwId, type: s.rwType, cmp: num(s.rwCmp), sub: s.rwSub === 'true', u: s.rwState === 'unlocked', via: el.classList.contains('is-sub'),
          t: num(ship ? x.shipTotal : x.total), n: num(ship ? x.shipItems : x.items), label: s.rwText, next: s.rwMystery ? s.rwMtext : s.rwNext || s.rwText };
      });
      const r = x.needsJs === 'true' && G.rate(x.shopCurrency);
      if (r) bar.convert(steps, r, total, items);
      bar.classList.remove('is-pending');
      const to = fill && fill.style.width, from = FILL[x.blockId];
      if (fill) FILL[x.blockId] = to;
      if (fill && from && from !== to && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
        fill.style.transition = 'none';
        fill.style.width = from;
        void fill.offsetWidth;
        fill.style.transition = '';
        fill.style.width = to;
      }
      const map = seen(), changes = steps.filter((s) => map[s.id] && map[s.id] !== (s.u ? 'u' : 'l'));
      steps.forEach((s) => (map[s.id] = s.u ? 'u' : 'l'));
      seen(map);
      changes.forEach((s) => {
        emit({ action: s.u ? 'unlocked' : 'locked', rewardId: s.id, rewardType: s.type, goalCents: s.cmp, totalCents: s.t, currency: x.currency, label: s.label });
        if (s.u) s.el.classList.add('is-new');
        setTimeout(() => s.el.classList.remove('is-new'), 700);
      });
      // one sentence each, said once (an empty Success message repeats the unlock: "Unlocked: Free shipping")
      x.cartAnnounce = ONE.splice(0).concat(changes.map((s) => t(s.u ? 'rewards_unlocked' : 'rewards_relocked', { reward: s.label })), msg ? msg.textContent.replace(/\s+/g, ' ').trim() : '')
        .filter((v, i, a) => v && a.indexOf(v) === i)
        .reduce((all, v) => (all ? all + (/[.!?…。！？:]$/.test(all) ? ' ' : '. ') + v : v), '');
      // re-lock captions under Subscribe & save controls (what the plan's lower price would lose)
      if (x.goalType !== 'quantity')
        (bar.closest('.cart-root, cart-drawer, cart-page, cart-items') || d).querySelectorAll('[data-sub-control]').forEach((c) => {
          const slot = $('[data-sub-relock]', c), sv = num(c.dataset.saving);
          const lost = present(c.dataset.currentPlan) || sv <= 0 ? [] : steps.filter((s) => s.u && !s.via && !s.sub && s.type !== 'milestone' && s.t - sv < s.cmp);
          if (!slot) return;
          slot.textContent = lost.length ? t(lost.length > 1 ? 'rewards_relock_many' : 'rewards_relock_' + lost[0].type) : '';
          slot.hidden = !lost.length;
        });
      const a = $('.cart-rewards__areas[data-rw-engine-wait]', bar);
      if (a) gate(bar, a);
      // a gift action's focus target, again after the engine's own render (that render replaces the focused element)
      if (FOCUS && Date.now() - FOCUS[1] < 4000)
        setTimeout(() => {
          const f = d.activeElement, el = (!f || f === d.body || !f.isConnected) && FOCUS && FOCUS[0]();
          if (el) el.focus();
        });
    },
    {
      // other currencies: store-currency goals converted, then §3.4's formulas again
      convert(steps, r, total, items) {
        const bar = this, x = bar.dataset, lay = x.layout, f = $('.cart-rewards__fill', bar), tr = $('.cart-rewards__track', bar), m = $('.cart-rewards__message', bar);
        steps.forEach((s) => {
          if (s.el.dataset.rwKind === 'shop') s.cmp = Math.round(num(s.el.dataset.rwCents) * r);
          s.u = s.n > 0 && (s.t >= s.cmp || (s.sub && x.hasPlan === 'true'));
          s.via = s.u && s.sub && s.t < s.cmp;
        });
        const sorted = steps.slice().sort((a, b) => a.cmp - b.cmp), n = sorted.length, max = Math.max(0, ...sorted.map((s) => s.cmp));
        let prev = 0, seg = 0, next = null;
        if (x.mixed === 'true') sorted.forEach((s) => s.el.parentNode.appendChild(s.el));
        sorted.forEach((s, i) => {
          const pos = Math.round((lay === 'proportional' ? (max > 0 ? (s.cmp * 100) / max : 100) : lay === 'even' ? ((i + 1) * 100) / n : 0) * 100) / 100, e = s.el;
          if (lay === 'even') seg += s.cmp > prev ? Math.min(1, Math.max(0, (total - prev) / (s.cmp - prev))) : total >= s.cmp ? 1 : 0;
          prev = s.cmp;
          [['is-next', !s.u && !next], ['is-unlocked', s.u], ['is-locked', !s.u], ['is-sub', s.via], ['is-edge-start', lay !== 'none' && pos <= 12], ['is-edge-end', lay !== 'none' && pos >= 88]].forEach((c) => e.classList.toggle(c[0], c[1]));
          if (!s.u && !next) next = s;
          e.style.setProperty('--rw-pos', pos + '%');
          e.dataset.rwCmp = s.cmp;
          e.dataset.rwState = s.u ? 'unlocked' : 'locked';
          if (bar.classList.contains('cart-rewards--amounts-on')) $('.cart-rewards__goal', e).textContent = fmt(s.cmp);
          $('.cart-rewards__status', e).textContent = s.u ? x.statusUnlocked : rep(x.statusLocked, '[amount]', fmt(Math.max(0, s.cmp - s.t)));
        });
        const fl = Math.round((lay === 'even' ? (n ? (seg * 100) / n : 0) : max > 0 ? Math.min(100, (total * 100) / max) : items > 0 ? 100 : 0) * 100) / 100;
        if (f) f.style.width = fl + '%';
        if (tr) tr.setAttribute('aria-valuenow', Math.round(fl));
        if (m)
          m.innerHTML = next
            ? kw(x.progressMessage, { amount: '<span class="cart-rewards__amount-left">' + fmt(Math.max(0, next.cmp - next.t)) + '</span>', next_goal: esc(next.next), next_goal_lowercase: esc(next.next.toLowerCase()) })
            : x.successMessage || esc(t('rewards_unlocked', { reward: n ? sorted[n - 1].label : '' }));
        bar.classList.toggle('is-complete', !next);
        bar.querySelectorAll('.cart-reward[data-reward-id]').forEach((a) => {
          const i = sorted.findIndex((s) => s.id === a.dataset.rewardId), s = sorted[i], st = !s ? 0 : !s.u ? 'locked' : a.dataset.removed === 'true' ? 'removed' : 'unlocked';
          if (!st) return;
          a.dataset.state = st;
          a.hidden = st === 'locked' || sorted.slice(i + 1).some((y) => y.type === 'gift' && y.el.dataset.rwReplace && y.u) || (st === 'unlocked' && a.dataset.count === '1' && a.dataset.display === 'line');
        });
      },
    }
  );

  // gift choice, removal, add back (§7.5): one cart attribute each (_reward_gift_<reward id> = handle | removed | ''); main.js's
  // gift engine adds or removes the gift on the render that follows
  const busy = (p, on) =>
    p && (p.setAttribute('aria-busy', on), p.querySelectorAll(on ? 'button:not([disabled])' : 'button[data-rw-busy]').forEach((b) => ((b.disabled = on), b.toggleAttribute('data-rw-busy', on))));
  const act = (rid, kind, key, handle, picker) => {
    const R = w.ShrineCartRequests, area = () => d.getElementById('CartReward-' + rid + '-area'), step = d.getElementById('CartReward-' + rid), sd = (step && step.dataset) || {};
    const bd = ((step && step.closest('cart-rewards-bar')) || {}).dataset || {}, eng = $('cart-drawer-gift[data-reward-id="' + rid + '"][data-handle="' + handle + '"]');
    const name = picker && $('[data-handle="' + handle + '"] .cart-reward__name', picker), attributes = { ['_reward_gift_' + rid]: kind === 'choose' ? handle : kind === 'remove' ? 'removed' : '' };
    const say = kind === 'choose' ? t('rewards_gift_chosen', { title: name ? name.textContent.trim() : '' }) : kind === 'remove' ? t('rewards_gift_removed') : '';
    const opts = {
      source: 'rewards:gift-' + (kind === 'add' ? 'add-back' : kind),
      standardEvent: kind === 'remove' ? 'remove' : null,
      focus() {
        const a = area(), s = d.getElementById('CartReward-' + rid);
        let el = a && !a.hidden && $(kind === 'choose' ? '[data-handle="' + handle + '"]' : kind === 'remove' ? '.cart-reward__add-back' : '.cart-reward__option:not([disabled])', a);
        if (!el && (el = s && $('.cart-rewards__message', s.closest('cart-rewards-bar')))) el.tabIndex = -1;
        return el;
      },
    };
    if (!R || !R.update) return;
    if (say) ONE.push(say);
    busy(picker, true);
    return R.update(kind === 'remove' && key ? { attributes, updates: { [key]: 0 } } : { attributes }, opts)
      .then((res) => (res && !res.ok && kind === 'remove' && key && res.error && /^(http|cart)$/.test(res.error.code) ? R.update({ attributes }, opts) : res))
      .then((res) => {
        const p = (picker && picker.isConnected && picker) || area(), e = p && $('.cart-reward__error', p);
        if (res && res.ok) FOCUS = [opts.focus, Date.now()];
        if (res && res.ok)
          return emit({ action: kind === 'choose' ? 'gift_chosen' : kind === 'remove' ? 'gift_removed' : 'gift_added_back', rewardId: rid, rewardType: 'gift', goalCents: num(sd.rwCmp),
            totalCents: num(bd.total), currency: bd.currency || cur().active, label: sd.rwText || '', handle: handle || undefined, variantId: eng ? num(eng.dataset.id) : undefined });
        if (ONE.indexOf(say) > -1) ONE.splice(ONE.indexOf(say), 1);
        busy(p, false);
        if (e) e.textContent = (w.cartStrings && w.cartStrings.error) || '';
      });
  };
  let warned;
  define('cart-reward-picker', function () {
    const p = this, x = p.dataset, rm = $('.cart-reward__remove', p), ch = $('[aria-pressed="true"] .cart-reward__name', p);
    if (p.rw) return;
    p.rw = 1;
    // no write path without the cart core (it may still come later on the page: a block's own script can run first)
    later(() => {
      if (w.ShrineCartRequests) return;
      p.querySelectorAll('button').forEach((b) => (b.disabled = true));
      warned = warned || !console.warn('[Shrine rewards] gift choices need component-cart.js');
    });
    if (rm && ch && !$('.visually-hidden', rm)) rm.insertAdjacentHTML('beforeend', '<span class="visually-hidden"> ' + esc(ch.textContent.trim()) + '</span>');
    p.addEventListener('click', (e) => {
      const b = e.target.closest('button'), c = (b && !b.disabled && b.classList) || { contains: () => 0 };
      if (c.contains('cart-reward__option') && b.getAttribute('aria-pressed') !== 'true') act(x.rewardId, 'choose', null, b.dataset.handle, p);
      if (c.contains('cart-reward__remove')) act(x.rewardId, 'remove', x.lineKey, x.chosen, p);
      if (c.contains('cart-reward__add-back')) act(x.rewardId, 'add', null, x.chosen, p);
    });
  });
  // a reward gift line's own remove button: the removal is remembered, else the engine would add the gift right back
  d.addEventListener(
    'click',
    (e) => {
      const btn = e.target.closest && e.target.closest('cart-remove-button'), line = btn && btn.closest('.cart-item.cart-item--reward-gift');
      const h = line && (btn.dataset.handle || line.dataset.handle), eng = h && $('cart-drawer-gift[data-reward-id][data-handle="' + h + '"]'), g = eng && eng.closest('[data-rw-engine]');
      if (!eng || !w.ShrineCartRequests || (g && g.dataset.readd === 'true')) return;
      e.preventDefault();
      e.stopImmediatePropagation();
      act(eng.dataset.rewardId, 'remove', line.dataset.lineKey, h, d.getElementById('CartReward-' + eng.dataset.rewardId + '-area'));
    },
    true
  );

  // the free shipping goal outside the cart (§7.6): announcement keyword (mode goal), product block (mode note)
  const getCart = () =>
    w.ShrineCartRequests ? w.ShrineCartRequests.getCart() : fetch(((w.routes && w.routes.cart_url) || '/cart') + '.js', { headers: { Accept: 'application/json' }, cache: 'no-store' }).then((r) => r.json()).catch(() => null);
  define(
    'free-shipping-goal',
    function () {
      const el = this, pending = el.hasAttribute('data-pending'), v = pending && G.toPresentment(el), m = el.closest('.announcement-bar__message');
      if (el.dataset.mode !== 'note') {
        if (pending && v === null && m) m.style.display = 'none';
        else if (pending) el.textContent = fmt(v);
        el.removeAttribute('data-pending');
        return el.style.removeProperty('visibility');
      }
      if (pending) el.draw();
      if (el.off) return;
      const go = (cart) => (clearTimeout(el.tm), (el.tm = setTimeout(() => (cart && cart.items ? el.draw(cart) : getCart().then((c) => c && el.draw(c))), 250)));
      const up = (e) => go(e.detail && e.detail.cart), add = () => go();
      let un;
      d.addEventListener('shrine:cart:updated', up);
      d.addEventListener('product-form:added', add);
      try {
        un = subscribe(PUB_SUB_EVENTS.cartUpdate, (m) => {
          try {
            go(m.cartData.items && m.cartData.total_price != null && m.cartData);
          } catch (e) {}
        });
      } catch (e) {}
      el.off = () => (d.removeEventListener('shrine:cart:updated', up), d.removeEventListener('product-form:added', add), un && un());
    },
    {
      disconnectedCallback() {
        if (this.off) this.off();
        this.off = null;
      },
      draw(cart) {
        const el = this, x = el.dataset, host = el.closest('.free-shipping-note'), goal = G.toPresentment(el), out = $('.free-shipping-note__text', el);
        const c = cart ? G.countedTotal(cart, { hiddenHandles: x.hiddenHandles, skipUnshipped: true }) : { total: num(x.totalCents), items: num(x.items) };
        const txt = goal === null ? '' : c.items > 0 && c.total >= goal ? x.reachedText : x.text;
        if (host) host.hidden = !present(txt);
        if (goal === null) return;
        out.innerHTML = kw(txt, { free_shipping_goal: '<span class="free-shipping-note__goal">' + fmt(goal) + '</span>', amount: '<span class="free-shipping-note__left">' + fmt(Math.max(0, goal - c.total)) + '</span>' });
        el.removeAttribute('data-pending');
      },
    }
  );

  // once the cart core is there: its config (the editor file, design mode only) and require('rewards')
  later(() => {
    try {
      const url = w.Shopify.designMode && config().assets.rewards.editor;
      if (url && !$('script[src="' + url + '"]')) d.head.appendChild(Object.assign(d.createElement('script'), { src: url, async: true }));
    } catch (e) {}
    if (core().provide) core().provide('rewards', G);
  });
})();

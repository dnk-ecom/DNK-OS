/* Cart checkout extras (footer area): the opt-in parts only some carts use. component-cart-checkout.js loads this file
   once a host that prints its URL (data-checkout-extras) is on the page: cart-totals-goal (a store-currency free shipping
   goal shown in another currency), cart-gift-card (Discount field > Accept gift cards) and cart-shipping-estimator (the
   Shipping estimator block). It uses the main file's helpers; every main.js and core name is optional. */
(() => {
  const C = window.ShrineCartCheckout;
  if (!C || !C.util || C.extras) return;
  C.extras = { version: 1 };
  const w = window;
  const d = document;
  const { t, store, define } = C.util;
  const read = (key) => {
    try { return JSON.parse(store(key)); } catch (e) { return null; }
  };
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => '&#' + c.charCodeAt(0) + ';');
  const money = (cents) => {
    const m = w.ShrineCart && w.ShrineCart.money;
    return m && m.format ? m.format(cents) : (cents / 100).toFixed(2);
  };
  const cartUrl = () => (w.routes && w.routes.cart_url) || '/cart';
  const getCart = () => (w.ShrineCartRequests && w.ShrineCartRequests.getCart ? w.ShrineCartRequests.getCart()
    : fetch(cartUrl() + '.js', { headers: { Accept: 'application/json' } }).then((r) => (r.ok ? r.json() : null)).catch(() => null));

  // ---------- cart-totals-goal: a store-currency free shipping goal in another currency. Liquid can't convert it,
  // so the row is corrected with the Rewards bar's rule (ShrineCartGoals.status); an unknown rate keeps Liquid's state.
  define('cart-totals-goal', class extends HTMLElement {
    connectedCallback() {
      if (this.dataset.state !== 'pending') return;
      if (w.ShrineCartGoals) return this.apply();
      if (w.ShrineCart && w.ShrineCart.require) w.ShrineCart.require('rewards').then(() => this.apply());
    }

    apply() {
      const x = this.dataset;
      const st = w.ShrineCartGoals && this.isConnected ? w.ShrineCartGoals.status(this, x.progress, x.items) : null;
      const q = (s) => this.querySelector(s) || {};
      if (!st) return;
      if (x.mode === 'progress') {
        const pct = Math.round(st.percent);
        const bar = q('[role="progressbar"]');
        q('[data-goal-text]').innerHTML = ((st.reached ? x.textSuccess : x.textProgress) || '').split('[amount]').join(esc(money(st.remainingCents)));
        if (bar.setAttribute) bar.setAttribute('aria-valuenow', pct);
        if (bar.firstElementChild) bar.firstElementChild.style.width = pct + '%';
        this.hidden = false;
      } else if (st.reached) {
        const value = q('[data-shipping-value]');
        value.textContent = x.freeText || '';
        if (value.dataset) value.dataset.state = 'free';
        q('[data-estimated-row]').hidden = false;
        q('[data-estimated-value]').textContent = x.freeTotal || '';
      }
    }
  });

  // ---------- gift cards in the Discount field (Accept gift cards, off by default; store test first): tokenless
  // Storefront API mutations on the session cart. Liquid has no applied gift card field, so chips come from storage.
  const CARDS = 'shrine-cart-gift-cards';
  const API = '/api/2026-10/graphql.json';
  const FIELDS = '{ cart { appliedGiftCards { id lastCharacters } } userErrors { code field message }';
  const ADD = 'mutation ShrineGiftCardAdd($cartId: ID!, $codes: [String!]!) { cartGiftCardCodesAdd(cartId: $cartId, giftCardCodes: $codes) ' + FIELDS + ' warnings { code message } } }';
  const REMOVE = 'mutation ShrineGiftCardRemove($cartId: ID!, $ids: [ID!]!) { cartGiftCardCodesRemove(cartId: $cartId, appliedGiftCardIds: $ids) ' + FIELDS + ' } }';
  const storefront = async (query, variables, again) => {
    const post = (url) => fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify({ query, variables }) })
      .then((r) => (r.ok ? r.json() : null)).catch(() => null);
    const data = (await post(API)) || (w.Shopify && w.Shopify.shop ? await post('https://' + w.Shopify.shop + API) : null);
    if (data && data.errors) {
      if (again || !data.errors.some((e) => e.extensions && e.extensions.code === 'THROTTLED')) return null;
      await sleep(2000);
      return storefront(query, variables, true);
    }
    return data && data.data;
  };
  const renderCards = () => d.querySelectorAll('cart-gift-card').forEach((el) => el.render());
  const saveCards = (token, list) => {
    store(CARDS, JSON.stringify({ token, cards: list.map((c) => ({ id: c.id, last: c.lastCharacters })) }));
    renderCards();
  };
  const unavailable = () => {
    const n = w.ShrineCart && w.ShrineCart.notices;
    if (n && n.set) n.set('checkout-gift-cards-unavailable', { level: 'warning', title: 'Discount field', text: "gift cards couldn't be added on this store. Turn off Accept gift cards." });
    return false;
  };
  const giftCards = {
    async add(code) {
      const cart = await getCart();
      if (!cart || !cart.token) return unavailable();
      const s = read(CARDS);
      const before = s && s.token === cart.token ? s.cards.map((c) => c.id) : [];
      const data = await storefront(ADD, { cartId: 'gid://shopify/Cart/' + cart.token, codes: [code] });
      const res = data && data.cartGiftCardCodesAdd;
      if (!res || (res.warnings || []).some((x) => x.code === 'PAYMENTS_GIFT_CARDS_UNAVAILABLE')) return unavailable();
      const cards = (res.cart && res.cart.appliedGiftCards) || [];
      const ok = !(res.userErrors || []).length && cards.some((c) => c.lastCharacters && !before.includes(c.id)
        && code.slice(-c.lastCharacters.length).toLowerCase() === c.lastCharacters.toLowerCase());
      if (ok) saveCards(cart.token, cards);
      return ok;
    },
    async remove(id) {
      const cart = await getCart();
      const data = cart && cart.token && (await storefront(REMOVE, { cartId: 'gid://shopify/Cart/' + cart.token, ids: [id] }));
      const res = data && data.cartGiftCardCodesRemove;
      if (res) saveCards(cart.token, (res.cart && res.cart.appliedGiftCards) || []);
      return !!res;
    },
  };
  let cardsChecked = false;
  define('cart-gift-card', class extends HTMLElement {
    connectedCallback() {
      if (!this.wired) {
        this.wired = true;
        this.addEventListener('click', (e) => {
          const button = e.target.closest && e.target.closest('.cart-gift-card__remove');
          const chip = button && button.closest('[data-gift-card-id]');
          if (!chip) return;
          e.preventDefault();
          button.disabled = true;
          const input = this.closest('cart-discount-block');
          giftCards.remove(chip.dataset.giftCardId).then((ok) => {
            button.disabled = false;
            const field = ok && input && input.querySelector('input[name="cart-discount-field"]');
            if (field) field.focus();
          });
        });
      }
      this.render();
      const s = read(CARDS);
      if (s && s.cards && s.cards.length && !cardsChecked) {
        cardsChecked = true;   // once per page: a new cart (after checkout) drops the stored cards
        getCart().then((cart) => cart && cart.token !== s.token && (store(CARDS, null), renderCards()));
      }
    }

    add(code) {
      return giftCards.add(code);
    }

    render() {
      const list = this.querySelector('[data-gift-card-chips]');
      const tpl = this.querySelector('template[data-gift-card-template]');
      const s = read(CARDS);
      if (!list || !tpl) return;
      list.textContent = '';
      ((s && s.cards) || []).forEach((card) => {
        const chip = tpl.content.firstElementChild.cloneNode(true);
        const fill = (text) => (text || '').split('[last]').join(card.last);
        const spans = chip.querySelectorAll('.cart-discount__pill-code > span');
        chip.dataset.giftCardId = card.id;
        spans[0].textContent = fill(this.dataset.chipLabel);
        spans[1].textContent = '•••• ' + card.last;
        chip.querySelector('button').setAttribute('aria-label', fill(this.dataset.removeLabel));
        list.appendChild(chip);
      });
    }
  });

  // ---------- cart-shipping-estimator: Shopify's rates for an address. The country list comes once per session from
  // the schema-less section cart-shipping-countries; the last address and its rates stay in sessionStorage.
  const ESTIMATE = 'shrine-cart-estimator';
  define('cart-shipping-estimator', class extends HTMLElement {
    connectedCallback() {
      if (this.f) return;
      const q = (s) => this.querySelector('[data-estimator-' + s + ']');
      const f = (this.f = { details: this.querySelector('details'), country: q('country'), field: q('province-field'), province: q('province'), zip: q('zip'), button: q('submit'), results: q('results') });
      this.addEventListener('change', (e) => {
        e.stopPropagation();
        if (e.target === f.country) this.provinces();
      });
      f.details.addEventListener('toggle', () => f.details.open && this.countries());
      f.country.addEventListener('focus', () => this.countries());
      f.button.addEventListener('click', () => this.estimate());
      f.zip.addEventListener('keydown', (e) => {
        if (e.key !== 'Enter') return;
        e.preventDefault();
        this.estimate();
      });
      this.restore();
      if (f.details.open) this.countries();
    }

    disconnectedCallback() {
      clearTimeout(this.timer);
    }

    live() {   // the instance in the page now (a render may have replaced this one during a request)
      const el = this.isConnected ? this : d.getElementById(this.f.details.id);
      return el && el.closest('cart-shipping-estimator');
    }

    countries() {
      if (this.loading) return this.loading;
      const x = this.dataset;
      const key = 'shrine-cart-estimator-countries:' + x.countriesKey;
      const cached = store(key);
      this.loading = (cached ? Promise.resolve(cached) : fetch(x.countriesUrl).then((r) => (r.ok ? r.text() : '')).then((html) => {
        const select = new DOMParser().parseFromString(html, 'text/html').querySelector('select[data-countries]');
        const options = select ? select.innerHTML.trim() : '';
        if (options) store(key, options);
        return options;
      }).catch(() => '')).then((options) => {
        const c = this.f.country;
        const label = c.selectedIndex > -1 ? c.options[c.selectedIndex].text.trim() : '';
        const value = c.value;
        if (!options) return;
        c.innerHTML = options;
        const all = [...c.options];
        const hit = all.find((o) => o.value === value) || all.find((o) => o.text.trim() === label) || all[0];
        if (hit) c.value = hit.value;
        this.provinces();
      });
      return this.loading;
    }

    provinces() {
      const { country, province, field } = this.f;
      const option = country.options[country.selectedIndex];
      const want = province.value || this.want || province.dataset.default || '';
      let list = [];
      try { list = JSON.parse((option && option.dataset.provinces) || '[]'); } catch (e) {}
      province.textContent = '';
      list.forEach((p) => province.add(new Option(p[1], p[0], false, p[0] === want || p[1] === want)));
      field.hidden = !list.length;
    }

    busyState(on) {
      const b = this.f.button;
      b.classList.toggle('loading', on);
      b.setAttribute('aria-disabled', on);
      b.querySelector('.loading-overlay__spinner').classList.toggle('hidden', !on);
      b.querySelector('.cart-estimator__submit-label').style.visibility = on ? 'hidden' : '';
      this.f.results.setAttribute('aria-busy', on);
    }

    async estimate() {
      const f = this.f;
      if (this.busy) return;
      this.busy = true;
      this.busyState(true);
      try {
        await this.countries();
        const address = { country: f.country.value, province: f.field.hidden ? '' : f.province.value, zip: f.zip.value.trim() };
        const params = new URLSearchParams({ 'shipping_address[zip]': address.zip, 'shipping_address[country]': address.country });
        if (address.province) params.set('shipping_address[province]', address.province);
        const call = (path, method) => fetch(cartUrl() + '/' + path + '?' + params, { method, headers: { Accept: 'application/json' } });
        let res = await call('prepare_shipping_rates.json', 'POST');
        if (!res.ok) return this.fail(await res.json().catch(() => null));
        for (const wait of [400, 600, 900, 1200, 1600, 2000, 2500]) {
          await sleep(wait);
          res = await call('async_shipping_rates.json', 'GET');
          const body = await res.json().catch(() => null);
          if (!res.ok) return this.fail(body);
          if (body && body.shipping_rates) return this.show(body.shipping_rates, address, true);
        }
        this.fail();
      } catch (e) {
        this.fail();
      } finally {
        this.busy = false;
        this.busyState(false);
      }
    }

    show(rates, address, keep) {
      const self = this.live();
      if (!self) return;
      const x = self.dataset;
      const c = self.f.country;
      const day = (s) => new Date(/^\d{4}-\d\d-\d\d$/.test(s) ? s + 'T12:00:00' : s);
      const range = (r) => {
        if (x.showDates !== 'true' || !r || !r[0]) return '';
        try {
          const fmt = new Intl.DateTimeFormat(d.documentElement.lang || undefined, { month: 'short', day: 'numeric' });
          const a = day(r[0]);
          const b = day(r[1] || r[0]);
          return +a === +b || !fmt.formatRange ? fmt.format(a) : fmt.formatRange(a, b);
        } catch (e) {
          return '';
        }
      };
      const sorted = [...rates].sort((a, b) => parseFloat(a.price) - parseFloat(b.price));
      const where = [address.zip, c.selectedIndex > -1 ? c.options[c.selectedIndex].text.trim() : address.country].filter(Boolean).join(', ');
      const rows = sorted.map((r) => {
        const cents = Math.round(parseFloat(r.price) * 100) || 0;
        const when = range(r.delivery_range);
        return '<li class="cart-estimator__rate"><span>' + esc(r.presentment_name || r.name) + (when ? '<span class="cart-estimator__rate-date">' +
          esc(t('checkout_estimator_arrives', { date: when }, 'Arrives [date]')) + '</span>' : '') + '</span><span>' + esc(cents ? money(cents) : x.freeText) + '</span></li>';
      });
      self.f.results.innerHTML = '<p class="cart-estimator__heading">' + esc(rows.length ? t('checkout_estimator_results', { address: where }, 'Shipping options for [address]')
        : t('checkout_estimator_none', null, 'There are no shipping options for this address.')) + '</p>' + (rows.length ? '<ul class="cart-estimator__rates" role="list">' + rows.join('') + '</ul>' : '');
      if (keep) store(ESTIMATE, JSON.stringify({ address, signature: x.signature, rates }));
    }

    fail(body) {
      const self = this.live();
      if (!self) return;
      const x = self.dataset;
      const labels = { zip: x.labelZip, country: x.labelCountry, province: x.labelProvince };
      const parts = body && typeof body === 'object' ? Object.keys(body).filter((k) => Array.isArray(body[k])).map((k) => (labels[k] || k) + ' ' + body[k].join(', ')) : [];
      self.f.results.innerHTML = '<p class="cart-estimator__error">' + esc(parts.join('. ') || t('checkout_estimator_error', null, "Shipping couldn't be estimated. Check the address and try again.")) + '</p>';
    }

    restore() {
      const s = read(ESTIMATE);
      const f = this.f;
      const a = s && s.address;
      if (!a) return;
      if (a.country) {
        if (![...f.country.options].some((o) => o.value === a.country)) f.country.add(new Option(a.country, a.country));
        f.country.value = a.country;
      }
      this.want = a.province;
      if (a.zip && f.zip.value === f.zip.defaultValue) f.zip.value = a.zip;
      if (!Array.isArray(s.rates)) return;
      if (s.signature === this.dataset.signature) this.show(s.rates, a);
      else this.timer = setTimeout(() => this.estimate(), 800);   // the cart changed since: estimate once more
    }
  });

  // ShrineCart.require('checkout') resolves to the main file's API object: it gets giftCards ({ add, remove }) here
  C.extras.giftCards = giftCards;
  if (C.api) C.api.giftCards = giftCards;
})();

/* Shrine PRO - cart upsells, theme cards. component-cart-upsells.js loads this file the first time a cart prints a
   <cart-upsell-item> (Cart page V2, per-item add-ons, upgrades), a price-band add-on or a cart attribute.
   - <cart-upsell-item>: Add, add-on switch and upgrade swap through ShrineCartRequests (one request renders every cart
     surface). On a store with the drawer a switch first mirrors its state onto the drawer's add-on card of the same
     product, so main.js keeps it after the render (A7).
   - Automatic requests, at most one per render and never the same within 8 s: price-band variant swap, per-item
     quantity, cart attribute. */
(() => {
  const w = window;
  const U = w.ShrineCartUpsells;
  if (!U || !U._ || U.auto) return;
  const { qsa, num, rootOf, inCart, isFilled, inert, setSel, decline, variants, paint, rate, emit, snap, sourceOf, clearError, showError, recent, TOGGLE, matchTarget, startQuantity } = U._;
  const d = document;
  const req = () => w.ShrineCartRequests;
  const sent = {};

  const mirror = (card, on) => {
    const dr = d.querySelector('cart-drawer');
    if (!dr || dr.contains(card)) return;
    qsa(TOGGLE + '[data-handle="' + card.dataset.handle + '"]', dr).forEach((e) => {
      if (inert(e)) return;
      setSel(e, on);
      if (!on) return;
      e.dataset.id = card.dataset.id;
      const i = e.querySelector('form [name="id"]');
      if (i) i.value = card.dataset.id;
    });
  };

  class CartUpsellItem extends HTMLElement {
    connectedCallback() {
      if (this.bound) return;
      this.bound = true;
      this.addEventListener('click', (e) => {
        const b = e.target.closest('[data-ups-action]');
        if (b && this.contains(b) && !b.disabled && !this.hasAttribute('aria-busy')) this.act(b.dataset.upsAction);
      });
      // a change inside a cart form reads as a quantity change to main.js
      this.addEventListener('change', (e) => {
        e.stopPropagation();
        if (e.target.matches && e.target.matches('[data-ups-quantity]')) return this.step(0);
        this.pick();
      });
    }
    // Quantity "Show quantity selector": the value an add-on goes in with; on a line in the cart, one change after the
    // shopper stops clicking
    step(delta) {
      const i = this.querySelector('[data-ups-quantity]');
      if (!i) return;
      const v = Math.max(1, Math.min(999, (Math.round(num(i.value)) || 1) + delta));
      i.value = v;
      const less = this.querySelector('[data-ups-action="less"]');
      if (less) less.disabled = v <= 1;
      clearTimeout(this.qtyTimer);
      if (this.dataset.upsInCart !== 'true' || v === num(this.dataset.upsLineQuantity)) return;
      this.qtyTimer = setTimeout(() => {
        const r = req();
        if (r) this.write('quantity', () => r.change({ key: this.dataset.upsLineKey, variantId: num(this.dataset.upsLineVariant) }, { quantity: v }, this.opts('upsells:quantity', 'update')));
      }, 450);
    }
    item(q) {
      const i = { id: num(this.dataset.id), quantity: q };
      if (this.dataset.upsSellingPlan) i.selling_plan = num(this.dataset.upsSellingPlan);
      return i;
    }
    opts(source, ev) {
      const root = rootOf(this);
      return { source, standardEvent: ev, context: root && root.matches('cart-drawer') ? 'dialog' : 'cart', focus: U.focusTarget };
    }
    pick() {
      const sels = qsa('.upsell__variant-picker select', this);
      const vals = sels.map((s) => s.value);
      const list = variants(this);
      let v = list.find((x) => vals.every((o, i) => x.options[i] === o));
      if (!v || !v.available) v = list.find((x) => x.available && x.options[0] === vals[0]) || v;
      if (!v) return;
      this.dataset.id = v.id;
      sels.forEach((s, i) => (s.value = v.options[i]));
      paint(this, v);
      const img = this.querySelector('.upsell__image__img');
      if (img && v.featured_image) img.src = v.featured_image.src;
      const b = this.querySelector('[data-ups-action]:not([data-ups-action="toggle"])');
      const t = b && b.querySelector('span');
      const host = this.closest('[data-ups-sold-out]');
      if (b) b.disabled = !v.available;
      if (t && host) {
        t.dataset.label = t.dataset.label || t.innerHTML;
        if (v.available) t.innerHTML = t.dataset.label;
        else t.textContent = host.dataset.upsSoldOut;
      }
      if (this.dataset.upsKind === 'upgrade') {
        const root = rootOf(this);
        const line = root && root.querySelector('.cart-item[data-variant-id="' + v.id + '"]');
        this.dataset.upsTargetKey = line ? line.dataset.lineKey : '';
        this.dataset.upsTargetQuantity = num(this.dataset.upsQuantity) + (line ? num(line.dataset.quantity) : 0);
      }
      if (this.dataset.upsKind === 'toggle' && this.dataset.upsInCart === 'true' && String(v.id) !== this.dataset.upsLineVariant)
        this.write('add', () => req().update({ updates: { [this.dataset.upsLineKey]: 0, [v.id]: num(this.dataset.upsLineQuantity) || 1 } }, this.opts('upsells:variant', 'update')));
    }
    act(kind) {
      if (kind === 'less' || kind === 'more') return this.step(kind === 'more' ? 1 : -1);
      const r = req();
      if (!r) return;
      const root = rootOf(this) || d;
      clearError(this);
      if (kind === 'add') return this.write('add', () => r.add([this.item(1)].concat(isFilled(root) ? [] : U.pendingAddonItems()), this.opts('upsells:add', 'add')));
      if (kind === 'upgrade')
        return this.write('upgrade', () => r.update({ updates: { [this.dataset.upsUpgradeKey]: 0, [this.dataset.upsTargetKey || this.dataset.id]: num(this.dataset.upsTargetQuantity) || 1 } }, this.opts('upsells:upgrade', 'update')), {
          replaced: { productId: num(this.dataset.upsUpgradeProduct) || null, variantId: num(this.dataset.upsUpgradeVariant) || null },
        });
      const on = this.dataset.selected !== 'true';
      const flip = (x) => {
        setSel(this, x);
        mirror(this, x);
      };
      // a matched add-on with nothing to match yet would be added and then removed by the per-item job
      const q = on ? startQuantity(this, root, !isFilled(root)) : 0;
      if (on && !q) return;
      flip(on);
      if (!isFilled(root)) decline(this.dataset.handle, !on);
      this.write(
        on ? 'add' : 'remove',
        () => (on ? r.add([this.item(q)], this.opts('upsells:toggle', 'add')) : r.change({ key: this.dataset.upsLineKey, variantId: num(this.dataset.upsLineVariant) }, { quantity: 0 }, this.opts('upsells:toggle', 'remove'))),
        null,
        () => flip(!on)
      );
    }
    write(action, run, extra, undo) {
      this.setAttribute('aria-busy', 'true');
      return run().then((res) => {
        this.removeAttribute('aria-busy');
        if (res && res.ok) return emit(action, Object.assign(snap(this, sourceOf(this)), extra));
        if (undo) undo();
        const e = res && res.error;
        // Shopify's own message for a refused change; never a technical one
        showError(this, e && e.code === 'cart' ? e.message : '');
      });
    }
  }
  if (!customElements.get('cart-upsell-item')) customElements.define('cart-upsell-item', CartUpsellItem);

  // price bands (on every build: re-applied after renders, as fixParsedHtml copies the old variant back without E12),
  // per-item quantity, cart attribute
  const jobs = (root) => {
    const r = req();
    const out = [];
    if (!r) return out;
    qsa('[data-ups-bands]', root).forEach((c) => {
      if (inert(c)) return;
      const k = rate((w.ShrineCart && w.ShrineCart.config && w.ShrineCart.config.shopCurrency) || '') || 1;
      const lim = c.dataset.upsBands.split(',').filter(Boolean);
      const vs = c.dataset.upsBandVariants.split(';').filter(Boolean).map((x) => x.split(':'));
      let i = lim.findIndex((l) => num(c.dataset.upsBandBase) <= num(l) * k);
      if (i < 0) i = lim.length;
      const v = vs[Math.min(i, vs.length - 1)];
      if (!v) return;
      if (c.dataset.id !== v[0]) {
        c.dataset.id = c.dataset.bandId = v[0];
        const inp = c.querySelector('form [name="id"]');
        if (inp) inp.value = v[0];
        paint(c, { price: v[1], compare_at_price: v[2] });
      }
      // the swapped line keeps its quantity: the matched count, or what the shopper chose
      const q = c.dataset.upsPerItem ? matchTarget(c, root) || 1 : c.dataset.upsQtyMode === 'selector' ? num(c.dataset.upsLineQuantity) || 1 : 1;
      if (c.dataset.upsInCart === 'true' && c.dataset.upsLineVariant !== v[0])
        out.push(['band:' + c.dataset.handle + ':' + v[0], () => r.update({ updates: { [c.dataset.upsLineKey]: 0, [v[0]]: q } }, { source: 'upsells:price-band', standardEvent: 'update' })]);
    });
    qsa('[data-ups-per-item="true"][data-ups-in-cart="true"]', root).forEach((c) => {
      const t = matchTarget(c, root);
      if (t !== num(c.dataset.upsLineQuantity))
        out.push(['item:' + c.dataset.handle + ':' + t, () => r.change({ key: c.dataset.upsLineKey, variantId: num(c.dataset.upsLineVariant) }, { quantity: t }, { source: 'upsells:per-item', standardEvent: 'update' })]);
    });
    qsa('[data-ups-attribute]', root).forEach((c) => {
      const n = c.dataset.upsAttribute;
      const want = c.dataset.upsInCart === 'true' ? 'true' : '';
      // render: false leaves the printed value stale until the next render: remember what was sent
      if ((n in sent ? sent[n] : c.dataset.upsAttributeValue) !== want)
        out.push(['attr:' + n + ':' + want, () => {
          sent[n] = want;
          return r.update({ attributes: { [n]: want } }, { source: 'upsells:attribute', render: false, publish: false, standardEvent: null });
        }]);
    });
    return out;
  };
  U.auto = (root) => {
    const job = jobs(root).find((j) => !(recent[j[0]] && Date.now() - recent[j[0]] < 8e3));
    if (!job) return;
    recent[job[0]] = Date.now();
    job[1]();
  };
  U.sync();
})();

/* Quantity breaks V2 nudge in the cart (blocks/cart_quantity-breaks-nudge.liquid): <qb-v2-cart-nudge> offers the next
   quantity deal of a product in the cart, from the tiers Quantity breaks V2 stored when the shopper opened that
   product (localStorage 'shrine-qb-tiers', written by component-quantity-breaks-v2-extras.js). main.js replaces the
   drawer's HTML on every cart change, so each render starts from connectedCallback. */
(() => {
  if (customElements.get('qb-v2-cart-nudge')) return;

  const escapeHtml = (value) => String(value == null ? '' : value).replace(/[&<>"']/g, (char) => `&#${char.charCodeAt(0)};`);
  const fill = (text, values) => String(text || '').replace(/\[([a-z_]+)\]/g, (match, key) => (key in values ? values[key] : match));
  const parse = (text, fallback) => {
    try {
      return JSON.parse(text);
    } catch (error) {
      return fallback;
    }
  };
  const readTiers = () => {
    try {
      const data = JSON.parse(window.localStorage.getItem('shrine-qb-tiers') || 'null');
      return data && data.v === 1 && data.products && typeof data.products === 'object' ? data.products : {};
    } catch (error) {
      return {};
    }
  };
  const each = (tier) => (tier.s || 0) / Math.max(1, tier.q);

  class QuantityBreaksCartNudge extends HTMLElement {
    connectedCallback() {
      try {
        this.render();
      } catch (error) {
        console.error('Quantity breaks V2', error);
      }
    }

    render() {
      const text = this.querySelector('.qb-v2-cart-nudge__text');
      const button = this.querySelector('.qb-v2-cart-nudge__button');
      if (!text) return;
      const offer = this.offer();
      this.current = offer;
      if (!offer) {
        // An empty text keeps the whole block hidden (CSS)
        text.textContent = '';
        if (button) button.hidden = true;
        return;
      }
      const values = {
        missing_quantity: offer.missing,
        title: escapeHtml(offer.item.title || offer.entry.t || ''),
        next_title: escapeHtml(offer.tier.title || ''),
        next_saving: offer.tier.p > 0 ? `${offer.tier.p}%` : this.money(offer.tier.s),
      };
      text.innerHTML = fill(this.dataset.text, values);
      if (!button) return;
      const label = fill(this.dataset.buttonLabel, values).trim();
      button.textContent = label;
      button.hidden = !label;
      if (!this.bound) {
        this.bound = true;
        button.addEventListener('click', () => this.raise());
      }
    }

    // The cart product closest to a better tier (fewest units missing; on a tie, the bigger percentage)
    offer() {
      const tiers = readTiers();
      const items = parse(this.dataset.items || '[]', []);
      let best = null;
      (Array.isArray(items) ? items : []).forEach((item) => {
        const entry = item && tiers[item.handle];
        if (!entry || !Array.isArray(entry.tiers)) return;
        const quantity = Number(item.quantity) || 0;
        // Money savings stored in another currency are never shown; percentages hold in every currency
        const sameCurrency = !entry.cur || entry.cur === this.dataset.currency;
        const list = entry.tiers.filter((tier) => tier && tier.q > 0 && (sameCurrency || tier.p > 0));
        const reached = list.filter((tier) => tier.q <= quantity).sort((a, b) => b.q - a.q)[0];
        const tier = list
          .filter((tier) => tier.q > quantity && (!reached || tier.p > reached.p || (tier.p === reached.p && each(tier) > each(reached))))
          .sort((a, b) => a.q - b.q)[0];
        if (!tier) return;
        const missing = tier.q - quantity;
        if (!best || missing < best.missing || (missing === best.missing && tier.p > best.tier.p)) best = { item, entry, tier, missing };
      });
      return best;
    }

    money(cents) {
      const format = this.dataset.moneyFormat || '{{amount}}';
      if (typeof formatMoney === 'function') {
        try {
          return formatMoney(cents, format);
        } catch (error) {
          // Falls back to the browser's currency format
        }
      }
      try {
        return new Intl.NumberFormat(document.documentElement.lang || undefined, { style: 'currency', currency: this.dataset.currency }).format(cents / 100);
      } catch (error) {
        return (cents / 100).toFixed(2);
      }
    }

    // Raises the product's first line by the missing units: /cart/change sets one line's quantity (M:428-441), and the
    // product's other lines already count toward the tier
    raise() {
      const offer = this.current;
      if (!offer) return;
      // 2.0.0 carts: one key-based request renders every cart surface (drawer, cart page, Cart page V2)
      const requests = window.ShrineCartRequests;
      if (requests && typeof requests.change === 'function' && offer.item.key) {
        const button = this.querySelector('.qb-v2-cart-nudge__button');
        const quantity = (Number(offer.item.line_quantity) || 0) + offer.missing;
        if (button) {
          button.disabled = true;
          button.setAttribute('aria-busy', 'true');
        }
        requests.change({ key: offer.item.key, variantId: offer.item.variant_id }, { quantity }, { source: 'upsells:qb-nudge', standardEvent: 'update' }).then((result) => {
          // A successful render brings a fresh nudge; this one only reports a failure
          if (!this.isConnected) return;
          if (button) {
            button.disabled = false;
            button.removeAttribute('aria-busy');
          }
          const text = this.querySelector('.qb-v2-cart-nudge__text');
          // Shopify's own message for a refused change (e.g. stock); a network failure just re-enables the button
          if (text && result && !result.ok && result.error && result.error.code === 'cart' && result.error.message) {
            text.textContent = result.error.message;
            text.setAttribute('role', 'alert');
          }
        });
        return;
      }
      const inDrawer = Boolean(this.closest('cart-drawer'));
      const items = (inDrawer ? document.querySelector('cart-drawer-items') : document.querySelector('cart-items')) || document.querySelector('cart-drawer-items') || document.querySelector('cart-items');
      if (!items || typeof items.updateQuantity !== 'function') return;
      const line = Number(offer.item.line) || 1;
      const quantity = (Number(offer.item.line_quantity) || 0) + offer.missing;
      // updateQuantity compares the cart's answer with this input (M:444, M:477): set first, or Shopify's quantity error shows
      const input = inDrawer
        ? document.getElementById(`Drawer-quantity-${line}`) || document.getElementById(`Quantity-${line}`)
        : document.getElementById(`Quantity-${line}`) || document.getElementById(`Drawer-quantity-${line}`);
      if (input) input.value = quantity;
      const button = this.querySelector('.qb-v2-cart-nudge__button');
      if (button) button.disabled = true;
      // The cart's new HTML brings a fresh nudge; one the update didn't re-render holds a taken offer and goes
      const settle = () => {
        if (!this.isConnected) return;
        const text = this.querySelector('.qb-v2-cart-nudge__text');
        if (text) text.textContent = '';
        if (button) button.hidden = true;
      };
      Promise.resolve(items.updateQuantity(String(line), quantity)).then(settle, settle);
    }
  }

  customElements.define('qb-v2-cart-nudge', QuantityBreaksCartNudge);
})();

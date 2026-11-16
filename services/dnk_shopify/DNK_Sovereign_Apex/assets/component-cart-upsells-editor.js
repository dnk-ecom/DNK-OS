/* Shrine PRO - cart upsells, theme editor only. component-cart-upsells.js loads it in design mode from
   #shrine-cart-config (assets.upsells.editor). Notices go through ShrineCart.notices / ShrineCart.editor and never
   reach shoppers.
   - "shows X, but the cart would charge Y": a display-only upsell discount without a matching automatic discount
   - an add-on product used twice, an add-on that counts in the item count, an add-on switch inside the Empty cart
   - no recommendations for this cart
   - V2 chunks the editor re-rendered without their Product upsells V2 block: their [[ups:…]] tokens and parts are
     filled the way the block does it */
(() => {
  if (window.ShrineCartUpsellsEditor) return;
  window.ShrineCartUpsellsEditor = { version: 1 };
  if (!(window.Shopify && window.Shopify.designMode)) return;

  const core = () => window.ShrineCart || null;
  const nameOf = (el) => {
    const b = el.closest('[data-ups-v]');
    return b && b.dataset.upsV === '2' ? 'Product upsells V2' : 'Product upsells';
  };
  const titleOf = (el) => {
    const h = el.querySelector('.upsell__title h3, h3');
    return (h && h.textContent.trim()) || el.dataset.handle || '';
  };
  const blockOf = (el) => {
    const block = el.closest('[data-ups-block]');
    return block ? block.dataset.upsBlock : undefined;
  };
  const money = (cents) => {
    const c = core();
    try {
      if (c && c.money && typeof c.money.format === 'function') return c.money.format(cents);
    } catch (e) {}
    return (cents / 100).toFixed(2);
  };

  // ---------------------------------------------------------------- checks that read the rendered cart
  const domChecks = (ctx) => {
    const root = (ctx && ctx.root) || document;
    const out = [];
    const byHandle = {};
    root.querySelectorAll('cart-drawer-upsell[data-toggle="true"], cart-drawer-gift').forEach((el) => {
      const handle = el.dataset.handle;
      if (!handle) return;
      (byHandle[handle] = byHandle[handle] || []).push(el);
    });
    Object.keys(byHandle).forEach((handle) => {
      const list = byHandle[handle];
      if (list.length < 2) return;
      const card = list.find((el) => el.matches('cart-drawer-upsell')) || list[0];
      out.push({ code: 'upsells-duplicate-' + handle, level: 'error', title: nameOf(card), blockId: blockOf(card),
        text: titleOf(card) + ' is used twice as an add-on or gift. Use each add-on product once.' });
    });
    root.querySelectorAll('cart-drawer-upsell[data-toggle="true"][data-ups-tagged="false"]').forEach((card) => {
      out.push({ code: 'upsells-addon-count-' + card.dataset.handle, level: 'info', title: nameOf(card), blockId: blockOf(card),
        text: titleOf(card) + " counts in the cart's item count. Tag it cart-hidden to leave it out." });
    });
    if (root.querySelector('.drawer__inner-empty cart-drawer-upsell[data-toggle="true"]')) {
      out.push({ code: 'upsells-empty-cart-toggle', level: 'error', title: 'Empty cart',
        text: 'an add-on switch shows here and can mix up add-on choices. Remove it, or use the Add button style.' });
    }
    return out;
  };

  // ---------------------------------------------------------------- no recommendations (the main file marks the host "empty")
  const recsNotice = (host) => {
    const c = core();
    const id = blockOf(host) || host.id;
    if (!c || !c.notices || !id) return;
    if (host.dataset.upsRecsState === 'empty')
      c.notices.set('upsells-recs-empty-' + id, { level: 'info', title: nameOf(host), blockId: id,
        text: 'no recommendations for this cart. Set up products in the Search & Discovery app, or add products to show instead.' });
    else if (host.dataset.upsRecsState === 'done') c.notices.clear('upsells-recs-empty-' + id);
  };
  new MutationObserver((records) => records.forEach((r) => recsNotice(r.target))).observe(document.documentElement, {
    subtree: true,
    attributes: true,
    attributeFilter: ['data-ups-recs-state'],
  });

  // ---------------------------------------------------------------- display-only discounts (T13)
  let timer = 0;
  let shown = new Set();
  const checkOffers = async () => {
    const c = core();
    const editor = c && c.editor;
    const notices = c && c.notices;
    const requests = window.ShrineCartRequests;
    if (!editor || typeof editor.checkDiscounts !== 'function' || !notices || !requests || typeof requests.getCart !== 'function') return;
    const cards = [...document.querySelectorAll('[data-ups-offer-cents][data-ups-uid]')].filter((card) => !card.closest('[data-ups-placeholder]'));
    const cart = cards.length ? await requests.getCart() : null;
    const lines = cart && Array.isArray(cart.items) ? cart.items.map((i) => ({ variantId: i.variant_id, quantity: i.quantity })) : [];
    const next = new Set();
    for (const card of cards) {
      const variantId = Number(card.dataset.id);
      const price = Number(card.dataset.upsPrice);
      const code = 'upsells-discount-' + card.dataset.upsUid;
      // a variant already in the cart would merge with the test line
      if (!variantId || !cart || lines.some((l) => Number(l.variantId) === variantId)) continue;
      let result = null;
      try {
        result = await editor.checkDiscounts(lines.concat({ variantId, quantity: 1 }), { country: c.config && c.config.country });
      } catch (e) {
        result = null;
      }
      if (!result || (result.errors && result.errors.length)) continue;
      const test = (result.lines || []).find((l) => Number(l.variantId) === variantId && Number(l.quantity) === 1);
      if (!test || !(Number(test.totalCents) > price + 1)) continue;
      next.add(code);
      notices.set(code, { level: 'warning', title: nameOf(card), blockId: blockOf(card),
        text: titleOf(card) + ' shows ' + money(price) + ', but the cart would charge ' + money(Number(test.totalCents)) + '. Create a matching automatic discount.' });
    }
    shown.forEach((code) => {
      if (!next.has(code)) notices.clear(code);
    });
    shown = next;
  };
  const schedule = () => {
    clearTimeout(timer);
    timer = setTimeout(() => {
      checkOffers().catch(() => {});
    }, 2000);
  };

  // ---------------------------------------------------------------- V2 chunks re-rendered without their block (05 §13)
  const cut = (html, start, end) => {
    const a = html.indexOf(start);
    const b = a < 0 ? -1 : html.indexOf(end, a);
    return b < 0 ? html : html.slice(0, a) + html.slice(b + end.length);
  };
  const choiceOf = (el) => {
    for (let n = el.previousSibling; n; n = n.previousSibling) {
      if (n.nodeType === 8 && n.data.indexOf('ups2:card|') === 0) return n.data.split('|')[9] || '0';
      if (n.nodeType === 1 && n.matches('[data-ups-uid]')) break;
    }
    return '0';
  };
  const repair = (root, el) => {
    const t = root.dataset;
    let html = el.outerHTML;
    if (html.indexOf('[[ups:') < 0) return;
    const sel = el.dataset.upsSelShown || (el.querySelector('[data-ups-sel-shown]') || { dataset: {} }).dataset.upsSelShown || 'false';
    const tokens = { add_class: t.upsTAddClass || '', add_label: t.upsTAddLabel || '', toggle_class: t.upsTToggleClass || '', toggle_role: t.upsTToggleRole || 'switch',
      toggle_inner: t.upsTToggleInner || '', savings: t.upsTSavings || '', selected: sel, media: 'all' };
    html = html.replace(/\[\[ups:([a-z_]+)\]\]/g, (m, k) => (k in tokens ? tokens[k] : m));
    const picker = t.upsTPicker !== 'false';
    if (!picker) html = cut(html, '<!--ups2:picker-->', '<!--/ups2:picker-->');
    if (choiceOf(el) !== '0' && html.indexOf('<!--ups2:choose-->') > -1)
      html = picker && html.indexOf('upsell__variant-picker') > -1 ? cut(html, '<!--ups2:choose-->', '<!--/ups2:choose-->') : cut(html, '<!--ups2:add-->', '<!--/ups2:add-->');
    const tpl = document.createElement('template');
    tpl.innerHTML = html;
    el.replaceWith(tpl.content);
  };
  const watchV2 = (root) => {
    if (root.shrineRepair) return;
    root.shrineRepair = new MutationObserver((records) =>
      records.forEach((r) => r.addedNodes.forEach((n) => n.nodeType === 1 && n.isConnected && repair(root, n)))
    );
    root.shrineRepair.observe(root, { childList: true, subtree: true });
  };
  const watchAll = () => document.querySelectorAll('cart-upsells').forEach(watchV2);

  const start = (editorApi) => {
    const c = core();
    const editor = editorApi || (c && c.editor);
    if (editor && typeof editor.registerCheck === 'function') editor.registerCheck('upsells', domChecks);
    if (c && typeof c.onRender === 'function')
      c.onRender(() => {
        watchAll();
        schedule();
      });
    document.addEventListener('shopify:section:load', watchAll);
    document.addEventListener('shopify:block:select', watchAll);
    document.querySelectorAll('[data-ups-recs-state]').forEach(recsNotice);
    watchAll();
    schedule();
  };
  const c = core();
  if (c && typeof c.require === 'function') c.require('editor').then(start, () => start(null));
  else start(null);
})();

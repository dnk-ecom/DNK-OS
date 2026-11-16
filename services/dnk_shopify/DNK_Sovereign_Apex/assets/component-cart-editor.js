/* Shrine cart editor helper (theme editor only, loader key "editor"): opens the drawer when its section or a block is
   selected, runs the editor checks after every render, renders the notice stacks and checks discounts with a throwaway
   Storefront cart. Never loaded on the storefront. Classic script, safe to run twice. */
(() => {
  if (!(window.Shopify && window.Shopify.designMode) || window.ShrineCartEditor) return;
  const SC = window.ShrineCart;
  if (!SC) return;
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
  const store = {
    get: (s, k) => att(() => w[s].getItem(k), null),
    set: (s, k, v) => att(() => w[s].setItem(k, v)),
  };
  const drawer = () => qs('cart-drawer');
  const isOpen = () => !!att(() => drawer().classList.contains('active'), false);
  const NEW_KEY = 'shrine-cart-editor-new-2-0';

  // #region blocks of the preview
  const blockIdOf = (el) => {
    const host = el && el.closest && el.closest('[data-shopify-editor-block]');
    if (!host) return null;
    const raw = host.getAttribute('data-shopify-editor-block') || '';
    return att(() => JSON.parse(raw).id, null) || null;
  };
  const findBlock = (id) =>
    id
      ? qsa('[data-shopify-editor-block]').find((el) => {
          const raw = el.getAttribute('data-shopify-editor-block') || '';
          const parsed = att(() => JSON.parse(raw).id, null);
          return parsed ? parsed === id : raw.indexOf(id) > -1;
        }) || null
      : null;
  const flash = (el) => {
    if (!el) return;
    att(() => el.scrollIntoView({ block: 'nearest' }));
    el.classList.add('cart-editor-flash');
    setTimeout(() => el.classList.remove('cart-editor-flash'), 2000);
  };
  // #endregion

  // #region notices
  const checkList = new Map(); // 'surface:code' -> notice (from checks)
  const owned = new Map(); // 'check|surface' -> Set of 'surface:code'
  const stacks = () => qsa('[data-cart-notices]');
  const surfaceOf = (stack) => (stack.closest('cart-drawer') ? 'drawer' : stack.closest('cart-page') ? 'page-v2' : 'page');
  const defaultSurface = () => (stacks().some((s) => surfaceOf(s) === 'drawer') ? 'drawer' : 'page-v2');
  const noticeEl = (n) => {
    const p = d.createElement('p');
    p.className = 'cart-editor-notice cart-editor-notice--' + (n.level || 'info');
    p.setAttribute('data-cart-notice', n.code);
    p.setAttribute('role', 'note');
    const strong = d.createElement('strong');
    strong.textContent = (n.title || '') + ':';
    const small = d.createElement('small');
    small.textContent = 'Only visible in the theme editor.';
    p.append(strong, ' ' + (n.text || '') + ' ', small);
    if (n.blockId) {
      p.dataset.blockId = n.blockId;
      p.classList.add('cart-editor-notice--link');
    }
    if (n.dismissible) {
      const b = d.createElement('button');
      b.type = 'button';
      b.className = 'cart-editor-notice__dismiss';
      b.textContent = 'Dismiss';
      b.dataset.dismiss = n.code;
      p.append(b);
    }
    return p;
  };
  const renderNotices = () => {
    const all = stacks();
    const dflt = defaultSurface();
    all.forEach((stack) => {
      const surface = surfaceOf(stack);
      const list = [];
      checkList.forEach((n) => n.surface === surface && list.push(n));
      att(() =>
        SC.notices.list.forEach((n, code) => {
          const s = n.surface || dflt;
          if (s === surface && !list.some((x) => x.code === code)) list.push(Object.assign({ code }, n));
        })
      );
      const order = { error: 0, warning: 1, info: 2 };
      list.sort((a, b) => (order[a.level] == null ? 3 : order[a.level]) - (order[b.level] == null ? 3 : order[b.level]));
      const sig = JSON.stringify(list.map((n) => [n.code, n.level, n.title, n.text, n.blockId || '', !!n.dismissible]));
      if (stack.dataset.sig === sig) return;
      stack.dataset.sig = sig;
      stack.replaceChildren(...list.map(noticeEl));
    });
  };
  on(d, 'click', (e) => {
    const t = e.target;
    const dismiss = t.closest && t.closest('[data-cart-notices] [data-dismiss]');
    if (dismiss) {
      const code = dismiss.dataset.dismiss;
      if (code === 'core-new-2-0') store.set('localStorage', NEW_KEY, '1');
      checkList.forEach((n, k) => n.code === code && checkList.delete(k));
      att(() => SC.notices.list.delete(code));
      renderNotices();
      return;
    }
    const link = t.closest && t.closest('[data-cart-notices] [data-block-id]');
    if (link) flash(findBlock(link.dataset.blockId));
  });
  // #endregion

  // #region checks
  const runCheck = (name, fn, ctx) => {
    const surface = (ctx && ctx.surface) || 'drawer';
    const key = name + '|' + surface;
    let out = [];
    try {
      out = fn(ctx) || [];
    } catch (e) {
      console.error('[Shrine cart] editor check "' + name + '" failed', e);
      return;
    }
    (owned.get(key) || new Set()).forEach((k) => checkList.delete(k));
    const mine = new Set();
    (Array.isArray(out) ? out : []).forEach((n) => {
      if (!n || !n.code) return;
      const k = surface + ':' + n.code;
      checkList.set(k, Object.assign({}, n, { surface }));
      mine.add(k);
    });
    owned.set(key, mine);
  };
  const run = (ctx) => {
    if (!ctx || ctx.surface === 'page') return;
    SC.editor.checks.forEach((fn, name) => runCheck(name, fn, ctx));
    renderNotices();
  };
  const contexts = () => {
    const out = [];
    const cd = d.getElementById('CartDrawer');
    if (cd) out.push({ surface: 'drawer', root: cd });
    qsa('cart-page').forEach((root) => out.push({ surface: 'page-v2', root }));
    return out;
  };
  const runAll = () => contexts().forEach(run);

  const cartRootOf = (ctx) => (ctx.surface === 'drawer' ? drawer() : ctx.root && ctx.root.closest ? ctx.root.closest('.cart-root') || ctx.root : null);
  const notice = (code, level, title, text, el) => ({ code, level, title, text, blockId: el ? blockIdOf(el) : null });
  const coreCheck = (ctx) => {
    const root = cartRootOf(ctx);
    if (!root) return [];
    const v2 = ctx.surface === 'page-v2';
    const form = v2 ? 'CartPage-Form' : 'CartDrawer-Form';
    const checkout = v2 ? 'CartPage-Checkout' : 'CartDrawer-Checkout';
    const filled = !root.classList.contains('is-empty');
    const out = [];
    const forms = qsa('[id="' + form + '"]', root);
    const outs = qsa('[id="' + checkout + '"]', root);
    if (forms.length > 1) out.push(notice('core-duplicate-items', 'error', 'Cart items', 'added twice. Remove one; a second copy breaks quantity changes and checkout.', forms[1]));
    if (!v2 && filled && !forms.length) out.push(notice('core-no-items', 'error', 'Cart drawer', "no Cart items block. Add one to Cart body, or customers can't see their items or check out."));
    if (outs.length > 1) out.push(notice('core-duplicate-checkout', 'warning', 'Checkout button', "there are two. Delete the one you don't use (recipes such as Split footer bring their own).", outs[1]));
    const buttons = qsa('[name="checkout"]', root).filter((b) => !b.closest('cart-compact-bar, [data-cart-page-bar]'));
    if (filled && !buttons.length) out.push(notice('core-no-checkout', 'warning', v2 ? 'Cart page V2' : 'Cart drawer', 'no Checkout button. Add one to ' + (v2 ? 'Summary' : 'Cart footer') + '.'));
    const totals = qsa('.cart-drawer__totals', root);
    if (totals.length > 1) out.push(notice('core-duplicate-subtotals', 'warning', 'Subtotals', "there are two. Delete the one you don't use (recipes such as Split footer bring their own).", totals[1]));
    if (!v2) {
      const bad = qsa('.cart-side-panel', root).map((p) => qs('#CartDrawer-Form, #CartDrawer-Checkout, .cart-drawer__totals', p)).find(Boolean);
      if (bad) out.push(notice('core-side-panel-checkout', 'warning', 'Side panel', 'it holds Cart items, Subtotals or the Checkout button. Move them to Cart body or Cart footer.', bad));
      if (SC.config.afterAdd === 'message' && !SC.has('afterAdd')) {
        out.push(notice('core-after-add-needs-update', 'warning', 'Theme settings', '"Show a message" after adding to cart isn\'t live on this store yet, so the cart drawer still opens. It starts working by itself once Shrine\'s script update is live.'));
      }
      if (root.classList.contains('is-empty') && qs('#CartDrawer .cart-item', root)) {
        out.push(notice('core-preview-empty', 'info', 'Cart drawer', 'showing the empty cart preview. Set Test mode > Preview to Current cart to see the items.'));
      }
    }
    const marks = [];
    qsa('[data-cart-override]', root).forEach((el) => {
      const [name, labels] = String(el.getAttribute('data-cart-override') || '').split('|');
      const item = name ? name + (labels ? ' (' + labels + ')' : '') : '';
      if (item && marks.indexOf(item) < 0) marks.push(item);
    });
    if (marks.length) out.push(notice('core-overrides', 'info', 'Cart style', marks.join(', ') + (marks.length === 1 ? ' keeps its own look. Set it to Same as cart to follow the style.' : ' keep their own look. Set them to Same as cart to follow the style.')));
    return out;
  };
  // #endregion

  // #region New in 2.0.0
  const newNotice = () => {
    if (store.get('localStorage', NEW_KEY) === '1') return;
    att(() =>
      SC.notices.list.set('core-new-2-0', {
        code: 'core-new-2-0',
        level: 'info',
        title: 'New in 2.0.0',
        text: 'cart styles, Subscribe & save, a Rewards bar, Product upsells V2, a two-column layout and more. Start with ' + (defaultSurface() === 'drawer' ? 'Cart drawer' : 'Cart page V2') + ' > Style.',
        surface: defaultSurface(),
        dismissible: true,
      })
    );
  };
  // #endregion

  // #region auto-open (plan §4.6)
  let closeTimer = 0;
  let wasOpen = false;
  let hiddenShown = false;
  const ours = (e) => ((e && e.detail) || {}).sectionId === 'cart-drawer';
  const open = () => {
    clearTimeout(closeTimer);
    const dr = drawer();
    if (dr && !isOpen() && typeof dr.open === 'function') att(() => dr.open());
  };
  const afterOpen = (fn) => {
    const dr = drawer();
    let done = false;
    const go = () => {
      if (done) return;
      done = true;
      fn();
    };
    if (dr) on(dr, 'transitionend', go, { once: true });
    setTimeout(go, 300);
  };
  on(d, 'shopify:section:select', (e) => ours(e) && open());
  on(d, 'shopify:block:select', (e) => {
    if (hiddenShown) {
      hiddenShown = false;
      att(() => SC.notices.list.delete('core-hidden-block'));
      renderNotices();
    }
    if (!ours(e)) return;
    const id = (e.detail || {}).blockId;
    const wasClosed = !isOpen();
    open();
    const el = findBlock(id) || (e.target && e.target.nodeType === 1 && e.target.matches('[data-shopify-editor-block]') ? e.target : null);
    if (!el) {
      hiddenShown = true;
      att(() =>
        SC.notices.list.set('core-hidden-block', {
          code: 'core-hidden-block',
          level: 'info',
          title: 'Cart drawer',
          text: "this block isn't in the preview. Empty cart blocks show when the cart is empty: turn on Test mode and set Preview to Empty cart.",
          surface: 'drawer',
        })
      );
      renderNotices();
    } else if (wasClosed) afterOpen(() => att(() => el.scrollIntoView({ block: 'nearest' })));
    else att(() => el.scrollIntoView({ block: 'nearest' }));
    runAll();
  });
  const deselect = (e) => {
    if (!ours(e)) return;
    clearTimeout(closeTimer);
    closeTimer = setTimeout(() => {
      const dr = drawer();
      if (dr && dr.getAttribute('data-test-mode') !== 'true' && isOpen() && typeof dr.close === 'function') att(() => dr.close());
    }, 150);
  };
  on(d, 'shopify:section:deselect', deselect);
  on(d, 'shopify:block:deselect', deselect);
  on(d, 'shopify:section:unload', (e) => {
    if (ours(e)) wasOpen = isOpen();
  });
  on(d, 'shopify:section:load', (e) => {
    if (ours(e)) {
      const reopen = wasOpen;
      wasOpen = false;
      setTimeout(() => {
        if (reopen) open();
        newNotice();
        runAll();
      }, 0);
    } else setTimeout(runAll, 0);
  });
  // #endregion

  // #region checkDiscounts (A26)
  const QUERY =
    'mutation ShrineCartDiscountCheck($input: CartInput!) { cartCreate(input: $input) { cart { id lines(first: 50) { nodes { quantity merchandise { ... on ProductVariant { id } } ' +
    'cost { subtotalAmount { amount currencyCode } totalAmount { amount currencyCode } } discountAllocations { __typename discountedAmount { amount currencyCode } ' +
    '... on CartAutomaticDiscountAllocation { title } ... on CartCodeDiscountAllocation { code } ... on CartCustomDiscountAllocation { title } } } } ' +
    'discountCodes { code applicable } } userErrors { field message code } warnings { code message } } }';
  const API = '/api/2026-10/graphql.json';
  const cents = (m) => Math.round(parseFloat((m && m.amount) || 0) * 100) || 0;
  const idOf = (gid) => String(gid || '').split('/').pop();
  const hash = (s) => {
    let h = 0x811c9dc5;
    for (let i = 0; i < s.length; i++) h = Math.imul(h ^ s.charCodeAt(i), 0x01000193) >>> 0;
    return h.toString(16);
  };
  let calls = 0;
  let gate = Promise.resolve();
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const send = async (body) => {
    const opts = { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body };
    const urls = [API];
    if (w.Shopify && w.Shopify.shop) urls.push('https://' + w.Shopify.shop + API);
    let last = 'network';
    for (const url of urls) {
      try {
        const r = await fetch(url, opts);
        if (r.ok) return { json: await r.json() };
        last = 'HTTP ' + r.status;
      } catch (e) {
        last = 'network';
      }
    }
    return { failed: last };
  };
  const checkDiscounts = (lines, o) => {
    o = o || {};
    const list = (lines || []).filter((l) => l && l.variantId).map((l) => ({ variantId: String(l.variantId), quantity: Number(l.quantity) || 1, sellingPlanId: l.sellingPlanId || null }));
    const codes = (o.discountCodes || []).filter(Boolean).map(String);
    const country = o.country || SC.config.country || null;
    const key = 'shrine-cart-check:' + hash(JSON.stringify([list, codes, country]));
    const cached = att(() => JSON.parse(store.get('sessionStorage', key)), null);
    if (cached && cached.t && Date.now() - cached.t < 600000 && cached.result) return Promise.resolve(cached.result);
    const result = { lines: [], currency: null, warnings: [], errors: [] };
    if (!list.length) return Promise.resolve(result);
    const job = gate.then(async () => {
      if (calls >= 8) return Object.assign(result, { errors: ['limit'] });
      calls++;
      const input = {
        lines: list.map((l) => {
          const x = { merchandiseId: 'gid://shopify/ProductVariant/' + l.variantId, quantity: l.quantity };
          if (l.sellingPlanId) x.sellingPlanId = 'gid://shopify/SellingPlan/' + l.sellingPlanId;
          return x;
        }),
      };
      if (country) input.buyerIdentity = { countryCode: country };
      if (codes.length) input.discountCodes = codes;
      const body = JSON.stringify({ query: QUERY, variables: { input } });
      let res = await send(body);
      const throttled = (j) => j && Array.isArray(j.errors) && j.errors.some((e) => ((e && e.extensions) || {}).code === 'THROTTLED');
      if (res.json && throttled(res.json)) {
        await sleep(2000);
        res = await send(body);
      }
      if (res.failed) return Object.assign(result, { errors: ['request failed (' + res.failed + ')'], failed: true });
      const j = res.json || {};
      if (Array.isArray(j.errors) && j.errors.length) {
        j.errors.forEach((e) => result.errors.push(((e && e.extensions) || {}).code || (e && e.message) || 'error'));
        return result;
      }
      const cc = j.data && j.data.cartCreate;
      if (!cc) return Object.assign(result, { errors: ['cartCreate returned nothing'] });
      (cc.userErrors || []).forEach((e) => result.errors.push((e && e.message) || (e && e.code) || 'error'));
      (cc.warnings || []).forEach((wn) => {
        const code = (wn && wn.code) || '';
        if (code) result.warnings.push(code);
        if (/^MERCHANDISE_/.test(code) || code === 'PRODUCT_UNAVAILABLE_IN_BUYER_LOCATION') result.errors.push(code);
      });
      const nodes = att(() => cc.cart.lines.nodes, []) || [];
      nodes.forEach((n) => {
        const allocs = n.discountAllocations || [];
        const titles = [];
        allocs.forEach((a) => {
          const t = a && (a.title || a.code);
          if (t && titles.indexOf(t) < 0) titles.push(t);
        });
        result.lines.push({
          variantId: idOf(att(() => n.merchandise.id, '')),
          quantity: Number(n.quantity) || 0,
          subtotalCents: cents(att(() => n.cost.subtotalAmount, null)),
          discountedCents: allocs.reduce((s, a) => s + cents(a && a.discountedAmount), 0),
          totalCents: cents(att(() => n.cost.totalAmount, null)),
          titles,
        });
        if (!result.currency) result.currency = att(() => n.cost.totalAmount.currencyCode, null) || null;
      });
      const want = {};
      list.forEach((l) => (want[l.variantId] = (want[l.variantId] || 0) + l.quantity));
      const got = {};
      result.lines.forEach((l) => (got[l.variantId] = (got[l.variantId] || 0) + l.quantity));
      if (Object.keys(want).some((k) => want[k] !== got[k])) result.errors.push('quantity mismatch');
      return result;
    });
    gate = job.then(() => sleep(300), () => sleep(300));
    return job.then((r) => {
      if (!r.failed && r.errors.indexOf('limit') < 0) store.set('sessionStorage', key, JSON.stringify({ t: Date.now(), result: r }));
      delete r.failed;
      return r;
    });
  };
  // #endregion

  const api = {
    version: 1,
    run,
    runAll,
    renderNotices,
    registerCheck: (name, fn) => SC.editor.registerCheck(name, fn),
    checkDiscounts,
  };
  window.ShrineCartEditor = api;
  SC.editor.registerCheck('core', coreCheck);
  SC.editor.checkDiscounts = checkDiscounts;
  newNotice();
  runAll();
  if (!contexts().length) renderNotices();
  SC.provide('editor', api);
})();

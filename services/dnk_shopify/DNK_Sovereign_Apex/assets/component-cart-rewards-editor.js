/* Shrine PRO cart rewards: theme editor checks (design mode only; 04-rewards §7.8). component-cart-rewards.js loads this
   file from #shrine-cart-config.assets.rewards.editor when Shopify.designMode is on; shoppers never download it.
   - registers the check 'rewards' with ShrineCart.editor (notices about gift products, paid gift lines, gifts that are off)
   - runs the reward discount check through ShrineCart.editor.checkDiscounts (Storefront API, a throwaway cart)
   - asks for a fresh render when a Reward was refreshed on its own and shows raw [[rw:…]] tokens */
(() => {
  if (window.ShrineCartRewardsEditor || !(window.Shopify && window.Shopify.designMode)) return;
  const w = window;
  const d = document;
  const num = (v) => parseFloat(v) || 0;
  const core = () => w.ShrineCart || null;
  const has = (flag) => {
    const c = core();
    return c && c.has ? !!c.has(flag) : !!(w.ShrineCartEngine && w.ShrineCartEngine[flag]);
  };
  const money = (cents) => (w.ShrineCartGoals ? w.ShrineCartGoals.format(cents) : (num(cents) / 100).toFixed(2));
  const text = (el) => (el ? el.textContent.replace(/\s+/g, ' ').trim() : '');
  const lineOf = (root, handle, extra) => [...root.querySelectorAll('.cart-item.cart-item--product-' + handle + (extra || ''))];
  const productName = (root, handle, el) => {
    if (el && el.dataset.title) return el.dataset.title;
    const line = lineOf(root, handle)[0];
    return text(line && line.querySelector('.cart-item__name')) || handle;
  };

  // ------------------------------------------------------------------ synchronous checks (the core replaces their notices on every run)
  const check = (ctx) => {
    const root = (ctx && ctx.root) || d;
    const out = [];
    const add = (code, level, title, msg, blockId) => out.push({ code, level, title, text: msg, blockId });
    const engines = [...root.querySelectorAll('cart-drawer-gift[data-reward-id]')];
    const seen = {};
    engines.forEach((g) => {
      const h = g.dataset.handle;
      const bar = g.closest('.cart-rewards-wrap');
      const blockId = (bar && bar.querySelector('cart-rewards-bar') && bar.querySelector('cart-rewards-bar').dataset.blockId) || g.dataset.rewardId;
      const name = productName(root, h, g);
      if (seen[h]) return;
      seen[h] = 1;
      const others = [...root.querySelectorAll('cart-drawer-gift, cart-drawer-upsell[data-toggle="true"]')].filter((x) => x !== g && x.dataset.handle === h && !(x.dataset.rewardId && x.dataset.rewardId === g.dataset.rewardId));
      if (others.length) add('rewards-gift-shared', 'warning', 'Rewards bar', name + " is also used by another gift or add-on. Use a product that's only given away.", blockId);
      const paid = lineOf(root, h).filter((l) => !l.classList.contains('cart-item--reward-gift') && num(l.dataset.linePrice) > 0);
      if (paid.length) {
        if (has('rewardGiftLines')) add('rewards-gift-paid-line', 'info', 'Rewards bar', name + ' is also in the cart as a paid item; the gift stays a separate line.', blockId);
        else
          add('rewards-gift-paid-line', 'warning', 'Rewards bar', name + " is also in the cart as a paid item. A gift that is also sold can remove the paid item, cut it to one unit or keep the gift out of the cart. Use a product that's only given away.", blockId);
      }
      const charged = lineOf(root, h, '.cart-item--reward-gift').filter((l) => num(l.dataset.linePrice) > 0);
      if (charged.length) add('rewards-gift-charged', 'warning', 'Rewards bar', name + ' is in the cart at ' + money(charged[0].dataset.linePrice) + '. Create an automatic discount that makes the gift free.', blockId);
    });
    root.querySelectorAll('.cart-drawer-gift-container cart-drawer-gift[data-selected="true"]').forEach((g) => {
      const line = lineOf(root, g.dataset.handle).find((l) => num(l.dataset.linePrice) > 0);
      if (line) add('rewards-free-gift-charged', 'warning', 'Free gift', productName(root, g.dataset.handle, null) + ' is in the cart at ' + money(line.dataset.linePrice) + '. Create an automatic discount that makes it free.', freeGiftId(g));
    });
    root.querySelectorAll('.cart-rewards.is-gifts-off').forEach((b) =>
      add('rewards-gifts-off', 'warning', 'Rewards bar', "free gifts on this cart page need the cart drawer (Theme settings > Cart) or the latest Shrine update. Until then, customers don't see the gifts here.", b.dataset.blockId)
    );
    root.querySelectorAll('.cart-drawer-gift-container.is-gifts-off').forEach((c) =>
      add('rewards-free-gift-off', 'warning', 'Free gift', "this gift needs the cart drawer (Theme settings > Cart) or the latest Shrine update. Until then, customers don't see it here.", freeGiftId(c.querySelector('cart-drawer-gift')))
    );
    // labels of rewards that sit close together on a line overlap (proportional positions)
    root.querySelectorAll('.cart-rewards--line_icons:not(.cart-rewards--labels-off), .cart-rewards--steps:not(.cart-rewards--labels-off)').forEach((b) => {
      const boxes = [...b.querySelectorAll('.cart-rewards__steps .cart-rewards__label:not(.cart-rewards__label--mystery)')].map((l) => l.getBoundingClientRect()).filter((r) => r.width);
      const hit = boxes.some((r, i) => boxes.slice(i + 1).some((q) => r.left < q.right - 1 && q.left < r.right - 1 && r.top < q.bottom && q.top < r.bottom));
      if (hit) add('rewards-labels-overlap', 'info', 'Rewards bar', 'two rewards sit close together on the bar, so their labels overlap. Use the Steps style, or turn off Show reward labels.', b.dataset.blockId);
    });
    repair(root);
    schedule(root);
    return out;
  };
  // the Free gift's block id from its form id (getAttribute: the form's input named "id" shadows form.id)
  const freeGiftId = (g) => {
    const f = g && g.querySelector('form[id^="cart-drawer-gift-"]');
    return f ? f.getAttribute('id').slice('cart-drawer-gift-'.length) : null;
  };

  // ------------------------------------------------------------------ raw tokens: a Reward refreshed without its bar (§7.4 #8)
  let repairTimer = 0;
  let repaired = 0;
  const repair = (root) => {
    const raw = [...(root || d).querySelectorAll('cart-rewards-bar, .cart-rewards-wrap')].some((b) => b.innerHTML.indexOf('[[rw:') > -1);
    const R = w.ShrineCartRequests;
    if (!raw || !R || !R.render || Date.now() - repaired < 5000) return;
    clearTimeout(repairTimer);
    repairTimer = setTimeout(() => {
      repaired = Date.now();
      R.render(null, { source: 'rewards:editor-repair' });
    }, 300);
  };

  // ------------------------------------------------------------------ discount check (plan §4.6; skeleton §3e checkDiscounts)
  const CACHE = 'shrine-cart-rewards-check:';
  let timer = 0;
  let asyncCodes = [];
  const hash = (s) => {
    let h = 0;
    for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0;
    return (h >>> 0).toString(36);
  };
  const baseLine = (root) =>
    [...root.querySelectorAll('.cart-item[data-line-price]')].find((l) => {
      const f = ' ' + (l.dataset.lineFlags || '') + ' ';
      return !l.classList.contains('cart-item--reward-gift') && f.indexOf(' cart-hidden ') < 0 && f.indexOf(' gift-card ') < 0 && num(l.dataset.linePrice) > 0;
    });
  const jobsOf = (root) => {
    const jobs = [];
    root.querySelectorAll('cart-rewards-bar').forEach((bar) => {
      if (bar.dataset.preview === 'sample') return;
      const qty = bar.dataset.goalType === 'quantity';
      bar.querySelectorAll('.cart-rewards__steps > [data-rw-id]').forEach((s) => {
        const type = s.dataset.rwType;
        if (type !== 'gift' && type !== 'discount') return;
        const area = bar.querySelector('#CartReward-' + s.dataset.rwId + '-area');
        const chosen = area && area.dataset.chosen;
        const engines = [...root.querySelectorAll('cart-drawer-gift[data-reward-id="' + s.dataset.rwId + '"]')].filter((g) => g.dataset.soldOut !== 'true');
        const gift = type === 'gift' ? engines.find((g) => g.dataset.handle === chosen) || engines[0] : null;
        if (type === 'gift' && !gift) return;
        jobs.push({ code: 'rewards-check-' + s.dataset.rwId, title: 'Rewards bar', blockId: s.dataset.rwId, type, qty, goal: num(s.dataset.rwCmp), label: s.dataset.rwText,
          gift: gift && gift.dataset.id, name: gift && (gift.dataset.title || gift.dataset.handle), country: bar.dataset.country });
      });
    });
    root.querySelectorAll('.cart-drawer-gift-container cart-drawer-gift').forEach((g) => {
      const container = g.closest('.cart-drawer-gift-container');
      jobs.push({ code: 'rewards-check-' + (freeGiftId(g) || g.dataset.handle), title: 'Free gift', blockId: freeGiftId(g), type: 'gift', qty: g.dataset.type === 'product_quantity',
        goal: num(g.dataset.requirement), gift: g.dataset.id, name: text(g.querySelector('.upsell__title h3')) || g.dataset.handle, country: container && container.dataset.country });
    });
    return jobs;
  };
  // the check can fail in some previews (dev stores answer 400): say how to test it by hand instead
  const checkFailed = (job) =>
    "the discount check couldn't run here. To test it, fill the preview cart past " + (job.qty ? job.goal + ' items' : money(job.goal)) + ' and look at the price in the cart.';
  const describe = (job, res, base) => {
    const goal = job.qty ? String(job.goal) : money(job.goal);
    const lines = (res && res.lines) || [];
    if (job.type === 'gift') {
      const g = lines.find((l) => String(l.variantId) === String(job.gift));
      if (!g) return { level: 'info', text: checkFailed(job) };
      if (num(g.totalCents) === 0) return { level: 'info', text: job.name + ' is free from ' + goal + '.' };
      return { level: 'warning', text: 'at ' + goal + ', ' + job.name + ' would cost ' + money(g.totalCents) + '. Create an automatic Buy X get Y discount that makes it free.' };
    }
    const b = lines.filter((l) => String(l.variantId) === String(base));
    const off = b.reduce((s, l) => s + num(l.discountedCents), 0);
    if (off > 0) {
      const titles = [...new Set([].concat(...b.map((l) => l.titles || [])))].join(', ');
      return { level: 'info', text: job.label + ' applies from ' + goal + (titles ? ' (' + titles + ')' : '') + '.' };
    }
    return { level: 'warning', text: 'no discount applies at ' + goal + ' for ' + job.label + '. Create an automatic discount with a minimum purchase of ' + goal + '.' };
  };
  const notices = () => (core() && core().notices) || null;
  const runChecks = async (root) => {
    const c = core();
    const N = notices();
    if (!c || !c.editor || !c.editor.checkDiscounts || !N) return;
    asyncCodes.forEach((code) => N.clear(code));
    asyncCodes = [];
    const set = (code, o) => {
      asyncCodes.push(code);
      N.set(code, o);
    };
    const jobs = jobsOf(root);
    if (!jobs.length) return;
    const base = baseLine(root);
    if (!base) return set('rewards-check-empty', { level: 'info', title: 'Rewards bar', text: 'add a product to the preview cart to check the reward discounts.' });
    const unit = num(base.dataset.linePrice) / Math.max(1, num(base.dataset.quantity) || 1);
    for (const job of jobs) {
      const lines = [{ variantId: base.dataset.variantId, quantity: job.qty ? Math.max(1, Math.round(job.goal)) : Math.min(50, Math.max(1, Math.ceil(job.goal / unit))) }];
      if (job.gift) lines.push({ variantId: job.gift, quantity: 1 });
      const key = CACHE + (job.blockId || job.code) + ':' + hash(JSON.stringify([lines, job.goal, job.country]));
      let res = null;
      try {
        const hit = JSON.parse(sessionStorage.getItem(key) || 'null');
        if (hit && Date.now() - hit.t < 600000) res = hit.res;
      } catch (e) {}
      if (!res) {
        try {
          res = await c.editor.checkDiscounts(lines, { country: job.country });
        } catch (e) {
          res = { errors: [String(e)] };
        }
        if (res && !(res.errors && res.errors.length)) {
          try {
            sessionStorage.setItem(key, JSON.stringify({ t: Date.now(), res }));
          } catch (e) {}
        }
        await new Promise((r) => setTimeout(r, 300));
      }
      if (!res || (res.errors && res.errors.length)) {
        set('rewards-check-failed', { level: 'info', title: job.title, text: checkFailed(job) });
        continue;
      }
      const msg = describe(job, res, base.dataset.variantId);
      set(job.code, { level: msg.level, title: job.title, text: msg.text, blockId: job.blockId });
    }
  };
  const schedule = (root) => {
    clearTimeout(timer);
    timer = setTimeout(() => runChecks(root || d), 1500);
  };

  const api = (w.ShrineCartRewardsEditor = { version: 1, check, runChecks, jobsOf, describe });
  const register = () => {
    const c = core();
    if (!c || !c.editor || !c.editor.registerCheck) return false;
    c.editor.registerCheck('rewards', check);
    if (c.onRender) c.onRender((o) => repair(o && o.root));
    return true;
  };
  if (!register()) d.addEventListener('DOMContentLoaded', register, { once: true });
  repair(d);
  return api;
})();

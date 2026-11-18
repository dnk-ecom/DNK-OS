/* Quantity breaks V2: the "Discount setup" panel, theme editor only (snippets/qb-v2-setup.liquid prints it under the widget).
   Fills it with the discounts to create in Shopify admin, warnings about the setup, a cart link per option and a check:
   one throwaway cart per option through the Storefront API (tokenless cartCreate) whose discount allocations are compared
   with the discount the option shows. The shop's own cart is never touched. Reads the setup JSON the widget, its options
   and children print in design mode, and each option's cart lines from the widget (component-quantity-breaks-v2.js).
   Merchant text is English. */
(() => {
  if (window.ShrineQBV2Editor) return;
  window.ShrineQBV2Editor = true;
  if (!(window.Shopify && Shopify.designMode)) return;

  const API = '/api/2026-10/graphql.json';
  const QUERY =
    'mutation QbV2DiscountCheck($input: CartInput!) { cartCreate(input: $input) { cart { id lines(first: 20) { nodes { quantity merchandise { ... on ProductVariant { id } } ' +
    'cost { subtotalAmount { amount currencyCode } totalAmount { amount currencyCode } } discountAllocations { __typename discountedAmount { amount currencyCode } ' +
    '... on CartAutomaticDiscountAllocation { title } ... on CartCodeDiscountAllocation { code } } } } discountCodes { code applicable } } ' +
    'userErrors { field message code } warnings { code message } } }';
  const NAMES = {
    bundle: 'Bundle products',
    gift: 'Free gift',
    upsell: 'Checkbox upsell',
    choice: 'Product choice',
    builder: 'Bundle builder',
    unlock: 'Unlockable gift',
    field: 'Personalisation',
  };
  // level → icon, the visually hidden word, the line's class in component-quantity-breaks-v2-editor.css; errors come first
  const ICONS = { error: ['✗', 'Error', 'error'], warning: ['⚠', 'Warning', 'warn'], info: ['ⓘ', 'Note', 'info'], ok: ['✓', 'OK', 'ok'] };
  const ORDER = ['error', 'warning', 'info', 'ok'];
  const HIDDEN = { b2b: 'B2B customer', country: 'country', tag: 'product tag', price_breaks: 'B2B price breaks', rules: 'quantity rules' };
  const BAD = ['missing', 'less', 'charged', 'code']; // check results meaning the card shows a price checkout won't charge: they open the panel
  const MAX1 = ['✓ Set a maximum number of uses per order: 1'];
  const DATE = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})(?::\d{2})?/; // read like the Schedule block's own script
  const PLAN_APPS = '.appstle-active-option [name="selling_plan"], .sls-purchase [name="selling_plan"], skio-plan-picker [name="selling_plan"]';
  const panels = new Set();
  const seen = new WeakSet();

  /* ---------- helpers ---------- */
  const esc = (value) => String(value == null ? '' : value).replace(/[&<>"']/g, (char) => `&#${char.charCodeAt(0)};`);
  const num = (value, fallback = 0) => (value === '' || value == null || !isFinite(value) ? fallback : +value);
  const json = (script) => {
    try {
      return script ? JSON.parse(script.textContent) : null;
    } catch (error) {
      return null;
    }
  };
  // store(key) reads, store(key, value) writes; sessionStorage may be blocked
  const store = (key, value) => {
    try {
      if (value === undefined) return JSON.parse(sessionStorage.getItem(key));
      sessionStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      return null;
    }
  };
  const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  const plural = (count, word) => `${count} ${word}${count === 1 ? '' : 's'}`;
  const and = (list) => (list.length > 1 ? `${list.slice(0, -1).join(', ')} and ${list[list.length - 1]}` : list[0] || '');
  const cents = (money) => Math.round(parseFloat(money && money.amount) * 100) || 0;
  const fixed = (amount) => (amount / 100).toFixed(2);
  const percent = (value) => `${Math.abs(value - Math.round(value)) < 0.05 ? Math.round(value) : value.toFixed(1)}%`;
  const copyValue = (count) => (count > 1 ? String(count) : '');
  const trim = (value) => String(value == null ? '' : value).trim();
  const country = (code) => {
    try {
      return new Intl.DisplayNames(['en'], { type: 'region' }).of(code) || code;
    } catch (error) {
      return code;
    }
  };
  const hash = (text) => {
    let value = 2166136261;
    for (let i = 0; i < text.length; i += 1) value = Math.imul(value ^ text.charCodeAt(i), 16777619);
    return (value >>> 0).toString(36);
  };
  // the product title of an extra item or a candidate card, without its "2×" prefix
  const titleOf = (element) => {
    const title = element && element.querySelector('.qb-v2-cand__title, .qb-v2-item__title');
    if (!title) return '';
    const copy = title.cloneNode(true);
    copy.querySelectorAll('.qb-v2-item__qty').forEach((prefix) => prefix.remove());
    return copy.textContent.trim();
  };
  // The page currency in the widget's format (main.js's formatMoney until the widget script runs); any other currency,
  // such as merchant-typed amounts while the preview shows another market, in the browser's format
  const moneyOf = (ctx) => (amount, currency = ctx.shop.shop_currency) => {
    const plain = (html) => {
      const template = document.createElement('template');
      template.innerHTML = html;
      return template.content.textContent.trim();
    };
    try {
      if (currency === ctx.shop.presentment_currency && window.ShrineQBV2) {
        ctx.format = ctx.format || ShrineQBV2.money.create(ctx.wrapper);
        return plain(ctx.format.format(amount, { trim: false }));
      }
      if (currency === ctx.shop.presentment_currency && typeof formatMoney === 'function') return plain(formatMoney(amount, ctx.wrapper.dataset.moneyFormat));
    } catch (error) {
      // the browser's format below
    }
    try {
      return new Intl.NumberFormat(document.documentElement.lang || undefined, { style: 'currency', currency }).format(amount / 100);
    } catch (error) {
      return `${fixed(amount)} ${currency}`;
    }
  };
  // Option-level selling plans work only while nothing else in the section chooses the plan (contract 6.7.9)
  const plansAllowed = (ctx) => {
    const form = document.getElementById(`product-form-${ctx.sid}`);
    const info = document.getElementById(`ProductInfo-${ctx.sid}`);
    const fields = (form ? Array.from(form.elements) : []).concat(info ? Array.from(info.querySelectorAll('[name="selling_plan"]')) : []);
    return (
      ctx.wrapper.planAllowed !== false &&
      !document.getElementById(`SubscriptionWidget-${ctx.sid}`) &&
      !document.querySelector(PLAN_APPS) &&
      !fields.some((field) => field.name === 'selling_plan' && !field.hasAttribute('data-qb-v2-plan'))
    );
  };

  /* ---------- price model (contract 5.4), cents ---------- */
  // The discount of an option, or of an extra's own discount (child.d: none | percentage | amount_each | free), on
  // lines [{ n, p }] (n units at p); conv turns shop-currency cents into the line currency, null = unknown
  const discountOf = (discount, lines, conv) => {
    const base = lines.reduce((sum, line) => sum + line.n * line.p, 0);
    const type = discount.type;
    if (type === 'percentage') return lines.reduce((sum, line) => sum + Math.round((line.n * line.p * discount.pct) / 100), 0);
    if (type === 'free') return base;
    if (type === 'free_items') {
      const prices = [].concat(...lines.map((line) => Array(line.n).fill(line.p))).sort((a, b) => a - b);
      return prices.slice(0, Math.max(0, Math.min(discount.freeSetting, prices.length - 1))).reduce((sum, price) => sum + price, 0);
    }
    if (!/^(amount_each|amount_total|set_price)$/.test(type)) return 0;
    const amount = conv(type === 'set_price' ? discount.total : discount.amount);
    if (amount == null) return null;
    if (type === 'amount_each') return lines.reduce((sum, line) => sum + line.n * Math.min(line.p, amount), 0);
    return type === 'amount_total' ? Math.min(base, amount) : Math.max(0, base - amount);
  };

  /* ---------- checklist texts (contract 6.8.3) ---------- */
  const offText = (ctx, option) =>
    ({
      percentage: `${option.pct}% off`,
      amount_each: `${ctx.money(option.amount)} off each`,
      amount_total: `${ctx.money(option.amount)} off`,
      set_price: `${option.units} for ${ctx.money(option.total)}`,
      free_items: `${option.free} free`,
    })[option.type] || '';
  const childOff = (ctx, child) => ({ percentage: `${child.d.pct}% off`, amount_each: `${ctx.money(child.d.amount)} off each`, free: 'free' })[child.d.type] || '';
  // the discount title the checklist suggests; the check repeats it when a discount comes out too small
  const suggest = (ctx, option, child) => {
    let end = '';
    if (!child) end = offText(ctx, option);
    else if (/gift|unlock/.test(child.type)) end = 'free gift';
    else end = (child.type === 'upsell' && child.items[0] ? child.items[0].title + ' ' : '') + childOff(ctx, child);
    return `${option ? option.title : ctx.product.title} – ${end}`;
  };
  const tail = (ctx) =>
    [['Markets: all markets where this product sells'], ['Combinations: ✓ Product discounts ✓ Order discounts ✓ Shipping discounts']].concat(
      ctx.product.has_selling_plans ? [['Purchase type: One-time purchase and subscription · Recurring payments: all']] : []
    );
  const method = (option, title) =>
    option && option.method === 'code' && option.code ? [`Method: Discount code · Code: ${option.code}`, option.code] : [`Method: Automatic discount · Title: ${title}`, title];
  // Buy X get Y steps; gets = "Specific products › …" or "Specific collections › …"
  const bxgy = (ctx, option, title, buys, quantity, gets, value, max) =>
    [
      ['Discounts › Create discount › Buy X get Y'],
      method(option, title),
      [`Customer buys: Minimum quantity of items ${buys} · Specific products › ${ctx.product.title}`, copyValue(buys)],
      [`Customer gets: Quantity ${quantity} · ${gets}`, copyValue(quantity)],
      ...value,
      max,
    ].concat(tail(ctx));
  const valueStep = (ctx, child) => {
    if (child.d.type === 'percentage') return [`At a discounted value: Percentage ${child.d.pct}%`, String(child.d.pct)];
    if (child.d.type === 'amount_each') return [`At a discounted value: Amount off each ${ctx.money(child.d.amount)}`, fixed(child.d.amount)];
    return ['At a discounted value: Free'];
  };
  const subscribers = (ctx) => (ctx.product.has_selling_plans ? [['warning', "Shopify's Buy X get Y doesn't apply to subscription purchases: subscribers pay for the gift."]] : []);

  const mainBlock = (ctx, option) => {
    const product = ctx.product;
    const money = ctx.money;
    const page = ctx.shop.presentment_currency;
    if (option.method === 'pack') {
      const variants = ctx.variants();
      const pack = variants.find((variant) => String(variant.id) === String(option.data.pack_variant_id));
      if (!pack) return null;
      const at = num(option.el.dataset.qbPackPosition) - 1;
      const packOptions = pack.options || [];
      const unit = variants.find((variant) => (variant.options || []).every((value, i) => value === (i === at ? option.el.dataset.qbUnitValue : packOptions[i]))) || pack;
      const count = num(option.data.quantity, 1);
      return {
        text: `No discount needed: variant ${packOptions[at] || option.data.pack_value} costs ${money(pack.price, page)}. Bought singly: ${count} × ${money(unit.price, page)} = ${money(count * unit.price, page)}.`,
        product: true,
      };
    }
    if (option.type === 'none') return null;
    const title = suggest(ctx, option);
    const notes = option.method === 'code' && option.code ? [['info', 'V2 adds this code to the cart when customers choose this option.']] : [];
    if (option.type === 'free_items') {
      return { steps: bxgy(ctx, option, title, option.units - option.free, option.free, `Specific products › ${product.title} · At a discounted value: Free`, [], MAX1), notes, admin: true };
    }
    const price = num(product.price);
    const setAmount = Math.max(0, option.units * price - option.total);
    let value = [`Value: Fixed amount · ${money(option.amount)}`, fixed(option.amount)];
    if (option.type === 'percentage') value = [`Value: Percentage · ${option.pct}%`, String(option.pct)];
    if (option.type === 'set_price') value = [`Value: Fixed amount · ${money(setAmount)} (= ${option.units} × ${money(price, page)} − ${money(option.total)})`, fixed(setAmount)];
    const steps = [['Discounts › Create discount › Amount off products'], method(option, title), value];
    if (option.type === 'amount_each') steps.push(['Don\'t tick "Only apply discount once per order"']);
    else if (option.type !== 'percentage') steps.push(['✓ Only apply discount once per order']);
    steps.push([`Applies to: Specific products › ${product.title}`, product.title], [`Minimum purchase requirements: Minimum quantity of items › ${option.units}`, String(option.units)]);
    if (option.type === 'set_price' && product.variant_prices_differ) notes.push(['warning', "Variants have different prices, so a fixed amount can't always reach the set price."]);
    return { steps: steps.concat(tail(ctx)), notes, admin: true };
  };

  // option = null for wrapper-level children (every option)
  const childBlock = (ctx, option, child) => {
    const product = ctx.product;
    const names = child.items.map((item) => item.title);
    const title = suggest(ctx, option, child);
    const s = child.s;
    const discounted = child.d.type !== 'none';
    if (!child.self) return null;
    if (child.type === 'bundle' && names.length && discounted) {
      const quantity = child.items.reduce((sum, item) => sum + Math.min(Math.max(Math.floor(num((s.quantities || [])[child.products.indexOf(item)], 1)), 1), 10), 0);
      return {
        title: `${NAMES.bundle} · ${names.join(' + ')} · ${childOff(ctx, child)}`,
        steps: bxgy(ctx, null, title, 1, quantity, `Specific products › ${names.join(', ')}`, [valueStep(ctx, child)], MAX1),
        notes: [['warning', `Shopify can't require the full set: the discount applies whenever these items are bought with ${product.title}.`]],
        admin: true,
      };
    }
    if (child.type === 'gift' && s.gift_type === 'product' && names.length) {
      const quantity = Math.max(1, num(s.quantity, 1));
      const choose = s.selection === 'one' && names.length > 1;
      return {
        title: `${NAMES.gift} · ${names.join(' / ')}${s.include_in_bigger_options ? ' · bigger options include it' : ''}`,
        steps: bxgy(ctx, null, title, option ? option.units : 1, choose ? quantity : quantity * names.length, `Specific products › ${choose ? `any ${quantity} of ` : ''}${names.join(', ')}`, [['At a discounted value: Free']], MAX1),
        notes: subscribers(ctx),
        admin: true,
      };
    }
    if (child.type === 'upsell' && names.length && s.source === 'product' && discounted) {
      const max = s.quantity_mode === 'match' ? [`Leave "Set a maximum number of uses per order" off, so each ${product.title} unlocks one ${names[0]}`] : MAX1;
      return { title: `${NAMES.upsell} · ${names[0]} · ${childOff(ctx, child)}`, steps: bxgy(ctx, null, title, 1, 1, `Specific products › ${names[0]}`, [valueStep(ctx, child)], max), notes: [], admin: true };
    }
    if (/^(choice|builder)$/.test(child.type) && discounted && !empty(child)) {
      const builder = child.type === 'builder';
      // a choice uses its products when it has any, else its collection; a builder always uses its collection
      const collection = trim(s.collection_title) || trim(s.collection_handle);
      const from = builder || !names.length;
      const quantity = Math.max(1, num(builder ? s.picks : s.quantity, 1));
      const inside = builder && (product.collections || []).includes(s.collection_handle);
      return {
        title: `${NAMES[child.type]} · ${builder ? `${quantity} from ` : ''}${from ? collection : names.join(' / ')} · ${childOff(ctx, child)}`,
        steps: bxgy(ctx, null, title, 1, quantity, from ? `Specific collections › ${collection}` : `Specific products › ${names.join(', ')}`, [valueStep(ctx, child)], MAX1),
        // #36 (to verify on a store)
        notes: inside ? [['info', `${product.title} is also in ${collection}. With more than one ${product.title} in the cart, Shopify may discount it instead of a chosen item.`]] : [],
        admin: true,
      };
    }
    if (child.type === 'unlock' && names.length) {
      const at = Math.max(1, num(s.unlock_quantity, 1));
      return {
        title: `${NAMES.unlock} · ${names[0]} · unlocks at ${at} items`,
        steps: bxgy(ctx, null, title, at, Math.max(1, num(s.quantity, 1)), `Specific products › ${names[0]}`, [['At a discounted value: Free']], MAX1),
        notes: subscribers(ctx),
        admin: true,
      };
    }
    if (child.type === 'field' && trim(s.field_name)) {
      return { title: `${NAMES.field} · ${trim(s.field_name)}`, notes: [['info', 'Nothing to set up in Discounts. The text is saved with the item in the cart and the order.']] };
    }
    return null;
  };

  /* ---------- the panel model: options, children, warnings (contract 6.8.4) ---------- */
  // Products come from the child's setup JSON; an Unlockable gift without them is read from its item, a Product choice
  // without them and without a collection from its candidates
  const childOf = (script, mainId) => {
    const data = json(script);
    if (!data || !data.type) return null;
    const s = data.settings || {};
    const el = script.closest('[data-qb-child]');
    let products = (data.products || []).filter(Boolean);
    if (!products.length && el && (data.type === 'unlock' || (data.type === 'choice' && !trim(s.collection_handle)))) {
      const template = el.querySelector('template[data-qb-candidates]');
      products = Array.from(data.type === 'unlock' ? el.querySelectorAll('[data-qb-item]') : template ? template.content.querySelectorAll('[data-qb-candidate]') : [], (item) => ({
        id: item.dataset.productId,
        title: titleOf(item),
        available: item.dataset.available !== 'false',
        is_main: String(item.dataset.productId) === String(mainId),
      }));
    }
    return {
      type: data.type,
      id: data.block_id,
      el,
      s,
      self: s.origin !== 'inherited',
      products,
      items: products.filter((product) => !product.requires_selling_plan), // subscription-only products are never added as extras
      d: { type: s.discount_type || 'none', pct: num(s.discount_percentage), amount: num(s.discount_amount_cents) },
    };
  };
  // children whose option hides itself on the storefront until they have products
  const empty = (child) => (child.type === 'bundle' ? !child.items.length : /^(choice|builder)$/.test(child.type) && !num(child.s.candidate_count));
  // the first Schedule decides, read like its inline script: [start, end] in ms (null = open) and the unreadable dates
  const scheduleOf = (child) => {
    const s = child.s;
    const bad = [];
    const times = ['start', 'end'].map((key) => {
      const text = trim(s[key]);
      const match = DATE.exec(text);
      if (text && (!match || s[`${key}_valid`] === false)) bad.push(text);
      if (!match) return null;
      const [year, month, day, hour, minute] = match.slice(1).map(Number);
      return s.timezone === 'fixed' ? Date.UTC(year, month - 1, day, hour, minute - Math.round(num(s.utc_offset) * 60)) : new Date(year, month - 1, day, hour, minute).getTime();
    });
    return { start: times[0], end: times[1], bad };
  };

  const build = (ctx) => {
    const { wrapper, shop, product, sid } = ctx;
    const patched = (customElements.get('quantity-breaks') || {}).qbApi >= 1;
    const plans = plansAllowed(ctx);
    const notes = [];
    const children = (root, test) => Array.from(root.querySelectorAll('script[data-qbv2-setup="child"]'), (script) => test(script) && childOf(script, product.id)).filter(Boolean);
    const options = [];
    wrapper.querySelectorAll('.qb-v2-option').forEach((el) => {
      const data = json(el.querySelector(':scope > script[data-qbv2-setup="option"]'));
      if (!data) return;
      const units = num(el.dataset.qbUnits, num(data.units, 1));
      // the method the option really uses: a pack value without a variant works as an automatic discount
      const used = el.dataset.qbMethod || data.method || 'automatic';
      const option = {
        el,
        data,
        id: el.dataset.qbV2Option || data.block_id,
        title: trim(el.dataset.qbTitle || data.title) || `${num(data.quantity, 1)}×`,
        units,
        method: used,
        code: trim(data.code),
        type: used === 'pack' ? 'none' : data.discount_type || 'none',
        pct: num(data.discount_percentage),
        amount: num(data.discount_amount_cents),
        total: num(data.total_price_cents),
        freeSetting: num(data.free_quantity, 1),
        plan: data.plan && data.plan.position > 0 && data.plan.id ? data.plan : null,
        dormant: options.length >= 4, // options 5-8
        mustChoose: el.dataset.qbMustChoose === 'true',
        children: children(el, () => true),
        blocks: [],
        notes: [],
      };
      option.free = Math.min(option.freeSetting, units - 1);
      if (option.type === 'free_items' && option.free < 1) option.type = 'none';
      option.missing = data.hidden === true || option.children.some((child) => child.self && empty(child));
      options.push(option);
    });
    const top = children(wrapper, (script) => !script.closest('.qb-v2-option'));
    const live = options.filter((option) => !option.missing && !(option.dormant && !patched));
    // the option customers find selected (contract 5.2.3): the pack option of the page's variant, the first ticked one, else the first that needs no choice
    const pickable = options.slice(0, 4).filter((option) => option.data.available !== false && !option.missing && option.el.dataset.qbScratch !== 'true');
    const def =
      pickable.find((option) => option.method === 'pack' && String(option.data.pack_variant_id) === String(product.variant_id)) ||
      pickable.find((option) => option.data.selected_by_default) ||
      pickable.find((option) => !option.mustChoose) ||
      pickable[0] ||
      null;
    const model = { options, top, live, def, patched, plans, notes, blocks: [], store: [] };
    const all = options.concat(...options.map((option) => option.children), top);

    // environment and the widget as a whole
    const tooMany = options.length > 4 && !patched;
    const update = "Options 5–8 need a Shrine update that isn't live yet. They stay hidden until then.";
    // Only where it matters: options 5-8 in use, or 4 options (a 5th wouldn't show yet; more than 4 is warning w6)
    model.env = patched ? (options.length > 4 ? 'Shrine update live: options 5–8, grouped cart lines and gift rules are on.' : '') : options.length === 4 ? update : '';
    const count = (selector) => document.querySelectorAll(selector).length;
    const note = (when, level, text, key) => when && notes.push([level, typeof text === 'function' ? text() : text, key]);
    const rules = options.filter((option) => option.data.reason === 'rules');
    const ticked = live.filter((option) => option.data.selected_by_default);
    const schedules = top.filter((child) => child.type === 'schedule');
    note(shop.hidden_reason && shop.hidden_reason !== 'rules', 'info', `Hidden for this visitor (${HIDDEN[shop.hidden_reason] || shop.hidden_reason}); shown here so you can edit it.`, 'w21');
    if (schedules[0]) {
      const { start, end, bad } = scheduleOf(schedules[0]);
      bad.forEach((text) => note(true, 'error', `Schedule: ${text} isn't in the format YYYY-MM-DDTHH:MM.`, `w20:${text}`));
      note(end != null && Date.now() >= end, 'info', 'Schedule: this window has ended, so the widget is hidden.', 'w20e');
      note(start != null && Date.now() < start && !(end != null && Date.now() >= end), 'info', `Schedule: this window hasn't started yet, so the widget is hidden until ${trim(schedules[0].s.start)}.`, 'w20s');
    }
    note(num(shop.schedule_count) > 1 || schedules.length > 1, 'warning', 'Only the first Schedule counts. Remove the others.', 'w37');
    note(tooMany, 'warning', update, 'w6');
    note(num(shop.dropped_count) > 0, 'warning', 'Only the first 8 options show.', 'w7');
    note(count(`[id="quantity-breaks-${sid}"]`) > 1, 'error', "Another quantity breaks widget is in this section. Remove one; both can't run together.", 'w8');
    note(
      // getAttribute: form.id is the form's <input name="id">, not its id
      Array.from(document.querySelectorAll('input[name="quantity"]')).some((input) => input.form && input.form.getAttribute('id') === `product-form-${sid}` && !wrapper.contains(input)),
      'info',
      "V2 hides the other quantity selector in this section while it's active. When V2 is hidden for a visitor, its own quantity field shows, so you can remove the other one.",
      'w9'
    );
    note(!!document.querySelector(`.main-offer-item-${sid}`), 'error', 'A Bundle offer of the Main type replaces this product in the cart (it ignores V2). Use its Separate type.', 'w10');
    note(count(`[id="SubscriptionWidget-${sid}"]`) > 1, 'warning', 'Only one Subscription widget works per section.', 'w13');
    note(count(`[id="Inventory-${sid}"]`) > 1, 'warning', 'Only one Inventory status works per section.', 'w13i');
    note(product.requires_selling_plan && plans && live.some((option) => !option.plan), 'error', 'This product needs a selling plan. Set Selling plan on every option or add the Subscription widget.', 'w22');
    note(options.length && rules.length === options.length, 'info', 'Customers see a plain quantity field instead, because no option meets the quantity rules.', 'w25');
    note(ticked.length > 1, 'warning', () => `${and(ticked.map((option) => option.title))} are ${ticked.length > 2 ? 'all' : 'both'} selected by default; ${(def || ticked[0]).title} is used.`, 'w26');
    note(
      // options carry their discount in type, children in d
      num(shop.enabled_currencies_count) > 1 && all.some((entry) => /^(amount_each|amount_total|set_price)$/.test(entry.data ? entry.type : entry.d.type)),
      'info',
      'Shopify converts fixed amounts at the exchange rate; percentages stay exact in every currency.',
      'w30'
    );
    note(/\bqb-v2--layout-(grid|columns)\b/.test(wrapper.className) && options.some((option) => option.data.has_pickers), 'info', 'Variant pickers are narrow in Grid and Columns layouts. Stack suits products with variants.', 'w35');

    const flagged = new Set();
    const gifts = {};
    // the page product (#4) and subscription-only products (#5) as extras, gift products used twice (#23)
    const extras = (option, child) => {
      if (!child.self) return;
      const list = option ? option.notes : notes;
      child.products.forEach((item) => {
        if (item.is_main && !flagged.has(child.id)) {
          flagged.add(child.id);
          list.push(['error', `${NAMES[child.type]}${option ? ` in ${option.title}` : ''} uses this product. It merges with the main line in the cart.`, `w4:${child.id}`]);
        }
        if (item.requires_selling_plan && !flagged.has(item.id)) {
          flagged.add(item.id);
          list.push(['error', `${item.title} can only be sold with a subscription, so it can't be added as an extra.`, `w5:${item.id}`]);
        }
      });
      if ((child.type === 'gift' && child.s.gift_type === 'product') || child.type === 'unlock') {
        child.items.forEach((item) => (gifts[item.id] = gifts[item.id] || { title: item.title, blocks: new Set() }).blocks.add(child.id));
      }
    };
    // #1: same quantity and the same extras (scratch cards and personalisation don't change the cart); #2: the share of the price an automatic tier takes off
    const signature = (option) =>
      [
        option.units,
        option.method === 'pack' && option.data.pack_value,
        option.plan && option.plan.position,
        option.children
          .filter((child) => !/^(scratch|field)$/.test(child.type))
          .map((child) =>
            [child.type, child.s.gift_type, child.products.map((item) => item.id), child.s.quantities, child.d.type, child.d.pct, child.d.amount, child.s.picks, child.s.quantity, child.s.selection, child.s.quantity_mode, child.s.collection_handle].join(':')
          )
          .sort(),
      ].join('#');
    const tier = (option) => {
      const price = num(product.price);
      return option.method === 'automatic' && !option.plan && price ? (100 * discountOf(option, [{ n: option.units, p: price }], (amount) => amount)) / (option.units * price) : null;
    };
    const hiddenPicker = wrapper.dataset.showProductPicker === 'false' && num(product.variants_count) > 1;

    options.forEach((option, i) => {
      const add = (level, text, key) => option.notes.push([level, text, `${key}:${option.id}`]);
      const { title, data } = option;
      if (data.method === 'code' && !option.code) add('error', `${title} uses Discount code but has no code.`, 'w14');
      if (data.method === 'pack' && !data.pack_variant_id) {
        // The value exists, but not with this variant's other values: unavailable on this variant only
        if (option.el.dataset.qbPackPosition) add('info', `${title} is unavailable on this variant: it has no ${trim(data.pack_value)} variant.`, 'w15m');
        else add('error', trim(data.pack_value) ? `No variant with the value ${trim(data.pack_value)} was found.` : `${title} uses Pack variant but has no value.`, 'w15');
      }
      if (option.method === 'code' && option.code && (data.discount_type || 'none') === 'none') {
        add('warning', `${title} adds code ${option.code} but shows no discount. Set Discount type to match the code.`, 'w28');
      }
      if (data.plan && data.plan.position > 0 && !data.plan.id) add('warning', `${title}: this product has no selling plan at position ${data.plan.position}, so the option is sold one-time.`, 'wp');
      if (option.plan && !plans) add('warning', `${title}'s selling plan is ignored: a Subscription widget or a subscription app chooses the plan.`, 'w16');
      if (option === def) {
        if (option.mustChoose) add('warning', `${title} is selected by default but needs a choice, so Add to cart starts disabled.`, 'w17');
        if (option.method === 'pack' && String(data.pack_variant_id) !== String(product.variant_id)) add('warning', `${title} is selected by default and switches the variant when the page loads.`, 'w18');
        if (option.plan && plans) add('warning', `${title} is a subscription and is selected by default. Shopify recommends selecting one-time purchase first.`, 'w33');
        if (option.units > 1 && !document.getElementById(`main-atc-price-${sid}`)) {
          add('info', `${title} is selected by default. Turn on Display price inside the button in Buy Buttons so customers see the total next to the button.`, 'w29');
        }
      }
      if (data.stepper && num(data.stepper_max, Infinity) < num(data.quantity, 1)) add('warning', `${title}: Maximum quantity is below Quantity.`, 'w27');
      if (data.stepper && i !== options.length - 1) add('info', 'The quantity stepper works best on the last option.', 'w24');
      if (data.reason === 'rules' && rules.length !== options.length) {
        add('info', `${title} breaks this product's quantity rules (minimum, maximum or increments) and can't be selected.`, 'w25');
      }
      if (hiddenPicker && live.includes(option) && !data.has_pickers) {
        add('warning', `${title} has no variant picker while the product's Variant picker is hidden, so customers can't choose a variant. Turn on Show variant pickers or turn this setting back on.`, 'w34');
      }
      if (option.type !== 'none' && option.children.some((child) => /^(bundle|choice|builder)$/.test(child.type))) {
        add('warning', `A discount on ${product.title} itself in this option can't depend on the other items in Shopify. Leave the option's discount at No discount and discount the included items.`, 'w3');
      }
      const main = mainBlock(ctx, option);
      if (main) option.blocks.push(main);
      option.children.forEach((child) => {
        extras(option, child);
        if (child.self && empty(child)) add('info', `${title} is hidden on your store until ${NAMES[child.type]} has products.`, `w19:${child.id}`);
        if (child.type === 'gift') {
          const giftType = child.s.gift_type;
          const names = child.items.map((item) => item.title);
          if (child.self && giftType === 'product' && !names.length) {
            // warning, not error: a freshly added Free gift preset has no product yet (setup still to do)
            add('warning', `${title} says it includes a free gift, but Free gift has no product yet. Choose one in Free gift, or set Gift type to Text only.`, `w31:${child.id}`);
          }
          if (giftType === 'product' && names.length && child.items.every((item) => item.available === false)) {
            add('warning', `${and(names)} ${names.length > 1 ? 'are' : 'is'} sold out, so ${title} adds no gift.`, `w32:${child.id}`);
          }
          if (giftType === 'product' && names.length && option.type !== 'none') {
            add(
              'warning',
              `Below Shopify Plus, products in a Buy X get Y discount can't get another product discount: ${title}'s ${option.type === 'percentage' ? `${option.pct}%` : offText(ctx, option)} and this gift may not both apply.`,
              `w11:${child.id}`
            );
          }
          if (child.self && giftType === 'shipping') {
            add('info', `Shopify's free shipping can't be limited to this product. A store-wide free-shipping discount with Minimum quantity of items ${option.units} applies to any ${option.units} items in the cart.`, `w12:${child.id}`);
          }
          if (child.self && giftType === 'text') add('info', 'Display only — nothing to set up.', `w12:${child.id}`);
        }
        const block = childBlock(ctx, option, child);
        if (block) option.blocks.push(block);
      });
      const at = live.indexOf(option);
      if (at < 0) return;
      // two different codes can price the same quantity differently: each applies only with its own option
      const codes = (other) => other.method === 'code' && option.method === 'code' && other.code.toLowerCase() !== option.code.toLowerCase();
      const twin = live.slice(0, at).find((other) => signature(other) === signature(option) && !codes(other));
      if (twin) add('error', `${twin.title} and ${title} have the same quantity. Shopify applies one discount per quantity, so they can't have different prices.`, 'w1');
      const own = tier(option);
      const better = own == null ? null : live.filter((other) => other.units < option.units && tier(other) > own + 0.01).sort((a, b) => tier(b) - tier(a))[0];
      if (better) add('warning', `${title} saves less than ${better.title}. Shopify always applies the best discount the cart qualifies for.`, 'w2');
    });
    top.forEach((child) => {
      extras(null, child);
      const block = childBlock(ctx, null, child);
      if (block) model.blocks.push(block);
    });
    Object.keys(gifts).forEach((id) => {
      if (gifts[id].blocks.size > 1) notes.push(['warning', `${gifts[id].title} is the gift in two places. The cart keeps one removal rule per gift product.`, `w23:${id}`]);
    });

    // store-wide notes: every automatic discount this widget asks for
    const wanted = (child) =>
      child.self &&
      (/gift|unlock/.test(child.type)
        ? child.items.length > 0 && (child.type === 'unlock' || child.s.gift_type === 'product')
        : child.d.type !== 'none' && (child.type === 'upsell' ? child.s.source === 'product' && child.items.length > 0 : !empty(child)));
    const automatic =
      options.reduce((sum, option) => sum + (option.method === 'automatic' && option.type !== 'none') + option.children.filter(wanted).length, 0) + top.filter(wanted).length;
    if (automatic) {
      model.store.push(
        `${plural(automatic, 'automatic discount')} for this product. Shopify allows 25 active automatic discounts in the whole store, apps included. Same tiers on many products? Create each tier once for a collection. Different products in that collection then count together toward the minimum.`
      );
    }
    model.store.push(
      'Promo codes: make them order discounts that combine with product discounts, so they stack with these tiers.',
      'On Shopify Plus, two product discounts on one line also need matching discount tags.',
      'Facebook, Instagram and Google checkouts never combine discounts.'
    );

    // the sidebar block each card answers to (block select)
    ctx.cards = {};
    options.forEach((option) => [option.id].concat(option.children.filter((child) => child.self).map((child) => child.id)).forEach((id) => (ctx.cards[id] = option.id)));
    top.forEach((child) => (ctx.cards[child.id] = 'wrapper'));
    return model;
  };

  /* ---------- cart lines of an option (discount check and cart link) ---------- */
  const stateOf = (wrapper, option) => wrapper.options.find((entry) => entry && (entry.el === option.el || entry.id === option.id));
  // The option's lines: the widget's main, bundle and gift lines; Product choice → the shown item, else the first
  // available candidate; Bundle builder → the first candidates; unlocked gifts; upsells that are ticked (the check takes
  // the pre-ticked ones and every one with a discount instead). withTop adds the wrapper-level upsells.
  const linesOf = (ctx, model, option, withTop, check) => {
    const wrapper = ctx.wrapper;
    const state = stateOf(wrapper, option);
    let lines = [];
    try {
      lines = (state && wrapper.getCartLines(state, { includeMain: true })) || [];
    } catch (error) {
      console.error('Quantity breaks V2', error);
    }
    lines = lines
      .filter((line) => line && line.variantId && /^(main|bundle|gift)$/.test(line.role || 'main'))
      .map((line) => ({ id: String(line.variantId), qty: num(line.quantity, 1), role: line.role || 'main', pid: String(line.productId || ''), title: line.title || '' }));
    const units = lines.reduce((sum, line) => sum + (line.role === 'main' ? line.qty : 0), 0);
    // "Same as option quantity" follows the option's quantity (the stepper's current one), like the widget's own lines
    const quantity = state ? num(state.stepper ? state.units : state.q, option.units) : num(option.data.quantity, 1);
    const push = (child, element, qty, role) =>
      element && element.dataset.variantId && lines.push({ id: String(element.dataset.variantId), qty, role, pid: String(element.dataset.productId || ''), title: titleOf(element), child });
    const candidates = (child) => {
      const template = child.el && child.el.querySelector('template[data-qb-candidates]');
      return template ? Array.from(template.content.querySelectorAll('[data-qb-candidate]')).filter((card) => card.dataset.available !== 'false') : [];
    };
    const upsell = (child) => {
      const root = child.el;
      const input = root && root.querySelector('.qb-v2-upsell__input');
      if (!child.items[0] || !root || root.dataset.available === 'false') return;
      if (!(check ? root.dataset.qbDefaultChecked === 'true' || child.d.type !== 'none' : input && input.checked)) return;
      push(child, root, child.s.quantity_mode === 'match' ? quantity : 1, 'upsell');
    };
    option.children.forEach((child) => {
      if (child.type === 'upsell') upsell(child);
      if (child.type === 'choice') push(child, (child.el && child.el.querySelector('[data-qb-choice-slot] [data-qb-item]')) || candidates(child)[0], Math.max(1, num(child.s.quantity, 1)), 'choice');
      if (child.type === 'builder') {
        const list = candidates(child);
        const picks = Math.max(1, num(child.s.picks, 1));
        for (let i = 0; i < picks && list.length && (i < list.length || child.s.allow_repeats !== false); i += 1) push(child, list[i % list.length], 1, 'builder');
      }
    });
    model.top.forEach((child) => {
      if (child.type === 'upsell' && withTop) upsell(child);
      const item = child.type === 'unlock' && child.el && child.el.querySelector('[data-qb-item]');
      if (item && item.dataset.available !== 'false' && units >= num(child.s.unlock_quantity, 2)) push(child, item, Math.max(1, num(child.s.quantity, 1)), 'unlock');
    });
    return lines;
  };
  const ready = (wrapper) => typeof wrapper.getCartLines === 'function' && Array.isArray(wrapper.options);

  // One test cart per visible option (at most 8); null while the widget's API is missing. Wrapper-level upsells go
  // into the cart of the option customers find selected
  const plan = (ctx, model) => {
    const wrapper = ctx.wrapper;
    if (!ready(wrapper)) return null;
    const host = model.live.includes(model.def) ? model.def : model.live[0];
    const config = model.top.map((child) => [child.id, child.d, child.s.unlock_quantity]);
    return model.live.slice(0, 8).map((option) => {
      const item = { option, request: [], children: {}, skip: '' };
      const lines = linesOf(ctx, model, option, option === host, true);
      lines.forEach((line) => {
        let group = line.role === 'main' ? 'main' : /gift|unlock/.test(line.role) ? `gift:${line.id}` : 'other';
        const child = line.child || option.children.find((entry) => entry.type === line.role && (line.role !== 'bundle' || entry.products.some((product) => String(product.id) === line.pid)));
        if (group === 'other' && child) item.children[(group = `c:${child.id}`)] = child;
        line.group = group;
        const sellingPlan = line.role === 'main' && option.plan && model.plans ? option.plan.id : null;
        let entry = item.request.find((other) => other.id === line.id && other.plan === sellingPlan);
        if (!entry) item.request.push((entry = { id: line.id, plan: sellingPlan, qty: 0, parts: [] }));
        entry.qty += line.qty;
        entry.parts.push(line);
      });
      item.input = {
        lines: item.request.map((entry) =>
          Object.assign({ merchandiseId: `gid://shopify/ProductVariant/${entry.id}`, quantity: entry.qty }, entry.plan ? { sellingPlanId: `gid://shopify/SellingPlan/${entry.plan}` } : {})
        ),
      };
      if (ctx.shop.country) item.input.buyerIdentity = { countryCode: ctx.shop.country };
      if (option.method === 'code' && option.code) item.input.discountCodes = [option.code];
      if (!lines.some((line) => line.role === 'main')) item.skip = 'no cart lines';
      else if (item.request.length > 20) item.skip = 'more than 20 cart lines';
      item.config = [option.type, option.pct, option.amount, option.total, option.freeSetting, option.method, option.code, option.children.map((child) => [child.id, child.d]), config];
      return item;
    });
  };

  // A cart permalink with the option's lines (contract 6.8.6); line properties can't travel in it
  const cartLink = (ctx, model, option) => {
    if (!ready(ctx.wrapper)) return null;
    if (option.plan && model.plans) return { blocked: "Cart links can't carry subscriptions." };
    const merged = [];
    linesOf(ctx, model, option, true, false).forEach((line) => {
      const entry = merged.find((other) => other.id === line.id);
      if (entry) entry.qty += line.qty;
      else merged.push({ id: line.id, qty: line.qty, main: line.role === 'main' });
    });
    if (!merged.some((line) => line.main)) return null;
    const root = (window.Shopify.routes && Shopify.routes.root) || '/';
    const base = trim(ctx.shop.shop_url).replace(/\/+$/, '') || `https://${ctx.shop.domain}`;
    const code = option.method === 'code' && option.code ? `&discount=${encodeURIComponent(option.code)}` : '';
    return {
      url: `${base}${root}cart/${merged.map((line) => `${line.id}:${line.qty}`).join(',')}?storefront=true${code}`,
      // line properties don't travel in a cart link; only the Personalisation text is more than a caption
      note: option.children.some((child) => child.type === 'field' && trim(child.s.field_name)) ? "Cart links can't carry Personalisation text." : '',
    };
  };

  /* ---------- discount check (contract 6.8.5) ---------- */
  // same origin first; on a network or HTTP failure, once more at the myshopify domain (remembered for later requests)
  const request = async (ctx, input) => {
    const body = JSON.stringify({ query: QUERY, variables: { input } });
    const other = `https://${ctx.shop.domain}${API}`;
    const post = (url) =>
      fetch(url, { method: 'POST', credentials: 'omit', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body }).then((response) =>
        response.ok ? response.json() : Promise.reject(response.status)
      );
    const throttled = (data) => (data.errors || []).some((error) => error && error.extensions && error.extensions.code === 'THROTTLED');
    let status = '';
    for (const url of ctx.endpoint === other ? [other, API] : [API, other]) {
      try {
        let data = await post(url);
        ctx.endpoint = url;
        if (throttled(data)) {
          await wait(2000);
          data = await post(url);
        }
        return { data };
      } catch (error) {
        status = typeof error === 'number' ? String(error) : error instanceof SyntaxError ? 'invalid response' : 'network error';
      }
    }
    return { failed: status };
  };

  // result rows [level, kind, text] for one option
  const evaluate = (ctx, model, item, data) => {
    const { option, request: lines } = item;
    const product = ctx.product;
    const title = option.title;
    const rows = [];
    const add = (level, kind, text) => rows.push([level, kind, text]);
    const fail = (reason) => add('info', 'couldnt', `${title}: couldn't check (${reason}).`) && rows;
    // product titles from the setup JSON (exact), else the item's own title
    const nameOf = (part) =>
      part.role === 'main'
        ? product.title
        : (option.children.concat(model.top).map((child) => child.products.find((entry) => String(entry.id) === part.pid)).find(Boolean) || {}).title || part.title || product.title;
    const error = (data.errors || [])[0];
    if (error) return fail((error.extensions && error.extensions.code) || error.message);
    const payload = (data.data || {}).cartCreate;
    if (payload && payload.userErrors && payload.userErrors[0]) return fail(payload.userErrors[0].message);
    const cart = payload && payload.cart;
    if (!cart) return fail('no cart');
    const codes = (payload.warnings || []).map((warning) => String(warning && warning.code));
    if (codes.includes('PRODUCT_UNAVAILABLE_IN_BUYER_LOCATION')) return add('info', 'couldnt', `${title}: couldn't check — ${product.title} isn't sold in ${country(ctx.shop.country)}.`) && rows;
    // the returned lines must be the requested ones: a lowered quantity can fall below a tier's minimum
    const nodes = ((cart.lines && cart.lines.nodes) || []).slice();
    const short = lines.find((entry) => {
      const at = nodes.findIndex((node) => node && node.merchandise && String(node.merchandise.id).split('/').pop() === entry.id);
      entry.node = at < 0 ? null : nodes.splice(at, 1)[0];
      return !entry.node || entry.node.quantity !== entry.qty;
    });
    if (short || codes.some((code) => /^MERCHANDISE_(NOT_ENOUGH_STOCK|OUT_OF_STOCK)$/.test(code))) {
      const entry = short || lines[0];
      return add('info', 'couldnt', `${title}: couldn't check — ${nameOf(entry.parts[0])} has less stock than ${entry.qty}.`) && rows;
    }
    const merchandise = (payload.warnings || []).find((warning) => /^MERCHANDISE_/.test(warning.code));
    if (merchandise) return fail(merchandise.message || merchandise.code);

    const units = lines.reduce((sum, entry) => sum + entry.parts.reduce((total, part) => total + (part.role === 'main' ? part.qty : 0), 0), 0);
    const code = item.input.discountCodes && option.code;
    const entered = code && (cart.discountCodes || []).find((entry) => entry && String(entry.code).toLowerCase() === code.toLowerCase());
    if (code && !(entered && entered.applicable)) {
      const cause = {
        DISCOUNT_NOT_FOUND: `code ${code} doesn't exist`,
        DISCOUNT_CURRENTLY_INACTIVE: `code ${code} is inactive or scheduled`,
        DISCOUNT_QUANTITY_NOT_IN_RANGE: `code ${code}: minimum not met by ${units} × ${product.title}`,
        DISCOUNT_PURCHASE_NOT_IN_RANGE: `code ${code}: minimum not met by ${units} × ${product.title}`,
        DISCOUNT_INCOMPATIBLE_PURCHASE_TYPE: `code ${code}: its purchase type excludes this cart`,
        DISCOUNT_NO_ENTITLED_LINE_ITEMS: `code ${code} doesn't apply to ${product.title}`,
      }[codes.find((value) => /^DISCOUNT_/.test(value))];
      add('warning', 'code', `${title}: ${cause || `code ${code} doesn't apply to this cart. Check its products, minimum quantity and dates`}.`);
    }

    // cents in the test cart's currency; merchant-typed amounts are shop currency; another currency than the page's
    // (no known rate) leaves only percentages to compare
    const node = lines[0].node;
    const currency = (node && node.cost && node.cost.subtotalAmount && node.cost.subtotalAmount.currencyCode) || ctx.shop.presentment_currency;
    const active = Shopify.currency || {};
    const conv = (amount) => (currency === ctx.shop.shop_currency ? amount : active.active === currency && active.rate > 0 ? Math.round(amount * active.rate) : null);
    const money = (amount) => ctx.money(Math.round(amount), currency);
    const groups = new Map();
    lines.forEach((entry) => {
      const subtotal = cents(entry.node.cost && entry.node.cost.subtotalAmount);
      const allocations = entry.node.discountAllocations || [];
      const off = allocations.reduce((sum, allocation) => sum + cents(allocation && allocation.discountedAmount), 0);
      entry.parts.forEach((part) => {
        const share = part.qty / entry.qty;
        const group = groups.get(part.group) || { part, lines: [], subtotal: 0, off: 0, names: new Set() };
        groups.set(part.group, group);
        group.lines.push({ n: part.qty, p: subtotal / entry.qty });
        group.subtotal += subtotal * share;
        group.off += off * share;
        allocations.forEach((allocation) => allocation && (allocation.title || allocation.code) && group.names.add(allocation.title || allocation.code));
      });
    });
    const bigger = model.live.map((other) => other.units).filter((value) => value > units);
    const next = bigger.length ? Math.min(...bigger) : units + 1;
    groups.forEach((group, key) => {
      const names = Array.from(group.names).join(', ');
      const named = names ? ` (${names})` : '';
      const off = Math.round(group.off);
      const subtotal = Math.round(group.subtotal);
      const share = subtotal > 0 ? (100 * off) / subtotal : 0;
      const tolerance = (expected) => Math.max(2 * group.lines.length, Math.round(0.005 * expected));
      if (/^gift:/.test(key)) {
        const gift = nameOf(group.part);
        if (subtotal - off > tolerance(subtotal)) add('warning', 'charged', `Free gift ${gift} in ${title}: charged ${money(subtotal - off)} — expected free. Create the Buy X get Y discount above.`);
        else add('ok', 'free', `Free gift ${gift} in ${title}: free, as shown.`);
        return;
      }
      const main = key === 'main';
      if (main && code && !(entered && entered.applicable)) return;
      const child = item.children[key];
      const expected = main ? discountOf(option, group.lines, conv) : child ? discountOf(child.d, group.lines, conv) : 0;
      const label = main ? title : `${title} · ${NAMES[child ? child.type : group.part.role] || group.part.role}`;
      if (expected == null) return add('info', 'couldnt', `${label}: couldn't check (fixed amounts in ${currency}).`);
      const limit = tolerance(expected);
      const asPercent = main ? option.type === 'percentage' : !!child && child.d.type === 'percentage';
      const shown = asPercent ? `${main ? option.pct : child.d.pct}%` : money(expected);
      const actual = asPercent ? percent(share) : money(off);
      const minimum = main ? units : 1;
      if (expected <= limit) {
        if (off > limit) {
          add('warning', 'unexpected', `${label}: ${percent(share)} applied${named} although this option shows no discount.${main ? ` If it's one of your tier discounts, raise its minimum quantity to ${next}.` : ''}`);
        } else if (main) add('ok', 'none', `${label}: no discount, as shown.`);
      } else if (off <= limit) {
        add('warning', 'missing', `${label}: no discount applied — expected ${shown}. Create the discount above. If it exists, check that it's active, applies to ${nameOf(group.part)} and has minimum quantity ${minimum}.`);
      } else if (Math.abs(off - expected) <= limit) {
        add('ok', 'ok', `${label}: ${asPercent ? shown : `${money(off)} off`} applied${named}.`);
      } else if (off < expected) {
        add('warning', 'less', `${label}: ${actual} applied${named} — expected ${shown}. Shopify applies the best discount the cart qualifies for: check the minimum quantity (${minimum}) and combinations of ${suggest(ctx, option, child)}.`);
      } else {
        add('warning', 'more', `${label}: ${actual} applied${named} — more than the ${shown} shown. Check the minimum quantity of ${names || 'the applied discount'}.`);
      }
    });
    return rows;
  };

  const runCheck = async (ctx, force) => {
    if (ctx.running || !ctx.panel.isConnected) return;
    let model;
    let items = null;
    try {
      model = build(ctx);
      items = plan(ctx, model);
    } catch (error) {
      console.error('Quantity breaks V2', error);
    }
    if (!items) {
      ctx.check = { at: Date.now(), failed: "the widget script isn't loaded", options: {} };
      return render(ctx);
    }
    const key = `shrine-qbv2-check:${ctx.shop.block_id}:${hash(JSON.stringify([ctx.shop.country, items.map((item) => [item.option.id, item.input, item.config])]))}`;
    const cached = !force && store(key);
    if (cached && Date.now() - cached.at < 600000) {
      ctx.check = cached;
      return render(ctx);
    }
    ctx.running = true;
    render(ctx);
    const check = { at: 0, failed: '', options: {}, banner: false };
    for (let i = 0; i < items.length && !check.failed; i += 1) {
      const item = items[i];
      if (item.skip) {
        check.options[item.option.id] = [['info', 'couldnt', `${item.option.title}: couldn't check (${item.skip}).`]];
        continue;
      }
      if (i) await wait(300);
      if (!ctx.panel.isConnected) return;
      const response = await request(ctx, item.input);
      if (response.failed) {
        check.failed = response.failed;
        break;
      }
      try {
        check.options[item.option.id] = evaluate(ctx, model, item, response.data || {});
      } catch (error) {
        console.error('Quantity breaks V2', error);
        check.options[item.option.id] = [['info', 'couldnt', `${item.option.title}: couldn't check (unexpected response).`]];
      }
    }
    // every discount the cards promise is missing: maybe this store doesn't apply automatic discounts to API carts
    const kinds = [].concat(...Object.values(check.options)).map((row) => row[1]).filter((kind) => /^(ok|free|missing|less|more|charged)$/.test(kind));
    check.banner = !check.failed && kinds.length > 0 && kinds.every((kind) => kind === 'missing' || kind === 'charged');
    check.at = Date.now();
    ctx.running = false;
    ctx.check = check;
    if (!check.failed) store(key, check);
    render(ctx);
  };

  /* ---------- rendering (class names of component-quantity-breaks-v2-editor.css) ---------- */
  // messages [level, text], errors first: warnings sit in the left-bordered __warnings box, check results in a plain __results list
  const list = (notes, kind = 'warnings') =>
    notes.length
      ? `<ul class="qb-v2-setup__${kind}">${notes
          .slice()
          .sort((a, b) => ORDER.indexOf(a[0]) - ORDER.indexOf(b[0]))
          .map(
            ([level, text]) =>
              `<li class="qb-v2-setup__msg qb-v2-setup__msg--${ICONS[level][2]}"><span class="qb-v2-setup__icon" aria-hidden="true">${ICONS[level][0]}</span> <span class="visually-hidden">${ICONS[level][1]}: </span>${esc(text)}</li>`
          )
          .join('')}</ul>`
      : '';
  const link = (href, text) => `<a href="${esc(href)}" target="_blank" rel="noopener">${text}</a>`;
  const button = (value, label, name) => `<button type="button" class="qb-v2-setup__btn" data-qbv2-copy="${esc(value)}" data-qbv2-label="${label}" aria-label="${esc(name)}">${label}</button>`;
  const blockHtml = (ctx, block) =>
    `<div class="qb-v2-setup__discount">${block.title ? `<h4 class="qb-v2-setup__discount-title">${esc(block.title)}</h4>` : ''}${block.text ? `<p class="qb-v2-setup__text">${esc(block.text)}</p>` : ''}${
      block.steps
        ? `<ol class="qb-v2-setup__steps">${block.steps
            .map(([text, value]) => `<li><span class="qb-v2-setup__step-text">${esc(text)}</span>${value ? button(value, 'Copy', `Copy ${value}`) : ''}</li>`)
            .join('')}</ol>`
        : ''
    }${list(block.notes || [])}${block.admin ? link(`https://${ctx.shop.domain}/admin/discounts/new`, 'Open Discounts in Shopify admin') : ''}${
      block.product ? link(ctx.product.admin_url, 'Open the product in Shopify admin') : ''
    }</div>`;
  const linkHtml = (title, cart) => {
    if (!cart) return '';
    if (cart.blocked) return `<p class="qb-v2-setup__muted"><button type="button" class="qb-v2-setup__btn" disabled>Copy cart link</button> ${esc(cart.blocked)}</p>`;
    return `<p>${button(cart.url, 'Copy cart link', `Copy cart link (${title})`)} <span class="qb-v2-setup__muted">${cart.note ? esc(cart.note) : 'A cart with this option, to test the price at checkout.'}</span></p>`;
  };
  // header, the discounts to create, the check result, warnings, the cart link (contract 6.8.2)
  const card = (ctx, id, title, blocks, notes, rows, cart) =>
    `<div class="qb-v2-setup__card${ctx.highlight && ctx.highlight.id === id && Date.now() < ctx.highlight.until ? ' is-highlighted' : ''}" data-qbv2-card="${esc(id)}"><h3 class="qb-v2-setup__card-title">${esc(
      title
    )}</h3>${blocks.map((block) => blockHtml(ctx, block)).join('')}${list(rows.map((row) => [row[0], row[2]]), 'results')}${list(notes)}${cart || ''}</div>`;
  const checked = (ctx) => {
    if (ctx.running) return 'Checking…';
    const minutes = ctx.check && ctx.check.at && !ctx.check.failed ? Math.floor((Date.now() - ctx.check.at) / 60000) : -1;
    return minutes < 0 ? '' : minutes < 1 ? 'Checked just now' : `Checked ${minutes} min ago`;
  };
  const header = (ctx, option) => {
    const plan = option.plan;
    const value = plan && num(plan.value);
    const page = ctx.shop.presentment_currency;
    return [
      option.title,
      `${option.units} × ${ctx.product.title}`,
      option.method === 'pack' ? `Pack variant ${option.data.pack_value}` : offText(ctx, option) || 'No discount',
      option.method === 'code' && option.code && `Code ${option.code}`,
      plan && `Selling plan ${plan.position}: ${plan.name}${{ percentage: `, ${value}% off`, fixed_amount: `, ${ctx.money(value, page)} off`, price: `, ${ctx.money(value, page)}` }[plan.type] || ''}`,
    ]
      .filter(Boolean)
      .join(' · ');
  };

  const render = (ctx) => {
    const { panel, body, ui } = ctx;
    if (!panel.isConnected) return;
    const focused = body.contains(document.activeElement) && document.activeElement;
    let model;
    try {
      model = build(ctx);
    } catch (error) {
      console.error('Quantity breaks V2', error);
      body.innerHTML = `<p>The discount setup couldn't load (${esc(error.message)}).</p>`;
      return;
    }
    const results = (ctx.check && ctx.check.options) || {};
    const all = model.notes.concat(...model.options.map((option) => option.notes.concat(...option.blocks.map((block) => block.notes || []))), ...model.blocks.map((block) => block.notes));
    const rows = [].concat(...model.options.map((option) => (results[option.id] || []).map((row) => row.concat(option.id))));
    const tally = (test) => all.filter(test).length + rows.filter(test).length;
    const ok = tally((row) => row[0] === 'ok');
    const warnings = tally((row) => row[0] === 'warning');
    const errors = all.filter((note) => note[0] === 'error');
    const kinds = (test) => rows.filter((row) => test.test(row[1])).length;
    // Something to create in Shopify admin (an option's discount, an included item's, a gift), a pack price to compare
    // or items an option adds to the cart? Plain quantity options without any of that: the panel says so in one line,
    // without their cards, cart links, check note or tips.
    const adds = (children) => children.some((child) => /^(bundle|gift|upsell|choice|builder|unlock)$/.test(child.type));
    const setup = model.blocks.length > 0 || adds(model.top) || model.options.some((option) => option.blocks.length > 0 || adds(option.children));
    const flagged = (option) => option.notes.length > 0 || (results[option.id] || []).some((row) => row[0] !== 'ok');
    const links = (option) => {
      try {
        return model.live.includes(option) ? linkHtml(option.title, cartLink(ctx, model, option)) : '';
      } catch (error) {
        console.error('Quantity breaks V2', error);
        return '';
      }
    };

    const caveat = "The check uses test carts that never touch your own cart. They have no customer login, so discounts for specific customers aren't checked.";
    const failed = ctx.check && ctx.check.failed;
    const why = /^\d+$/.test(String(failed)) ? `Shopify answered ${failed}` : failed;
    const plansList = (ctx.product.selling_plans || []).length
      ? `<p>Selling plan positions (Quantity option › Selling plan position):</p><ul>${ctx.product.selling_plans
          .map((sellingPlan) => `<li>${esc(`${sellingPlan.position} · ${sellingPlan.group} · ${sellingPlan.name}`)}</li>`)
          .join('')}</ul>`
      : '';
    const tips = setup && model.store.length ? `<ul>${model.store.map((text) => `<li>${esc(text)}</li>`).join('')}</ul>` : '';
    body.innerHTML =
      (model.env ? `<div class="qb-v2-setup__env"><p>${esc(model.env)}</p></div>` : '') +
      (setup
        ? ''
        : '<p class="qb-v2-setup__intro">None of these options has a discount, so there\'s nothing to create in Shopify admin. Set a Discount on an option and its setup steps show here.</p>') +
      list(model.notes.concat(failed && setup ? [['info', `The discount check couldn't run here (${why}). To test an option, add it to the cart in the preview and look at the price in the cart.`]] : [])) +
      (setup && ctx.check && ctx.check.banner
        ? "<p class=\"qb-v2-setup__banner\">No option got a discount in the test carts. Either the discounts aren't created yet, or this store doesn't apply automatic discounts to API test carts. A real add to cart in the preview shows what customers pay.</p>"
        : '') +
      model.options
        .filter((option) => setup || flagged(option))
        .map((option) => card(ctx, option.id, header(ctx, option), option.blocks, option.notes, results[option.id] || [], links(option)))
        .join('') +
      (model.blocks.length ? card(ctx, 'wrapper', 'Every option', model.blocks, [], []) : '') +
      // store-wide tips and the plan positions: folded, they're reference, not tasks
      (tips || plansList ? `<details class="qb-v2-setup__notes"><summary>Good to know</summary>${tips}${plansList}</details>` : '') +
      (setup
        ? `<div class="qb-v2-setup__footer"><button type="button" class="qb-v2-setup__btn" data-qbv2-recheck${ctx.running ? ' disabled' : ''}>${
            ctx.check && ctx.check.at ? 'Check again' : 'Check discounts'
          }</button><span class="qb-v2-setup__muted" data-qbv2-checked>${checked(ctx)}</span><p class="qb-v2-setup__muted">${esc(caveat)}</p></div>`
        : '');

    // summary: the problem in words when something is wrong, otherwise counts
    const words = [
      [kinds(/^(missing|code)$/), 'discount', ' missing'],
      [kinds(/^less$/), 'discount', ' too low'],
      [kinds(/^charged$/), 'gift', ' charged'],
      [errors.length, 'setup error', ''],
    ]
      .filter((entry) => entry[0])
      .map((entry) => plural(entry[0], entry[1]) + entry[2]);
    ctx.title.textContent = `Discount setup — ${words.length ? words.join(' · ') : setup ? 'only you see this' : 'nothing to set up'}`;
    const counts = [
      [ok, 'ok', 'OK', 'OK'],
      [warnings, 'warning', 'warning', 'warnings'],
      [errors.length, 'error', 'error', 'errors'],
    ].filter((entry) => entry[0]);
    ctx.status.innerHTML = ctx.running
      ? 'Checking…'
      : counts.map(([n, level, one, many]) => `${n} <span aria-hidden="true">${ICONS[level][0]}</span><span class="visually-hidden"> ${n === 1 ? one : many}</span>`).join(' · ');

    // opens itself for new problems; the merchant's own open / close choice is kept per block
    ctx.problems = errors
      .map((note) => note[2])
      .concat(rows.filter((row) => BAD.includes(row[1])).map((row) => `${row[1]}:${row[3]}`))
      .sort()
      .join('|');
    if (ctx.problems && ctx.problems !== ui.dismissed && !ui.open) store(ctx.key, Object.assign(ui, { open: true }));
    // only apply changes: a click on the summary that hasn't fired its toggle event yet must not be undone
    if (ctx.expected !== !!ui.open) panel.open = ctx.expected = !!ui.open;
    if (ui.scroll) body.scrollTop = ui.scroll;
    if (focused) {
      const again = focused.hasAttribute('data-qbv2-recheck')
        ? body.querySelector('[data-qbv2-recheck]')
        : Array.from(body.querySelectorAll('[data-qbv2-copy]')).find((other) => other.dataset.qbv2Copy === focused.dataset.qbv2Copy);
      if (again) again.focus({ preventScroll: true });
    }
  };

  // navigator.clipboard is blocked in some editor frames: fall back to a selected textarea
  const copy = (target) => {
    const text = target.dataset.qbv2Copy;
    const done = () => {
      target.textContent = 'Copied';
      setTimeout(() => (target.textContent = target.dataset.qbv2Label || 'Copy'), 1500);
    };
    const fallback = () => {
      const area = document.createElement('textarea');
      area.value = text;
      area.style.cssText = 'position:absolute;opacity:0;inset-inline-start:-9999px';
      target.after(area);
      area.focus({ preventScroll: true });
      area.select();
      let copied = false;
      try {
        copied = document.execCommand('copy');
      } catch (error) {
        // nothing copied
      }
      area.remove();
      target.focus({ preventScroll: true });
      if (copied) done();
    };
    if (navigator.clipboard) navigator.clipboard.writeText(text).then(done, fallback);
    else fallback();
  };

  /* ---------- panels ---------- */
  const init = (panel) => {
    const wrapper = panel.closest('quantity-breaks-v2');
    const shop = json(wrapper && wrapper.querySelector('script[data-qbv2-setup="shop"]'));
    const body = panel.querySelector('[data-qbv2-setup-body]');
    if (seen.has(panel) || !shop || !shop.product || !body) return;
    seen.add(panel);
    const key = `shrine-qbv2-panel:${shop.block_id}`;
    const ctx = {
      panel,
      wrapper,
      shop,
      body,
      key,
      product: shop.product,
      sid: wrapper.dataset.section || shop.section_id,
      title: panel.querySelector('summary > span'),
      status: panel.querySelector('[data-qbv2-status]'),
      ui: store(key) || {},
    };
    ctx.money = moneyOf(ctx);
    ctx.variants = () => (ctx.list = ctx.list || [].concat(json(wrapper.querySelector('quantity-breaks > script[type="application/json"]')) || []));
    panels.add(ctx);
    panel.addEventListener('toggle', () => {
      if (panel.open === ctx.expected) return; // our own change
      ctx.expected = panel.open;
      store(key, Object.assign(ctx.ui, { open: panel.open, dismissed: panel.open ? '' : ctx.problems }));
      if (panel.open && ctx.ui.scroll) body.scrollTop = ctx.ui.scroll;
    });
    body.addEventListener(
      'scroll',
      () => {
        clearTimeout(ctx.scrolled);
        ctx.scrolled = setTimeout(() => store(key, Object.assign(ctx.ui, { scroll: body.scrollTop })), 150);
      },
      { passive: true }
    );
    panel.addEventListener('click', (event) => {
      const target = event.target.closest('[data-qbv2-copy], [data-qbv2-recheck]');
      if (target && target.hasAttribute('data-qbv2-recheck')) runCheck(ctx, true);
      else if (target) copy(target);
    });
    render(ctx);
    // the first check, 1.5 s after the panel appears, once the widget is ready (or after 10 s without it)
    setTimeout(() => {
      if (!panel.isConnected) return;
      if (ready(wrapper) && wrapper.classList.contains('qb-v2--js')) return runCheck(ctx);
      const go = () => {
        wrapper.removeEventListener('qbv2:ready', go);
        clearTimeout(timer);
        runCheck(ctx);
      };
      const timer = setTimeout(go, 10000);
      wrapper.addEventListener('qbv2:ready', go);
    }, 1500);
  };
  const scan = (root) => {
    panels.forEach((ctx) => ctx.panel.isConnected || panels.delete(ctx));
    if (root && root.querySelectorAll) root.querySelectorAll('[data-qbv2-setup-root]').forEach(init);
  };

  document.addEventListener('qbv2:ready', (event) => scan(event.target));
  document.addEventListener('shopify:section:load', (event) => scan(event.target));
  document.addEventListener('qbv2:change', (event) => {
    panels.forEach((ctx) => {
      if (!ctx.wrapper.contains(event.target)) return;
      clearTimeout(ctx.changed);
      ctx.changed = setTimeout(() => render(ctx), 300);
    });
  });
  // a block selected in the sidebar: scroll its card into view inside the panel (never the page) and highlight it for 2 s
  document.addEventListener('shopify:block:select', (event) => {
    const id = event.detail && event.detail.blockId;
    panels.forEach((ctx) => {
      const target = ctx.cards && ctx.cards[id];
      const element = target && ctx.body.querySelector(`[data-qbv2-card="${CSS.escape(target)}"]`);
      if (!element) return;
      ctx.highlight = { id: target, until: Date.now() + 2000 };
      element.classList.add('is-highlighted');
      setTimeout(() => ctx.body.querySelectorAll('.is-highlighted').forEach((other) => other.classList.remove('is-highlighted')), 2000);
      if (ctx.panel.open && ctx.body.scrollHeight > ctx.body.clientHeight + 1) ctx.body.scrollTop += element.getBoundingClientRect().top - ctx.body.getBoundingClientRect().top - 8;
    });
  });
  // back from creating the discount in the admin tab: check again when the last check found a missing one
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState !== 'visible') return;
    panels.forEach((ctx) => {
      const rows = [].concat(...Object.values((ctx.check && ctx.check.options) || {}));
      if (ctx.panel.isConnected && rows.some((row) => BAD.includes(row[1]))) runCheck(ctx, true);
    });
  });
  setInterval(() => panels.forEach((ctx) => ctx.body.querySelectorAll('[data-qbv2-checked]').forEach((label) => (label.textContent = checked(ctx)))), 30000);
  scan(document);
})();

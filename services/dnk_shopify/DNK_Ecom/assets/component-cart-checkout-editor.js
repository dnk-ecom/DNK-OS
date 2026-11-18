/* Cart checkout editor checks (design mode only; loaded by component-cart-checkout.js). The core runs every check after
   each render and on section/block selection, per cart root, and replaces a check's previous notices. */
(() => {
  const cart = window.ShrineCart;
  if (window.ShrineCartCheckoutEditor || !cart || !cart.editor || !cart.editor.registerCheck) return;
  window.ShrineCartCheckoutEditor = { version: 1 };
  const blockIdOf = (el) => {
    const host = el.closest('[data-shopify-editor-block]');
    try { return host ? JSON.parse(host.getAttribute('data-shopify-editor-block')).id : undefined; } catch (e) { return undefined; }
  };
  const noExpress = (root) => !root.querySelector('.cart__dynamic-checkout-buttons');
  const EXPRESS_OFF = 'express buttons are off, so Require for express checkout has no effect.';

  cart.editor.registerCheck('checkout-terms', (ctx) => {
    const out = [];
    const boxes = [...ctx.root.querySelectorAll('tnc-chekcbox[data-form]')];
    if (boxes.length > 1) {
      out.push({ code: 'checkout-terms-duplicate', level: 'warning', title: 'Terms checkbox', blockId: blockIdOf(boxes[1]),
        text: 'this cart has two terms checkboxes, and they share one warning. Keep one.' });
    }
    const gated = boxes.find((box) => box.dataset.gateExpress === 'true');
    if (gated && noExpress(ctx.root)) {
      out.push({ code: 'checkout-terms-express-off', level: 'info', title: 'Terms checkbox', blockId: blockIdOf(gated), text: EXPRESS_OFF });
    }
    return out;
  });

  cart.editor.registerCheck('checkout-fields', (ctx) => {
    const out = [];
    const seen = {};
    const fields = [...ctx.root.querySelectorAll('cart-field[data-attribute]')];
    fields.forEach((field) => {
      const name = field.dataset.attribute;
      if (seen[name]) {
        out.push({ code: 'checkout-field-duplicate', level: 'error', title: 'Cart field', blockId: blockIdOf(field),
          text: 'two fields save to the same attribute name (' + name + '). Give each field its own name.' });
      }
      seen[name] = true;
    });
    const gated = fields.find((field) => field.dataset.gateExpress === 'true');
    if (gated && noExpress(ctx.root)) {
      out.push({ code: 'checkout-field-express-off', level: 'info', title: 'Cart field', blockId: blockIdOf(gated), text: EXPRESS_OFF });
    }
    return out;
  });

  cart.editor.registerCheck('checkout-timers', (ctx) => {
    const out = [];
    ctx.root.querySelectorAll('countdown-timer').forEach((timer) => {
      const type = timer.dataset.timerType;
      const blockId = blockIdOf(timer);
      const wrapper = timer.closest('.cart-timer');
      if (type === 'end_date' && timer.dataset.endTime && timer.end === null) {
        out.push({ code: 'checkout-timer-bad-date', level: 'error', title: 'Countdown timer', blockId,
          text: "the end date can't be read. Use the format 2026-12-24 18:00." });
      } else if (type === 'end_date' && typeof timer.end === 'number' && timer.end <= Date.now()) {
        out.push({ code: 'checkout-timer-ended', level: 'info', title: 'Countdown timer', blockId, text: 'the end date has passed.' });
      }
      if (type === 'cutoff' && wrapper && wrapper.hasAttribute('data-ended')) {
        out.push({ code: 'checkout-timer-no-workday', level: 'warning', title: 'Countdown timer', blockId,
          text: "every day of the next 14 is skipped, so customers don't see the timer. Check Week days to skip and Specific dates to skip." });
      }
    });
    return out;
  });

  // this file loads after the first renders: run the checks once now instead of waiting for the next render
  if (cart.require) cart.require('editor').then((api) => api && api.runAll && api.runAll());
})();

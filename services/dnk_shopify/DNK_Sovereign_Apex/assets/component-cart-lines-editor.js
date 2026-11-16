/* Shrine PRO cart lines, theme editor only (loaded by component-cart-lines.js in design mode, skeleton A37):
   the Subscribe & save notices lines-sub-hidden-gift, lines-upgrade-hidden-gift and lines-sub-both.
   The editor keeps one notice per code, so the results of one code are merged (their items joined). */
(() => {
  if (window.ShrineCartLinesEditor) return;
  const d = document;
  const qsa = (s, r) => Array.from((r || d).querySelectorAll(s));
  const esc = (v) => (window.CSS && CSS.escape ? CSS.escape(String(v)) : String(v).replace(/["\\\][]/g, '\\$&'));
  const blockOf = (el) => {
    try {
      return JSON.parse(el.dataset.shopifyEditorBlock || '{}').id;
    } catch (e) {
      return undefined;
    }
  };
  const uniq = (list) => list.filter((x, i) => x && list.indexOf(x) === i);
  const check = (ctx) => {
    const root = (ctx && ctx.root) || d;
    const hidden = uniq(qsa('cart-subscription-toggle[data-hidden-reason="gift"]', root).map((el) => el.dataset.title || el.dataset.handle));
    const upHidden = [];
    const both = [];
    let upBlock;
    let bothBlock;
    qsa('cart-subscription-upgrade', root).forEach((u) => {
      if (u.dataset.hiddenReason === 'gift') {
        upHidden.push(...(u.dataset.hiddenTitles || '').split(', '));
        upBlock = upBlock || blockOf(u);
        return;
      }
      if (u.hidden || u.querySelector('[data-upgrade-sample]')) return;
      // the items this block offers now that also show a per-line toggle in the same cart (02 L17)
      const shared = qsa(u.dataset.offer === 'all' ? '[data-upgrade-item]' : '[data-upgrade-offer]:not([hidden])', u).filter((el) =>
        root.querySelector('cart-subscription-toggle[data-line-key="' + esc(el.dataset.lineKey) + '"]:not([hidden])')
      );
      if (shared.length) {
        both.push(...shared.map((el) => el.dataset.title));
        bothBlock = bothBlock || blockOf(u);
      }
    });
    const out = [];
    const some = (list) => (list.length > 1 ? ', because they are also gifts or add-ons.' : ', because it is also a gift or add-on.');
    if (hidden.length) {
      out.push({ code: 'lines-sub-hidden-gift', level: 'info', title: 'Cart items', text: 'Subscribe & save is hidden on ' + hidden.join(', ') + some(hidden) });
    }
    const uh = uniq(upHidden);
    if (uh.length) {
      out.push({ code: 'lines-upgrade-hidden-gift', level: 'info', title: 'Subscribe & save', text: 'hidden for ' + uh.join(', ') + some(uh), blockId: upBlock });
    }
    const b = uniq(both);
    if (b.length) {
      out.push({
        code: 'lines-sub-both',
        level: 'info',
        title: 'Subscribe & save',
        blockId: bothBlock,
        text: 'two offers show for ' + b.join(', ') + ' (Cart items and this block). To keep one, turn off Show subscribe & save in Cart items or remove this block.',
      });
    }
    return out;
  };
  window.ShrineCartLinesEditor = { check };
  try {
    window.ShrineCart.editor.registerCheck('lines', check);
  } catch (e) {}
})();

/* Shrine PRO 2.0.0 cart pages, theme editor only: the Cart page V2 checks. Printed by sections/main-cart-v2.liquid in
   design mode only, after component-cart.js; the cart core runs the checks after every render of the page and shows
   their notices in the page's notice stack. Classic script, safe to run twice. */
(() => {
  if (window.ShrineCartPageEditor) return;
  const d = document;
  const check = (ctx) => {
    const root = ctx && ctx.surface === 'page-v2' && ctx.root;
    const out = [];
    const add = (code, level, text) => out.push({ code, level, title: 'Cart page V2', text });
    if (!root) return out;
    if (d.querySelector('cart-items, #main-cart-footer')) {
      add('pages-v2-classic-present', 'warning', 'the classic Cart items and Subtotal sections are also on this page. Remove them so customers see one cart.');
    }
    if (root.classList.contains('is-empty')) return out;
    if (!root.querySelector('#CartPage-Form')) {
      add('pages-v2-no-form', 'error', "the Cart items block is hidden, so checkout can't work. Show it again.");
    }
    if (!root.querySelector('.cart-page__summary [name="checkout"]')) {
      add('pages-v2-no-checkout', 'warning', 'the Summary has no Checkout button. Add a Checkout button block to it.');
    }
    return out;
  };
  const register = () => {
    const editor = window.ShrineCart && window.ShrineCart.editor;
    if (window.ShrineCartPageEditor || !editor || typeof editor.registerCheck !== 'function') return;
    window.ShrineCartPageEditor = { version: 1, check };
    editor.registerCheck('pages-v2', check);
  };
  register();
  if (!window.ShrineCartPageEditor) document.addEventListener('DOMContentLoaded', register, { once: true });
})();

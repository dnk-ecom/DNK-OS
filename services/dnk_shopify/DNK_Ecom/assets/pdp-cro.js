/*
  DNK-Ecom-Zerno-v.0.1.0 - PDP CRO Suite
  Custom elements for: StickyATC, QuantityBreaks, BundleBuilder, SizeChart
*/

class StickyATC extends HTMLElement {
  connectedCallback() {
    this.buyButtons = document.querySelector("[data-product-buy-buttons]");
    this.variantSelect = this.querySelector("[data-sticky-variant-select]");
    this.submitBtn = this.querySelector("[data-sticky-submit]");
    this.priceCurrent = this.querySelector(".sticky-atc-current-price");
    this.priceCompare = this.querySelector(".sticky-atc-compare-price");

    if (this.buyButtons) {
      this.observer = new IntersectionObserver(
        (entries) => {
          for (const entry of entries) {
            if (!entry.isIntersecting) {
              this.classList.add("is-visible");
            } else {
              this.classList.remove("is-visible");
            }
          }
        },
        { threshold: 0.1 }
      );
      this.observer.observe(this.buyButtons);
    }

    if (this.variantSelect) {
      this.variantSelect.addEventListener("change", this.handleVariantChange.bind(this));
    }

    if (this.submitBtn) {
      this.submitBtn.addEventListener("click", this.handleSubmit.bind(this));
    }

    document.addEventListener("variant:change", this.handleMainVariantChange.bind(this));
  }

  disconnectedCallback() {
    if (this.observer) {
      this.observer.disconnect();
    }
  }

  handleVariantChange() {
    const selectedOption = this.variantSelect?.selectedOptions[0];
    if (!selectedOption) return;

    const price = selectedOption.dataset.price;
    const comparePrice = selectedOption.dataset.comparePrice;

    if (this.priceCurrent && price) this.priceCurrent.textContent = price;
    if (this.priceCompare) {
      if (comparePrice) {
        this.priceCompare.textContent = comparePrice;
        this.priceCompare.hidden = false;
      } else {
        this.priceCompare.hidden = true;
      }
    }

    const mainVariantInput = document.querySelector("[data-product-variant-input]");
    if (mainVariantInput) {
      mainVariantInput.value = this.variantSelect.value;
      mainVariantInput.dispatchEvent(new Event("change", { bubbles: true }));
    }
  }

  handleMainVariantChange(event) {
    const variantId = event.detail?.variant?.id;
    if (variantId && this.variantSelect) {
      this.variantSelect.value = String(variantId);
      const selectedOption = this.variantSelect.selectedOptions[0];
      if (selectedOption) {
        const price = selectedOption.dataset.price;
        if (this.priceCurrent && price) this.priceCurrent.textContent = price;
      }
    }
  }

  async handleSubmit(event) {
    event.preventDefault();
    const mainForm = document.querySelector("theme-product-form form");
    if (mainForm) {
      const submitBtn = mainForm.querySelector('[type="submit"]');
      if (submitBtn) {
        submitBtn.click();
        return;
      }
    }

    const variantId = this.variantSelect ? this.variantSelect.value : document.querySelector("[data-product-variant-input]")?.value;
    if (!variantId) return;

    this.submitBtn.setAttribute("aria-busy", "true");
    this.submitBtn.disabled = true;

    try {
      if (window.Shopify?.actions?.updateCart) {
        await window.Shopify.actions.updateCart(
          { lines: [{ merchandiseId: String(variantId), quantity: 1 }] },
          { event: { context: "drawer", detail: { source: "sticky-atc" } } }
        );
      } else {
        const rootUrl = window.Shopify?.routes?.root || "/";
        await fetch(`${rootUrl}cart/add.js`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ items: [{ id: Number(variantId), quantity: 1 }] })
        });
        document.dispatchEvent(new CustomEvent("theme:cart:change"));
      }
    } catch (e) {
      console.error("[StickyATC] Add to cart failed", e);
    } finally {
      this.submitBtn.removeAttribute("aria-busy");
      this.submitBtn.disabled = false;
    }
  }
}

if (!customElements.get("sticky-atc")) {
  customElements.define("sticky-atc", StickyATC);
}

class QuantityBreaks extends HTMLElement {
  connectedCallback() {
    this.cards = this.querySelectorAll(".quantity-break-card");
    this.addEventListener("change", this.handleChange.bind(this));
  }

  handleChange(event) {
    const targetRadio = event.target.closest(".quantity-break-radio");
    if (!targetRadio) return;

    const qty = Number(targetRadio.value) || 1;

    this.cards.forEach((card) => {
      const isSelected = card.contains(targetRadio);
      card.classList.toggle("is-selected", isSelected);
    });

    const mainQtyInput = document.querySelector("theme-product-form input[name='quantity']");
    if (mainQtyInput) {
      mainQtyInput.value = String(qty);
      mainQtyInput.dispatchEvent(new Event("change", { bubbles: true }));
    }
  }
}

if (!customElements.get("quantity-breaks")) {
  customElements.define("quantity-breaks", QuantityBreaks);
}

class BundleBuilder extends HTMLElement {
  connectedCallback() {
    this.checkboxes = this.querySelectorAll("[data-bundle-input]");
    this.submitBtn = this.querySelector("[data-bundle-submit]");
    this.totalEl = this.querySelector("[data-bundle-total]");
    this.compareEl = this.querySelector("[data-bundle-compare]");
    this.discountPct = Number(this.dataset.discount) || 0;

    this.addEventListener("change", this.handleCheckboxChange.bind(this));
    if (this.submitBtn) {
      this.submitBtn.addEventListener("click", this.handleSubmit.bind(this));
    }
  }

  handleCheckboxChange() {
    let rawTotal = 0;
    this.checkboxes.forEach((cb) => {
      if (cb.checked) {
        rawTotal += Number(cb.dataset.price) || 0;
      }
    });

    const discountMultiplier = (100 - this.discountPct) / 100.0;
    const discountedTotal = Math.round(rawTotal * discountMultiplier);

    const formatMoney = (cents) => `$${(cents / 100).toFixed(2)}`;

    if (this.totalEl) this.totalEl.textContent = formatMoney(discountedTotal);
    if (this.compareEl) this.compareEl.textContent = formatMoney(rawTotal);
  }

  async handleSubmit(event) {
    event.preventDefault();
    const selectedLines = [];
    this.checkboxes.forEach((cb) => {
      if (cb.checked && cb.value) {
        selectedLines.push({ merchandiseId: String(cb.value), quantity: 1 });
      }
    });

    if (selectedLines.length === 0) return;

    this.submitBtn.setAttribute("aria-busy", "true");
    this.submitBtn.disabled = true;

    try {
      if (window.Shopify?.actions?.updateCart) {
        await window.Shopify.actions.updateCart(
          { lines: selectedLines },
          { event: { context: "drawer", detail: { source: "bundle-builder" } } }
        );
      } else {
        const rootUrl = window.Shopify?.routes?.root || "/";
        const items = selectedLines.map((l) => ({ id: Number(l.merchandiseId), quantity: l.quantity }));
        await fetch(`${rootUrl}cart/add.js`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ items })
        });
        document.dispatchEvent(new CustomEvent("theme:cart:change"));
      }
    } catch (e) {
      console.error("[BundleBuilder] Failed to add bundle items", e);
    } finally {
      this.submitBtn.removeAttribute("aria-busy");
      this.submitBtn.disabled = false;
    }
  }
}

if (!customElements.get("bundle-builder")) {
  customElements.define("bundle-builder", BundleBuilder);
}

class SizeChart extends HTMLElement {
  connectedCallback() {
    this.table = this.querySelector(".size-chart-table");
    this.pills = this.querySelectorAll(".size-chart-pill");
    this.addEventListener("click", this.handleClick.bind(this));
  }

  handleClick(event) {
    const pill = event.target.closest(".size-chart-pill");
    if (!pill) return;

    const unit = pill.dataset.unit;
    if (!unit) return;

    this.pills.forEach((p) => p.classList.toggle("is-active", p === pill));

    if (this.table) {
      const unitKey = unit.toLowerCase();
      const cells = this.table.querySelectorAll(`[data-unit-${unitKey}]`);
      cells.forEach((cell) => {
        const val = cell.getAttribute(`data-unit-${unitKey}`);
        if (val) cell.textContent = val;
      });
    }
  }
}

if (!customElements.get("size-chart")) {
  customElements.define("size-chart", SizeChart);
}

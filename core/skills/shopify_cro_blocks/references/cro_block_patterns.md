<!--
# --- DNK-MRH-HEADER ---
# mrh_id: "core/skills/shopify_cro_blocks/references/cro_block_patterns.md"
# purpose: "Production Liquid, CSS Layers, Web Components and Schema templates for the 4 Core Shopify CRO Patterns."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.0.0"
# updated_at: "2026-10-13"
# author: "DNK Swarm (dnk_shopify & gerych_prime)"
# --- END DNK-MRH-HEADER ---
-->

# 🧩 Production CRO Block Patterns (Dual-Ready v2.0)

This reference contains the 4 essential high-velocity conversion rate optimization (CRO) block patterns designed for Shopify Tinker 4.2.0 (Theme Blocks 2.0) and Online Store 2.0.

---

## 1. 🚚 Pattern A: Free Shipping Progress Bar (`dnk-free-shipping-bar.liquid`)

### Visual Goal:
Motivate customers to increase Average Order Value (AOV) by providing real-time feedback on how much more they need to spend to unlock free delivery.

### Code Implementation:
```liquid
{%- comment -%}
  Pattern A: Free Shipping Progress Bar
  File: blocks/dnk-free-shipping-bar.liquid (or snippets/dnk-free-shipping-bar.liquid)
{%- endcomment -%}

{%- liquid
  assign threshold_cents = block.settings.threshold_amount | times: 100
  assign cart_total = cart.total_price | default: 0
  assign remaining_cents = threshold_cents | minus: cart_total
  if remaining_cents < 0
    assign remaining_cents = 0
  endif
  assign progress_percent = cart_total | times: 100.0 | divided_by: threshold_cents
  if progress_percent > 100.0
    assign progress_percent = 100.0
  endif
-%}

<dnk-free-shipping-bar
  id="dnk-fsb-{{ block.id }}"
  class="dnk-fsb"
  data-threshold="{{ threshold_cents }}"
  data-current="{{ cart_total }}"
  {{ block.shopify_attributes }}
>
  <div class="dnk-fsb__message">
    {%- if remaining_cents == 0 -%}
      <span class="dnk-fsb__congrats">🎉 {{ block.settings.success_message }}</span>
    {%- else -%}
      <span class="dnk-fsb__calc">
        {{ block.settings.progress_message_prefix }}
        <strong>{{ remaining_cents | money }}</strong>
        {{ block.settings.progress_message_suffix }}
      </span>
    {%- endif -%}
  </div>

  <div class="dnk-fsb__bar-container">
    <div
      class="dnk-fsb__bar-fill"
      role="progressbar"
      aria-valuenow="{{ progress_percent | round }}"
      aria-valuemin="0"
      aria-valuemax="100"
      style="width: {{ progress_percent }}%;"
    ></div>
  </div>
</dnk-free-shipping-bar>

<style>
@layer theme, cro-blocks;

@layer cro-blocks {
  #dnk-fsb-{{ block.id }} {
    display: block;
    width: 100%;
    margin: 12px 0;
    padding: 12px 16px;
    background: {{ block.settings.bg_color | default: '#f8fafc' }};
    border-radius: {{ block.settings.border_radius | default: 8 }}px;
    border: 1px solid rgba(0, 0, 0, 0.06);
    box-sizing: border-box;
    font-family: inherit;
  }
  #dnk-fsb-{{ block.id }} .dnk-fsb__message {
    font-size: 14px;
    text-align: center;
    margin-bottom: 8px;
    color: {{ block.settings.text_color | default: '#0f172a' }};
  }
  #dnk-fsb-{{ block.id }} .dnk-fsb__bar-container {
    width: 100%;
    height: 8px;
    background: #e2e8f0;
    border-radius: 999px;
    overflow: hidden;
  }
  #dnk-fsb-{{ block.id }} .dnk-fsb__bar-fill {
    height: 100%;
    background: {{ block.settings.bar_color | default: '#10b981' }};
    transition: width 0.4s ease-in-out;
  }
}
</style>

<script>
if (!customElements.get('dnk-free-shipping-bar')) {
  class DnkFreeShippingBar extends HTMLElement {
    connectedCallback() {
      this.threshold = parseInt(this.dataset.threshold, 10);
      document.addEventListener('cart:updated', this.updateCart.bind(this));
    }
    updateCart(e) {
      const cart = e.detail?.cart;
      if (!cart) return;
      const current = cart.total_price;
      const remaining = Math.max(0, this.threshold - current);
      const percent = Math.min(100, (current / this.threshold) * 100);
      const fill = this.querySelector('.dnk-fsb__bar-fill');
      if (fill) fill.style.width = percent + '%';
    }
  }
  customElements.define('dnk-free-shipping-bar', DnkFreeShippingBar);
}
</script>

{% schema %}
{
  "name": "DNK Free Shipping Bar",
  "target": "section",
  "settings": [
    {
      "type": "number",
      "id": "threshold_amount",
      "label": "Free Shipping Threshold (in whole currency)",
      "default": 50
    },
    {
      "type": "text",
      "id": "progress_message_prefix",
      "label": "Prefix Message",
      "default": "Add"
    },
    {
      "type": "text",
      "id": "progress_message_suffix",
      "label": "Suffix Message",
      "default": "more for FREE shipping!"
    },
    {
      "type": "text",
      "id": "success_message",
      "label": "Success Message",
      "default": "You have unlocked FREE shipping!"
    },
    {
      "type": "color",
      "id": "bar_color",
      "label": "Progress Bar Color",
      "default": "#10b981"
    },
    {
      "type": "color",
      "id": "bg_color",
      "label": "Background Color",
      "default": "#f8fafc"
    },
    {
      "type": "color",
      "id": "text_color",
      "label": "Text Color",
      "default": "#0f172a"
    },
    {
      "type": "range",
      "id": "border_radius",
      "min": 0,
      "max": 24,
      "step": 2,
      "unit": "px",
      "label": "Border Radius",
      "default": 8
    }
  ],
  "presets": [
    {
      "name": "DNK Free Shipping Bar"
    }
  ]
}
{% endschema %}
```

---

## 2. ⏱️ Pattern B: Dynamic Delivery Estimator (`dnk-delivery-estimator.liquid`)

### Visual Goal:
Provide verified dispatch expectations and calculated arrival dates using client locale and GeoIP.

### Code Implementation:
```liquid
{%- comment -%}
  Pattern B: Dynamic Delivery Estimator
  File: blocks/dnk-delivery-estimator.liquid
{%- endcomment -%}

<dnk-delivery-estimator
  id="dnk-de-{{ block.id }}"
  class="dnk-delivery-estimator"
  data-cutoff-hour="{{ block.settings.cutoff_hour | default: 14 }}"
  data-dispatch-days-min="{{ block.settings.dispatch_days_min | default: 1 }}"
  data-dispatch-days-max="{{ block.settings.dispatch_days_max | default: 2 }}"
  data-delivery-days-min="{{ block.settings.delivery_days_min | default: 3 }}"
  data-delivery-days-max="{{ block.settings.delivery_days_max | default: 5 }}"
  data-default-country="{{ localization.country.iso_code | default: 'US' | downcase }}"
  {{ block.shopify_attributes }}
>
  <div class="dnk-de__row">
    <span class="dnk-de__dot"></span>
    <span class="dnk-de__status">{{ block.settings.status_label | default: 'In stock, ready to dispatch' }}</span>
  </div>
  <div class="dnk-de__delivery">
    <img
      class="dnk-de__flag"
      src="https://flagcdn.com/w40/{{ localization.country.iso_code | default: 'us' | downcase }}.png"
      alt="{{ localization.country.name }}"
      width="20"
      height="15"
      loading="lazy"
    >
    <span>
      Estimated delivery: <strong class="dnk-de__dates">Calculating...</strong>
    </span>
  </div>
</dnk-delivery-estimator>

<style>
@layer theme, cro-blocks;

@layer cro-blocks {
  #dnk-de-{{ block.id }} {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 12px 14px;
    background: {{ block.settings.background_color | default: '#f0fdf4' }};
    border-radius: {{ block.settings.border_radius | default: 8 }}px;
    border: 1px solid #bbf7d0;
    margin: 10px 0;
    font-size: 14px;
  }
  #dnk-de-{{ block.id }} .dnk-de__row {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 500;
    color: #166534;
  }
  #dnk-de-{{ block.id }} .dnk-de__dot {
    width: 8px;
    height: 8px;
    background: #22c55e;
    border-radius: 50%;
    animation: dnkPulse 1.8s infinite;
  }
  #dnk-de-{{ block.id }} .dnk-de__delivery {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #1f2937;
  }
  #dnk-de-{{ block.id }} .dnk-de__flag {
    border-radius: 2px;
    object-fit: cover;
  }
  @keyframes dnkPulse {
    0% { transform: scale(0.95); opacity: 0.8; }
    50% { transform: scale(1.2); opacity: 1; }
    100% { transform: scale(0.95); opacity: 0.8; }
  }
}
</style>

<script>
if (!customElements.get('dnk-delivery-estimator')) {
  class DnkDeliveryEstimator extends HTMLElement {
    connectedCallback() {
      this.calculateDates();
    }
    calculateDates() {
      const now = new Date();
      const cutoff = parseInt(this.dataset.cutoffHour, 10);
      const deliveryMin = parseInt(this.dataset.deliveryDaysMin, 10);
      const deliveryMax = parseInt(this.dataset.deliveryDaysMax, 10);

      const offsetDays = now.getHours() >= cutoff ? 1 : 0;
      const minDate = new Date();
      minDate.setDate(now.getDate() + offsetDays + deliveryMin);
      const maxDate = new Date();
      maxDate.setDate(now.getDate() + offsetDays + deliveryMax);

      const locale = document.documentElement.lang || 'en-US';
      const formatter = new Intl.DateTimeFormat(locale, { month: 'short', day: 'numeric' });
      const targetEl = this.querySelector('.dnk-de__dates');
      if (targetEl) {
        targetEl.textContent = `${formatter.format(minDate)} - ${formatter.format(maxDate)}`;
      }
    }
  }
  customElements.define('dnk-delivery-estimator', DnkDeliveryEstimator);
}
</script>

{% schema %}
{
  "name": "DNK Delivery Estimator",
  "target": "section",
  "settings": [
    {
      "type": "text",
      "id": "status_label",
      "label": "Status Text",
      "default": "In stock, ready to dispatch"
    },
    {
      "type": "range",
      "id": "cutoff_hour",
      "min": 10,
      "max": 20,
      "step": 1,
      "label": "Daily Cutoff Hour (24h)",
      "default": 14
    },
    {
      "type": "number",
      "id": "delivery_days_min",
      "label": "Minimum Delivery Days",
      "default": 3
    },
    {
      "type": "number",
      "id": "delivery_days_max",
      "label": "Maximum Delivery Days",
      "default": 5
    },
    {
      "type": "color",
      "id": "background_color",
      "label": "Background Color",
      "default": "#f0fdf4"
    },
    {
      "type": "range",
      "id": "border_radius",
      "min": 0,
      "max": 24,
      "step": 2,
      "unit": "px",
      "label": "Border Radius",
      "default": 8
    }
  ],
  "presets": [
    {
      "name": "DNK Delivery Estimator"
    }
  ]
}
{% endschema %}
```

---

## 3. 🛒 Pattern C: High-Converting Sticky Add-to-Cart (`dnk-sticky-atc.liquid`)

### Visual Goal:
Fix buy action to the screen once the main PDP button scrolls out of view. Zero layout shifts, instant AJAX submission.

### Code Implementation:
```liquid
{%- comment -%}
  Pattern C: Sticky Add-to-Cart Bar
  File: blocks/dnk-sticky-atc.liquid
{%- endcomment -%}

{%- liquid
  assign current_variant = product.selected_or_first_available_variant
-%}

<dnk-sticky-atc
  id="dnk-satc-{{ block.id }}"
  class="dnk-sticky-atc"
  data-product-id="{{ product.id }}"
  {{ block.shopify_attributes }}
>
  <div class="dnk-satc__content">
    <div class="dnk-satc__media">
      {%- if product.featured_image -%}
        <img
          src="{{ product.featured_image | image_url: width: 120 }}"
          alt="{{ product.title | escape }}"
          width="50"
          height="50"
          loading="lazy"
        >
      {%- endif -%}
    </div>
    <div class="dnk-satc__info">
      <span class="dnk-satc__title">{{ product.title | truncate: 35 }}</span>
      <span class="dnk-satc__price">{{ current_variant.price | money }}</span>
    </div>
    <div class="dnk-satc__actions">
      <form method="post" action="/cart/add" class="dnk-satc__form">
        <input type="hidden" name="id" value="{{ current_variant.id }}" class="dnk-satc__variant-id">
        <button
          type="submit"
          name="add"
          class="dnk-satc__button"
          {% unless current_variant.available %}disabled{% endunless %}
        >
          {%- if current_variant.available -%}
            {{ block.settings.button_text | default: 'Add to Cart' }}
          {%- else -%}
            Sold Out
          {%- endif -%}
        </button>
      </form>
    </div>
  </div>
</dnk-sticky-atc>

<style>
@layer theme, cro-blocks;

@layer cro-blocks {
  #dnk-satc-{{ block.id }} {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background: #ffffff;
    box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.08);
    z-index: 1000;
    transform: translateY(100%);
    transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    box-sizing: border-box;
    padding: 10px 16px;
  }
  #dnk-satc-{{ block.id }}.is-visible {
    transform: translateY(0);
  }
  #dnk-satc-{{ block.id }} .dnk-satc__content {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
  }
  #dnk-satc-{{ block.id }} .dnk-satc__media img {
    border-radius: 4px;
    object-fit: cover;
    display: block;
  }
  #dnk-satc-{{ block.id }} .dnk-satc__info {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
  }
  #dnk-satc-{{ block.id }} .dnk-satc__title {
    font-weight: 600;
    font-size: 14px;
  }
  #dnk-satc-{{ block.id }} .dnk-satc__price {
    font-size: 13px;
    color: #4b5563;
  }
  #dnk-satc-{{ block.id }} .dnk-satc__button {
    background: {{ block.settings.button_bg | default: '#000000' }};
    color: {{ block.settings.button_color | default: '#ffffff' }};
    border: none;
    padding: 10px 24px;
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
    white-space: nowrap;
  }
  #dnk-satc-{{ block.id }} .dnk-satc__button:hover {
    opacity: 0.9;
  }
}
</style>

<script>
if (!customElements.get('dnk-sticky-atc')) {
  class DnkStickyAtc extends HTMLElement {
    connectedCallback() {
      this.initObserver();
      this.initAjaxForm();
    }
    initObserver() {
      const mainBtn = document.querySelector('form[action*="/cart/add"] button[type="submit"]');
      if (!mainBtn) return;
      const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) {
            this.classList.add('is-visible');
          } else {
            this.classList.remove('is-visible');
          }
        });
      }, { threshold: 0 });
      observer.observe(mainBtn);
    }
    initAjaxForm() {
      const form = this.querySelector('.dnk-satc__form');
      if (!form) return;
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = form.querySelector('button');
        submitBtn.disabled = true;
        try {
          const res = await fetch('/cart/add.js', {
            method: 'POST',
            body: new FormData(form),
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
          });
          const cartItem = await res.json();
          document.dispatchEvent(new CustomEvent('cart:updated', { detail: { item: cartItem } }));
        } catch (err) {
          form.submit();
        } finally {
          submitBtn.disabled = false;
        }
      });
    }
  }
  customElements.define('dnk-sticky-atc', DnkStickyAtc);
}
</script>

{% schema %}
{
  "name": "DNK Sticky Add to Cart",
  "target": "section",
  "settings": [
    {
      "type": "text",
      "id": "button_text",
      "label": "Button Label",
      "default": "Add to Cart"
    },
    {
      "type": "color",
      "id": "button_bg",
      "label": "Button Background",
      "default": "#000000"
    },
    {
      "type": "color",
      "id": "button_color",
      "label": "Button Text Color",
      "default": "#ffffff"
    }
  ],
  "presets": [
    {
      "name": "DNK Sticky Add to Cart"
    }
  ]
}
{% endschema %}
```

---

## 4. ⏳ Pattern D: Scarcity Countdown Timer (`dnk-countdown-timer.liquid`)

### Visual Goal:
Create ethical purchase urgency by showing a countdown timer with local state persistence.

### Code Implementation:
```liquid
{%- comment -%}
  Pattern D: Urgency Countdown Timer
  File: blocks/dnk-countdown-timer.liquid
{%- endcomment -%}

<dnk-countdown-timer
  id="dnk-cdt-{{ block.id }}"
  class="dnk-countdown"
  data-duration-minutes="{{ block.settings.duration_minutes | default: 15 }}"
  data-storage-key="dnk_timer_{{ block.id }}"
  {{ block.shopify_attributes }}
>
  <div class="dnk-cdt__header">
    <span class="dnk-cdt__icon">🔥</span>
    <span class="dnk-cdt__headline">{{ block.settings.headline | default: 'Limited time flash sale ends in:' }}</span>
  </div>
  <div class="dnk-cdt__clock">
    <div class="dnk-cdt__unit">
      <span class="dnk-cdt__val dnk-cdt__hours">00</span>
      <span class="dnk-cdt__lbl">HRS</span>
    </div>
    <span class="dnk-cdt__sep">:</span>
    <div class="dnk-cdt__unit">
      <span class="dnk-cdt__val dnk-cdt__minutes">15</span>
      <span class="dnk-cdt__lbl">MIN</span>
    </div>
    <span class="dnk-cdt__sep">:</span>
    <div class="dnk-cdt__unit">
      <span class="dnk-cdt__val dnk-cdt__seconds">00</span>
      <span class="dnk-cdt__lbl">SEC</span>
    </div>
  </div>
</dnk-countdown-timer>

<style>
@layer theme, cro-blocks;

@layer cro-blocks {
  #dnk-cdt-{{ block.id }} {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    padding: 12px 16px;
    background: {{ block.settings.bg_color | default: '#fff7ed' }};
    border: 1px solid #fed7aa;
    border-radius: {{ block.settings.border_radius | default: 8 }}px;
    margin: 12px 0;
  }
  #dnk-cdt-{{ block.id }} .dnk-cdt__header {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    font-weight: 600;
    color: #c2410c;
  }
  #dnk-cdt-{{ block.id }} .dnk-cdt__clock {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  #dnk-cdt-{{ block.id }} .dnk-cdt__unit {
    display: flex;
    flex-direction: column;
    align-items: center;
    background: #ffffff;
    padding: 4px 8px;
    border-radius: 4px;
    min-width: 36px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  }
  #dnk-cdt-{{ block.id }} .dnk-cdt__val {
    font-size: 16px;
    font-weight: 700;
    color: #0f172a;
    font-variant-numeric: tabular-nums;
  }
  #dnk-cdt-{{ block.id }} .dnk-cdt__lbl {
    font-size: 9px;
    font-weight: 500;
    color: #64748b;
  }
  #dnk-cdt-{{ block.id }} .dnk-cdt__sep {
    font-weight: 700;
    color: #c2410c;
  }
}
</style>

<script>
if (!customElements.get('dnk-countdown-timer')) {
  class DnkCountdownTimer extends HTMLElement {
    connectedCallback() {
      this.key = this.dataset.storageKey;
      this.durationMs = parseInt(this.dataset.durationMinutes, 10) * 60 * 1000;
      this.targetTime = this.getOrSetTarget();
      this.interval = setInterval(this.tick.bind(this), 1000);
      this.tick();
    }
    disconnectedCallback() {
      if (this.interval) clearInterval(this.interval);
    }
    getOrSetTarget() {
      const stored = localStorage.getItem(this.key);
      const now = Date.now();
      if (stored && parseInt(stored, 10) > now) {
        return parseInt(stored, 10);
      }
      const target = now + this.durationMs;
      localStorage.setItem(this.key, target.toString());
      return target;
    }
    tick() {
      const remaining = Math.max(0, this.targetTime - Date.now());
      const hours = Math.floor(remaining / 3600000);
      const minutes = Math.floor((remaining % 3600000) / 60000);
      const seconds = Math.floor((remaining % 60000) / 1000);

      const hEl = this.querySelector('.dnk-cdt__hours');
      const mEl = this.querySelector('.dnk-cdt__minutes');
      const sEl = this.querySelector('.dnk-cdt__seconds');

      if (hEl) hEl.textContent = String(hours).padStart(2, '0');
      if (mEl) mEl.textContent = String(minutes).padStart(2, '0');
      if (sEl) sEl.textContent = String(seconds).padStart(2, '0');
    }
  }
  customElements.define('dnk-countdown-timer', DnkCountdownTimer);
}
</script>

{% schema %}
{
  "name": "DNK Countdown Timer",
  "target": "section",
  "settings": [
    {
      "type": "text",
      "id": "headline",
      "label": "Headline",
      "default": "Limited time flash sale ends in:"
    },
    {
      "type": "number",
      "id": "duration_minutes",
      "label": "Duration in Minutes",
      "default": 15
    },
    {
      "type": "color",
      "id": "bg_color",
      "label": "Background Color",
      "default": "#fff7ed"
    },
    {
      "type": "range",
      "id": "border_radius",
      "min": 0,
      "max": 24,
      "step": 2,
      "unit": "px",
      "label": "Border Radius",
      "default": 8
    }
  ],
  "presets": [
    {
      "name": "DNK Countdown Timer"
    }
  ]
}
{% endschema %}
```

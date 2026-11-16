/* --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_shopify/DNK-e.com/assets/dnk-vton.js"
# purpose: "DNK AI Virtual Try-On Client Engine for DNK-ecom OS 2.0"
# canonical_source: true
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER --- */

(function () {
  'use strict';

  const STORAGE_KEY = 'dnk_vton_state_v1';
  const PHOTO_STORAGE_KEY = 'dnk_vton_user_photo_v1';
  const MAX_CANVAS_DIM = 1024;
  const JPEG_QUALITY = 0.85;

  const DEFAULT_CONFIG = {
    endpoint: '/apps/dnk-vton/generate',
    locale: document.documentElement.lang || 'uk',
    slots: [
      { key: 'upper', label: 'Верх (Upper)', icon: 'shirt' },
      { key: 'bottom', label: 'Низ (Bottom)', icon: 'pants' },
      { key: 'full_body', label: 'Образ / Сукня (Full)', icon: 'dress' },
      { key: 'shoes', label: 'Взуття (Shoes)', icon: 'shoes' },
      { key: 'accessory', label: 'Аксесуари (Accessory)', icon: 'bag' }
    ]
  };

  const I18N = {
    uk: {
      title: 'DNK Примірочна',
      subtitle: 'Штучний Інтелект примірки',
      uploadPrompt: 'Завантажте фото на повний зріст',
      uploadHint: 'JPG або PNG до 15MB. Обличчя та фігура зберігаються 100%',
      removePhoto: 'Видалити фото',
      emptySlot: 'Слот порожній. Натисніть «Приміряти» на товарі',
      generateBtn: 'Згенерувати образ з ШІ',
      generatingMsg1: 'Аналіз пропорцій та освітлення...',
      generatingMsg2: 'Підбір крою та посадки тканини...',
      generatingMsg3: 'Фінальна рендеринг-генерація...',
      addToCartBtn: 'Купити весь образ',
      itemAddedToast: 'Товар додано до примірочної',
      cartSuccessToast: 'Всі товари додано до кошика!',
      errorNoPhoto: 'Будь ласка, завантажте своє фото',
      errorNoGarments: 'Оберіть хоча б одну річ для примірки',
      errorNetwork: 'Помилка генерації. Спробуйте ще раз'
    },
    en: {
      title: 'DNK Fitting Room',
      subtitle: 'AI Virtual Try-On',
      uploadPrompt: 'Upload a full-body photo',
      uploadHint: 'JPG or PNG up to 15MB. 100% identity and pose preservation',
      removePhoto: 'Remove photo',
      emptySlot: 'Slot is empty. Click «Try On» on any product',
      generateBtn: 'Generate AI Fitting',
      generatingMsg1: 'Analyzing proportions and lighting...',
      generatingMsg2: 'Adapting garment drape & fabric texture...',
      generatingMsg3: 'Final photorealistic rendering...',
      addToCartBtn: 'Add Full Outfit to Cart',
      itemAddedToast: 'Item added to fitting room',
      cartSuccessToast: 'All items added to cart!',
      errorNoPhoto: 'Please upload your photo first',
      errorNoGarments: 'Please select at least one garment to try on',
      errorNetwork: 'Generation error. Please try again'
    }
  };

  class DNKVirtualFittingRoom {
    constructor() {
      this.config = Object.assign({}, DEFAULT_CONFIG, window.DNK_VTON_CONFIG || {});
      const lang = this.config.locale.startsWith('uk') ? 'uk' : 'en';
      this.t = I18N[lang] || I18N.uk;

      this.state = {
        photo: null,
        items: {},
        resultImage: null,
        isGenerating: false
      };

      this.elements = {};
      this.init();
    }

    init() {
      this.loadState();
      this.bindDOM();
      this.bindEvents();
      this.updateUI();
      this.attachProductPageListeners();
    }

    loadState() {
      try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (raw) {
          const parsed = JSON.parse(raw);
          if (parsed && typeof parsed.items === 'object') {
            this.state.items = parsed.items;
          }
        }
        const cachedPhoto = localStorage.getItem(PHOTO_STORAGE_KEY);
        if (cachedPhoto && cachedPhoto.startsWith('data:image/')) {
          this.state.photo = cachedPhoto;
        }
      } catch (err) {
        console.warn('[DNK VTON] State storage warning:', err);
      }
    }

    saveState() {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify({ items: this.state.items }));
        if (this.state.photo) {
          localStorage.setItem(PHOTO_STORAGE_KEY, this.state.photo);
        } else {
          localStorage.removeItem(PHOTO_STORAGE_KEY);
        }
      } catch (err) {
        console.warn('[DNK VTON] LocalStorage quota reached');
      }
    }

    bindDOM() {
      this.elements.launcher = document.getElementById('dnk-vton-launcher');
      this.elements.badge = document.getElementById('dnk-vton-badge');
      this.elements.backdrop = document.getElementById('dnk-vton-backdrop');
      this.elements.drawer = document.getElementById('dnk-vton-drawer');
      this.elements.closeBtn = document.getElementById('dnk-vton-close');
      this.elements.dropzone = document.getElementById('dnk-vton-dropzone');
      this.elements.fileInput = document.getElementById('dnk-vton-file-input');
      this.elements.photoPreview = document.getElementById('dnk-vton-photo-preview');
      this.elements.photoImg = document.getElementById('dnk-vton-photo-img');
      this.elements.photoRemove = document.getElementById('dnk-vton-photo-remove');
      this.elements.slotsContainer = document.getElementById('dnk-vton-slots');
      this.elements.generateBtn = document.getElementById('dnk-vton-btn-generate');
      this.elements.cartBtn = document.getElementById('dnk-vton-btn-cart');
      this.elements.resultContainer = document.getElementById('dnk-vton-result-container');
      this.elements.resultImg = document.getElementById('dnk-vton-result-img');
      this.elements.loader = document.getElementById('dnk-vton-loader');
      this.elements.loaderText = document.getElementById('dnk-vton-loader-text');
      this.elements.toast = document.getElementById('dnk-vton-toast');
    }

    bindEvents() {
      if (this.elements.launcher) {
        this.elements.launcher.addEventListener('click', () => this.openDrawer());
      }
      if (this.elements.closeBtn) {
        this.elements.closeBtn.addEventListener('click', () => this.closeDrawer());
      }
      if (this.elements.backdrop) {
        this.elements.backdrop.addEventListener('click', () => this.closeDrawer());
      }

      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && this.isDrawerOpen()) {
          this.closeDrawer();
        }
      });

      if (this.elements.fileInput) {
        this.elements.fileInput.addEventListener('change', (e) => {
          if (e.target.files && e.target.files[0]) {
            this.handleUserPhotoUpload(e.target.files[0]);
          }
        });
      }

      if (this.elements.photoRemove) {
        this.elements.photoRemove.addEventListener('click', () => {
          this.state.photo = null;
          this.state.resultImage = null;
          this.saveState();
          this.updateUI();
        });
      }

      if (this.elements.generateBtn) {
        this.elements.generateBtn.addEventListener('click', () => this.generateTryOn());
      }

      if (this.elements.cartBtn) {
        this.elements.cartBtn.addEventListener('click', () => this.addOutfitToCart());
      }

      // Delegate clear slot buttons
      if (this.elements.slotsContainer) {
        this.elements.slotsContainer.addEventListener('click', (e) => {
          const btn = e.target.closest('[data-clear-slot]');
          if (btn) {
            const slotKey = btn.getAttribute('data-clear-slot');
            this.removeItem(slotKey);
          }
        });
      }
    }

    openDrawer() {
      if (this.elements.drawer) {
        this.elements.drawer.classList.add('is-open');
      }
      if (this.elements.backdrop) {
        this.elements.backdrop.classList.add('is-open');
      }
      document.body.style.overflow = 'hidden';
    }

    closeDrawer() {
      if (this.elements.drawer) {
        this.elements.drawer.classList.remove('is-open');
      }
      if (this.elements.backdrop) {
        this.elements.backdrop.classList.remove('is-open');
      }
      document.body.style.overflow = '';
    }

    isDrawerOpen() {
      return this.elements.drawer && this.elements.drawer.classList.contains('is-open');
    }

    handleUserPhotoUpload(file) {
      if (!file.type.match(/image\/(jpeg|png|webp)/i)) {
        this.showToast('Підтримуються тільки формати JPG, PNG, WebP');
        return;
      }

      const reader = new FileReader();
      reader.onload = (event) => {
        const img = new Image();
        img.onload = () => {
          // Canvas compression
          let width = img.width;
          let height = img.height;
          if (width > MAX_CANVAS_DIM || height > MAX_CANVAS_DIM) {
            if (width > height) {
              height = Math.round((height * MAX_CANVAS_DIM) / width);
              width = MAX_CANVAS_DIM;
            } else {
              width = Math.round((width * MAX_CANVAS_DIM) / height);
              height = MAX_CANVAS_DIM;
            }
          }

          const canvas = document.createElement('canvas');
          canvas.width = width;
          canvas.height = height;
          const ctx = canvas.getContext('2d');
          ctx.drawImage(img, 0, 0, width, height);

          this.state.photo = canvas.toDataURL('image/jpeg', JPEG_QUALITY);
          this.state.resultImage = null; // reset previous result
          this.saveState();
          this.updateUI();
          this.showToast('Фото успішно завантажено');
        };
        img.src = event.target.result;
      };
      reader.readAsDataURL(file);
    }

    addItem(slotKey, itemData) {
      if (!slotKey || !itemData || !itemData.variantId) return;

      this.state.items[slotKey] = {
        productId: itemData.productId,
        variantId: itemData.variantId,
        title: itemData.title || '',
        variantTitle: itemData.variantTitle || '',
        price: itemData.price || 0,
        image: itemData.image || '',
        slotKey: slotKey
      };

      this.state.resultImage = null;
      this.saveState();
      this.updateUI();
      this.showToast(this.t.itemAddedToast);
      this.openDrawer();
    }

    removeItem(slotKey) {
      if (this.state.items[slotKey]) {
        delete this.state.items[slotKey];
        this.state.resultImage = null;
        this.saveState();
        this.updateUI();
      }
    }

    updateUI() {
      // Badge count
      const count = Object.keys(this.state.items).length;
      if (this.elements.badge) {
        this.elements.badge.textContent = count;
        if (count > 0) {
          this.elements.badge.classList.add('is-visible');
        } else {
          this.elements.badge.classList.remove('is-visible');
        }
      }

      // User photo section
      if (this.state.photo) {
        if (this.elements.dropzone) this.elements.dropzone.style.display = 'none';
        if (this.elements.photoPreview) this.elements.photoPreview.style.display = 'block';
        if (this.elements.photoImg) this.elements.photoImg.src = this.state.photo;
      } else {
        if (this.elements.dropzone) this.elements.dropzone.style.display = 'flex';
        if (this.elements.photoPreview) this.elements.photoPreview.style.display = 'none';
        if (this.elements.photoImg) this.elements.photoImg.src = '';
      }

      // Slots Grid
      if (this.elements.slotsContainer) {
        this.renderSlots();
      }

      // Generate button disabled state
      const hasGarments = count > 0;
      const hasPhoto = Boolean(this.state.photo);
      if (this.elements.generateBtn) {
        this.elements.generateBtn.disabled = !hasGarments || !hasPhoto || this.state.isGenerating;
      }

      // Result vs Loader view
      if (this.state.isGenerating) {
        if (this.elements.resultContainer) this.elements.resultContainer.style.display = 'none';
        if (this.elements.loader) this.elements.loader.style.display = 'flex';
      } else if (this.state.resultImage) {
        if (this.elements.loader) this.elements.loader.style.display = 'none';
        if (this.elements.resultContainer) this.elements.resultContainer.style.display = 'block';
        if (this.elements.resultImg) this.elements.resultImg.src = this.state.resultImage;
      } else {
        if (this.elements.loader) this.elements.loader.style.display = 'none';
        if (this.elements.resultContainer) this.elements.resultContainer.style.display = 'none';
      }

      // Cart button visibility
      if (this.elements.cartBtn) {
        this.elements.cartBtn.style.display = hasGarments ? 'flex' : 'none';
      }
    }

    renderSlots() {
      const container = this.elements.slotsContainer;
      container.innerHTML = '';

      this.config.slots.forEach((slot) => {
        const item = this.state.items[slot.key];
        const card = document.createElement('div');
        card.className = `dnk-vton-slot-card ${item ? 'is-active' : ''}`;

        if (item) {
          card.innerHTML = `
            <div class="dnk-vton-slot-header">
              <span class="dnk-vton-slot-tag">${slot.label}</span>
              <button class="dnk-vton-slot-clear" data-clear-slot="${slot.key}" title="Видалити">&times;</button>
            </div>
            <img class="dnk-vton-slot-image" src="${item.image}" alt="${item.title}" />
            <div class="dnk-vton-slot-info">
              <div class="dnk-vton-slot-title">${item.title}</div>
              <div class="dnk-vton-slot-variant">${item.variantTitle || ''}</div>
            </div>
          `;
        } else {
          card.innerHTML = `
            <div class="dnk-vton-slot-header">
              <span class="dnk-vton-slot-tag">${slot.label}</span>
            </div>
            <div class="dnk-vton-slot-empty">
              <span>+ Слот вільний</span>
            </div>
          `;
        }
        container.appendChild(card);
      });
    }

    async generateTryOn() {
      if (!this.state.photo) {
        this.showToast(this.t.errorNoPhoto);
        return;
      }

      const activeSlots = Object.values(this.state.items);
      if (activeSlots.length === 0) {
        this.showToast(this.t.errorNoGarments);
        return;
      }

      this.state.isGenerating = true;
      this.updateUI();

      // Progressive status updates
      const messages = [this.t.generatingMsg1, this.t.generatingMsg2, this.t.generatingMsg3];
      let msgIdx = 0;
      const interval = setInterval(() => {
        msgIdx = (msgIdx + 1) % messages.length;
        if (this.elements.loaderText) {
          this.elements.loaderText.textContent = messages[msgIdx];
        }
      }, 2500);

      try {
        const payload = {
          user_image: this.state.photo,
          slots: activeSlots.map((s) => ({
            slot_key: s.slotKey,
            product_id: s.productId,
            variant_id: s.variantId,
            product_title: s.title,
            variant_label: s.variantTitle,
            garment_image_url: s.image
          }))
        };

        const res = await fetch(this.config.endpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify(payload)
        });

        clearInterval(interval);

        if (!res.ok) {
          throw new Error('HTTP ' + res.status);
        }

        const data = await res.json();
        if (data.image_url) {
          this.state.resultImage = data.image_url;
        } else {
          throw new Error(data.message || 'No image returned');
        }
      } catch (err) {
        clearInterval(interval);
        console.error('[DNK VTON] Generation failed:', err);
        this.showToast(this.t.errorNetwork);
      } finally {
        this.state.isGenerating = false;
        this.updateUI();
      }
    }

    async addOutfitToCart() {
      const items = Object.values(this.state.items).map((item) => ({
        id: item.variantId,
        quantity: 1
      }));

      if (items.length === 0) return;

      try {
        const res = await fetch('/cart/add.js', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify({ items })
        });

        if (res.ok) {
          this.showToast(this.t.cartSuccessToast);
          // Dispatch standard Shopify cart events
          document.dispatchEvent(new CustomEvent('cart:refresh', { bubbles: true }));
          document.dispatchEvent(new CustomEvent('dnk:cart:updated', { bubbles: true }));
          this.closeDrawer();
        } else {
          throw new Error('Failed to add to cart');
        }
      } catch (err) {
        console.error('[DNK VTON] Cart error:', err);
        this.showToast('Не вдалося додати речі до кошика');
      }
    }

    showToast(msg) {
      if (!this.elements.toast) return;
      this.elements.toast.textContent = msg;
      this.elements.toast.classList.add('is-visible');
      clearTimeout(this.toastTimer);
      this.toastTimer = setTimeout(() => {
        this.elements.toast.classList.remove('is-visible');
      }, 3500);
    }

    attachProductPageListeners() {
      // Find all DNK VTON trigger buttons on PDP or cards
      document.addEventListener('click', (e) => {
        const btn = e.target.closest('[data-dnk-vton-trigger]');
        if (!btn) return;

        e.preventDefault();
        const slotKey = btn.getAttribute('data-vton-slot') || 'upper';
        const productId = btn.getAttribute('data-product-id');
        let variantId = btn.getAttribute('data-variant-id');
        const title = btn.getAttribute('data-product-title') || document.title;
        let image = btn.getAttribute('data-product-image') || '';

        // If on PDP, dynamically inspect selected variant
        const variantInput = document.querySelector('input[name="id"]:checked, select[name="id"]');
        if (variantInput && variantInput.value) {
          variantId = variantInput.value;
        }

        // Active variant image check
        const activeMediaImg = document.querySelector('.product__media img, [data-media-id] img');
        if (activeMediaImg && activeMediaImg.src) {
          image = activeMediaImg.src;
        }

        this.addItem(slotKey, {
          productId: productId,
          variantId: variantId,
          title: title,
          variantTitle: '',
          image: image
        });
      });
    }
  }

  // Auto-boot when DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      window.DNK_VTON = new DNKVirtualFittingRoom();
    });
  } else {
    window.DNK_VTON = new DNKVirtualFittingRoom();
  }
})();

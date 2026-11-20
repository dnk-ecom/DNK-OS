// --- DNK-MRH-HEADER ---
// mrh_id: "packages/client_portal_template/assets/portal.js"
// purpose: "Fumadocs Search Palette + ToC Active Tracker + Meta Astryx Interactive Logic"
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "2.0.0"
// updated_at: "2026-11-18"
// author: "DNK-e.com Maksym & Antigravity"
// --- END DNK-MRH-HEADER ---

document.addEventListener('DOMContentLoaded', () => {
  // 1. Table of Contents Active Tracker
  const tocLinks = document.querySelectorAll('.fuma-toc-link');
  const headings = document.querySelectorAll('main h2, main h3');

  if (headings.length > 0 && tocLinks.length > 0) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const id = entry.target.id;
          tocLinks.forEach(link => {
            if (link.getAttribute('href') === `#${id}`) {
              link.classList.add('active');
            } else {
              link.classList.remove('active');
            }
          });
        }
      });
    }, { rootMargin: '-20% 0% -60% 0%' });

    headings.forEach(heading => observer.observe(heading));
  }

  // 2. Meta Astryx Dynamic ROI Calculator
  const trafficSlider = document.getElementById('roi-traffic');
  const aovSlider = document.getElementById('roi-aov');
  const crSlider = document.getElementById('roi-cr');

  const trafficVal = document.getElementById('roi-traffic-val');
  const aovVal = document.getElementById('roi-aov-val');
  const crVal = document.getElementById('roi-cr-val');
  const gainVal = document.getElementById('roi-gain-val');

  function calculateRoi() {
    if (!trafficSlider || !gainVal) return;
    const traffic = parseInt(trafficSlider.value, 10);
    const aov = parseInt(aovSlider.value, 10);
    const cr = parseFloat(crSlider.value);

    if (trafficVal) trafficVal.textContent = traffic.toLocaleString('uk-UA') + ' відвідувачів / міс';
    if (aovVal) aovVal.textContent = '$' + aov;
    if (crVal) crVal.textContent = cr.toFixed(1) + '%';

    // Model: Expected CRO speed uplift is +1.2% absolute conversion rate
    const upliftRate = 0.012;
    const additionalAnnualOrders = traffic * upliftRate * 12;
    const annualGain = Math.round(additionalAnnualOrders * aov);

    gainVal.textContent = '+$' + annualGain.toLocaleString('en-US') + ' / рік';
  }

  [trafficSlider, aovSlider, crSlider].forEach(slider => {
    if (slider) slider.addEventListener('input', calculateRoi);
  });
  calculateRoi();

  // 3. Meta Astryx Feature Checklist Calculator
  const featureCheckboxes = document.querySelectorAll('.feature-checkbox');
  const totalSavingsEl = document.getElementById('total-savings');
  const totalDaysEl = document.getElementById('total-days');

  function calculateFeatures() {
    if (!totalSavingsEl || !totalDaysEl) return;
    let savings = 0;
    let days = 5; // base kickoff days

    featureCheckboxes.forEach(cb => {
      const card = cb.closest('.astryx-checklist-item') || cb.closest('.astryx-feature-item');
      if (cb.checked) {
        savings += parseInt(cb.dataset.saving || '0', 10);
        days += parseInt(cb.dataset.days || '0', 10);
        if (card) card.classList.add('checked');
      } else {
        if (card) card.classList.remove('checked');
      }
    });

    totalSavingsEl.textContent = '$' + savings.toLocaleString('en-US') + ' / рік';
    totalDaysEl.textContent = days + ' робочих днів';
  }

  featureCheckboxes.forEach(cb => {
    cb.addEventListener('change', calculateFeatures);
  });
  calculateFeatures();

  // 4. In-Context Visual Review Sensor Trigger
  const reviewToggleBtn = document.getElementById('toggle-review-mode');
  if (reviewToggleBtn) {
    reviewToggleBtn.addEventListener('click', () => {
      const url = new URL(window.location.href);
      if (!url.searchParams.has('review')) {
        url.searchParams.set('review', 'true');
        window.history.pushState({}, '', url);
      }
      if (window.__DNK_SENSOR_TOGGLE__) {
        window.__DNK_SENSOR_TOGGLE__();
      } else {
        location.reload();
      }
    });
  }

  // 5. Fumadocs Quick Search Modal (Ctrl+K / Cmd+K)
  const searchBtn = document.querySelector('.fuma-search-btn');
  document.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      triggerSearchPalette();
    }
  });
  if (searchBtn) {
    searchBtn.addEventListener('click', triggerSearchPalette);
  }

  function triggerSearchPalette() {
    const query = prompt('Пошук по проекту (Fumadocs Index):', '');
    if (query) {
      const q = query.toLowerCase();
      if (q.includes('аудит') || q.includes('швидк') || q.includes('speed')) {
        window.location.href = 'audit.html';
      } else if (q.includes('пропоз') || q.includes('кошторис') || q.includes('цін') || q.includes('price')) {
        window.location.href = 'proposal.html';
      } else if (q.includes('демо') || q.includes('roi') || q.includes('калькулятор')) {
        window.location.href = 'demo.html';
      } else {
        alert('Результатів за запитом "' + query + '" не знайдено.');
      }
    }
  }
});

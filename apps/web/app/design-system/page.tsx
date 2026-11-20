// --- DNK-MRH-HEADER ---
// mrh_id: "apps_web_app_design_system_page"
// purpose: "Interactive Visual Showcase & Review Console for DNK OS Polaris Core Design System."
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-11-17"
// author: "DNK-e.com Maksym & Antigravity"
// --- END DNK-MRH-HEADER ---

'use client';

import React, { useState, useEffect } from 'react';

export default function DesignSystemShowcasePage() {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [copiedToken, setCopiedToken] = useState<string | null>(null);
  const [btnClicked, setBtnClicked] = useState(false);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedToken(text);
    setTimeout(() => setCopiedToken(null), 1500);
  };

  const isDark = theme === 'dark';

  return (
    <div className={`min-h-screen transition-colors duration-200 font-sans ${isDark ? 'bg-[#0d0e10] text-[#f0f2f5]' : 'bg-[#f1f2f4] text-[#202223]'}`}>
      {/* Top Banner / Theme Switcher Bar */}
      <header className={`sticky top-0 z-50 border-b backdrop-blur-md px-6 py-4 flex items-center justify-between transition-colors ${
        isDark ? 'bg-[#16181b]/90 border-[#26292e]' : 'bg-white/90 border-[#e3e5e8]'
      }`}>
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center font-bold text-white shadow-sm" style={{ backgroundColor: isDark ? '#30cd90' : '#008060' }}>
            🛍️
          </div>
          <div>
            <h1 className="text-base font-semibold leading-tight flex items-center gap-2">
              DNK OS Polaris Core Design System
              <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                isDark ? 'bg-[#30cd90]/15 text-[#30cd90]' : 'bg-[#e3f1df] text-[#008060]'
              }`}>
                Shopify Merchant Parity
              </span>
            </h1>
            <p className={`text-xs ${isDark ? 'text-[#9da3ae]' : 'text-[#6d7175]'}`}>
              Grounded in Shopify.com & Shopify Polaris 2.0 (DEC-139) | W3C DTCG Standard
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className={`p-1 rounded-lg border flex items-center gap-1 ${
            isDark ? 'bg-[#1d2024] border-[#33383f]' : 'bg-[#f6f6f7] border-[#e3e5e8]'
          }`}>
            <button
              onClick={() => setTheme('light')}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all flex items-center gap-1.5 ${
                theme === 'light'
                  ? 'bg-white text-[#202223] shadow-sm'
                  : 'text-[#6d7175] hover:text-[#202223]'
              }`}
            >
              ☀️ Polaris Snow
            </button>
            <button
              onClick={() => setTheme('dark')}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all flex items-center gap-1.5 ${
                theme === 'dark'
                  ? 'bg-[#16181b] text-[#f0f2f5] shadow-sm border border-[#33383f]'
                  : 'text-[#9da3ae] hover:text-[#f0f2f5]'
              }`}
            >
              🌙 Matte Obsidian
            </button>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-6 py-8 space-y-10">

        {/* 1. Shopify Top KPI Metrics Grid */}
        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold tracking-wide uppercase text-opacity-70">
              1. Shopify Admin KPI Grid & Metrics Cards
            </h2>
            <span className="text-xs opacity-60">WCAG 2.2 AA Contrast Certified</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Card 1 */}
            <div className={`p-5 rounded-lg border transition-all ${
              isDark ? 'bg-[#16181b] border-[#26292e] shadow-sm' : 'bg-white border-[#e3e5e8] shadow-sm'
            }`}>
              <div className="flex justify-between items-start">
                <span className={`text-xs font-medium ${isDark ? 'text-[#9da3ae]' : 'text-[#6d7175]'}`}>Total Sales</span>
                <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
                  isDark ? 'bg-[#30cd90]/15 text-[#30cd90]' : 'bg-[#e3f1df] text-[#008060]'
                }`}>+14.2%</span>
              </div>
              <div className="text-2xl font-bold mt-2">$142,850.00</div>
              <div className={`text-xs mt-1 ${isDark ? 'text-[#636b78]' : 'text-[#8c9196]'}`}>vs. $125,050.00 last 30 days</div>
            </div>

            {/* Card 2 */}
            <div className={`p-5 rounded-lg border transition-all ${
              isDark ? 'bg-[#16181b] border-[#26292e] shadow-sm' : 'bg-white border-[#e3e5e8] shadow-sm'
            }`}>
              <div className="flex justify-between items-start">
                <span className={`text-xs font-medium ${isDark ? 'text-[#9da3ae]' : 'text-[#6d7175]'}`}>Conversion Rate (CVR)</span>
                <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
                  isDark ? 'bg-[#30cd90]/15 text-[#30cd90]' : 'bg-[#e3f1df] text-[#008060]'
                }`}>+0.42%</span>
              </div>
              <div className="text-2xl font-bold mt-2">3.84%</div>
              <div className={`text-xs mt-1 ${isDark ? 'text-[#636b78]' : 'text-[#8c9196]'}`}>60-30-10 CRO Engine Active</div>
            </div>

            {/* Card 3 */}
            <div className={`p-5 rounded-lg border transition-all ${
              isDark ? 'bg-[#16181b] border-[#26292e] shadow-sm' : 'bg-white border-[#e3e5e8] shadow-sm'
            }`}>
              <div className="flex justify-between items-start">
                <span className={`text-xs font-medium ${isDark ? 'text-[#9da3ae]' : 'text-[#6d7175]'}`}>Average Order Value</span>
                <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
                  isDark ? 'bg-[#30cd90]/15 text-[#30cd90]' : 'bg-[#e3f1df] text-[#008060]'
                }`}>+$12.30</span>
              </div>
              <div className="text-2xl font-bold mt-2">$94.20</div>
              <div className={`text-xs mt-1 ${isDark ? 'text-[#636b78]' : 'text-[#8c9196]'}`}>Apex Cart Drawer Upsell</div>
            </div>

            {/* Card 4 */}
            <div className={`p-5 rounded-lg border transition-all ${
              isDark ? 'bg-[#16181b] border-[#26292e] shadow-sm' : 'bg-white border-[#e3e5e8] shadow-sm'
            }`}>
              <div className="flex justify-between items-start">
                <span className={`text-xs font-medium ${isDark ? 'text-[#9da3ae]' : 'text-[#6d7175]'}`}>Autonomous Swarm</span>
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-500/15 text-blue-500">4 Active</span>
              </div>
              <div className="text-2xl font-bold mt-2">105/105 Passed</div>
              <div className={`text-xs mt-1 ${isDark ? 'text-[#636b78]' : 'text-[#8c9196]'}`}>Zero-Context Bleed (FastMCP)</div>
            </div>
          </div>
        </section>

        {/* 2. Interactive Component Gallery */}
        <section className="space-y-4">
          <h2 className="text-sm font-semibold tracking-wide uppercase text-opacity-70">
            2. Shopify Polaris Canonical Component Set
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

            {/* Buttons & Actions */}
            <div className={`p-6 rounded-lg border space-y-5 ${
              isDark ? 'bg-[#16181b] border-[#26292e]' : 'bg-white border-[#e3e5e8]'
            }`}>
              <div>
                <h3 className="text-sm font-semibold">Buttons & Focal CTAs</h3>
                <p className={`text-xs mt-0.5 ${isDark ? 'text-[#9da3ae]' : 'text-[#6d7175]'}`}>
                  60-30-10 Focal Conversion Accent (Shopify Emerald #008060)
                </p>
              </div>

              <div className="flex flex-wrap gap-3 items-center">
                {/* Primary CTA */}
                <button
                  onClick={() => setBtnClicked(true)}
                  className="btn-polaris-primary shadow-sm"
                  style={{
                    backgroundColor: isDark ? '#30cd90' : '#008060',
                    color: isDark ? '#000000' : '#ffffff',
                  }}
                >
                  <span>✓ Save & Publish Store</span>
                </button>

                {/* Secondary Button */}
                <button className={`px-3 py-1.5 text-xs font-medium rounded border transition-colors ${
                  isDark ? 'bg-[#1d2024] text-[#f0f2f5] border-[#33383f] hover:bg-[#25282d]' : 'bg-[#f6f6f7] text-[#202223] border-[#c9cccf] hover:bg-[#edeeef]'
                }`}>
                  Discard Changes
                </button>

                {/* Critical Button */}
                <button className="px-3 py-1.5 text-xs font-medium rounded border border-[#d82c0d]/30 text-[#d82c0d] hover:bg-[#d82c0d]/10 transition-colors">
                  Purge Cache
                </button>

                {/* Plain Link */}
                <button className={`text-xs font-medium underline underline-offset-4 ${
                  isDark ? 'text-[#30cd90]' : 'text-[#008060]'
                }`}>
                  View live store ↗
                </button>
              </div>

              {btnClicked && (
                <div className={`p-3 rounded text-xs flex items-center justify-between border ${
                  isDark ? 'bg-[#30cd90]/10 border-[#30cd90]/30 text-[#30cd90]' : 'bg-[#e3f1df] border-[#008060]/30 text-[#008060]'
                }`}>
                  <span>🚀 <strong>Action Triggered!</strong> Microkernel received save command without re-render lag.</span>
                  <button onClick={() => setBtnClicked(false)} className="opacity-60 hover:opacity-100">✕</button>
                </div>
              )}
            </div>

            {/* Badges & Status Tags */}
            <div className={`p-6 rounded-lg border space-y-5 ${
              isDark ? 'bg-[#16181b] border-[#26292e]' : 'bg-white border-[#e3e5e8]'
            }`}>
              <div>
                <h3 className="text-sm font-semibold">Semantic Badges & Indicators</h3>
                <p className={`text-xs mt-0.5 ${isDark ? 'text-[#9da3ae]' : 'text-[#6d7175]'}`}>
                  High-contrast status signals for orders, inventory, and agent state
                </p>
              </div>

              <div className="flex flex-wrap gap-2.5 items-center">
                <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
                  isDark ? 'bg-[#30cd90]/15 text-[#30cd90]' : 'bg-[#e3f1df] text-[#008060]'
                }`}>
                  <span className="w-1.5 h-1.5 rounded-full bg-current"></span>
                  Paid & Fulfilled
                </span>

                <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
                  isDark ? 'bg-amber-400/15 text-amber-400' : 'bg-amber-100 text-amber-800'
                }`}>
                  <span className="w-1.5 h-1.5 rounded-full bg-current"></span>
                  Low Stock (3 left)
                </span>

                <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
                  isDark ? 'bg-red-400/15 text-red-400' : 'bg-red-100 text-red-800'
                }`}>
                  <span className="w-1.5 h-1.5 rounded-full bg-current"></span>
                  Checkout Blocked
                </span>

                <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
                  isDark ? 'bg-sky-400/15 text-sky-400' : 'bg-sky-100 text-sky-800'
                }`}>
                  <span className="w-1.5 h-1.5 rounded-full bg-current"></span>
                  Theme Check: 0 Errors
                </span>
              </div>
            </div>

            {/* Inputs & Form Elements */}
            <div className={`p-6 rounded-lg border space-y-4 ${
              isDark ? 'bg-[#16181b] border-[#26292e]' : 'bg-white border-[#e3e5e8]'
            }`}>
              <div>
                <h3 className="text-sm font-semibold">Form Controls & Customizer Inputs</h3>
                <p className={`text-xs mt-0.5 ${isDark ? 'text-[#9da3ae]' : 'text-[#6d7175]'}`}>
                  Clean 8pt spatial padding with Shopify Focus Ring
                </p>
              </div>

              <div className="space-y-3">
                <div>
                  <label className="block text-xs font-medium mb-1">Product Title</label>
                  <input
                    type="text"
                    defaultValue="DNK Sovereign Silk Robe"
                    className={`w-full px-3 py-2 text-xs rounded border transition-colors outline-none focus:ring-2 ${
                      isDark
                        ? 'bg-[#1d2024] border-[#33383f] text-[#f0f2f5] focus:ring-[#30cd90] focus:border-[#30cd90]'
                        : 'bg-white border-[#c9cccf] text-[#202223] focus:ring-[#008060] focus:border-[#008060]'
                    }`}
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium mb-1">Price ($)</label>
                    <input
                      type="text"
                      defaultValue="189.00"
                      className={`w-full px-3 py-2 text-xs rounded border transition-colors outline-none focus:ring-2 ${
                        isDark
                          ? 'bg-[#1d2024] border-[#33383f] text-[#f0f2f5] focus:ring-[#30cd90]'
                          : 'bg-white border-[#c9cccf] text-[#202223] focus:ring-[#008060]'
                      }`}
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium mb-1">Inventory SKU</label>
                    <input
                      type="text"
                      defaultValue="DNK-SOV-001"
                      className={`w-full px-3 py-2 text-xs rounded border transition-colors outline-none focus:ring-2 ${
                        isDark
                          ? 'bg-[#1d2024] border-[#33383f] text-[#f0f2f5] focus:ring-[#30cd90]'
                          : 'bg-white border-[#c9cccf] text-[#202223] focus:ring-[#008060]'
                      }`}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Living Canvas Node Preview */}
            <div className={`p-6 rounded-lg border space-y-4 polaris-canvas-dotgrid ${
              isDark ? 'border-[#26292e]' : 'border-[#e3e5e8]'
            }`}>
              <div>
                <h3 className="text-sm font-semibold">Living Canvas Node (Agent Task Preview)</h3>
                <p className={`text-xs mt-0.5 ${isDark ? 'text-[#9da3ae]' : 'text-[#6d7175]'}`}>
                  How swarm agents render in the spatial cockpit on dot-matrix canvas
                </p>
              </div>

              {/* Node Card */}
              <div className={`p-4 rounded-lg border shadow-md max-w-sm mx-auto transition-transform hover:scale-[1.01] ${
                isDark ? 'bg-[#16181b] border-[#30cd90]/40' : 'bg-white border-[#008060]/40'
              }`}>
                <div className="flex items-center justify-between pb-2 border-b border-inherit">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full animate-ping" style={{ backgroundColor: isDark ? '#30cd90' : '#008060' }}></span>
                    <span className="text-xs font-bold">Node #12: Theme Token Synthesis</span>
                  </div>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${
                    isDark ? 'bg-[#30cd90]/15 text-[#30cd90]' : 'bg-[#e3f1df] text-[#008060]'
                  }`}>Denchik 🛠️</span>
                </div>
                <div className="py-2.5 text-xs opacity-80 leading-relaxed">
                  Synthesizing Shopify <code>dnk-tokens.css</code> and Tailwind v4 <code>@theme</code> for Sovereign Apex store.
                </div>
                <div className="flex justify-between items-center pt-2 border-t border-inherit text-[11px] opacity-60">
                  <span>FastMCP in-RAM &lt; 12ms</span>
                  <span>Exit Code 0 ✓</span>
                </div>
              </div>
            </div>

          </div>
        </section>

        {/* 3. Color Token Matrix & WCAG Scores */}
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold tracking-wide uppercase text-opacity-70">
              3. Color Token Matrix & WCAG 2.2 AA Contrast
            </h2>
            <span className="text-xs opacity-60">Click token card to copy variable</span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
            {[
              { name: '--bg-app', hex: isDark ? '#0D0E10' : '#F1F2F4', label: 'App Canvas', wcag: 'Base Surface' },
              { name: '--bg-surface', hex: isDark ? '#16181B' : '#FFFFFF', label: 'Card Surface', wcag: 'Container Base' },
              { name: '--color-accent', hex: isDark ? '#30CD90' : '#008060', label: 'Shopify Emerald', wcag: '4.5:1 (AA CTA)' },
              { name: '--text-primary', hex: isDark ? '#F0F2F5' : '#202223', label: 'Text Primary', wcag: '12.4:1 (AAA)' },
              { name: '--text-secondary', hex: isDark ? '#9DA3AE' : '#6D7175', label: 'Text Subdued', wcag: '4.8:1 (AA)' },
              { name: '--border-subtle', hex: isDark ? '#26292E' : '#E3E5E8', label: 'Subtle Hairline', wcag: '1px Border' },
            ].map((tok) => (
              <div
                key={tok.name}
                onClick={() => copyToClipboard(`var(${tok.name})`)}
                className={`p-3 rounded-lg border cursor-pointer transition-all hover:scale-105 ${
                  isDark ? 'bg-[#16181b] border-[#26292e]' : 'bg-white border-[#e3e5e8]'
                }`}
              >
                <div className="w-full h-10 rounded border border-black/10 mb-2 flex items-center justify-center font-mono text-[10px] font-bold" style={{ backgroundColor: tok.hex, color: tok.name.includes('text') || tok.name.includes('accent') ? (isDark && tok.name !== '--color-accent' ? '#000' : '#fff') : (isDark ? '#fff' : '#000') }}>
                  {tok.hex}
                </div>
                <div className="text-xs font-semibold truncate">{tok.label}</div>
                <div className="font-mono text-[10px] opacity-60 truncate">{tok.name}</div>
                <div className={`mt-1.5 text-[10px] font-medium px-1.5 py-0.5 rounded inline-block ${
                  isDark ? 'bg-white/5 text-[#9da3ae]' : 'bg-black/5 text-[#6d7175]'
                }`}>
                  {tok.wcag}
                </div>
              </div>
            ))}
          </div>

          {copiedToken && (
            <div className="text-center text-xs font-mono text-emerald-500 animate-pulse">
              Copied {copiedToken} to clipboard!
            </div>
          )}
        </section>

        {/* 4. Fluid Typography Scale */}
        <section className={`p-6 rounded-lg border space-y-4 ${
          isDark ? 'bg-[#16181b] border-[#26292e]' : 'bg-white border-[#e3e5e8]'
        }`}>
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-sm font-semibold uppercase tracking-wide text-opacity-70">
                4. Fluid Typography Scale (Major Third 1.25)
              </h2>
              <p className={`text-xs mt-0.5 ${isDark ? 'text-[#9da3ae]' : 'text-[#6d7175]'}`}>
                Non-negotiable 16px mobile body floor for Zero-CLS & Core Web Vitals
              </p>
            </div>
            <span className="font-mono text-xs opacity-60">System Font Stack: San Francisco / Inter</span>
          </div>

          <div className="space-y-3 pt-2">
            <div className="flex items-baseline justify-between border-b pb-2 border-inherit">
              <span className="text-3xl font-bold tracking-tight">Display Headline</span>
              <span className="text-xs font-mono opacity-60">clamp(2.25rem, 1.8rem + 2.25vw, 3.5rem)</span>
            </div>
            <div className="flex items-baseline justify-between border-b pb-2 border-inherit">
              <span className="text-2xl font-bold">H1 Section Title</span>
              <span className="text-xs font-mono opacity-60">clamp(1.75rem, 1.5rem + 1.25vw, 2.25rem)</span>
            </div>
            <div className="flex items-baseline justify-between border-b pb-2 border-inherit">
              <span className="text-xl font-semibold">H2 Feature Heading</span>
              <span className="text-xs font-mono opacity-60">clamp(1.375rem, 1.22rem + 0.75vw, 1.625rem)</span>
            </div>
            <div className="flex items-baseline justify-between border-b pb-2 border-inherit">
              <span className="text-base font-medium">H3 Card Header</span>
              <span className="text-xs font-mono opacity-60">1.25rem (20px)</span>
            </div>
            <div className="flex items-baseline justify-between">
              <span className="text-base">Body Copy Standard Text (Floor)</span>
              <span className="text-xs font-mono opacity-60">1.00rem (16px Non-Negotiable)</span>
            </div>
          </div>
        </section>

      </main>
    </div>
  );
}

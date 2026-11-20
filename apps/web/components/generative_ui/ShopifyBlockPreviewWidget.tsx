// --- DNK-MRH-HEADER ---
// mrh_id: "apps_web_components_generative_ui_ShopifyBlockPreviewWidget"
// purpose: "Astryx Generative UI: Interactive Shopify Theme Block Preview (Sticky ATC, Cart Rewards, Upsell)"
// author: "DNK-e.com Maksym & Denchik"
// license: "DNK-INTERNAL"
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-11-17"
// --- END DNK-MRH-HEADER ---

"use client";

import React, { useState } from "react";
import {
  ShoppingBag,
  ShoppingCart,
  Sparkles,
  Gift,
  Truck,
  Check,
  CheckCircle2,
  Plus,
  Minus,
  Sliders,
  Code2,
  Eye,
  ArrowRightCircle,
  Zap,
  Tag,
  Star,
  ExternalLink,
} from "lucide-react";

export interface ShopifyBlockPreviewWidgetProps {
  blockType: "sticky_atc" | "cart_rewards" | "upsell";
  title: string;
  price?: number;
  variants?: string[];
  settings?: Record<string, any>;
  onApplyToCanvas?: () => void;
  className?: string;
}

export const ShopifyBlockPreviewWidget: React.FC<ShopifyBlockPreviewWidgetProps> = ({
  blockType,
  title,
  price = 49.0,
  variants = ["Default", "Obsidian Black", "Emerald Green"],
  settings = {},
  onApplyToCanvas,
  className = "",
}) => {
  const [selectedVariant, setSelectedVariant] = useState<string>(variants[0] || "Default");
  const [quantity, setQuantity] = useState<number>(1);
  const [cartTotal, setCartTotal] = useState<number>(settings.initialCartTotal || 45.0);
  const [activeTab, setActiveTab] = useState<"preview" | "schema" | "liquid">("preview");
  const [isAddedFeedback, setIsAddedFeedback] = useState<boolean>(false);
  const [isAppliedFeedback, setIsAppliedFeedback] = useState<boolean>(false);
  const [upsellIncluded, setUpsellIncluded] = useState<boolean>(false);

  // Rewards thresholds
  const tier1Threshold = settings.tier1Threshold || 50;
  const tier2Threshold = settings.tier2Threshold || 100;
  const progressPercent = Math.min(100, Math.round((cartTotal / tier2Threshold) * 100));

  const handleAddToCart = () => {
    setIsAddedFeedback(true);
    setTimeout(() => setIsAddedFeedback(false), 2000);
  };

  const handleApply = () => {
    setIsAppliedFeedback(true);
    if (onApplyToCanvas) {
      onApplyToCanvas();
    }
    setTimeout(() => setIsAppliedFeedback(false), 2200);
  };

  const discountPercent = settings.discountPercent || 20;
  const compareAtPrice = price ? (price * (1 + discountPercent / 100)).toFixed(2) : "59.99";

  return (
    <div
      className={`rounded-2xl border border-white/10 bg-[#16181d] text-zinc-100 shadow-2xl backdrop-blur-xl transition-all duration-300 hover:border-emerald-500/30 ${className}`}
      data-agent-target="shopify-block-preview-widget"
    >
      {/* Astryx Top Header Navigation */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 px-5 py-3.5 bg-[#111317]/80 rounded-t-2xl">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-500/10 border border-emerald-500/25 text-emerald-400">
            {blockType === "sticky_atc" && <ShoppingBag className="h-4 w-4" />}
            {blockType === "cart_rewards" && <Gift className="h-4 w-4" />}
            {blockType === "upsell" && <Sparkles className="h-4 w-4" />}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-400">
                Shopify Block
              </span>
              <span className="rounded-full bg-white/5 px-2 py-0.5 text-[10px] font-mono text-zinc-400 border border-white/5">
                {blockType}
              </span>
            </div>
            <h3 className="text-sm font-semibold text-zinc-100 line-clamp-1">{title}</h3>
          </div>
        </div>

        {/* View Mode Switcher & Apply Button */}
        <div className="flex items-center gap-2">
          <div className="flex items-center rounded-lg bg-zinc-900/90 p-0.5 border border-white/5 text-xs">
            <button
              type="button"
              onClick={() => setActiveTab("preview")}
              className={`flex items-center gap-1 rounded-md px-2.5 py-1 text-xs font-medium transition-colors ${
                activeTab === "preview"
                  ? "bg-zinc-800 text-emerald-400 shadow-sm"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              <Eye className="h-3 w-3" />
              Preview
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("schema")}
              className={`flex items-center gap-1 rounded-md px-2.5 py-1 text-xs font-medium transition-colors ${
                activeTab === "schema"
                  ? "bg-zinc-800 text-emerald-400 shadow-sm"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              <Sliders className="h-3 w-3" />
              Schema
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("liquid")}
              className={`flex items-center gap-1 rounded-md px-2.5 py-1 text-xs font-medium transition-colors ${
                activeTab === "liquid"
                  ? "bg-zinc-800 text-emerald-400 shadow-sm"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              <Code2 className="h-3 w-3" />
              Liquid
            </button>
          </div>

          <button
            type="button"
            onClick={handleApply}
            className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold transition-all ${
              isAppliedFeedback
                ? "bg-emerald-500 text-zinc-950 shadow-lg shadow-emerald-500/20"
                : "bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 hover:bg-emerald-500 hover:text-zinc-950"
            }`}
          >
            {isAppliedFeedback ? (
              <>
                <Check className="h-3.5 w-3.5" />
                Applied to Canvas
              </>
            ) : (
              <>
                <ArrowRightCircle className="h-3.5 w-3.5" />
                Apply to Canvas
              </>
            )}
          </button>
        </div>
      </div>

      {/* Main Block Content */}
      <div className="p-5">
        {activeTab === "preview" && (
          <div className="space-y-4">
            {/* 1. STICKY ATC BLOCK */}
            {blockType === "sticky_atc" && (
              <div className="rounded-xl border border-white/10 bg-[#111317] p-4 shadow-inner">
                {/* Storefront Mock Badge */}
                <div className="mb-3 flex items-center justify-between text-[11px] text-zinc-400">
                  <span className="flex items-center gap-1.5 font-mono">
                    <span className="h-2 w-2 rounded-full bg-emerald-400 animate-ping" />
                    Live Storefront PDP Sticky Anchor
                  </span>
                  <span className="flex items-center gap-1 text-emerald-400">
                    <Zap className="h-3 w-3" />
                    Pulse CTA Enabled
                  </span>
                </div>

                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  {/* Thumbnail & Product Details */}
                  <div className="flex items-center gap-3">
                    <div className="relative flex h-14 w-14 flex-shrink-0 items-center justify-center rounded-lg border border-white/10 bg-gradient-to-br from-zinc-800 to-zinc-900 text-zinc-400 shadow-md">
                      <ShoppingBag className="h-6 w-6 text-emerald-400" />
                      <div className="absolute -top-1 -right-1 flex h-4 items-center rounded-full bg-rose-500/90 px-1.5 text-[9px] font-bold text-white shadow">
                        -{discountPercent}%
                      </div>
                    </div>
                    <div>
                      <h4 className="text-sm font-semibold text-zinc-100">{title}</h4>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className="text-base font-bold text-emerald-400">
                          ${(price * quantity).toFixed(2)}
                        </span>
                        <span className="text-xs text-zinc-500 line-through">
                          ${(Number(compareAtPrice) * quantity).toFixed(2)}
                        </span>
                        <span className="rounded bg-emerald-500/10 px-1.5 py-0.5 text-[10px] font-medium text-emerald-400 border border-emerald-500/20">
                          Save ${(Number(compareAtPrice) - price).toFixed(2)}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Variant Selector Pills */}
                  {variants && variants.length > 0 && (
                    <div className="flex flex-wrap items-center gap-1.5">
                      {variants.map((v) => (
                        <button
                          key={v}
                          type="button"
                          onClick={() => setSelectedVariant(v)}
                          className={`rounded-md px-2.5 py-1 text-xs font-medium transition-all ${
                            selectedVariant === v
                              ? "bg-emerald-500/20 border border-emerald-500 text-emerald-300 shadow-sm"
                              : "border border-white/5 bg-zinc-900 text-zinc-400 hover:border-white/20 hover:text-zinc-200"
                          }`}
                        >
                          {v}
                        </button>
                      ))}
                    </div>
                  )}

                  {/* Quantity Stepper & CTA Pulse Button */}
                  <div className="flex items-center gap-2.5">
                    <div className="flex items-center rounded-lg border border-white/10 bg-zinc-900 px-1 py-0.5">
                      <button
                        type="button"
                        onClick={() => setQuantity((q) => Math.max(1, q - 1))}
                        className="rounded p-1 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-100"
                      >
                        <Minus className="h-3 w-3" />
                      </button>
                      <span className="w-8 text-center text-xs font-mono font-bold text-zinc-200">
                        {quantity}
                      </span>
                      <button
                        type="button"
                        onClick={() => setQuantity((q) => q + 1)}
                        className="rounded p-1 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-100"
                      >
                        <Plus className="h-3 w-3" />
                      </button>
                    </div>

                    <button
                      type="button"
                      onClick={handleAddToCart}
                      className={`relative flex items-center justify-center gap-2 rounded-xl px-5 py-2.5 text-xs font-bold transition-all duration-200 ${
                        isAddedFeedback
                          ? "bg-emerald-400 text-zinc-950 scale-105 shadow-lg shadow-emerald-500/30"
                          : "bg-emerald-500 hover:bg-emerald-400 text-zinc-950 shadow-md shadow-emerald-500/20 animate-pulse-subtle"
                      }`}
                    >
                      {isAddedFeedback ? (
                        <>
                          <Check className="h-4 w-4" />
                          Added to Cart!
                        </>
                      ) : (
                        <>
                          <ShoppingCart className="h-4 w-4" />
                          Add to Cart • ${(price * quantity).toFixed(2)}
                        </>
                      )}
                    </button>
                  </div>
                </div>

                {/* Micro Invariants Bar */}
                <div className="mt-3 pt-2.5 border-t border-white/5 flex flex-wrap items-center justify-between text-[11px] text-zinc-500">
                  <div className="flex items-center gap-1.5">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                    <span>In Stock — Dispatches within 24 hours</span>
                  </div>
                  <div className="flex items-center gap-1 text-zinc-400">
                    <Tag className="h-3 w-3 text-emerald-400" />
                    <span>Selected: {selectedVariant}</span>
                  </div>
                </div>
              </div>
            )}

            {/* 2. CART DRAWER REWARDS BLOCK */}
            {blockType === "cart_rewards" && (
              <div className="rounded-xl border border-white/10 bg-[#111317] p-5">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Gift className="h-4 w-4 text-emerald-400" />
                    <h4 className="text-sm font-semibold text-zinc-100">{title}</h4>
                  </div>
                  <span className="text-xs font-mono font-bold text-emerald-400">
                    ${cartTotal.toFixed(2)} / ${tier2Threshold.toFixed(2)}
                  </span>
                </div>

                {/* Motivational Status Text */}
                <p className="text-xs text-zinc-300 mb-3">
                  {cartTotal < tier1Threshold && (
                    <>
                      Add <span className="font-bold text-emerald-400">${(tier1Threshold - cartTotal).toFixed(2)}</span> more to unlock <span className="font-semibold text-zinc-100">Free Express Shipping</span>!
                    </>
                  )}
                  {cartTotal >= tier1Threshold && cartTotal < tier2Threshold && (
                    <>
                      🎉 <span className="text-emerald-400 font-semibold">Free Shipping Unlocked!</span> Add <span className="font-bold text-emerald-400">${(tier2Threshold - cartTotal).toFixed(2)}</span> more for a <span className="font-semibold text-zinc-100">Free Mystery Gift</span>!
                    </>
                  )}
                  {cartTotal >= tier2Threshold && (
                    <span className="text-emerald-400 font-bold flex items-center gap-1">
                      <Sparkles className="h-3.5 w-3.5" />
                      All Reward Tiers Unlocked! Maximum Savings Activated!
                    </span>
                  )}
                </p>

                {/* Tiered Progress Track */}
                <div className="relative mb-5">
                  <div className="h-2.5 w-full overflow-hidden rounded-full bg-zinc-800 border border-white/5">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-emerald-500 via-teal-400 to-emerald-300 transition-all duration-500 shadow-sm"
                      style={{ width: `${progressPercent}%` }}
                    />
                  </div>

                  {/* Milestones markers */}
                  <div className="mt-2.5 flex justify-between text-[11px]">
                    <div className="flex items-center gap-1.5">
                      <div
                        className={`flex h-5 w-5 items-center justify-center rounded-full border text-[10px] ${
                          cartTotal >= tier1Threshold
                            ? "bg-emerald-500 border-emerald-400 text-zinc-950 font-bold"
                            : "bg-zinc-800 border-white/10 text-zinc-400"
                        }`}
                      >
                        <Truck className="h-2.5 w-2.5" />
                      </div>
                      <span className={cartTotal >= tier1Threshold ? "text-emerald-300 font-medium" : "text-zinc-500"}>
                        Free Shipping (${tier1Threshold})
                      </span>
                    </div>

                    <div className="flex items-center gap-1.5">
                      <div
                        className={`flex h-5 w-5 items-center justify-center rounded-full border text-[10px] ${
                          cartTotal >= tier2Threshold
                            ? "bg-emerald-500 border-emerald-400 text-zinc-950 font-bold"
                            : "bg-zinc-800 border-white/10 text-zinc-400"
                        }`}
                      >
                        <Gift className="h-2.5 w-2.5" />
                      </div>
                      <span className={cartTotal >= tier2Threshold ? "text-emerald-300 font-medium" : "text-zinc-500"}>
                        Free Gift (${tier2Threshold})
                      </span>
                    </div>
                  </div>
                </div>

                {/* Interactive Simulator Slider */}
                <div className="rounded-lg border border-white/5 bg-zinc-900/80 p-3">
                  <div className="flex items-center justify-between text-xs text-zinc-400 mb-1.5">
                    <span>Simulate Cart Subtotal:</span>
                    <span className="font-mono font-bold text-zinc-200">${cartTotal.toFixed(2)}</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="150"
                    step="5"
                    value={cartTotal}
                    onChange={(e) => setCartTotal(parseFloat(e.target.value))}
                    className="w-full accent-emerald-400 cursor-pointer"
                  />
                  <div className="flex justify-between gap-2 mt-2">
                    <button
                      type="button"
                      onClick={() => setCartTotal(30)}
                      className="flex-1 rounded bg-zinc-800 py-1 text-[10px] text-zinc-300 hover:bg-zinc-700"
                    >
                      $30 (Tier 0)
                    </button>
                    <button
                      type="button"
                      onClick={() => setCartTotal(65)}
                      className="flex-1 rounded bg-zinc-800 py-1 text-[10px] text-zinc-300 hover:bg-zinc-700"
                    >
                      $65 (Tier 1)
                    </button>
                    <button
                      type="button"
                      onClick={() => setCartTotal(110)}
                      className="flex-1 rounded bg-zinc-800 py-1 text-[10px] text-zinc-300 hover:bg-zinc-700"
                    >
                      $110 (Maxed)
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* 3. 1-CLICK UPSELL BLOCK */}
            {blockType === "upsell" && (
              <div className="rounded-xl border border-white/10 bg-[#111317] p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span className="rounded bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-amber-400">
                      Frequently Bought Together
                    </span>
                    <span className="flex items-center gap-1 text-[11px] text-zinc-400">
                      <Star className="h-3 w-3 fill-amber-400 text-amber-400" />
                      4.9 (420+ reviews)
                    </span>
                  </div>
                  <span className="text-xs font-mono text-emerald-400 font-bold">
                    Save 25% Off
                  </span>
                </div>

                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 rounded-lg border border-white/5 bg-zinc-900/60 p-3.5">
                  <div className="flex items-center gap-3">
                    <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
                      <Sparkles className="h-6 w-6" />
                    </div>
                    <div>
                      <h4 className="text-sm font-semibold text-zinc-100">{title}</h4>
                      <p className="text-xs text-zinc-400 line-clamp-1">
                        {settings.subtitle || "Premium Obsidian Care Kit & Microfiber Pouch"}
                      </p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-sm font-bold text-emerald-400">+$18.00</span>
                        <span className="text-xs text-zinc-500 line-through">$24.00</span>
                      </div>
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={() => setUpsellIncluded(!upsellIncluded)}
                    className={`flex items-center gap-2 rounded-lg px-4 py-2 text-xs font-bold transition-all ${
                      upsellIncluded
                        ? "bg-emerald-500 text-zinc-950 shadow-md shadow-emerald-500/20"
                        : "bg-zinc-800 text-zinc-200 hover:bg-zinc-700 border border-white/10"
                    }`}
                  >
                    {upsellIncluded ? (
                      <>
                        <Check className="h-4 w-4" />
                        Added to Bundle
                      </>
                    ) : (
                      <>
                        <Plus className="h-4 w-4" />
                        Add Upgrade (+$18)
                      </>
                    )}
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Schema Inspector Tab */}
        {activeTab === "schema" && (
          <div className="rounded-xl border border-white/10 bg-[#0d0e12] p-4 font-mono text-xs text-zinc-300 overflow-x-auto max-h-64">
            <pre>
              {JSON.stringify(
                {
                  name: title,
                  type: `astryx_${blockType}`,
                  category: "CRO Conversion Blocks",
                  settings: {
                    block_type: blockType,
                    accent_color: "#10b981",
                    pulse_cta: true,
                    variants: variants,
                    base_price: price,
                    ...settings,
                  },
                  invariants: {
                    mrh_verified: true,
                    fastmcp_ready: true,
                    runtime: "Shopify Hydrogen / Horizon 2026",
                  },
                },
                null,
                2
              )}
            </pre>
          </div>
        )}

        {/* Liquid AST Tab */}
        {activeTab === "liquid" && (
          <div className="rounded-xl border border-white/10 bg-[#0d0e12] p-4 font-mono text-xs text-emerald-300/90 overflow-x-auto max-h-64">
            <pre>{`{% comment %}
  Astryx Dual-Ready CRO Block: ${blockType}
  Canonical AST for DNK OS Horizon
{% endcomment %}
<div class="astryx-block astryx-block--${blockType}" data-block-id="{{ block.id }}">
  <div class="astryx-container border border-emerald-500/20 bg-zinc-950 p-4 rounded-xl">
    <div class="flex items-center justify-between">
      <h3 class="text-sm font-bold text-white">{{ block.settings.title | default: '${title}' }}</h3>
      <span class="text-xs text-emerald-400 font-mono">{{ product.price | money }}</span>
    </div>
    {% if block.settings.show_cta %}
      <button type="submit" name="add" class="btn-astryx-pulse bg-emerald-500 text-black font-bold">
        {{ block.settings.cta_text | default: 'Add to Cart' }}
      </button>
    {% endif %}
  </div>
</div>`}</pre>
          </div>
        )}
      </div>
    </div>
  );
};

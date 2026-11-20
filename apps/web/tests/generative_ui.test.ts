// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/tests/generative_ui.test.ts"
// purpose: "Automated verification test for Astryx Generative UI component library"
// author: "DNK-e.com Maksym & Denchik"
// license: "DNK-INTERNAL"
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-11-17"
// --- END DNK-MRH-HEADER ---

import test from "node:test";
import assert from "node:assert";
import React from "react";
import {
  ShopifyBlockPreviewWidget,
  AnalyticsMetricCardWidget,
  SocialContentCardWidget,
  ThoughtDAGCardWidget,
} from "../components/generative_ui/index";

test("Astryx Generative UI - Exports and Components Initialization", async (t) => {
  await t.test("All widgets are defined as React components", () => {
    assert.strictEqual(typeof ShopifyBlockPreviewWidget, "function");
    assert.strictEqual(typeof AnalyticsMetricCardWidget, "function");
    assert.strictEqual(typeof SocialContentCardWidget, "function");
    assert.strictEqual(typeof ThoughtDAGCardWidget, "function");
  });

  await t.test("ShopifyBlockPreviewWidget instantiates with sticky_atc", () => {
    const element = React.createElement(ShopifyBlockPreviewWidget, {
      blockType: "sticky_atc",
      title: "Obsidian Titanium Case",
      price: 89.99,
      variants: ["S", "M", "L"],
    });
    assert.ok(element);
    assert.strictEqual(element.props.blockType, "sticky_atc");
    assert.strictEqual(element.props.title, "Obsidian Titanium Case");
  });

  await t.test("ShopifyBlockPreviewWidget instantiates with cart_rewards", () => {
    const element = React.createElement(ShopifyBlockPreviewWidget, {
      blockType: "cart_rewards",
      title: "Free Shipping & Mystery Gift Bar",
      settings: { tier1Threshold: 50, tier2Threshold: 100 },
    });
    assert.ok(element);
    assert.strictEqual(element.props.blockType, "cart_rewards");
  });

  await t.test("ShopifyBlockPreviewWidget instantiates with upsell", () => {
    const element = React.createElement(ShopifyBlockPreviewWidget, {
      blockType: "upsell",
      title: "Premium Care Kit Add-on",
      price: 18.0,
    });
    assert.ok(element);
    assert.strictEqual(element.props.blockType, "upsell");
  });

  await t.test("AnalyticsMetricCardWidget instantiates with metric types", () => {
    const element = React.createElement(AnalyticsMetricCardWidget, {
      title: "Storefront Conversion Rate",
      value: "4.82%",
      changePercent: 14.5,
      timeframe: "vs last 7d",
      metricType: "cvr",
      sparklineData: [3.2, 3.5, 3.8, 4.1, 4.82],
    });
    assert.ok(element);
    assert.strictEqual(element.props.metricType, "cvr");
    assert.strictEqual(element.props.changePercent, 14.5);
  });

  await t.test("SocialContentCardWidget instantiates with tiktok and x", () => {
    const tiktokElement = React.createElement(SocialContentCardWidget, {
      platform: "tiktok",
      hook: "Stop losing 70% of your cart checkouts today.",
      caption: "Here is how we boosted CVR by 28% using one simple block.",
      cta: "Grab the free template in bio",
      scenesCount: 4,
    });
    assert.ok(tiktokElement);
    assert.strictEqual(tiktokElement.props.platform, "tiktok");

    const xElement = React.createElement(SocialContentCardWidget, {
      platform: "x",
      hook: "Most Shopify stores fail because of PDP friction.",
      caption: "Here are the 3 blocks that double AOV without extra ad spend.",
      cta: "Read full breakdown",
    });
    assert.ok(xElement);
    assert.strictEqual(xElement.props.platform, "x");
  });

  await t.test("ThoughtDAGCardWidget instantiates with all node kinds", () => {
    const goalNode = React.createElement(ThoughtDAGCardWidget, {
      nodeKind: "goal",
      title: "Synthesize High-Converting Sticky ATC Block",
      agent: "Antigravity Mentor",
      summary: "Deploy an accessible, sticky add-to-cart block on Horizon PDP.",
    });
    assert.ok(goalNode);

    const critiqueNode = React.createElement(ThoughtDAGCardWidget, {
      nodeKind: "critique",
      title: "Flaw Analysis of Client-side Cart Transform",
      agent: "Gerych Prime",
      summary: "Adversarial critique on network overhead and cart collision.",
      flaws: [
        "Network latency on mobile 3G networks.",
        "Race condition on rapid double clicks.",
        "Missing fallback when Cart API returns 429.",
      ],
    });
    assert.ok(critiqueNode);
    assert.strictEqual(critiqueNode.props.flaws?.length, 3);

    const decisionNode = React.createElement(ThoughtDAGCardWidget, {
      nodeKind: "decision",
      title: "Lock Astryx Generative UI Standard",
      agent: "Denchik Builder",
      summary: "Adopt Astryx Dark Obsidian theme with emerald accents.",
      lockedDecRef: "DEC-072",
    });
    assert.ok(decisionNode);
    assert.strictEqual(decisionNode.props.lockedDecRef, "DEC-072");
  });
});

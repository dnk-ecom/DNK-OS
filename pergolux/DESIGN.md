---
title: "DESIGN.md: Pergolux"
description: "Visual Design System and Token Specification for Pergolux (Google Labs Standard)"
version: "1.0.0"
brand: "Pergolux"
archetype: "ecommerce_conversion"
tokens:
  color:
    surface_primary: "#ffffff"
    text_primary: "#121212"
    action_primary: "#0F766E"
    action_primary_text: "#FFFFFF"
    action_secondary: "#121212"
  typography:
    font_display: "Inter, -apple-system, sans-serif"
    font_body: "Inter, -apple-system, sans-serif"
    base_size_px: 16
    modular_ratio: 1.25
  spacing:
    grid_base_px: 8
    scale:
      xs: 4
      sm: 8
      md: 16
      lg: 24
      xl: 32
---

# 🎨 Pergolux Design System (DESIGN.md)

> Canonical design token specification following Google Labs DESIGN.md standard.
> AI coding agents (Cursor, Claude Code, Antigravity) must strictly adhere to these tokens.

## 1. Color Palette (60-30-10 CRO Law)
- **Surface (60%)**: `#ffffff` (Canvas & primary card backgrounds)
- **Text & Structure (30%)**: `#121212` (Headings, body typography, borders)
- **Primary Action (10%)**: `#0F766E` (Conversion CTAs only: Add to Cart, Buy Now)
- **Action Text**: `#FFFFFF` (High contrast label on action buttons)
- **Secondary Accent**: `#121212` (Badges, supporting chips, subtle links)

## 2. Typography Hierarchy
- **Display Font**: `Inter, -apple-system, sans-serif`
- **Body Font**: `Inter, -apple-system, sans-serif`
- **Scale Base**: `16px` (Strict mobile floor to prevent viewport auto-zoom)
- **Modular Scale**: `Major Third (1.25)`

## 3. Spatial Grid & Corner Radii
- **Base Grid**: `8px` (Multiples of 4px / 8px strictly enforced)
- **Corner Radius**: `8px` standard, `9999px` full pill for CTAs.

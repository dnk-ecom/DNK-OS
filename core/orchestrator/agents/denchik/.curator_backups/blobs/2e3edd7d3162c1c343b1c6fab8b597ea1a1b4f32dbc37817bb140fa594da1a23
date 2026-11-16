# --- DNK-MRH-HEADER ---
# mrh_id: "references/live_vton_streaming_and_joyai_video_edit_patterns.md"
# purpose: "Architecture patterns and recipes for Live Virtual Try-On (VTON) via RV2V Autoregressive Diffusion & WebRTC."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-25"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# 👗 Live Virtual Try-On (VTON) & JoyAI-Video-Edit Architectural Patterns

## 1. Overview & SOTA Landscape
Live Virtual Try-On (VTON) allows consumers to view themselves in target clothing in real-time (24–30 FPS) via webcams or mobile cameras.
- **Proprietary Benchmark:** Anywear (Decart AI, `Lucy V-TON`) — Chrome Extension + WebRTC + Autoregressive video diffusion.
- **Open-Source Engine:** `jd-opensource/JoyAI-Video-Edit` (Apache 2.0 by JD.com) — RV2V (Reference-Guided Video-to-Video) diffusion model capable of 720p (720x1248) @ 24-30 FPS on a single RTX 4090 / L40S.

---

## 2. Dual Delivery Architecture

### A. Surface 1: Chrome Extension (Manifest V3)
1. **Injected UI**: Floating iframe or Shadow DOM mounted across arbitrary e-commerce sites (Zara, ASOS, Revolve, Shopify).
2. **Camera Capture**: `navigator.mediaDevices.getUserMedia({ video: { width: 720, height: 1280, frameRate: 30 } })`.
3. **Drag-and-Drop Ingestion**: Listens to `dragover` / `drop` DOM events on product imagery to extract high-res garment image URLs.

### B. Surface 2: Embedded E-Commerce Widget (Shopify / Headless)
1. **Isolation Engine**: Uses `jd-opensource/micro-app` for zero-iframe, zero-CSS-bleed micro-frontend mounting directly in `theme.liquid`.
2. **One-Click Try-On CTA**: Placed alongside the "Add to Cart" button.

---

## 3. Streaming Infrastructure & Pipeline
```
[ Web Client / Chrome Extension ]
     │ WebRTC / WebSocket (H.264 / VP8 Stream @ 720p 30 FPS)
     ▼
[ LiveKit SFU / FastAPI Gateway ]
     ├── Session Auth, Token Spend, Quota (e.g. 2 min / session)
     ├── Garment Image Preprocessing (JoyAI-Image / RMBG-1.4 background removal)
     └── GPU Stream Dispatcher
     ▼
[ GPU Inference Node (JoyAI-Video-Edit Server) ]
     ├── Model: Autoregressive Latent Diffusion with reference attention
     ├── Inputs: Garment Image Tensor + Video Ingest Stream
     └── Output: Real-time 720p synthesized stream back to WebRTC peer
```

---

## 4. B2B SaaS Unit Economics
- **Inference Cost:** ~0.50 $/hr per RTX 4090 (RunPod / Modal / Lambda).
- **Session Cost:** 2-minute live try-on = ~$0.017 GPU cost.
- **Retail Pricing:** $99/month for 2,000 try-on sessions + $0.06/overage.
- **Gross Margin:** 65% – 75% margin on dedicated B2B Shopify app tiers.

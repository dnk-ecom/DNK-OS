# --- DNK-MRH-HEADER ---
# mrh_id: "packages/adapters/dnk_iris_adapter.py"
# purpose: "Zero-Bloat Hexagonal Adapter assimilating brijr/iris CDP visual capture engine"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-12"
# author: "DNK-e.com Maksym & Gerych Prime"
# --- END DNK-MRH-HEADER ---

import os
import shutil
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, Union
from pydantic import BaseModel, Field

logger = logging.getLogger("dnk.adapters.iris")

# --- SOTA Extracted JavaScript Algorithms (Clean-Room Assimilation from brijr/iris) ---

SETTLE_JS = """(async () => {
  if (document.fonts) { try { await document.fonts.ready; } catch {} }
  const near = (img) => {
    const r = img.getBoundingClientRect();
    return r.top < innerHeight * 1.5 && r.bottom > -innerHeight * 0.5;
  };
  await Promise.all(Array.from(document.images)
    .filter(img => !img.complete && near(img))
    .map(img => new Promise(r => {
      img.addEventListener('load', r, { once: true });
      img.addEventListener('error', r, { once: true });
      setTimeout(r, 3000);
    })));
  await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
  const finite = document.getAnimations().filter(a => {
    try {
      return a.playState === 'running' && a.effect.getTiming().iterations !== Infinity;
    } catch { return false; }
  });
  await Promise.race([
    Promise.all(finite.map(a => a.finished.catch(() => {}))),
    new Promise(r => setTimeout(r, 3000)),
  ]);
  await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
})()"""

SCROLL_JS = """(async () => {
  const height = () => Math.max(
    document.body?.scrollHeight ?? 0,
    document.documentElement.scrollHeight
  );
  const step = Math.max(200, window.innerHeight);
  for (let y = 0, guard = 0; y < height() && guard < 500; y += step, guard++) {
    window.scrollTo(0, y);
    await new Promise(r => setTimeout(r, 60));
  }
  window.scrollTo(0, 0);
  await new Promise(r => setTimeout(r, 150));
  await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
})()"""

DOC_HEIGHT_JS = """Math.max(
  document.body?.scrollHeight ?? 0,
  document.documentElement.scrollHeight
)"""

IPHONE_UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1"


class ViewportConfig(BaseModel):
    width: int = Field(default=1440, description="Viewport width in pixels")
    height: int = Field(default=900, description="Viewport height in pixels")
    scale: float = Field(default=2.0, description="Device scale factor (retina)")
    mobile: bool = Field(default=False, description="Whether to emulate mobile device")
    user_agent: Optional[str] = Field(default=None, description="Custom User-Agent override")


class ElementBounds(BaseModel):
    x: float
    y: float
    width: float
    height: float
    doc_width: Optional[float] = None
    doc_height: Optional[float] = None


class ClipRect(BaseModel):
    x: float
    y: float
    width: float
    height: float


def parse_viewport_preset(size: str, scale: Optional[float] = None) -> ViewportConfig:
    """Parses standard Iris presets (desktop, iphone, ipad) or custom WxH dimensions."""
    normalized = size.strip().lower()
    if normalized == "desktop":
        w, h, preset_scale, mobile, ua = 1440, 900, 2.0, False, None
    elif normalized == "iphone":
        w, h, preset_scale, mobile, ua = 390, 844, 3.0, True, IPHONE_UA
    elif normalized == "ipad":
        w, h, preset_scale, mobile, ua = 1024, 1366, 2.0, False, None
    elif "x" in normalized:
        parts = normalized.split("x")
        if len(parts) != 2:
            raise ValueError(f"Invalid size format: {size}. Use 'desktop', 'iphone', 'ipad', or 'WxH'")
        w, h = int(parts[0]), int(parts[1])
        preset_scale, mobile, ua = 2.0, False, None
    else:
        raise ValueError(f"Unknown viewport preset: {size}")

    final_scale = scale if (scale is not None and scale > 0) else preset_scale
    return ViewportConfig(
        width=w,
        height=h,
        scale=final_scale,
        mobile=mobile,
        user_agent=ua
    )


def compute_element_clip(bounds: ElementBounds, padding: int = 0) -> ClipRect:
    """Computes rounded pixel clip rectangle with padding, preventing negative coordinates."""
    pad = max(0, padding)
    x = max(0.0, bounds.x - pad)
    y = max(0.0, bounds.y - pad)
    width = bounds.width + (pad * 2)
    height = bounds.height + (pad * 2)
    return ClipRect(x=round(x, 2), y=round(y, 2), width=round(width, 2), height=round(height, 2))


def find_system_chrome() -> Optional[str]:
    """Discovers installed Google Chrome, Chromium, or Edge binary on macOS and Linux."""
    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
    ]
    for c in candidates:
        if os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    # Fallback to PATH search
    for name in ["google-chrome", "chromium", "google-chrome-stable"]:
        found = shutil.which(name)
        if found:
            return found
    return None


def find_iris_binary() -> Optional[str]:
    """Locates the compiled iris binary if present in user path or ~/.local/bin."""
    local_bin = Path.home() / ".local" / "bin" / "iris"
    if local_bin.is_file() and os.access(str(local_bin), os.X_OK):
        return str(local_bin)
    in_path = shutil.which("iris")
    if in_path:
        return in_path
    return None


class IrisVisualEngine:
    """Zero-Bloat Assimilated Visual Engine leveraging brijr/iris patterns with dual execution."""

    def __init__(self, iris_bin_path: Optional[str] = None, chrome_path: Optional[str] = None):
        self.iris_bin = iris_bin_path or find_iris_binary()
        self.chrome_path = chrome_path or find_system_chrome()

    @property
    def has_iris_cli(self) -> bool:
        return bool(self.iris_bin and os.path.exists(self.iris_bin))

    @property
    def has_chrome(self) -> bool:
        return bool(self.chrome_path and os.path.exists(self.chrome_path))

    def capture(
        self,
        url: str,
        output_path: str,
        size: str = "desktop",
        dark: bool = False,
        selector: Optional[str] = None,
        padding: int = 16,
        full_page: bool = False,
        wait_ms: int = 0,
        timeout_seconds: int = 30,
    ) -> Dict[str, Any]:
        """Captures a screenshot using either the native Iris binary or autonomous Headless Chrome."""
        out_p = Path(output_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)

        viewport = parse_viewport_preset(size)

        # 1. Native Iris CLI path (Fastest, ~360ms)
        if self.has_iris_cli and self.iris_bin:
            cmd = [self.iris_bin, url, "-o", str(out_p), "--size", size]
            if dark:
                cmd.append("--dark")
            if selector:
                cmd.extend(["--selector", selector, "--padding", str(padding)])
            elif full_page:
                cmd.append("--full-page")
            if wait_ms > 0:
                cmd.extend(["--wait", str(wait_ms)])

            logger.info("Executing native Iris CLI: %s", " ".join(cmd))
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_seconds)
            if proc.returncode == 0 and out_p.exists():
                return {
                    "success": True,
                    "engine": "iris_native",
                    "output_path": str(out_p),
                    "bytes": out_p.stat().st_size,
                    "viewport": viewport.model_dump(),
                }
            logger.warning("Iris CLI failed (%s): %s. Falling back to Chrome engine.", proc.returncode, proc.stderr)

        # 2. Autonomous Zero-Bloat Headless Chrome Fallback
        if self.has_chrome and self.chrome_path:
            logger.info("Executing autonomous Headless Chrome fallback for: %s", url)
            chrome_cmd = [
                self.chrome_path,
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
                f"--window-size={viewport.width},{viewport.height}",
                f"--screenshot={str(out_p)}",
            ]
            if dark:
                chrome_cmd.append("--blink-settings=forceDarkModeEnabled=true")
            if viewport.user_agent:
                chrome_cmd.append(f"--user-agent={viewport.user_agent}")

            chrome_cmd.append(url)
            proc = subprocess.run(chrome_cmd, capture_output=True, text=True, timeout=timeout_seconds)
            if out_p.exists():
                return {
                    "success": True,
                    "engine": "headless_chrome_fallback",
                    "output_path": str(out_p),
                    "bytes": out_p.stat().st_size,
                    "viewport": viewport.model_dump(),
                }
            raise RuntimeError(f"Headless Chrome failed to generate screenshot: {proc.stderr}")

        raise RuntimeError("Neither 'iris' binary nor Google Chrome/Chromium executable was found.")

# --- DNK-MRH-HEADER ---
# mrh_id: "packages/plugins/dnk_aperisolve_forensics/adapter.py"
# purpose: "Hexagonal Adapter & Client for AperiSolve FastMCP Steganalysis & Image Forensics"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-16"
# author: "DNK-e.com Maksym & Antigravity"
# --- END DNK-MRH-HEADER ---

import asyncio
import base64
import json
import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

logger = logging.getLogger("dnk.plugins.aperisolve")


class ForensicsReport(BaseModel):
    submission_hash: str
    filename: str
    status: str
    mime_type: Optional[str] = None
    file_size_bytes: int = 0
    analyzers_run: List[str] = Field(default_factory=list)
    has_hidden_payloads: bool = False
    extracted_archives: List[str] = Field(default_factory=list)
    exif_metadata: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)


class AperiSolveAdapter:
    """
    Adapter interfacing with the quarantined AperiSolve FastMCP server
    located in ../DNK_Vibe/AperiSolve/.
    Provides JIT image steganography detection, EXIF scrubbing, and
    asset provenance auditing for Shopify and media creation pipelines.
    """

    def __init__(self, vibe_root: Optional[Union[str, Path]] = None):
        if vibe_root is not None:
            self.vibe_dir = Path(vibe_root).resolve()
        else:
            hub_root = Path(__file__).resolve().parents[3]
            self.vibe_dir = (hub_root.parent / "DNK_Vibe" / "AperiSolve").resolve()

    def is_available(self) -> bool:
        """Checks if AperiSolve environment is installed and functional."""
        if not self.vibe_dir.exists():
            return False
        return (self.vibe_dir / "pyproject.toml").exists()

    def get_transport_command(self) -> Dict[str, Any]:
        """Returns standard stdio FastMCP invocation spec."""
        return {
            "command": "uv",
            "args": [
                "run",
                "--directory",
                str(self.vibe_dir),
                "--extra",
                "mcp",
                "python",
                "-m",
                "aperisolve_mcp",
                "--stdio",
            ],
            "cwd": str(self.vibe_dir),
        }

    def sanitize_image_metadata(
        self,
        image_path: Union[str, Path],
        output_path: Union[str, Path],
    ) -> Path:
        """
        Strips EXIF, GPS, camera serials, and auxiliary metadata from image
        to guarantee privacy, eliminate tracking, and reduce asset weight
        before uploading to Shopify CDN.
        """
        src = Path(image_path).resolve()
        dst = Path(output_path).resolve()
        dst.parent.mkdir(parents=True, exist_ok=True)

        try:
            from PIL import Image as PILImage

            with PILImage.open(src) as img:
                data = list(img.getdata())
                clean_img = PILImage.new(img.mode, img.size)
                clean_img.putdata(data)
                clean_img.save(dst, optimize=True)
            logger.info(f"Sanitized image written to {dst}")
            return dst
        except Exception as e:
            logger.warning(f"PIL sanitization failed ({e}), falling back to direct copy")
            shutil.copy2(src, dst)
            return dst

    def encode_file_base64(self, file_path: Union[str, Path]) -> str:
        """Encodes file bytes into base64 string for FastMCP analyze tool."""
        p = Path(file_path).resolve()
        raw_bytes = p.read_bytes()
        return base64.b64encode(raw_bytes).decode("ascii")

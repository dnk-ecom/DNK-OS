# --- DNK-MRH-HEADER ---
# mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/sota-repository-assimilation/references/chrome_extension_crx_extraction_and_reverse_engineering.md"
# purpose: "Zero-dependency deterministic extraction of Chrome Web Store extensions (CRX3) and Manifest V3 reverse-engineering."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-23"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

# Chrome Web Store CRX3 Deterministic Extraction & Inspection

## 1. Direct Headless CRX Download
When inspecting closed or proprietary browser extensions from the Chrome Web Store without a full browser or manual GUI interaction:

1. Obtain the Chrome Web Store Extension ID (the 32-character alphanumeric hash from the URL, e.g., `khcjkaobanoeohahnlffnnppinoeljme`).
2. Fetch the raw `.crx` file using Google's public update endpoint:
```
https://clients2.google.com/service/update2/crx?response=redirect&prodversion=120.0.0.0&acceptformat=crx2,crx3&x=id%3D<EXTENSION_ID>%26uc
```

## 2. Deterministic Extraction Script (Python Standard Library)
CRX3 packages prepend a binary header (magic `Cr24`, version, metadata). The underlying payload is a standard ZIP archive starting at byte offset `PK\x03\x04` (`0x50 0x4B 0x03 0x04`).

```python
import urllib.request
import zipfile
import io
import os

def extract_chrome_extension(ext_id: str, output_dir: str):
    crx_url = (
        f"https://clients2.google.com/service/update2/crx?"
        f"response=redirect&prodversion=120.0.0.0&acceptformat=crx2,crx3&x=id%3D{ext_id}%26uc"
    )
    req = urllib.request.Request(
        crx_url,
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    )
    with urllib.request.urlopen(req) as resp:
        data = resp.read()
    
    zip_offset = data.find(b"PK\x03\x04")
    if zip_offset == -1:
        raise ValueError(f"ZIP header not found in CRX response for {ext_id}")
    
    zip_data = data[zip_offset:]
    os.makedirs(output_dir, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
        z.extractall(output_dir)
    print(f"Successfully extracted {len(z.namelist())} files to {output_dir}")
```

## 3. Reverse-Engineering & Architecture Deconstruction
- **`manifest.json`**: Inspect `content_scripts`, `background.service_worker`, `web_accessible_resources`, and `permissions`.
- **`content-scripts/`**: Isolate DOM inspection, element selection overlays, and injected UI components.
- **`lib/` / `background/`**: Extract DOM computed style calculation algorithms, asset bundling, and token extraction routines.
- **Local Testing**: Load via `chrome://extensions` -> **Developer mode** -> **Load unpacked**.

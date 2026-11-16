<!-- --- DNK-MRH-HEADER ---
mrh_id: "core/orchestrator/agents/gerych_prime/skills/software-development/chrome-extension-engineering/references/crx_teardown_and_declarative_net_request_iframe_rules.md"
purpose: "Reference guide for CRX3 package harvesting, unpacking, and DeclarativeNetRequest rules for iframe embedding."
canonical_source: true
alters_files: []
triggers_tasks: []
status: "Active"
version: "1.0.0"
updated_at: "2026-10-28"
author: "DNK-e.com Maksym & Gerych Prime"
--- END DNK-MRH-HEADER --- -->

# CRX3 Teardown & DeclarativeNetRequest IFrame Embedding Guide

## 1. Direct CRX3 Download & Binary Extraction

To inspect, audit, or clean-room reverse engineer any Chrome extension directly from the Chrome Web Store without third-party scrapers:

### Download URL Pattern
```bash
curl -sL "https://clients2.google.com/service/update2/crx?response=redirect&prodversion=128.0&acceptformat=crx2,crx3&x=id%3D<EXTENSION_ID>%26uc" -o extension.crx
```

### Python Unpacker (CRX3 Header Stripper)
A `.crx` file is a ZIP archive prepended with a binary header. For CRX3:
- Header magic: `Cr24` (4 bytes)
- Version: `3` (uint32, 4 bytes)
- Header length: `header_len` (uint32, 4 bytes)
- The raw ZIP payload starts at offset `12 + header_len`.

```python
import struct, zipfile

def extract_crx3(crx_path: str, extract_to: str):
    with open(crx_path, "rb") as f:
        magic = f.read(4)
        if magic != b"Cr24":
            raise ValueError("Not a valid CRX file")
        version = struct.unpack("<I", f.read(4))[0]
        if version == 3:
            header_len = struct.unpack("<I", f.read(4))[0]
            f.seek(12 + header_len)
        elif version == 2:
            pk_len = struct.unpack("<I", f.read(4))[0]
            sig_len = struct.unpack("<I", f.read(4))[0]
            f.seek(16 + pk_len + sig_len)
        zip_data = f.read()

    with open("/tmp/temp.zip", "wb") as zf:
        zf.write(zip_data)

    with zipfile.ZipFile("/tmp/temp.zip", "r") as z:
        z.extractall(extract_to)
```

---

## 2. DeclarativeNetRequest Rules for IFrame Embedding

When developing multi-screen responsive previewers or canvas editors that load arbitrary URLs into `<iframe>`, browsers enforce:
1. `X-Frame-Options: DENY` or `SAMEORIGIN`
2. `Content-Security-Policy: frame-ancestors ...`

In Manifest V3, `webRequestBlocking` is deprecated for header modification in standard extensions. The canonical solution is `declarativeNetRequest`.

### Required Permissions (`manifest.json`)
```json
{
  "permissions": [
    "declarativeNetRequest",
    "declarativeNetRequestFeedback",
    "activeTab",
    "storage"
  ]
}
```

### Session Rule Injection in Service Worker (`background.js`)
Instead of persisting static rules globally, use `updateSessionRules` scoped to target `tabId` and `SUB_FRAME` resource types:

```javascript
async function enableIframeEmbedding(tabId) {
  const rules = [
    {
      id: 1001,
      priority: 1,
      action: {
        type: "modifyHeaders",
        responseHeaders: [
          { header: "x-frame-options", operation: "remove" },
          { header: "content-security-policy", operation: "remove" }
        ]
      },
      condition: {
        tabIds: [tabId],
        resourceTypes: ["sub_frame"]
      }
    }
  ];

  await chrome.declarativeNetRequest.updateSessionRules({
    removeRuleIds: [1001],
    addRules: rules
  });
}

async function disableIframeEmbedding() {
  await chrome.declarativeNetRequest.updateSessionRules({
    removeRuleIds: [1001]
  });
}
```

### Invariants:
- Never strip security headers globally across all tabs — always scope `condition.tabIds` to the active viewer tab.
- Always clean up session rules when the tab or window closes (`chrome.tabs.onRemoved`).

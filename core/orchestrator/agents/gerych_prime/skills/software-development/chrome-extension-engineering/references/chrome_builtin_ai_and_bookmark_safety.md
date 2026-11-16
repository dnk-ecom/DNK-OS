# Chrome Built-in AI (Prompt API) & MV3 Data Protection Recipes

## 1. Chrome Built-in AI (Prompt API & Summarization API)
Chrome 128+ provides on-device Gemini Nano inference directly in windowed extension contexts (Side Panel, Popup, Offscreen Documents).

### Availability Check & Session Creation
```javascript
// Side Panel or Popup context (window context required - not available in Service Worker)
export async function getLocalAiSession(systemPrompt = '') {
  if (!window.ai?.languageModel) {
    throw new Error('Chrome Built-in AI is not supported or not enabled in chrome://flags');
  }

  const capabilities = await window.ai.languageModel.capabilities();
  if (capabilities.available === 'no') {
    throw new Error('Gemini Nano is not available on this device');
  }

  // 'after-download' means Chrome needs to download the model (~1.5GB)
  const session = await window.ai.languageModel.create({
    systemPrompt: systemPrompt || 'You are a helpful assistant assisting with browser organization.',
    temperature: 0.2,
    topK: 3
  });

  return session;
}
```

### Streaming Prompt Execution
```javascript
export async function promptLocalAiStream(session, promptText, onChunk) {
  const stream = session.promptStreaming(promptText);
  let fullResponse = '';
  for await (const chunk of stream) {
    fullResponse = chunk; // Prompt API streaming chunks contain accumulated response
    if (onChunk) onChunk(chunk);
  }
  return fullResponse;
}
```

### Deterministic Fallback Pipeline (Tier 1 -> Tier 2)
To guarantee 100% uptime without external API keys:
1. **Tier 1 (Deterministic Regex & Rules)**: Run instant local matching (<5ms) for known domains (e.g. `github.com` -> Development, `youtube.com` -> Media).
2. **Tier 2 (Gemini Nano Prompt API)**: If unmatched, invoke local `window.ai.languageModel` for categorizing or tagging.
3. **Tier 3 (Fuzzy / TF-IDF)**: If model is unavailable or downloading, fallback to local string token similarity.

---

## 2. Bookmark & Tab Data Protection Invariants

### Pain Points from CWS Post-Mortems (OneTab, Session Buddy)
- **WebSQL Deprecation & IndexedDB Migration Failure**: Session Buddy v6 lost user histories across 5-10 years during migration.
- **Cache Cleaners Wiping Unindexed Storage**: OneTab stored URLs in `localStorage`; OS cleaners (CleanMyMac) wiped it out without warning.
- **Silent Multi-Tab Moving**: Automations moving hundreds of bookmarks into wrong folders without review or undo.

### Invariant 1: Transactional Snapshot Before Any Mutation
Before executing any batch bookmark/tab modification, capture a timestamped snapshot into `chrome.storage.local`:

```javascript
export async function createMutationSnapshot(description) {
  const tree = await chrome.bookmarks.getTree();
  const snapshot = {
    id: `snap_${Date.now()}`,
    timestamp: new Date().toISOString(),
    description,
    treeData: tree
  };

  const { snapshots = [] } = await chrome.storage.local.get(['snapshots']);
  // Keep rolling last 10 snapshots
  snapshots.unshift(snapshot);
  if (snapshots.length > 10) snapshots.pop();

  await chrome.storage.local.set({ snapshots });
  return snapshot.id;
}
```

### Invariant 2: Visual Diff & Review Barrier
- Never execute batch reorganization or deletion in the background without explicit user confirmation.
- Present a list of planned mutations with toggle checkboxes (approved/rejected).
- Only apply confirmed items to `chrome.bookmarks.move` or `chrome.bookmarks.remove`.

### Invariant 3: Single-Click Instant Undo
```javascript
export async function rollbackLastSnapshot() {
  const { snapshots = [] } = await chrome.storage.local.get(['snapshots']);
  if (!snapshots.length) throw new Error('No snapshots available to restore');

  const targetSnapshot = snapshots[0];
  // Restore bookmarks or present restore guide to prevent accidental overwrite
  return targetSnapshot;
}
```

---

## 3. Pre-Save URL Hygiene & Privacy Invariants

### Tracking Parameter Stripping (URL Sanitizer)
Before storing or categorizing URLs, strip tracking and marketing query parameters to prevent duplicate bookmarks and bloated storage:
```javascript
const TRACKING_PARAMS = new Set([
  'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
  'fbclid', 'gclid', 'msclkid', 'mc_eid', '_hsenc', '_hsmi', 'ref', 'source'
]);

export function sanitizeBookmarkUrl(rawUrl) {
  try {
    const url = new URL(rawUrl);
    for (const key of Array.from(url.searchParams.keys())) {
      if (TRACKING_PARAMS.has(key.toLowerCase()) || key.startsWith('utm_')) {
        url.searchParams.delete(key);
      }
    }
    return url.toString();
  } catch {
    return rawUrl;
  }
}
```

### Privacy & Auth Token Leak Prevention
Warn or redact URLs containing credential fragments prior to export or synchronization:
```javascript
const SENSITIVE_QUERY_PATTERNS = [
  /token/i, /auth/i, /key/i, /session/i, /jwt/i, /secret/i, /password/i
];

export function hasSensitiveParams(urlStr) {
  try {
    const url = new URL(urlStr);
    for (const key of url.searchParams.keys()) {
      if (SENSITIVE_QUERY_PATTERNS.some(p => p.test(key))) return true;
    }
  } catch {}
  return false;
}
```

---

## 4. Tree Organization Constraints ("Rule of 3" & Max Depth)

When prompting an LLM or running clustering algorithms to organize bookmarks:
1. **Max Depth Cap (`maxDepth: 3`)**: Prevent deep recursive nesting that degrades UX on mobile/panels.
2. **Rule of 3 (Cluster Justification)**: Never generate a dedicated folder unless at least 3 bookmarks belong to it. Singletons or pairs must be kept at the parent category level.
3. **Domain Anchor Priority**: Always classify the top-level intent by domain archetype (e.g. `Dev Docs`, `SaaS`, `E-Commerce`, `Media`) before subtopic tagging.

---

## 5. Bookmark Health & Dead Link Verification

Lightweight asynchronous HEAD checks to detect bitrot without saturating network connections:
```javascript
export async function checkBookmarkHealth(url) {
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 6000);
    const res = await fetch(url, {
      method: 'HEAD',
      signal: controller.signal,
      headers: { 'User-Agent': 'Mozilla/5.0 (compatible; LinkHealthCheck/1.0)' }
    });
    clearTimeout(timeout);
    return { ok: res.ok, status: res.status };
  } catch (err) {
    return { ok: false, status: err.name === 'AbortError' ? 408 : 0, error: err.message };
  }
}
```

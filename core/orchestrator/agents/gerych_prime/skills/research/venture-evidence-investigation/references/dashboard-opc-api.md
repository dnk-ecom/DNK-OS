# OnePersonCompany Dashboard API & Arctic Shift Reddit Reference

## Base URL and Authentication
- Base URL: `http://127.0.0.1:8787`
- Authentication Header: `x-opc-key: <SERVICE_KEY>`
- Key Storage: `server/data/service-key` in the OnePersonCompany repo root or environment variable `$OPC_SERVICE_KEY`.

## Essential Endpoints

### 1. Venture Management
- `GET /api/ventures`: Lists all ventures in the portfolio with stages, status counts, and metadata.
- `GET /api/ventures/:slug`: Retrieves single venture record (id, stage, host, brand properties).
- `GET /api/venture-journey/:slug`: Retrieves journey stage definitions, milestones, and current progress.
- `POST /api/ventures/:slug/stage`: Updates stage (`idea`, `pre-launch`, `launched`). Payload: `{"stage": "pre-launch"}`.

### 2. Live Automated Audits
- `POST /api/audit/:slug`: Triggers automated live audit of venture website, checking SSL certificates, HTTP redirects, sitemap.xml, robots.txt, and response codes. Returns errors, warnings, notices, and response timings.

### 3. Analytics & Integration Links
- `GET /api/venture-links/:slug`: Lists connected search consoles, webmaster tools, and analytics accounts.
- `POST /api/venture-links/:slug`: Links a new service (e.g. Google Search Console, Bing Webmaster, Umami).

### 4. Reddit Archive (Arctic Shift Proxy)
- `GET /api/reddit/search?subreddit=<subvy>&q=<query>&days=<N>&limit=<K>`: Searches Reddit submissions through the local Arctic Shift proxy cache. Avoids direct reddit.com rate-limiting and blocking.
- `GET /api/reddit/comments?subreddit=<subvy>&q=<query>&days=<N>&limit=<K>`: Searches post comments matching terms.
- `GET /api/reddit/thread?id=<id>`: Retrieves full thread hierarchy and comments.

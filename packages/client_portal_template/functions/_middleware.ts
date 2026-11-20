// --- DNK-MRH-HEADER ---
// mrh_id: "packages/client_portal_template/functions/_middleware.ts"
// purpose: "Edge Password Gate for Cloudflare Pages Client Portal"
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-11-17"
// author: "DNK-e.com Maksym"
// --- END DNK-MRH-HEADER ---

interface Env {
  CLIENT_PASSWORD?: string;
}

export const onRequest: PagesFunction<Env> = async (context) => {
  const { request, env } = context;
  const url = new URL(request.url);

  // Target password: from Cloudflare Environment Variables or default fallback
  const validPassword = env.CLIENT_PASSWORD || "dnk2026";
  const sessionCookieName = "dnk_client_session";

  // Allow static assets and API endpoints through without authentication (Prevent CSS MIME 401 lockout)
  const isPublicResource =
    url.pathname.startsWith("/assets/") ||
    url.pathname.startsWith("/api/") ||
    url.pathname === "/favicon.ico" ||
    url.pathname === "/robots.txt" ||
    url.pathname === "/llms.txt" ||
    /\.(css|js|svg|png|jpg|jpeg|gif|webp|woff|woff2|ico|json|txt|map)$/i.test(url.pathname);

  if (isPublicResource) {
    return context.next();
  }

  // Check URL query parameter shortcut: ?key=PASSWORD
  const keyParam = url.searchParams.get("key");
  if (keyParam === validPassword) {
    url.searchParams.delete("key");
    return new Response(null, {
      status: 302,
      headers: {
        Location: url.pathname + (url.search ? url.search : ""),
        "Set-Cookie": `${sessionCookieName}=authorized; Path=/; HttpOnly; SameSite=Lax; Max-Age=2592000`,
      },
    });
  }

  // Handle Login POST
  if (request.method === "POST" && url.pathname === "/_auth_login") {
    try {
      const formData = await request.formData();
      const enteredPassword = formData.get("password")?.toString();

      if (enteredPassword === validPassword) {
        const returnTo = formData.get("return_to")?.toString() || "/";
        return new Response(null, {
          status: 302,
          headers: {
            Location: returnTo,
            "Set-Cookie": `${sessionCookieName}=authorized; Path=/; HttpOnly; SameSite=Lax; Max-Age=2592000`,
          },
        });
      }

      return new Response(renderLoginForm(url.pathname, true), {
        status: 401,
        headers: { "Content-Type": "text/html; charset=utf-8" },
      });
    } catch {
      return new Response("Invalid request", { status: 400 });
    }
  }

  // Handle Logout
  if (url.pathname === "/_auth_logout" || url.searchParams.get("logout") === "1") {
    url.searchParams.delete("logout");
    return new Response(null, {
      status: 302,
      headers: {
        Location: url.pathname === "/_auth_logout" ? "/" : (url.pathname + (url.search ? url.search : "")),
        "Set-Cookie": `${sessionCookieName}=deleted; Path=/; HttpOnly; SameSite=Lax; Max-Age=0`,
      },
    });
  }

  // Check existing session cookie
  const cookieHeader = request.headers.get("Cookie") || "";
  if (cookieHeader.includes(`${sessionCookieName}=authorized`)) {
    return context.next();
  }

  // If not authenticated, render login page
  return new Response(renderLoginForm(url.pathname), {
    status: 401,
    headers: { "Content-Type": "text/html; charset=utf-8" },
  });
};

function renderLoginForm(returnTo: string, isError = false): string {
  return `<!DOCTYPE html>
<html lang="uk">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🔒 Закритий доступ | DNK Ecom Client Space</title>
  <style>
    :root {
      --bg: #090a0f;
      --card-bg: #12141c;
      --border: #232738;
      --accent: #2563eb;
      --accent-hover: #1d4ed8;
      --text: #f3f4f6;
      --text-muted: #9ca3af;
      --error: #ef4444;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 1.5rem;
    }
    .card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 1rem;
      padding: 2.5rem 2rem;
      width: 100%;
      max-width: 420px;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
    }
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      background: rgba(37, 99, 235, 0.15);
      color: #60a5fa;
      border: 1px solid rgba(37, 99, 235, 0.3);
      padding: 0.25rem 0.75rem;
      border-radius: 9999px;
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 1.25rem;
    }
    h1 { font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem; letter-spacing: -0.02em; }
    p { color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1.75rem; line-height: 1.5; }
    .input-group { margin-bottom: 1.25rem; }
    label { display: block; font-size: 0.8rem; font-weight: 600; margin-bottom: 0.5rem; color: var(--text-muted); }
    input[type="password"] {
      width: 100%;
      background: #0d0f17;
      border: 1px solid var(--border);
      color: var(--text);
      padding: 0.75rem 1rem;
      border-radius: 0.5rem;
      font-size: 1rem;
      outline: none;
      transition: border-color 0.2s;
    }
    input[type="password"]:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
    }
    button {
      width: 100%;
      background: var(--accent);
      color: white;
      border: none;
      padding: 0.85rem;
      border-radius: 0.5rem;
      font-size: 0.95rem;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.2s;
    }
    button:hover { background: var(--accent-hover); }
    .error-msg {
      background: rgba(239, 68, 68, 0.1);
      border: 1px solid rgba(239, 68, 68, 0.3);
      color: #fca5a5;
      padding: 0.65rem 0.85rem;
      border-radius: 0.5rem;
      font-size: 0.85rem;
      margin-bottom: 1.25rem;
    }
    .footer {
      margin-top: 2rem;
      text-align: center;
      font-size: 0.75rem;
      color: #4b5563;
    }
  </style>
</head>
<body>
  <div class="card">
    <div class="badge">🔒 Конфіденційний проект</div>
    <h1>Клієнтський Простір</h1>
    <p>Цей портал містить персональний аудит та комерційну пропозицію. Введіть пароль для доступу.</p>

    ${isError ? `<div class="error-msg">⚠️ Невірний пароль. Спробуйте ще раз або зверніться до менеджера.</div>` : ""}

    <form method="POST" action="/_auth_login">
      <input type="hidden" name="return_to" value="${escapeHtml(returnTo)}">
      <div class="input-group">
        <label for="password">Пароль доступу</label>
        <input type="password" id="password" name="password" required autofocus placeholder="••••••••">
      </div>
      <button type="submit">Увійти в простір</button>
    </form>

    <div class="footer">
      Powered by DNK OS • Sovereign E-commerce Infrastructure
    </div>
  </div>
</body>
</html>`;
}

function escapeHtml(str: string): string {
  return str.replace(/[&<>'"]/g, 
    tag => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      "'": '&#39;',
      '"': '&quot;'
    }[tag] || tag)
  );
}

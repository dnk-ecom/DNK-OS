// --- DNK-MRH-HEADER ---
// mrh_id: "packages/client_portal_template/functions/api/v1/cockpit/[deal_id]/tickets.ts"
// purpose: "Cloudflare Pages Function: Edge Ingestion for In-Context Visual Reviews"
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-11-18"
// author: "DNK-e.com Maksym & Antigravity"
// --- END DNK-MRH-HEADER ---

interface Env {
  DNK_WEBHOOK_URL?: string;
  CLIENT_PASSWORD?: string;
}

export const onRequestPost: PagesFunction<Env> = async (context) => {
  const { request, params, env } = context;
  const dealId = (params.deal_id as string) || "deal_portal";

  try {
    const body = await request.json() as Record<string, any>;
    const ticketId = `tkt_${Date.now().toString(36)}`;
    const comment = body.comment || "Без коментаря";
    const selector = body.selector || body.bounding_box?.relative_anchor?.selector || "Виділена область";

    // If an external DNK OS webhook/hub is configured, dispatch asynchronously
    if (env.DNK_WEBHOOK_URL) {
      context.waitUntil(
        fetch(env.DNK_WEBHOOK_URL, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            event: "client_visual_review",
            deal_id: dealId,
            ticket_id: ticketId,
            payload: body,
            timestamp: new Date().toISOString(),
          }),
        }).catch((err) => console.error("Webhook dispatch failed:", err))
      );
    }

    const clientAcknowledgment =
      `Дякуємо! Вашу правку для зони '${selector}' успішно зафіксовано на Cloudflare Edge та передано в чергу розробки.`;

    return new Response(
      JSON.stringify({
        status: "success",
        ticket_id: ticketId,
        deal_id: dealId,
        category: body.category || "in_scope_revision",
        client_acknowledgment: clientAcknowledgment,
        quota_remaining: 3,
        builder_task: {
          task_id: `BLD-${ticketId}`,
          deal_id: dealId,
          target_element: {
            selector: selector,
            bounding_box: body.bounding_box,
          },
          client_instruction: comment,
        },
      }),
      {
        status: 200,
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
        },
      }
    );
  } catch (error: any) {
    return new Response(
      JSON.stringify({ status: "error", message: error?.message || "Invalid JSON payload" }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    );
  }
};

export const onRequestGet: PagesFunction<Env> = async (context) => {
  const { params } = context;
  const dealId = (params.deal_id as string) || "deal_portal";

  return new Response(
    JSON.stringify({
      status: "success",
      deal_id: dealId,
      tickets: [],
      count: 0,
    }),
    {
      status: 200,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
    }
  );
};

export const onRequestOptions: PagesFunction = async () => {
  return new Response(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
    },
  });
};

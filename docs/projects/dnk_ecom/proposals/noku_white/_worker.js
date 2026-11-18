// --- DNK-MRH-HEADER ---
// mrh_id: "docs/projects/dnk_ecom/proposals/noku_white/_worker.js"
// purpose: "Cloudflare Pages Advanced Worker: in-context review edge API + static asset proxy."
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "2.0.0"
// updated_at: "2026-11-18"
// author: "DNK-e.com Maksym & Antigravity"
// --- END DNK-MRH-HEADER ---

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Standard CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      'Content-Type': 'application/json; charset=utf-8',
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    // Match /api/v1/cockpit/*
    if (url.pathname.startsWith('/api/v1/cockpit')) {
      const subPath = url.pathname.replace('/api/v1/cockpit', '').replace(/^\/+/, '');
      const parts = subPath.split('/');
      const dealId = parts[0] || 'deal_noku_2026';
      const action = parts[1] || '';

      // 1. POST /api/v1/cockpit/{dealId}/tickets
      if (request.method === 'POST' && action === 'tickets') {
        try {
          const body = await request.json();
          const title = body.title || 'Нова правка';
          const comment = body.comment || '';
          const textLower = (title + ' ' + comment).toLowerCase();

          // Scope Guard Triage
          let category = body.category || 'auto';
          if (category === 'auto') {
            if (/як |чи можна|де подивитися|чому|\?/.test(textLower)) {
              category = 'question';
            } else if (/crm|кастомний додаток|1с|інтеграція з бас|нова мова/.test(textLower)) {
              category = 'out_of_scope_upsell';
            } else {
              category = 'in_scope_revision';
            }
          }

          const ticketId = 'TKT-' + Math.random().toString(36).substring(2, 8).toUpperCase();
          const targetName = body.block_id || body.section_id || body.selector || 'виділеної області';

          let clientAck = '';
          let quotaRem = '2 / 3 раунди';

          if (category === 'question') {
            clientAck = `Дякуємо за запитання! Ми детально роз'яснимо логіку роботи для зони '${targetName}'. Ваш ліміт правок не використовується.`;
          } else if (category === 'out_of_scope_upsell') {
            clientAck = `Дякуємо за побажання! Запит по зоні '${targetName}' передбачає новий розширений функціонал поза базовим скоупом. Ми прорахуємо вартість і запропонуємо рішення.`;
          } else {
            clientAck = `Дякуємо! Вашу правку по зоні '${targetName}' зафіксовано та передано агенту розробки (Денчік). Правка виконується в межах погодженого пакету.`;
          }

          const responsePayload = {
            status: 'success',
            ticket_id: ticketId,
            deal_id: dealId,
            category: category,
            client_acknowledgment: clientAck,
            quota_remaining: quotaRem,
            builder_task: {
              task_id: `BLD-${ticketId}`,
              deal_id: dealId,
              target_element: {
                section: body.section_id || 'global',
                block: body.block_id || '',
                selector: body.selector || '',
                bounding_box: body.bounding_box || null,
                relative_anchor: body.bounding_box && body.bounding_box.relative_anchor ? body.bounding_box.relative_anchor : null,
              },
              client_instruction: comment,
              category: category,
              suggested_file: body.block_id ? `blocks/${body.block_id}.liquid` : `sections/${body.section_id || 'main-product'}.liquid`
            }
          };

          return new Response(JSON.stringify(responsePayload, null, 2), {
            status: 200,
            headers: corsHeaders,
          });
        } catch (err) {
          return new Response(JSON.stringify({ status: 'error', message: err.message }), {
            status: 400,
            headers: corsHeaders,
          });
        }
      }

      // 2. GET /api/v1/cockpit/{dealId}
      if (request.method === 'GET') {
        const dummyState = {
          deal: {
            deal_id: dealId,
            client_name: 'Андрій Ніколаєв',
            brand: 'NOKU',
            total_amount: 1500.0,
            prepay_amount: 750.0,
            revision_quota: 3,
            revisions_used: 1,
            status: 'active'
          },
          stages: [
            { stage_num: 1, title: 'Архітектура, стиль (Polaris Snow) та прототип картки', status: 'completed' },
            { stage_num: 2, title: 'Верстка головної сторінки та нативних Theme Blocks', status: 'in_progress' },
            { stage_num: 3, title: 'Синхронізація відгуків Etsy та розмітка Google Shopping', status: 'pending' },
            { stage_num: 4, title: 'Оптова B2B сторінка та висувний кошик (Slide Drawer)', status: 'pending' },
            { stage_num: 5, title: 'QA, оптимізація швидкості (Core Web Vitals 90+) та чекаут', status: 'pending' },
            { stage_num: 6, title: 'Фінальний реліз на noku.store та передача прав на тему', status: 'pending' },
          ],
          tickets: [],
          artifacts: [
            { name: 'Жива комерційна пропозиція', url: 'https://noku-proposal.pages.dev' },
            { name: 'Поточний діючий магазин', url: 'https://noku.store' }
          ]
        };

        return new Response(JSON.stringify(dummyState, null, 2), {
          status: 200,
          headers: corsHeaders,
        });
      }

      return new Response(JSON.stringify({ error: 'Endpoint not found' }), {
        status: 404,
        headers: corsHeaders,
      });
    }

    // Static assets fallback
    return env.ASSETS.fetch(request);
  }
};

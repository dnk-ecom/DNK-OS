# Приклад: DLNAPM/eGreetz_Veo (для перевірки промпту)

Прочитано: метадані GitHub, дерево (29 файлів), `package.json`, початок `README.md`, `firestore.rules`, `storage.rules`,
`services/geminiService.ts` (номери рядків звідти). Компоненти `components/*`
не відкрито. Обидва файли в `migrated_prompt_history/` мають розмір 0 байт, тож промптами не вважаються.
Репозиторій цінний як **джерело шаблонів і оркестрації відеогенерації**, а не як застосунок.

```json
{
  "repo": "DLNAPM/eGreetz_Veo", "sha": "c6ff94b", "fetched_at": "2026-11-06",
  "identity": {"what_it_is": "React 19 + Firebase застосунок: сценарій (Gemini), озвучка (Gemini TTS), відео (Veo 3.1) і публічні посилання. Згенерований із google-gemini/aistudio-repository-template.",
               "kind": "prompts", "derived_from": "google-gemini/aistudio-repository-template", "license": "none",
               "stars": 0, "pushed": "2026-04-08", "authors": 1},
  "claims": [
    {"claim": "Генерація відео через Veo", "status": "CONFIRMED", "evidence": "c6ff94b:services/geminiService.ts:L150 (ai.models.generateVideos), L201 (veo-3.1-generate-preview)"},
    {"claim": "Озвучка Gemini TTS", "status": "CONFIRMED", "evidence": "c6ff94b:services/geminiService.ts:L278 (gemini-2.5-flash-preview-tts)"},
    {"claim": "Фото як референс персонажа", "status": "CONFIRMED", "evidence": "c6ff94b:services/geminiService.ts:L133-L147 (referenceImages)"},
    {"claim": "Авторизація Google і Firestore", "status": "CONFIRMED", "evidence": "c6ff94b:firestore.rules:L11 (list лише за власником), c6ff94b:firestore.rules:L14 (create), c6ff94b:storage.rules:L9 (запис лише власник)"},
    {"claim": "Голосове введення тексту", "status": "NOT_FOUND", "evidence": "не шукали в components/*"}
  ],
  "mechanics": [
    {"name": "Вибір тривалості відео за довжиною озвучки", "kind": "algorithm",
     "what": "Цільова тривалість 7 с (14 с в режимі extended). Якщо відома тривалість аудіо, потрібна = ceil(аудіо + 1 с); якщо вона більша за цільову, цільова стає нею.",
     "io": "audioDuration, extended → targetDuration (секунди)", "edge_cases": "аудіо коротше 6 с не змінює 7 с",
     "where": "c6ff94b:services/geminiService.ts:L81-L88", "spec": "target = extended ? 14 : 7; if audio: target = max(target, ceil(audio + 1)).",
     "dnk_module": "медіа-пайплайн", "effort": "S", "action": "CLEAN_ROOM"},
    {"name": "Подовження відео сегментами", "kind": "algorithm",
     "what": "Поки вироблена тривалість менша за цільову, робиться повторний виклик Veo з промптом продовження того самого кадру, до виробленого додається довжина сегмента.",
     "io": "відео-сегмент, targetDuration → довше відео", "edge_cases": "не прочитано: обмеження кількості ітерацій і обробка помилок",
     "where": "c6ff94b:services/geminiService.ts:L196-L221", "spec": "loop: extend(prompt='Seamlessly continue the cinematic shot with matching lighting and atmosphere'); produced += segment.",
     "dnk_module": "медіа-пайплайн", "effort": "M", "action": "CLEAN_ROOM"},
    {"name": "Блоковий шаблон відео-промпта", "kind": "prompt_pattern",
     "what": "Промпт складається з заголовка режиму (CINEMATIC PRODUCTION / TRANSFORMATION), опису події, блоку VISUAL STYLE (8k, світло, рух камери); два варіанти: атмосфера свята і до/після за референсами.",
     "io": "змінні: occasion, тема або scenicDescription, наявність референс-зображень → текст промпта",
     "where": "c6ff94b:services/geminiService.ts:L101-L117", "spec": "[РЕЖИМ]: [подія]. [СЦЕНА]. VISUAL STYLE: [якість], [світло], [рух камери]. Варіант залежить від наявності референсів.",
     "dnk_module": "бібліотека промптів для відео", "effort": "S", "action": "CLEAN_ROOM"},
    {"name": "Тривалість PCM-аудіо з base64", "kind": "formula",
     "what": "duration_sec = (довжина_байтів / 2) / 24000 для 16-бітного моно PCM 24 кГц; при помилці 10",
     "io": "base64 → секунди", "where": "c6ff94b:services/geminiService.ts:L11-L20", "spec": "семпли = байти / 2; секунди = семпли / 24000.",
     "dnk_module": "медіа-пайплайн", "effort": "S", "action": "CLEAN_ROOM"},
    {"name": "Публічне читання за ID, перелік лише власнику", "kind": "access_rules",
     "what": "get відкрито всім (посилання), list/update/delete лише власнику за userId",
     "where": "c6ff94b:firestore.rules:L8-L11", "spec": "get без авторизації; list за resource.data.userId == request.auth.uid.",
     "dnk_module": "обмін результатами", "effort": "S", "action": "CLEAN_ROOM"}
  ],
  "quality": {"tests": false, "ci": false, "typed": true, "notes": "TypeScript 97%, один автор, 88 комітів, без тестів і CI"},
  "risks": [
    {"type": "access_rules", "evidence": "c6ff94b:firestore.rules:L8 і L23: get дозволено всім, безпека залежить від непередбачуваності ID", "severity": "medium"},
    {"type": "public_storage", "evidence": "c6ff94b:storage.rules:L8: читання відкрите всім, включно з фото й озвучкою користувачів", "severity": "medium"},
    {"type": "license", "evidence": "ліцензії немає: код і тексти копіювати не можна", "severity": "high"}
  ],
  "dnk_fit": {"module": "медіа-генерація (відео з озвучкою)", "overlap": "не перевірено проти каталогу",
              "gap": "обробка помилок і ліміти ітерацій у продовженні відео не прочитані", "similar_in_catalog": []},
  "verdict": {"tier": "WATCH", "confidence": "medium",
              "reasons": ["Три відтворювані механіки генерації відео з озвучкою підтверджені в коді",
                          "Немає ліцензії, 0 зірок, шаблонне походження, один автор: лише CLEAN_ROOM",
                          "Непрочитані компоненти й правила"],
              "take": ["правило тривалості за аудіо", "подовження відео сегментами", "блокова структура промпта"],
              "skip": ["UI-компоненти", "налаштування розгортання", "Firebase-обв'язка"],
              "next": "відкрити components/PromptForm.tsx і types.ts: перелік тем, свят і параметрів, що підставляються в промпт"},
  "unverified": ["components/*", "voice-to-text", "ліміти ітерацій у подовженні відео", "перетин з каталогом DNK", "services/firebase.ts не читали"]
}
```

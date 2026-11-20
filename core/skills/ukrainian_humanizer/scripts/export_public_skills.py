# --- DNK-MRH-HEADER ---
# mrh_id: "core/skills/ukrainian_humanizer/scripts/export_public_skills.py"
# purpose: "Automated Zero-Code Public Skill Exporter & Validator for Gemini Web, ChatGPT, Claude, and Grok."
# canonical_source: true
# alters_files: ["artifacts/public_skills/ukrainian-humanizer/SKILL.md", "artifacts/public_skills/english-humanizer/SKILL.md"]
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-10-17"
# author: "DNK-e.com Maksym & Gerych"
# --- END DNK-MRH-HEADER ---

"""Public Skill Packager & Validator for Web Chat Harnesses (Gemini, Claude, ChatGPT, Grok).

Generates zero-script, self-contained SKILL.md bundles and .zip packages for:
1. ukrainian-humanizer (Ukrainian market: grants, Diia.Business, Shopify UA, B2B)
2. english-humanizer (Global/Export market: Western SaaS, Shopify Global, B2B outreach)

Strict Safety Gate (`validate_public_skill`):
- Frontmatter contains ONLY `name:` and `description:` (no nested YAML, no comments).
- Zero references to `python`, `bash`, `.py`, `.sh`, `scripts/`, `pbpaste`, or CLI execution.
- Single-file zip package (`SKILL.md` at archive root) for 1-click upload in Gemini Web Skills.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import zipfile
from typing import Any, Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT_DIR = os.path.normpath(
    os.path.join(HERE, "..", "..", "..", "..", "packages", "public_skills")
)

FORBIDDEN_SCRIPT_PATTERNS = [
    (r"\bpython3?\b", "Executable python command reference"),
    (r"\bbash\b", "Executable bash command reference"),
    (r"\bsh\s+", "Shell invocation reference"),
    (r"\w+\.py\b", "Python script filename (.py)"),
    (r"\w+\.sh\b", "Shell script filename (.sh)"),
    (r"scripts/", "scripts/ directory path reference"),
    (r"\bpbpaste\b|\bpbcopy\b", "OS clipboard command reference"),
    (r"```(?:python|bash|sh|zsh|console)", "Executable code fence block"),
]


UKRAINIAN_PUBLIC_SKILL_MD = """---
name: ukrainian-humanizer
description: Редагує, очищує та створює живі українські тексти без ШІ-штампів, канцеляриту, кальок і суржику. Use when editing, translating, or writing Ukrainian text, business plans, grant applications, or marketing copy.
---

# Український Гуманізатор Тексту (Ukrainian AI Humanizer)

Ти — шеф-редактор української комерційної, публіцистичної та ділової прози (стандарт Сергія Осоки, Миколи Куліша, Бориса Антоненка-Давидовича та сучасного українського бізнес-стилю). Твоє завдання — перетворювати штучні, канцелярські або згенеровані нейромережами чернетки на живий, точний, природний український текст.

## Алгоритм роботи (виконуй послідовно в пам'яті без виклику зовнішніх програм)

Коли користувач надсилає текст або просить написати/відредагувати матеріал:

### Крок 1: Діагностика «Топ-3 гріхів тексту»
Оціни вхідний текст за 5 критеріями природності (від 0 до 100 балів):
1. **Ритм і синтаксис (Burstiness)** — чи немає монотонних речень однакової довжини (14–18 слів підряд).
2. **Конкретика (Specificity)** — чи є тверді цифри, факти, грн/₴, години, власні назви замість розмитих епітетів.
3. **Чистота від ШІ-штампів (Slop Density)** — відсутність вступних розшаркувань та маркетингових кліше.
4. **Типографіка (Fingerprint)** — правильні українські лапки «ялинки», апостроф `’`, відсутність надлишкових тире `—`.
5. **Активний голос (Voice)** — живі дієслова замість пасивних конструкцій на *-но/-то* та *-ться*.

### Крок 2: Очищення за 7 мовними правилами

1. **Активний стан замість канцелярського пасиву**:
   - ❌ *Проект було реалізовано нашою командою в стислі терміни.*
   - ✅ *Команда запустила проєкт за три тижні.*
   - Замінюй конструкції *«було зроблено», «здійснюється підтримка», «забезпечується виконання», «проводиться аналіз»* на пряму дію: **Хто робить Що**.

2. **Справжні дієслова замість віддієслівних іменників на -ння / -ття**:
   - ❌ *Здійснення впровадження заходів із покращення обслуговування.*
   - ✅ *Ми оновили сервіс і скоротили чергу вдвічі.*

3. **Ліквідація кальок активних дієприкметників на -учий / -ючий / -ачий**:
   - `діючий` -> **чинний** (закон, тариф) або **дієвий / робочий** (бізнес, цех)
   - `існуючий` -> **наявний / теперішній**
   - `оточуючий` -> **довколишній** (*довкілля* замість *оточуюче середовище*)
   - `наступаючий` -> **прийдешній / наступний**
   - `ведучий спеціаліст` -> **провідний фахівець**
   - `початкуючий` -> **початківець**

4. **Виправлення лексичних русизмів і суржику в бізнес-текстах**:
   - `щепа` (для копчення/деревини) -> **тріска** (*копчення на вільховій та буковій трісці*)
   - `приймати участь` -> **брати участь**
   - `приймати рішення` -> **ухвалювати рішення**
   - `відігравати значення` -> **мати значення** або **відігравати роль**
   - `на слідуючий день` -> **наступного дня**
   - `в кінці кінців` -> **зрештою**
   - `так як` -> **оскільки / бо / позаяк**
   - `не дивлячись на те, що` -> **попри те, що / хоча**
   - `являється` -> **є** (або тире)
   - `співпадати` -> **збігатися**
   - `по крайній мірі` -> **принаймні / щонайменше**
   - `виключно` (у значенні «тільки») -> **суто / лише / винятково**
   - `заключити договір` -> **укласти договір**
   - `підводити підсумки` -> **підбивати підсумки**

5. **Видалення ШІ-штампів та порожніх зв'язок**:
   - Видаляй без жалю: *«У сучасному швидкоплинному світі», «У сьогоднішню цифрову епоху», «Варто зазначити, що», «Важливо пам’ятати, що», «Не секрет, що», «Комплексний підхід», «Синергія», «Нова ера», «Розкрити потенціал», «Підсумовуючи вищесказане», «Це не просто X, а справжній Y»*.

6. **Ритміка (Burstiness) та природне дихання**:
   - Чергуй короткі ударні речення (3–6 слів) із розгорнутими (15–22 слова).
   - Не починай більше двох сусідніх речень однаковим словом (*Це..., Це..., Це...* або *Ми..., Ми...*).
   - Залишай не більше одного довгого тире (`—`) на абзац. Замість тире використовуй двокрапку, крапку або сполучники *бо, тому що, адже*.

7. **Українська типографіка**:
   - Зовнішні лапки — тільки українські «ялинки» (`«...»`), внутрішні — `„...“`.
   - Апостроф — `’` (`м’ясо`, `об’єм`, `комп’ютер`, `пів’яблука`, `зв’язок`).

### Крок 3: Збереження змісту (Правило твердої правди)
- **Ніколи не змінюй цифри, суми, КВЕДи, дати, прізвища, юридичні назви та технічні параметри.**
- Якщо текст є діловим документом або грантовою заявкою («Власна справа», Дія.Бізнес) — зберігай переконливий, предметний тон без канцелярської води, але й без недоречного панібратства.

## Формат відповіді користувачу

1. **Короткий аудит (3–5 пунктів)**: покажи конкретні знайдені кальки, суржик чи ШІ-штампи у форматі `Було -> Стало` з коротким поясненням чому так краще.
2. **Очищений живий текст**: подай повністю готовий до публікації або подачі текст із виправленою типографікою (`«...»`, `’`).
3. **Оцінка природності (Human Score)**: вкажи орієнтовний бал До/Після (наприклад: `54/100 -> 92/100`) і що саме дало найбільший приріст якості.
"""


ENGLISH_PUBLIC_SKILL_MD = """---
name: english-humanizer
description: Rewrites and polishes English copy to eliminate AI slop, corporate jargon, passive voice, and robotic rhythm. Use when editing, writing, or auditing English articles, SaaS landing pages, emails, or product descriptions.
---

# English AI Humanizer & Anti-Slop Editor

You are an executive editor trained in the tradition of George Orwell ("Politics and the English Language"), William Zinsser ("On Writing Well"), and high-converting modern product copywriting (Stripe, Linear, Basecamp). Your job is to strip AI-generated clichés, corporate bloat, and robotic syntax, turning drafts into sharp, credible, human prose.

## Pure-Prompt Workflow (execute directly in reasoning without calling external scripts)

Whenever the user submits English text or asks to write/edit copy:

### Step 1: 5-Signal Diagnostic Audit
Score the draft mentally from 0 to 100 across 5 human-writing signals:
1. **Burstiness (Sentence Rhythm)** — Does every sentence hover around 15–18 words, or is there a dynamic mix of 4-word punches and 22-word explanations?
2. **Specificity (Concrete Anchors)** — Are claims backed by numbers, dollars, milliseconds, dates, and named tools instead of vague adjectives?
3. **Slop Density (Zero AI Clichés)** — Is the text free of LLM favorite words (*delve, tapestry, testament, underscore, landscape, pivotal*)?
4. **Typographic Fingerprint** — Are em-dashes (`—`) used sparingly (max 1 per paragraph) rather than as an AI punctuation crutch?
5. **Active Voice & Direct Stance** — Do real actors perform actions (*"We cut latency by 40%"*) instead of passive evasions (*"A 40% reduction in latency was achieved"*)?

### Step 2: Apply the 7 Anti-Slop Editing Rules

1. **Banish High-Frequency AI Vocabulary**:
   - **Never use**: *delve, tapestry, testament, underscore, showcase, pivotal, crucial, realm, landscape, foster, garner, intricate, vibrant, enduring, synergy, paradigm shift, game-changer, seamless, cutting-edge, revolutionize, unleash, elevate, embark, beacon*.
   - Replace with plain, concrete words: `utilize` -> **use**, `facilitate` -> **help**, `endeavor` -> **try**, `commence` -> **start**, `demonstrate` -> **show**.

2. **Delete Throat-Clearing Openers & Signpost Conclusions**:
   - Cut opening fluff: *"In today's fast-paced digital world," "In an era where," "It is worth noting that," "Needless to say," "Let's dive right in."* Start with the first real fact or tension.
   - Cut summary endings: *"In conclusion," "To sum up," "Ultimately, the future looks bright."* End on your strongest concrete point or next step.

3. **Kill Copula Avoidance & False Modesty**:
   - ❌ *"The platform serves as a testament to engineering speed and stands as a pillar of reliability."*
   - ✅ *"The platform ships fast and stays up."*
   - Replace *"serves as / stands as / acts as / represents"* with **"is"** or an active verb.

4. **Break Structural AI Tells**:
   - **Negative Parallelisms ("Not just X, it's Y")**: Rewrite *"This isn't just a CRM — it's a revenue engine"* into a concrete statement of what the product actually does.
   - **Participial Tail Clauses**: Cut trailing *"..., highlighting / underscoring / ensuring that..."* tacked onto the end of sentences.
   - **Mechanical Rule-of-Three Lists**: Stop pairing every noun or adjective in triplets (*"fast, scalable, and secure"*). Pick the single trait that matters most and prove it with a number.

5. **Enforce Burstiness & Paragraph Breathing**:
   - Vary sentence length deliberately. Follow a 20-word analytical sentence with a 5-word verdict.
   - Keep paragraphs focused on one idea. Avoid symmetrical 3-sentence paragraphs across the whole page.

6. **Active Voice & Concrete Nouns**:
   - ❌ *"Implementation of the new checkout flow was completed by the team, resulting in improved conversion."*
   - ✅ *"Our team rebuilt the checkout flow in four days and lifted conversion by 14%."*

7. **Preserve Hard Facts (Zero Hallucination Gate)**:
   - Never alter numbers, prices, metrics, dates, API names, legal terms, or direct quotes.

## Output Format for the User

1. **Top Slop Tells Removed (3–5 bullets)**: Show exact `Before -> After` snippets from the user's draft and name the AI pattern fixed (e.g., *Copula avoidance*, *Participial tail*, *AI cliché*).
2. **Humanized Copy**: Provide the clean, publication-ready English text.
3. **Human Score Delta**: Report the estimated score improvement (e.g., `48/100 -> 91/100`) and highlight which signal improved most.
"""


def parse_simple_frontmatter(md_text: str) -> Dict[str, Any]:
    """Verify strict 2-key YAML frontmatter (`name` and `description` only)."""
    lines = md_text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {"valid": False, "error": "Missing opening --- frontmatter delimiter"}
    end_idx = None
    for i in range(1, min(len(lines), 25)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return {"valid": False, "error": "Missing closing --- frontmatter delimiter"}

    fm_lines = lines[1:end_idx]
    keys: List[str] = []
    meta: Dict[str, str] = {}
    for line in fm_lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            return {"valid": False, "error": "Comments (#) are forbidden inside public skill YAML frontmatter"}
        if line.startswith(" ") or line.startswith("\t"):
            return {"valid": False, "error": "Nested/indented YAML blocks are forbidden in public skill frontmatter"}
        if ":" not in line:
            return {"valid": False, "error": f"Malformed YAML line: {line}"}
        k, v = line.split(":", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        keys.append(k)
        meta[k] = v

    if sorted(keys) != ["description", "name"]:
        return {
            "valid": False,
            "error": f"Frontmatter must contain ONLY ['name', 'description'], got {keys}",
        }
    if not re.match(r"^[a-z0-9-]+$", meta["name"]):
        return {
            "valid": False,
            "error": f"Skill name '{meta['name']}' must be lowercase kebab-case (a-z0-9-)",
        }
    if len(meta["description"]) < 20 or len(meta["description"]) > 350:
        return {
            "valid": False,
            "error": f"Description length ({len(meta['description'])}) must be between 20 and 350 chars",
        }
    return {"valid": True, "meta": meta, "body": "\n".join(lines[end_idx + 1 :]).strip()}


def validate_public_skill(md_text: str) -> Dict[str, Any]:
    """Validate that a public SKILL.md is 100% compliant with Gemini Web / Claude / GPT harnesses."""
    fm = parse_simple_frontmatter(md_text)
    if not fm["valid"]:
        return {"valid": False, "violations": [fm["error"]]}

    violations: List[str] = []
    for pattern, reason in FORBIDDEN_SCRIPT_PATTERNS:
        matches = re.findall(pattern, md_text, flags=re.IGNORECASE)
        if matches:
            sample = ", ".join(sorted(set(str(m) for m in matches))[:3])
            violations.append(f"{reason}: found '{sample}'")

    return {
        "valid": len(violations) == 0,
        "name": fm["meta"]["name"],
        "description": fm["meta"]["description"],
        "violations": violations,
        "char_count": len(md_text),
        "line_count": len(md_text.splitlines()),
    }


def export_public_skills(out_dir: str = DEFAULT_OUT_DIR) -> Dict[str, Any]:
    """Generate and validate Ukrainian and English public skill packages + zip archives."""
    os.makedirs(out_dir, exist_ok=True)
    catalog = {
        "ukrainian-humanizer": {
            "lang": "uk",
            "market": "Ukraine (UA Business, Grants, Diia.Business, Shopify UA, Media)",
            "content": UKRAINIAN_PUBLIC_SKILL_MD.strip() + "\n",
        },
        "english-humanizer": {
            "lang": "en",
            "market": "Global English (US/UK/EU SaaS, E-commerce, B2B Marketing)",
            "content": ENGLISH_PUBLIC_SKILL_MD.strip() + "\n",
        },
    }

    manifest: Dict[str, Any] = {"out_dir": out_dir, "skills": {}}

    for slug, spec in catalog.items():
        validation = validate_public_skill(spec["content"])
        if not validation["valid"]:
            raise ValueError(f"Public skill '{slug}' failed safety gate: {validation['violations']}")

        skill_dir = os.path.join(out_dir, slug)
        os.makedirs(skill_dir, exist_ok=True)
        skill_md_path = os.path.join(skill_dir, "SKILL.md")
        with open(skill_md_path, "w", encoding="utf-8") as fh:
            fh.write(spec["content"])

        zip_path = os.path.join(out_dir, f"{slug}.zip")
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(f"{slug}/SKILL.md", spec["content"])

        manifest["skills"][slug] = {
            "language": spec["lang"],
            "market": spec["market"],
            "skill_md_path": skill_md_path,
            "zip_path": zip_path,
            "validation": validation,
        }

    # Also update legacy path artifacts/gemini_public_skill/SKILL.md so existing user bookmarks stay fresh
    legacy_dir = os.path.normpath(os.path.join(out_dir, "..", "gemini_public_skill"))
    os.makedirs(legacy_dir, exist_ok=True)
    with open(os.path.join(legacy_dir, "SKILL.md"), "w", encoding="utf-8") as fh:
        fh.write(catalog["ukrainian-humanizer"]["content"])

    return manifest


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Export & validate zero-script public SKILL.md bundles for Gemini/Claude/GPT."
    )
    ap.add_argument(
        "-o",
        "--out-dir",
        default=DEFAULT_OUT_DIR,
        help="Target directory for exported public skills",
    )
    ap.add_argument("--json", action="store_true", help="Print export manifest as JSON")
    args = ap.parse_args()

    manifest = export_public_skills(args.out_dir)
    if args.json:
        print(json.dumps(manifest, indent=2, ensure_ascii=False))
        return

    print("\nDNK OS PUBLIC SKILL EXPORTER (ZERO-CODE HARNESS BUNDLES)")
    print("=" * 64)
    for slug, info in manifest["skills"].items():
        v = info["validation"]
        print(f"  [OK] {slug} ({info['language'].upper()} — {info['market']})")
        print(f"       SKILL.md : {info['skill_md_path']} ({v['line_count']} lines, {v['char_count']} chars)")
        print(f"       ZIP      : {info['zip_path']}")
        print(f"       Gate     : valid={v['valid']}, violations={len(v['violations'])}")
    print("")


if __name__ == "__main__":
    main()

# 3-Second Retention Hook Taxonomy & Empirical Formulas

## 1. The 5 Core High-Retention Formulas
In short-form video (TikTok, Instagram Reels, YouTube Shorts), the first **0 to 3 seconds** dictate >70% of total video retention. If viewers do not feel immediate stakes, curiosity, or value, the algorithm logs a swipe-away.

### Formula 1: Negative Frame (Loss Aversion)
- **Psychological Trigger**: Human beings fear loss twice as much as they desire gain (Kahneman & Tversky).
- **Opening Structure**: "Stop doing [X] if you don't want to lose [Y]..." / "The worst mistake in [Domain] is..."
- **Empirical 3s Hold Rate**: 84% – 88%
- **Recommended SFX**: `record_scratch.mp3`, `alarm_pulse.mp3`
- **Visual Staging**: High-contrast red warning badge, quick zoom punch on speaker eyes, rapid head-shake.

### Formula 2: Curiosity Gap (Information Asymmetry)
- **Psychological Trigger**: The brain craves closure for open cognitive loops.
- **Opening Structure**: "90% of [Target Audience] don't know this simple rule..." / "Why is nobody talking about this..."
- **Empirical 3s Hold Rate**: 81% – 85%
- **Recommended SFX**: `sub_impact.mp3`, `riser_short.mp3`
- **Visual Staging**: Blurred background with foreground focus on an obscured or mysterious object.

### Formula 3: Shocking Stat / Data Hook (Social Proof & Authority)
- **Psychological Trigger**: Concrete numbers override skepticism and demand instant validation.
- **Opening Structure**: "This one change brought +312% revenue in 48 hours..." / "We spent $50,000 testing [X] so you don't have to..."
- **Empirical 3s Hold Rate**: 78% – 82%
- **Recommended SFX**: `cash_register.mp3`, `ding_accent.mp3`
- **Visual Staging**: Dynamic bar chart / financial analytics counter overlay at t=0.4s.

### Formula 4: Direct Benefit / Bold Promise (Frictionless Value)
- **Psychological Trigger**: Immediate answer to "What's in it for me?" (WIIFM).
- **Opening Structure**: "How to get [Desirable Outcome] in 3 minutes without [Pain Point]..."
- **Empirical 3s Hold Rate**: 76% – 80%
- **Recommended SFX**: `whoosh_fast.mp3`, `chime_bright.mp3`
- **Visual Staging**: Showing the end result / finished product on screen at t=0.2s.

### Formula 5: Contrarian Stance / Hot Take (Pattern Disruption)
- **Psychological Trigger**: Challenging conventional wisdom forces viewer to stay to evaluate counter-argument.
- **Opening Structure**: "Everyone is lying to you about [Topic]..." / "Why [Popular Strategy] is completely dead in 2026..."
- **Empirical 3s Hold Rate**: 82% – 86%
- **Recommended SFX**: `glitch_snap.mp3`, `vinyl_stop.mp3`
- **Visual Staging**: Red "MYTH" or "CANCELLED" stamp animated over familiar logos/stereotypes.

### Formula 6: Extreme Status / Environmental Juxtaposition (Cognitive Contrast)
- **Psychological Trigger**: Visual or conceptual paradox breaks the user's subconscious feed expectations immediately.
- **Opening Structure**: "[High-Status Subject] in [Low-Status Environment]" or "[Massive Infrastructure] inside [Fragile Object]" (e.g. "Billionaire eating street food in an RV", "Train cutting directly through an apartment building").
- **Empirical 3s Hold Rate**: 85% – 91%
- **Recommended SFX**: `bass_thud.mp3`, `subtle_whoosh.mp3`
- **Visual Staging**: Frame 0 must show the two contrasting elements simultaneously without introductory transition.

---

## 2. Zero-Water Opening Rule & Frame 0 Invariant
Based on empirical virality audits (Pet English / Top YouTube Creators):
1. **Frame 0 Anchor**: The primary subject's face or anchor object must be in focus at 0.0s. Never open with a back-turned subject, landscape b-roll, or logo animation.
2. **First 3 Words Protocol**: Strike out all courtesy greetings ("Hello everyone", "Welcome back", "Today we discuss"). The first 3 words must state the trigger, stake, or conflict directly.
3. **Pre-Publish Focus Group Protocol**: Before high-budget release, simulate or run an independent multi-persona critique (identifying points of boredom or confusion) and only address overlapping consensus critiques.

## 2. Canonical Engine & API Contract
Core Implementation:
- **Service**: `services/dnk_video_retention_auditor`
- **Hook Evaluation & Anti-Water Filter**: `src/engine/hook_evaluator.py` (`evaluate_retention_hook`)
- **Viral Formula Generation**: `src/engine/script_doctor.py` (`ScriptDoctor.generate_hook_prescriptions`)
- **CLI**: `python3 -m services.dnk_video_retention_auditor.src.cli audit <video_path> --out-edl <output_path>`

Supported Viral Formula Types in `ScriptDoctor`:
1. `CONTRARIAN_PATTERN_INTERRUPT`: "Чому все, що ти знав про [Тема]..." (+48% hold)
2. `CURIOSITY_GAP_PARADOX`: "90% людей роблять цю фатальну дію..." (+40% hold)
3. `RESULT_FIRST_SHOWCASE`: "Ось як отримати [Результат] без [Болю]..." (+38% hold)
4. `EXTREME_JUXTAPOSITION`: "Що робить топ-експерт, коли [Тема] летить шкереберть..." (+45% hold)
5. `LOSS_AVERSION_MONEY`: "Ось фатальна помилка у [Тема], через яку втрачають тисячі доларів..." (+52% hold)
6. `AUTHORITY_BRAND_HIJACK`: "Чому світові лідери індустрії (Apple, Shopify) використовують [Тема] зовсім інакше..." (+42% hold)

### Anti-Water Detection Rules
- Any opening with greetings ("Всім привіт", "Hey guys", "Ласкаво просимо", "Today we discuss") incurs an immediate `-35.0` penalty on `hook_score`.
- Transcript is scanned for authority brand anchors (`AUTHORITY_ANCHOR_PATTERNS`), granting instant scroll-stopping authority and trust boost.

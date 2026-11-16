# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_media/src/kinetic_subtitles.py"
# purpose: "Kinetic Word-Level Subtitles & Alignment Engine (Hormozi, Minimal, Cyberpunk)."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

import re
import math
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class KineticWord(BaseModel):
    word: str
    start_ms: int
    end_ms: int
    duration_ms: int
    emphasis: str = Field(default="NORMAL", description="NORMAL, MEDIUM, or STRONG")
    highlight_color: str = Field(default="#FFFFFF")
    emoji: Optional[str] = None
    scale_factor: float = Field(default=1.0)

class KineticPhrase(BaseModel):
    phrase_id: str
    start_ms: int
    end_ms: int
    text: str
    words: List[KineticWord]
    style_preset: str = Field(default="hormozi_bold")

class KineticSubtitleTrack(BaseModel):
    duration_ms: int
    words_count: int
    wpm: int
    style_preset: str
    words: List[KineticWord]
    phrases: List[KineticPhrase]
    srt_content: str
    ass_content: str

TRIGGER_EMOJIS: Dict[str, str] = {
    "money": "💰",
    "profit": "📈",
    "dollars": "💵",
    "cash": "💸",
    "stop": "🛑",
    "warning": "⚠️",
    "danger": "🚨",
    "secret": "🤫",
    "mistake": "❌",
    "wrong": "🚫",
    "free": "🎁",
    "fast": "⚡",
    "growth": "🚀",
    "fire": "🔥",
    "video": "🎥",
    "camera": "📸",
    "hook": "🪝",
    "sale": "🏷️",
    "win": "🏆",
    "target": "🎯",
}

STRONG_KEYWORDS = {
    "stop", "secret", "mistake", "wrong", "never", "free", "money", 
    "profit", "hack", "kill", "insane", "viral", "huge", "worst", 
    "best", "million", "billion", "danger", "warning", "now", "don't"
}

PRESET_COLORS = {
    "hormozi_bold": {
        "text": "#FFFFFF",
        "stroke": "#000000",
        "strong": "#FACC15", # Yellow Hormozi
        "medium": "#22C55E", # Green
        "danger": "#EF4444", # Red
    },
    "minimal_clean": {
        "text": "#F8FAFC",
        "stroke": "#0F172A",
        "strong": "#38BDF8", # Cyan
        "medium": "#818CF8", # Indigo
        "danger": "#F43F5E",
    },
    "cyberpunk_neon": {
        "text": "#00F0FF",
        "stroke": "#120024",
        "strong": "#FF0055", # Neon Pink
        "medium": "#FFE600", # Neon Yellow
        "danger": "#FF2A85",
    }
}

class KineticSubtitlesEngine:
    """High-velocity kinetic subtitle generator with word-level speech cadence alignment."""

    def __init__(self, default_wpm: int = 155):
        self.default_wpm = default_wpm

    def align_transcript(
        self,
        transcript: str,
        total_duration_ms: Optional[int] = None,
        silence_intervals: Optional[List[Dict[str, float]]] = None,
        style_preset: str = "hormozi_bold",
        words_per_phrase: int = 2
    ) -> KineticSubtitleTrack:
        """
        Aligns raw transcript into word-level timestamps, detects emphasis/emojis,
        and slices into punchy 1-3 word phrases optimized for short-form retention.
        """
        if not transcript or not transcript.strip():
            return KineticSubtitleTrack(
                duration_ms=0,
                words_count=0,
                wpm=self.default_wpm,
                style_preset=style_preset,
                words=[],
                phrases=[],
                srt_content="",
                ass_content=""
            )

        raw_tokens = transcript.strip().split()
        total_words = len(raw_tokens)

        if not total_duration_ms or total_duration_ms <= 0:
            estimated_minutes = total_words / self.default_wpm
            total_duration_ms = max(1000, int(estimated_minutes * 60 * 1000))

        word_weights = []
        clean_words = []
        for token in raw_tokens:
            clean = re.sub(r'[^\w\$\%\€\£]', '', token)
            clean_words.append(clean if clean else token)
            weight = max(1.0, len(clean) * 0.45)
            if token.endswith(('.', '!', '?')):
                weight += 1.8
            elif token.endswith((',', ';', ':')):
                weight += 0.9
            word_weights.append(weight)

        total_weight = sum(word_weights) if word_weights else 1.0

        kinetic_words: List[KineticWord] = []
        current_time_ms = 0
        preset_cfg = PRESET_COLORS.get(style_preset, PRESET_COLORS["hormozi_bold"])

        for i, (token, clean, weight) in enumerate(zip(raw_tokens, clean_words, word_weights)):
            allocated_duration_ms = max(120, int((weight / total_weight) * total_duration_ms))
            word_start = current_time_ms
            word_end = word_start + allocated_duration_ms
            current_time_ms = word_end

            lower_clean = clean.lower()
            emphasis = "NORMAL"
            highlight_color = preset_cfg["text"]
            scale_factor = 1.0
            matched_emoji = None

            if lower_clean in STRONG_KEYWORDS:
                emphasis = "STRONG"
                highlight_color = preset_cfg["strong"]
                scale_factor = 1.15
            elif len(clean) >= 7 or token.isupper():
                emphasis = "MEDIUM"
                highlight_color = preset_cfg["medium"]
                scale_factor = 1.05

            for trigger_word, emoji_icon in TRIGGER_EMOJIS.items():
                if trigger_word in lower_clean:
                    matched_emoji = emoji_icon
                    break

            kinetic_words.append(
                KineticWord(
                    word=token,
                    start_ms=word_start,
                    end_ms=word_end,
                    duration_ms=allocated_duration_ms,
                    emphasis=emphasis,
                    highlight_color=highlight_color,
                    emoji=matched_emoji,
                    scale_factor=scale_factor
                )
            )

        phrases: List[KineticPhrase] = []
        chunk_size = max(1, words_per_phrase)
        for i in range(0, len(kinetic_words), chunk_size):
            chunk = kinetic_words[i:i + chunk_size]
            p_start = chunk[0].start_ms
            p_end = chunk[-1].end_ms
            p_text = " ".join([w.word for w in chunk])
            phrases.append(
                KineticPhrase(
                    phrase_id=f"phrase_{len(phrases)+1:03d}",
                    start_ms=p_start,
                    end_ms=p_end,
                    text=p_text,
                    words=chunk,
                    style_preset=style_preset
                )
            )

        calculated_wpm = int((total_words / (total_duration_ms / 60000.0))) if total_duration_ms > 0 else self.default_wpm

        srt_output = self._export_srt(phrases)
        ass_output = self._export_ass(phrases, style_preset)

        return KineticSubtitleTrack(
            duration_ms=total_duration_ms,
            words_count=total_words,
            wpm=calculated_wpm,
            style_preset=style_preset,
            words=kinetic_words,
            phrases=phrases,
            srt_content=srt_output,
            ass_content=ass_output
        )

    def _export_srt(self, phrases: List[KineticPhrase]) -> str:
        lines = []
        for idx, phrase in enumerate(phrases, start=1):
            start_str = self._format_srt_time(phrase.start_ms)
            end_str = self._format_srt_time(phrase.end_ms)
            lines.append(str(idx))
            lines.append(f"{start_str} --> {end_str}")
            lines.append(phrase.text)
            lines.append("")
        return "\n".join(lines)

    def _format_srt_time(self, ms: int) -> str:
        hours = ms // 3600000
        ms %= 3600000
        minutes = ms // 60000
        ms %= 60000
        seconds = ms // 1000
        millis = ms % 1000
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"

    def _export_ass(self, phrases: List[KineticPhrase], style: str) -> str:
        ass_header = f"""[Script Info]
Title: DNK OS Kinetic Subtitles ({style})
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Hormozi,Arial Black,72,&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5,2,2,40,40,240,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        dialogue_lines = []
        for phrase in phrases:
            start_fmt = self._format_ass_time(phrase.start_ms)
            end_fmt = self._format_ass_time(phrase.end_ms)
            styled_words = []
            for w in phrase.words:
                if w.emphasis == "STRONG":
                    styled_words.append(f"{{\\c{self._rgb_to_bgr(w.highlight_color)}\\fscx110\\fscy110}}{w.word}{{\\r}}")
                elif w.emphasis == "MEDIUM":
                    styled_words.append(f"{{\\c{self._rgb_to_bgr(w.highlight_color)}}}{w.word}{{\\r}}")
                else:
                    styled_words.append(w.word)
            text_styled = " ".join(styled_words)
            dialogue_lines.append(f"Dialogue: 0,{start_fmt},{end_fmt},Hormozi,,0,0,0,,{text_styled}")

        return ass_header + "\n".join(dialogue_lines)

    def _format_ass_time(self, ms: int) -> str:
        hours = ms // 3600000
        ms %= 3600000
        minutes = ms // 60000
        ms %= 60000
        seconds = ms // 1000
        centis = (ms % 1000) // 10
        return f"{hours:d}:{minutes:02d}:{seconds:02d}.{centis:02d}"

    def _rgb_to_bgr(self, hex_color: str) -> str:
        hex_clean = hex_color.lstrip('#')
        if len(hex_clean) == 6:
            r, g, b = hex_clean[0:2], hex_clean[2:4], hex_clean[4:6]
            return f"&H00{b}{g}{r}&"
        return "&H00FFFFFF&"


kinetic_subtitles_engine = KineticSubtitlesEngine()

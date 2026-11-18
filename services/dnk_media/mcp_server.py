# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_media/mcp_server.py"
# purpose: "FastMCP Server for dnk_media Sovereign Brick"
# canonical_source: true
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK Swarm & Antigravity"
# --- END DNK-MRH-HEADER ---

import asyncio
import json
from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
from services.dnk_media.src.service import (
    cut_silence,
    reframe_smart,
    generate_kinetic_subtitles,
    compose_sound_design,
    process_data,
    sign_provenance,
    verify_provenance,
    synthesize_ecommerce_alt,
    generate_social_card,
    generate_schema_org_json_ld,
    generate_opengraph_tags,
    generate_serp_dominator_graph,
)
from core.adapters.dnk_agentic_video_adapter import (
    DNKAgenticVideoAdapter,
    ProcessingMode,
    fetch_youtube_transcript,
)

mcp = FastMCP("dnk_media")


@mcp.tool()
def media_cut_silence(
    words: List[Dict[str, Any]],
    total_duration_ms: int,
    min_silence_ms: int = 400,
    padding_ms: int = 70
) -> Dict[str, Any]:
    """Detect dead air gaps and return jump-cut interval plan and FFmpeg select filters."""
    plan = cut_silence(words, total_duration_ms, min_silence_ms, padding_ms)
    return plan.model_dump()


@mcp.tool()
def media_smart_reframe(
    original_width: int = 1920,
    original_height: int = 1080,
    duration_ms: int = 5000
) -> Dict[str, Any]:
    """Calculate 9:16 vertical crop with smooth speaker face centering."""
    plan = reframe_smart(original_width, original_height, None, duration_ms)
    return plan.model_dump()


@mcp.tool()
def media_kinetic_subtitles(
    transcript: str,
    total_duration_ms: Optional[int] = None,
    style_preset: str = "hormozi_bold",
    words_per_phrase: int = 2
) -> Dict[str, Any]:
    """Generate word-level kinetic subtitles in Hormozi style (ASS and SRT)."""
    track = generate_kinetic_subtitles(transcript, total_duration_ms, style_preset, words_per_phrase)
    return track.model_dump()


@mcp.tool()
def media_sound_design(
    video_duration_s: float,
    music_preset: str = "electronic_pulse"
) -> Dict[str, Any]:
    """Compose audio ducking keyframes and synchronous SFX timeline."""
    from services.dnk_media.src.sound_design import DuckingSettings
    plan = compose_sound_design(video_duration_s, custom_settings=DuckingSettings(music_preset=music_preset))
    return plan.model_dump()


@mcp.tool()
def media_fetch_youtube_transcript(
    url_or_video_id: str,
    languages: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Fetch structured transcript from YouTube without downloading video bytes."""
    res = fetch_youtube_transcript(url_or_video_id, languages=languages)
    return res.model_dump()


@mcp.tool()
async def media_analyze_youtube(
    video_url: str,
    prompt: str = "Analyze key points and moments",
    mode: str = "agentic",
) -> Dict[str, Any]:
    """Analyze YouTube video using Gemini 3.8 Agentic Video Understanding (dynamic zooming, 88% token reduction)."""
    adapter = DNKAgenticVideoAdapter()
    proc_mode = ProcessingMode.AGENTIC if mode.lower() == "agentic" else ProcessingMode.STATIC
    res = await adapter.analyze_video(video_url, prompt=prompt, mode=proc_mode)
    return res.model_dump()


@mcp.tool()
async def media_retrieve_video_moments(
    video_url: str,
    target_description: str,
) -> List[Dict[str, Any]]:
    """Pinpoint exact start and end timestamps (MM:SS) for key actions or moments in video."""
    adapter = DNKAgenticVideoAdapter()
    moments = await adapter.retrieve_moments(video_url, target_description)
    return [m.model_dump() for m in moments]


@mcp.tool()
async def media_generate_video_chapters(
    video_url: str,
) -> List[Dict[str, Any]]:
    """Generate structured semantic video chapters with timestamps and summaries."""
    adapter = DNKAgenticVideoAdapter()
    chapters = await adapter.generate_smart_chapters(video_url)
    return [c.model_dump() for c in chapters]


@mcp.tool()
async def media_extract_video_insights(
    video_url: str,
    focus_query: str = "Key ideas, architectural insights, and actionable thoughts",
) -> Dict[str, Any]:
    """Extract core thesis, key architectural ideas, actionable takeaways, and moments from video."""
    adapter = DNKAgenticVideoAdapter()
    return await adapter.extract_actionable_insights(video_url, focus_query=focus_query)


@mcp.tool()
async def media_benchmark_video_sota(
    topic: str,
    video_diamond: str,
    video_source_url: str = "",
) -> Dict[str, Any]:
    """Benchmark a video diamond against active SOTA leaders as of today and synthesize DNK adaptation."""
    from core.orchestrator.video_sota_research_bridge import VideoSotaResearchBridge
    bridge = VideoSotaResearchBridge()
    res = await bridge.benchmark_video_diamond(topic, video_diamond, video_source_url=video_source_url)
    return res.model_dump()


@mcp.tool()
def media_sign_provenance(
    image_path: str,
    author_name: str = "DNK-e.com",
    author_url: str = "https://dnk-e.com",
    copyright_notice: Optional[str] = None,
    watermark_payload: Optional[str] = None,
    alt_text_uk: Optional[str] = None,
    alt_text_en: Optional[str] = None,
    seo_keywords: Optional[List[str]] = None,
    price: Optional[str] = None,
    currency: str = "UAH",
    usp: Optional[str] = None,
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Sign media file with C2PA manifest, multilingual Alt text, SEO & rich metadata (DEC-143)."""
    res = sign_provenance(
        image_path=image_path,
        author_name=author_name,
        author_url=author_url,
        copyright_notice=copyright_notice,
        watermark_payload=watermark_payload,
        alt_text_uk=alt_text_uk,
        alt_text_en=alt_text_en,
        seo_keywords=seo_keywords,
        price=price,
        currency=currency,
        usp=usp,
        output_path=output_path,
    )
    return res.model_dump()


@mcp.tool()
def media_generate_social_card(
    product_title: str,
    price: str,
    currency: str = "UAH",
    brand: str = "DNK",
    in_stock: bool = True,
    usp: Optional[str] = None,
    image_path: Optional[str] = None,
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a luxury 1200x630 social preview card (SVG) with OpenGraph and JSON-LD."""
    res = generate_social_card(
        product_title=product_title,
        price=price,
        currency=currency,
        brand=brand,
        in_stock=in_stock,
        usp=usp,
        image_path=image_path,
        output_path=output_path,
    )
    return res.model_dump()


@mcp.tool()
def media_generate_jsonld(
    product_title: str,
    price: str,
    currency: str = "UAH",
    brand: str = "DNK",
    in_stock: bool = True,
    description: Optional[str] = None,
    image_url: Optional[str] = None,
    sku: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate Schema.org Product+Offer JSON-LD structured data for Google & AI search bots."""
    return generate_schema_org_json_ld(
        product_title=product_title,
        price=price,
        currency=currency,
        brand=brand,
        in_stock=in_stock,
        description=description,
        image_url=image_url,
        sku=sku,
    )


@mcp.tool()
def media_generate_serp_graph(
    product_title: str,
    price: str,
    currency: str = "UAH",
    brand: str = "DNK",
    in_stock: bool = True,
    description: Optional[str] = None,
    image_url: Optional[str] = None,
    sku: Optional[str] = None,
    breadcrumbs: Optional[List[List[Optional[str]]]] = None,
    faqs: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """Generate unified Schema.org @graph (Product + BreadcrumbList + FAQPage) for SERP dominance."""
    bc_tuples = [(b[0], b[1]) for b in (breadcrumbs or []) if len(b) >= 2]
    return generate_serp_dominator_graph(
        product_title=product_title,
        price=price,
        currency=currency,
        brand=brand,
        in_stock=in_stock,
        description=description,
        image_url=image_url,
        sku=sku,
        breadcrumbs=bc_tuples if bc_tuples else None,
        faqs=faqs,
    )


@mcp.tool()
def media_synthesize_alt_text(
    product_title: str,
    color: Optional[str] = None,
    material: Optional[str] = None,
    brand: str = "DNK",
    category: Optional[str] = None,
) -> Dict[str, str]:
    """Synthesize W3C WCAG 2.2 compliant bilingual Alt text pairs (<125 chars) for UK & EN markets."""
    uk, en = synthesize_ecommerce_alt(
        product_title=product_title,
        color=color,
        material=material,
        brand=brand,
        category=category,
    )
    return {
        "alt_text_uk": uk,
        "alt_text_en": en,
        "char_count_uk": len(uk),
        "char_count_en": len(en),
    }


@mcp.tool()
def media_verify_provenance(
    image_path: str,
    expected_author: Optional[str] = None,
) -> Dict[str, Any]:
    """Verify C2PA manifest, metadata chunks and authorship of a media asset (DEC-143)."""
    res = verify_provenance(image_path=image_path, expected_author=expected_author)
    return res.model_dump()


@mcp.tool()
def media_compose_video_9_16(
    transcript: str,
    source_video_path: Optional[str] = None,
    duration_ms: Optional[int] = None,
    style_preset: str = "hormozi_bold",
    enable_silence_cut: bool = True,
    enable_smart_reframe: bool = True,
    enable_sound_design: bool = True,
    output_path: Optional[str] = None,
    dry_run: bool = True
) -> Dict[str, Any]:
    """Harmonizes kinetic subtitles, smart reframing, dead-air jump cuts, and audio into 9:16 video."""
    from services.dnk_media.src.service import compose_video_9_16
    res = compose_video_9_16(
        transcript=transcript,
        source_video_path=source_video_path,
        duration_ms=duration_ms,
        style_preset=style_preset,
        enable_silence_cut=enable_silence_cut,
        enable_smart_reframe=enable_smart_reframe,
        enable_sound_design=enable_sound_design,
        output_path=output_path,
        dry_run=dry_run
    )
    return res.model_dump()


@mcp.tool()
def execute(query: str) -> str:
    """Fallback query execution."""
    return process_data(query)


if __name__ == "__main__":
    mcp.run()

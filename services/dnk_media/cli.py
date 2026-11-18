# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_media/cli.py"
# purpose: "Standalone CLI for dnk_media Sovereign Brick"
# canonical_source: true
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-17"
# author: "DNK Swarm & Antigravity"
# --- END DNK-MRH-HEADER ---

import sys
import json
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
)


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m services.dnk_media.cli [subtitles|reframe|silence|sound|sign|verify|audit|synthesize-alt|social-card|jsonld|process] <args>")
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == "subtitles":
        text = sys.argv[2] if len(sys.argv) > 2 else "Stop making this huge mistake right now"
        track = generate_kinetic_subtitles(text)
        print(f"Generated {track.words_count} kinetic words in {track.duration_ms}ms ({track.wpm} WPM)")
        print("\n--- SRT Preview ---")
        print("\n".join(track.srt_content.splitlines()[:12]))
    elif cmd == "reframe":
        plan = reframe_smart(1920, 1080, duration_ms=5000)
        print(f"Reframed 1920x1080 -> {plan.target_width}x{plan.target_height}")
        print(f"FFmpeg filter: {plan.ffmpeg_filter}")
    elif cmd == "silence":
        sample_words = [
            {"start_ms": 500, "end_ms": 1200, "word": "Hello"},
            {"start_ms": 2500, "end_ms": 3200, "word": "World"},
        ]
        plan = cut_silence(sample_words, total_duration_ms=4000)
        print(f"Saved {plan.saved_duration_ms}ms ({plan.retention_boost_estimate_pct}% retention boost)")
        print(f"Kept segments: {len(plan.keep_segments)}")
    elif cmd == "sound":
        plan = compose_sound_design(video_duration_s=15.0)
        print(f"Soundtrack preset: {plan.music_preset.title} | SFX Cues: {len(plan.sfx_timeline)}")
    elif cmd == "sign":
        if len(sys.argv) < 3:
            print("Usage: python -m services.dnk_media.cli sign <image_path> [author_name] [alt_uk] [alt_en]")
            sys.exit(1)
        path = sys.argv[2]
        author = sys.argv[3] if len(sys.argv) > 3 else "DNK-e.com"
        alt_uk = sys.argv[4] if len(sys.argv) > 4 else None
        alt_en = sys.argv[5] if len(sys.argv) > 5 else None
        try:
            res = sign_provenance(
                image_path=path,
                author_name=author,
                alt_text_uk=alt_uk,
                alt_text_en=alt_en,
            )
            print(f"✓ Signed: {res.signed_asset_path} (Mode: {res.c2pa_mode})")
            print(f"  SHA256: {res.asset_sha256[:16]}...")
            if res.alt_text_uk:
                print(f"  Alt-UK: {res.alt_text_uk}")
            if res.alt_text_en:
                print(f"  Alt-EN: {res.alt_text_en}")
            if res.manifest_path:
                print(f"  Manifest: {res.manifest_path}")
        except Exception as e:
            print(f"✗ Signing failed: {e}")
            sys.exit(1)
    elif cmd == "verify":
        if len(sys.argv) < 3:
            print("Usage: python -m services.dnk_media.cli verify <image_path> [expected_author]")
            sys.exit(1)
        path = sys.argv[2]
        author = sys.argv[3] if len(sys.argv) > 3 else None
        res = verify_provenance(image_path=path, expected_author=author)
        status_icon = "✓" if res.valid else "✗"
        print(f"{status_icon} Verified: {res.message}")
        print(f"  Detected Author: {res.detected_author or 'None'}")
        if res.detected_alt_uk:
            print(f"  Detected Alt-UK: {res.detected_alt_uk}")
        if res.detected_alt_en:
            print(f"  Detected Alt-EN: {res.detected_alt_en}")
        print(f"  Mode: {res.c2pa_mode}")
    elif cmd == "synthesize-alt":
        if len(sys.argv) < 3:
            print("Usage: python -m services.dnk_media.cli synthesize-alt <title> [color] [material] [brand]")
            sys.exit(1)
        title = sys.argv[2]
        color = sys.argv[3] if len(sys.argv) > 3 else None
        material = sys.argv[4] if len(sys.argv) > 4 else None
        brand = sys.argv[5] if len(sys.argv) > 5 else "DNK"
        uk, en = synthesize_ecommerce_alt(product_title=title, color=color, material=material, brand=brand)
        print(f"🇺🇦 UK Alt: {uk} ({len(uk)} chars)")
        print(f"🇬🇧 EN Alt: {en} ({len(en)} chars)")
    elif cmd == "audit":
        from pathlib import Path
        if len(sys.argv) < 3:
            print("Usage: python -m services.dnk_media.cli audit <image_path>")
            sys.exit(1)
        target = Path(sys.argv[2])
        if not target.exists():
            print(f"✗ File not found: {target}")
            sys.exit(1)

        from services.dnk_media.src.provenance import ProvenanceEngine
        from packages.plugins.dnk_aperisolve_forensics.adapter import AperiSolveAdapter

        fmt = ProvenanceEngine.detect_format(target)
        sha, size_bytes = ProvenanceEngine.compute_sha256(target)
        print(f"🔍 FORENSIC AUDIT: {target.name}")
        print(f"  Format:   {fmt.upper()} ({size_bytes:,} bytes)")
        print(f"  SHA-256:  {sha}")

        # 1. Embedded Metadata / Stego Chunks
        if fmt == "png":
            chunks = ProvenanceEngine.extract_png_metadata(target)
            print(f"  PNG Metadata Chunks ({len(chunks)} found):")
            for k, v in chunks.items():
                print(f"    - {k}: {v}")
            if not chunks:
                print("    - (No tEXt metadata chunks embedded)")

        # 2. C2PA Sidecar
        sidecar = target.with_suffix(f"{target.suffix}.c2pa.json")
        if sidecar.exists():
            print(f"  ✓ C2PA Sidecar Manifest Present: {sidecar.name}")
        else:
            print("  ℹ C2PA Sidecar: None detected")

        # 3. AperiSolve Forensics Engine Bridge Status
        aperi = AperiSolveAdapter()
        if aperi.is_available():
            print(f"  🟢 AperiSolve Forensics Bridge: Connected & Ready (Vibe: {aperi.vibe_dir.name})")
        else:
            print("  ⚠️ AperiSolve Forensics Bridge: Not hydrated (Run 'just hydrate-vibe' to provision)")
    elif cmd == "social-card":
        if len(sys.argv) < 4:
            print("Usage: python -m services.dnk_media.cli social-card <title> <price> [currency] [brand] [usp] [output_path]")
            sys.exit(1)
        title = sys.argv[2]
        price = sys.argv[3]
        currency = sys.argv[4] if len(sys.argv) > 4 else "UAH"
        brand = sys.argv[5] if len(sys.argv) > 5 else "DNK"
        usp = sys.argv[6] if len(sys.argv) > 6 else None
        output_path = sys.argv[7] if len(sys.argv) > 7 else None
        card = generate_social_card(
            product_title=title,
            price=price,
            currency=currency,
            brand=brand,
            usp=usp,
            output_path=output_path,
        )
        print(f"✓ Social Card Generated: {card.width}x{card.height}")
        if card.output_path:
            print(f"  Saved to: {card.output_path}")
        print("\n--- OpenGraph Meta Tags Preview ---")
        print("\n".join(card.opengraph_html.splitlines()[:6]))
        print("\n--- Schema.org JSON-LD Snippet ---")
        print(json.dumps(card.json_ld, indent=2, ensure_ascii=False)[:300] + "...")
    elif cmd == "jsonld":
        if len(sys.argv) < 4:
            print("Usage: python -m services.dnk_media.cli jsonld <title> <price> [currency] [brand]")
            sys.exit(1)
        title = sys.argv[2]
        price = sys.argv[3]
        currency = sys.argv[4] if len(sys.argv) > 4 else "UAH"
        brand = sys.argv[5] if len(sys.argv) > 5 else "DNK"
        data = generate_schema_org_json_ld(
            product_title=title,
            price=price,
            currency=currency,
            brand=brand,
        )
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        query = sys.argv[2] if len(sys.argv) > 2 else "default"
        print(process_data(query))


if __name__ == "__main__":
    main()

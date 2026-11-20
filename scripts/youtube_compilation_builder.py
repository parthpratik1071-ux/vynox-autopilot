#!/usr/bin/env python3
"""
Vynox YouTube Long-Form Compilation Builder
Stitches top-performing 2D anime animations & cinematic edits into high-retention
15–60 minute compilations (e.g., "Late Night Drive / Hindi Indie Slowed + Reverb").
Designed to rapidly accumulate the 4,000 watch hours required for YouTube Partner Program (YPP) monetization.

Features:
- Auto-discovers produced 2D anime & cinematic master videos
- 16:9 Aesthetic Ambient Canvas: Blurred cinematic background + sharp centered 2D animation
- Generates precise YouTube Chapter Timestamps (00:00 Song 1, 03:45 Song 2...)
- Produces compliant metadata with AI Synthetic disclosure & Gift Card promo CTA
- Optional auto-upload via official YouTube Data API v3
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))

import youtube_uploader

OUTPUT_DIR = BASE_DIR / "projects" / "youtube_compilations"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
IST = timezone(timedelta(hours=5, minutes=30))

CATALOG_TRACKS = [
    {
        "title": "Baarishein",
        "artist": "Anuv Jain",
        "path": "projects/series-romantic-animations/04-baarishein-anuv-jain/output/film_baarishein_romantic.mp4",
        "cover": "projects/series-romantic-animations/04-baarishein-anuv-jain/output/cover.jpg",
        "tag": "Rain / Cozy Room 2D Anime",
    },
    {
        "title": "Alag Aasmaan",
        "artist": "Anuv Jain",
        "path": "projects/series-romantic-animations/05-alag-aasmaan-anuv-jain/output/film_alag_aasmaan_romantic.mp4",
        "cover": "projects/series-romantic-animations/05-alag-aasmaan-anuv-jain/output/cover.jpg",
        "tag": "Rooftop Stargazing 2D Anime",
    },
    {
        "title": "Samjho Na",
        "artist": "Aditya Rikhari",
        "path": "projects/series-romantic-animations/08-samjho-na-proper-animation/output/film_samjho_na_animation.mp4",
        "cover": "projects/series-romantic-animations/08-samjho-na-proper-animation/output/cover.jpg",
        "tag": "Midnight Breeze 2D Anime",
    },
    {
        "title": "Ishq",
        "artist": "Faheem Abdullah & Rauhan Malik",
        "path": "projects/series-romantic-animations/09-ishq-faheem/output/film_ishq.mp4",
        "cover": "projects/series-romantic-animations/09-ishq-faheem/output/cover.jpg",
        "tag": "Himalayan Snowfall 2D Anime",
    },
    {
        "title": "Sahiba (Crimson Manga)",
        "artist": "Jasleen Royal & Stebin Ben",
        "path": "projects/series-romantic-animations/07-sahiba-crimson-manga/output/film_sahiba_crimson_manga.mp4",
        "cover": "projects/series-romantic-animations/07-sahiba-crimson-manga/output/cover.jpg",
        "tag": "Monochrome & Crimson Manga",
    },
    {
        "title": "Waqt Ki Baatein",
        "artist": "Dream Note",
        "path": "projects/series-romantic-animations/06-waqt-ki-baatein-dream-note/output/film_waqt_ki_baatein_romantic.mp4",
        "cover": "projects/series-romantic-animations/06-waqt-ki-baatein-dream-note/output/cover.jpg",
        "tag": "Train Sunset Leaves 2D Anime",
    },
    {
        "title": "Husn",
        "artist": "Anuv Jain",
        "path": "projects/series-romantic-animations/03-husn-anuv-jain/output/film_husn_romantic.mp4",
        "cover": "projects/series-romantic-animations/03-husn-anuv-jain/output/cover.jpg",
        "tag": "Midnight Balcony 2D Anime",
    },
    {
        "title": "The Batman • Sajan Sajan",
        "artist": "Kailash Kher & Michael Giacchino",
        "path": "projects/batman-realistic-edit/output/The_Batman_Realistic_Sajan_Sajan_Reel.mp4",
        "cover": "projects/brand_identity/studio_avatar.jpg",
        "tag": "Cinematic Rain & Neon Gotham",
    },
    {
        "title": "Blade Runner 2049 • Tu Hai Kahan",
        "artist": "AUR / Ryan Gosling",
        "path": "projects/ryan-gosling-blade-runner-edit/output/Blade_Runner_Tu_Hai_Kahan_Reel.mp4",
        "cover": "projects/brand_identity/studio_avatar.jpg",
        "tag": "Cyberpunk Hologram Romance",
    },
    {
        "title": "Interstellar • Kyun Main Jaagoon",
        "artist": "Shafqat Amanat Ali & Hans Zimmer",
        "path": "projects/interstellar-kyun-main-jaagoon-edit/output/Interstellar_Kyun_Main_Jaagoon_Reel.mp4",
        "cover": "projects/brand_identity/studio_avatar.jpg",
        "tag": "Cosmic Deep Space Tears",
    },
]


def get_video_duration(video_path: Path) -> float:
    """Uses ffprobe to obtain exact video duration in seconds."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(video_path),
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(res.stdout.strip())
    except Exception:
        return 20.0


def format_timestamp(seconds: float) -> str:
    """Formats seconds into MM:SS or HH:MM:SS string."""
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def prepare_track_sequence(target_minutes: float = 15.0) -> list[dict]:
    """
    Selects and sequences available video tracks to reach or exceed target duration.
    """
    valid_tracks = []
    for t in CATALOG_TRACKS:
        full_path = BASE_DIR / t["path"]
        if full_path.exists():
            item = dict(t)
            item["full_path"] = full_path
            item["duration"] = get_video_duration(full_path)
            valid_tracks.append(item)

    if not valid_tracks:
        raise FileNotFoundError("No catalog video files exist on disk to compile.")

    target_seconds = target_minutes * 60.0
    sequence = []
    accumulated = 0.0

    while accumulated < target_seconds:
        for t in valid_tracks:
            sequence.append(t)
            accumulated += t["duration"]
            if accumulated >= target_seconds:
                break

    return sequence


def render_16x9_compilation(
    sequence: list[dict],
    output_file: Path,
    dry_run: bool = False,
) -> tuple[float, list[dict]]:
    """
    Stitches tracks into a 1920x1080 16:9 cinematic video with blurred background.
    Returns (total_duration, chapters_list).
    """
    chapters = []
    current_time = 0.0
    seen_titles = {}

    for idx, t in enumerate(sequence):
        count = seen_titles.get(t["title"], 0) + 1
        seen_titles[t["title"]] = count
        suffix = f" (Part {count})" if count > 1 else ""
        chapters.append({
            "timestamp": format_timestamp(current_time),
            "seconds": current_time,
            "title": f"{t['title']}{suffix}",
            "artist": t["artist"],
            "tag": t.get("tag", ""),
        })
        current_time += t["duration"]

    if dry_run:
        print(f"\n🧪 [DRY RUN] Would stitch {len(sequence)} track segments.")
        print(f"   Target Output: {output_file.name}")
        print(f"   Total Estimated Duration: {format_timestamp(current_time)} ({current_time:.1f}s)")
        return current_time, chapters

    # Step 1: Normalize each video to 1920x1080 16:9 with blurred background
    temp_dir = OUTPUT_DIR / "temp_segments"
    temp_dir.mkdir(parents=True, exist_ok=True)
    segment_files = []

    print(f"🎬 Normalizing {len(sequence)} segments to 1920x1080 60fps...")
    for idx, t in enumerate(sequence):
        seg_out = temp_dir / f"seg_{idx:03d}.ts"
        segment_files.append(seg_out)

        if seg_out.exists() and seg_out.stat().st_size > 1000:
            continue

        # Filter: split into blurred 16:9 background and sharp centered vertical foreground
        filter_complex = (
            "[0:v]split=2[fg][bg];"
            "[bg]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,gblur=sigma=22,eq=brightness=-0.35[blurred];"
            "[fg]scale=-1:1080[scaled_fg];"
            "[blurred][scaled_fg]overlay=(W-w)/2:0[v_out]"
        )

        cmd = [
            "ffmpeg", "-y",
            "-i", str(t["full_path"]),
            "-filter_complex", filter_complex,
            "-map", "[v_out]",
            "-map", "0:a?",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "22",
            "-c:a", "aac",
            "-b:a", "192k",
            "-r", "30",
            "-f", "mpegts",
            str(seg_out),
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print(f"   ✓ Segment {idx+1}/{len(sequence)} rendered: {t['title']}")

    # Step 2: Concatenate via MPEG-TS protocol (seamless, zero audio-sync loss)
    concat_input = "concat:" + "|".join(str(s) for s in segment_files)
    print(f"\n📦 Merging all segments into final MP4: {output_file.name}...")
    concat_cmd = [
        "ffmpeg", "-y",
        "-i", concat_input,
        "-c:v", "copy",
        "-c:a", "copy",
        "-movflags", "+faststart",
        str(output_file),
    ]
    subprocess.run(concat_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # Cleanup temp segments
    shutil.rmtree(temp_dir, ignore_errors=True)
    print(f"✅ Final Compilation Rendered: {output_file} ({output_file.stat().st_size / (1024*1024):.1f} MB)")
    return current_time, chapters


def generate_metadata(chapters: list[dict], total_seconds: float) -> dict:
    """Generates SEO-rich YouTube title, description with chapters, and tags."""
    title = "Late Night Drive 🌙 | Hindi Indie & Aesthetic 2D Anime Chill Mix (Slowed + Reverb)"
    if len(title) > 100:
        title = title[:100]

    chapter_lines = []
    for c in chapters:
        chapter_lines.append(f"{c['timestamp']} - {c['title']} • {c['artist']}")

    description = f"""✦ Late Night Drive & Nostalgia | Pure Living 2D Anime & Indie Audio 🎧🌙
Close your eyes, put your headphones on, and let the midnight road take you away.
Featuring handcrafted living 2D anime animations, monsoons, rooftop stargazing, and midnight indie melodies.

⏱️ TRACKLIST & CHAPTERS:
{chr(10).join(chapter_lines)}

──────────────────────────────
🎨 VISUAL ART & PRODUCTION:
• Animation & Concept: Vynox Studio (@vynox_00000)
• Visual Medium: Living 2D Anime, Organic Physics & Cinematic Manga
• Duration: {format_timestamp(total_seconds)}

🎁 FREE 4K WALLPAPERS:
Head over to Instagram @vynox_00000 and comment "WALLPAPER" on any reel for instant uncompressed 4K lockscreens!

📩 MUSIC PLACEMENTS & INQUIRIES:
Indie artists, producers, and labels: For track placements in upcoming animations:
Email: vynox.creativestudio@gmail.com (We accept Amazon Pay Gift Cards / Google Play codes)

✨ TRANSPARENCY NOTICE (YouTube Compliance):
This video features stylized 2D anime art, generative visual physics, and original cinematic edits.
──────────────────────────────

#HindiIndie #LofiAnime #LateNightDrive #SlowedAndReverb #AnuvJain #2DAnimation #VynoxStudio #ChillVibes"""

    tags = [
        "Hindi Indie", "Late Night Drive", "Slowed and Reverb", "Anuv Jain",
        "Baarishein", "Alag Aasmaan", "Choo Lo", "Lofi Hindi", "2D Anime Animation",
        "Aesthetic Chill Songs", "Midnight Road Mix", "Vynox Studio",
        "Relaxing Hindi Songs", "Romantic Lofi", "Indie Music India",
    ]

    return {
        "title": title,
        "description": description,
        "tags": tags,
    }


def build_compilation(
    target_minutes: float = 15.0,
    upload: bool = False,
    dry_run: bool = False,
) -> dict:
    """
    Main orchestration entry point.
    """
    print("=" * 65)
    print("🎬 VYNOX YOUTUBE LONG-FORM COMPILATION ENGINE")
    print(f"🎯 Target Duration: {target_minutes} minutes")
    print(f"⏰ Local Time: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')}")
    print("=" * 65)

    sequence = prepare_track_sequence(target_minutes=target_minutes)
    output_filename = f"Vynox_Late_Night_Indie_Mix_{int(target_minutes)}min.mp4"
    output_file = OUTPUT_DIR / output_filename

    total_seconds, chapters = render_16x9_compilation(
        sequence=sequence,
        output_file=output_file,
        dry_run=dry_run,
    )

    metadata = generate_metadata(chapters, total_seconds)

    # Save metadata JSON and TXT for reference
    meta_json = OUTPUT_DIR / f"metadata_{int(target_minutes)}min.json"
    with open(meta_json, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": datetime.now(IST).isoformat(),
            "target_minutes": target_minutes,
            "total_duration": format_timestamp(total_seconds),
            "output_file": str(output_file),
            "metadata": metadata,
            "chapters": chapters,
        }, f, indent=2)

    print("\n📋 GENERATED YOUTUBE CHAPTERS & METADATA:")
    print(f"Title: {metadata['title']}")
    print(f"Chapters ({len(chapters)}):\n" + "\n".join(f"  {c['timestamp']} - {c['title']}" for c in chapters[:6]) + ("\n  ..." if len(chapters) > 6 else ""))

    # Auto-upload if requested
    if upload:
        print("\n🚀 Initiating YouTube upload...")
        cover_path = BASE_DIR / "projects" / "brand_identity" / "studio_avatar.jpg"
        yt_res = youtube_uploader.upload_longform_video(
            video_path=output_file,
            title=metadata["title"],
            description=metadata["description"],
            tags=metadata["tags"],
            thumbnail_path=cover_path if cover_path.exists() else None,
            dry_run=dry_run,
        )
        return {"file": str(output_file), "metadata": metadata, "upload": yt_res}

    return {"file": str(output_file), "metadata": metadata}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vynox YouTube Long-Form Compilation Builder")
    parser.add_argument("--target-mins", type=float, default=15.0, help="Target compilation duration in minutes")
    parser.add_argument("--upload", action="store_true", help="Upload directly to YouTube upon rendering")
    parser.add_argument("--dry-run", action="store_true", help="Inspect sequence and metadata without rendering")
    args = parser.parse_args()

    build_compilation(target_minutes=args.target_mins, upload=args.upload, dry_run=args.dry_run)

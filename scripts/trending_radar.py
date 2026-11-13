#!/usr/bin/env python3
"""
Automated Trending Intelligence Radar for Vynox Autopilot.
Scans YouTube Data API v3 and Instagram Music for emerging viral Hindi indie songs,
lo-fi aesthetic tracks, and high-velocity lyric formats.
Filters everything through Zero-Repeat Duplicate Guard to ensure 100% unique suggestions.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))

import duplicate_guard
import youtube_uploader
import insta_local_post

RADAR_JSON = BASE_DIR / "projects" / "trending_radar.json"
REPORT_MD = BASE_DIR / "projects" / "trending_report.md"
IST = timezone(timedelta(hours=5, minutes=30))


DEFAULT_SEARCH_QUERIES = [
    "hindi indie aesthetic shorts",
    "lofi hindi lyric shorts",
    "anuv jain aesthetic status shorts",
    "trending romantic hindi shorts 2026",
    "acoustic hindi indie love song shorts",
]


def scan_youtube_trends(queries: list[str] = None, max_results_per_query: int = 5) -> list[dict]:
    """Scans YouTube Data API v3 for high-performing Hindi Indie Shorts."""
    queries = queries or DEFAULT_SEARCH_QUERIES
    try:
        service = youtube_uploader.get_youtube_service()
    except Exception as e:
        print(f"⚠️ YouTube API not available: {e}")
        return []

    published_after = (datetime.now(timezone.utc) - timedelta(days=21)).isoformat()
    trends = []
    seen_ids = set()

    for q in queries:
        try:
            res = service.search().list(
                part="snippet",
                q=q,
                type="video",
                videoDuration="short",
                order="viewCount",
                publishedAfter=published_after,
                maxResults=max_results_per_query,
            ).execute()

            video_ids = [item["id"]["videoId"] for item in res.get("items", []) if "videoId" in item.get("id", {})]
            if not video_ids:
                continue

            # Fetch statistics for views/likes
            stat_res = service.videos().list(
                part="snippet,statistics",
                id=",".join(video_ids),
            ).execute()

            for item in stat_res.get("items", []):
                vid = item["id"]
                if vid in seen_ids:
                    continue
                seen_ids.add(vid)

                snippet = item["snippet"]
                stats = item.get("statistics", {})
                title = snippet.get("title", "")
                views = int(stats.get("viewCount", 0))
                likes = int(stats.get("likeCount", 0))
                channel = snippet.get("channelTitle", "")
                pub_at = snippet.get("publishedAt", "")

                # Parse clean candidate title
                clean_title = title.split("|")[0].split("~")[0].split("#")[0].strip()
                is_dup, dup_reason = duplicate_guard.is_duplicate_song(clean_title)

                trends.append({
                    "id": vid,
                    "raw_title": title,
                    "clean_title": clean_title,
                    "channel": channel,
                    "views": views,
                    "likes": likes,
                    "published_at": pub_at,
                    "url": f"https://youtube.com/shorts/{vid}",
                    "is_duplicate": is_dup,
                    "duplicate_reason": dup_reason,
                    "source": "youtube_shorts",
                })
        except Exception as e:
            print(f"⚠️ Error querying YouTube for '{q}': {e}")

    # Rank by view count
    trends.sort(key=lambda x: x["views"], reverse=True)
    return trends


def scan_instagram_audio(keywords: list[str] = None) -> list[dict]:
    """Searches Instagram's live audio catalog for high-relevance tracks."""
    keywords = keywords or ["anuv jain", "dikshant", "faheem abdullah", "prateek kuhad", "lofi romance", "aditya rikhari"]
    ok, code, cl = insta_local_post.check_auth_health()
    if not ok or not cl:
        print(f"⚠️ Instagram search unavailable: {code}")
        return []

    audio_trends = []
    seen_audio_ids = set()

    for kw in keywords:
        try:
            tracks = cl.search_music(kw)
            for t in tracks[:3]:
                aid = str(getattr(t, "id", getattr(t, "audio_id", "")))
                if aid in seen_audio_ids:
                    continue
                seen_audio_ids.add(aid)

                title = getattr(t, "title", "")
                artist = getattr(t, "display_artist", getattr(t, "artist_name", ""))
                is_dup, dup_reason = duplicate_guard.is_duplicate_song(title, artist)

                audio_trends.append({
                    "audio_id": aid,
                    "title": title,
                    "artist": artist,
                    "is_duplicate": is_dup,
                    "duplicate_reason": dup_reason,
                    "source": "instagram_music",
                })
        except Exception as e:
            print(f"⚠️ Instagram music search warning for '{kw}': {e}")

    return audio_trends


def generate_radar_report(yt_trends: list[dict], ig_trends: list[dict]) -> dict:
    """Combines trends and generates structured report and Markdown."""
    now_ist = datetime.now(IST).strftime("%d %b %Y, %I:%M %p IST")

    fresh_yt = [t for t in yt_trends if not t["is_duplicate"]]
    dup_yt = [t for t in yt_trends if t["is_duplicate"]]

    fresh_ig = [t for t in ig_trends if not t["is_duplicate"]]
    dup_ig = [t for t in ig_trends if t["is_duplicate"]]

    report_data = {
        "generated_at": now_ist,
        "summary": {
            "fresh_youtube_shorts": len(fresh_yt),
            "queued_or_posted_youtube": len(dup_yt),
            "fresh_instagram_tracks": len(fresh_ig),
            "queued_or_posted_instagram": len(dup_ig),
        },
        "fresh_candidates": fresh_yt[:10],
        "instagram_tracks": fresh_ig[:10],
        "already_handled": dup_yt + dup_ig,
    }

    # Write JSON
    RADAR_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(RADAR_JSON, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    # Write Markdown
    md_lines = [
        f"# 📡 Vynox Trending Intelligence Radar",
        f"*Generated: {now_ist}*",
        "",
        "## 🔥 Top Fresh Trending YouTube Shorts (Unproduced & Non-Duplicate)",
        "| Rank | Title | Views | Channel | URL |",
        "|---|---|---|---|---|",
    ]

    for idx, t in enumerate(fresh_yt[:8], 1):
        md_lines.append(f"| {idx} | **{t['clean_title']}** | {t['views']:,} | {t['channel']} | [Watch Short]({t['url']}) |")

    md_lines.extend([
        "",
        "## 🎧 Live Instagram Audio Catalog Candidates",
        "| Song Title | Artist | Audio ID | Status |",
        "|---|---|---|---|",
    ])
    for t in fresh_ig[:8]:
        md_lines.append(f"| **{t['title']}** | {t['artist']} | `{t['audio_id']}` | 🎯 Ready for Production |")

    if dup_yt or dup_ig:
        md_lines.extend([
            "",
            "## 🛡️ Zero-Repeat Filtered (Already Produced or Queued)",
        ])
        for t in (dup_yt + dup_ig)[:5]:
            title = t.get("clean_title") or t.get("title")
            reason = t.get("duplicate_reason", "Already queued")
            md_lines.append(f"- ⏭️ **{title}**: *{reason}*")

    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    return report_data


def main():
    parser = argparse.ArgumentParser(description="Vynox Trending Intelligence Scanner")
    parser.add_argument("--scan", action="store_true", help="Run full scan across YouTube Shorts and Instagram Audio")
    parser.add_argument("--report-only", action="store_true", help="Print existing report if available")
    args = parser.parse_args()

    if args.report_only and REPORT_MD.exists():
        print(REPORT_MD.read_text())
        return 0

    print("🚀 [Trending-Radar] Initiating multi-platform trend scan...")
    yt_trends = scan_youtube_trends()
    ig_trends = scan_instagram_audio()

    report = generate_radar_report(yt_trends, ig_trends)

    print("\n" + "=" * 60)
    print(f"📡 TRENDING RADAR SCAN COMPLETED ({report['generated_at']})")
    print(f"• Fresh YouTube Shorts Candidates: {report['summary']['fresh_youtube_shorts']}")
    print(f"• Fresh Instagram Music Tracks: {report['summary']['fresh_instagram_tracks']}")
    print(f"• Filtered Out Duplicates: {report['summary']['queued_or_posted_youtube'] + report['summary']['queued_or_posted_instagram']}")
    print("=" * 60)

    if report["fresh_candidates"]:
        print("\n🔥 TOP 3 FRESH VIRAL RECOMMENDATIONS:")
        for idx, c in enumerate(report["fresh_candidates"][:3], 1):
            print(f"  {idx}. {c['clean_title']} ({c['views']:,} views) -> {c['url']}")

    if report["instagram_tracks"]:
        print("\n🎧 TOP 3 INSTAGRAM MUSIC CANDIDATES:")
        for idx, t in enumerate(report["instagram_tracks"][:3], 1):
            print(f"  {idx}. {t['title']} by {t['artist']} (ID: {t['audio_id']})")

    print(f"\n📄 Full Markdown report generated at: {REPORT_MD.resolve()}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())


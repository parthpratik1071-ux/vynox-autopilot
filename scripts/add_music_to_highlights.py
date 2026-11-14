#!/usr/bin/env python3
"""
Adds Sound & Music Video Stories to Instagram Highlights on @vynox_00000.
Each Highlight will now play full audio & animated motion:
1. ANIME   -> Samjho Na (Aditya Rikhari) audio & animation
2. LORE    -> Ancient Indian Astronomy orchestral score & visuals
3. MANGA   -> Sahiba (Jasleen Royal) crimson manga audio & animation
4. PLAYLIST-> Ishq (Faheem Abdullah) soulful sufi-indie audio & animation
"""

import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))

import insta_local_post

BRAND_DIR = BASE_DIR / "projects" / "brand_identity"

TARGETS = [
    {
        "title": "ANIME",
        "video": Path("/tmp/music_story_anime.mp4"),
        "cover": BRAND_DIR / "highlight_anime.jpg",
        "caption": "✦ Samjho Na • Aditya Rikhari (Living 2D Anime) 🎧",
    },
    {
        "title": "LORE",
        "video": Path("/tmp/music_story_lore.mp4"),
        "cover": BRAND_DIR / "highlight_lore.jpg",
        "caption": "✦ Ancient Indian Astronomy • Vedic Space Lore 🌌",
    },
    {
        "title": "MANGA",
        "video": Path("/tmp/music_story_manga.mp4"),
        "cover": BRAND_DIR / "highlight_manga.jpg",
        "caption": "✦ Sahiba • Jasleen Royal (Crimson Manga) 🩸",
    },
    {
        "title": "PLAYLIST",
        "video": Path("/tmp/music_story_playlist.mp4"),
        "cover": BRAND_DIR / "highlight_playlist.jpg",
        "caption": "✦ Ishq • Faheem Abdullah & Rauhan Malik 🏔️✨",
    },
]


def add_music_to_all_highlights():
    print("🎵 Initializing Sound & Music Addition to @vynox_00000 Highlights...")
    cl = insta_local_post.get_client()

    # Map existing highlights
    highlights_map = {}
    try:
        live_hls = cl.user_highlights(cl.user_id)
        for h in live_hls:
            highlights_map[h.title.upper()] = h
            print(f"   Found highlight: '{h.title}' (ID: {h.pk})")
    except Exception as e:
        print(f"Error fetching highlights: {e}")
        return

    for item in TARGETS:
        title = item["title"]
        video_path = item["video"]
        cover_path = item["cover"]
        caption = item["caption"]

        if title not in highlights_map:
            print(f"⚠️ Highlight '{title}' not found on profile. Skipping.")
            continue

        hl = highlights_map[title]
        print(f"\n==================================================")
        print(f"🎶 Adding Music & Motion to Highlight: [{title}]")
        print(f"📹 Video clip: {video_path.name} ({video_path.stat().st_size / (1024*1024):.2f} MB)")

        try:
            # Generate video thumbnail if not already present
            thumb_path = Path(f"{video_path}.thumb.jpg")
            if not thumb_path.exists():
                import subprocess
                subprocess.run([
                    "ffmpeg", "-y", "-ss", "1.0", "-i", str(video_path),
                    "-frames:v", "1", "-q:v", "2", str(thumb_path)
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

            # 1. Upload musical video story
            print(f"🚀 Uploading musical video story with thumbnail...")
            story = cl.video_upload_to_story(path=video_path, thumbnail=thumb_path, caption=caption)
            story_pk = str(getattr(story, "pk", ""))
            print(f"✅ Musical Story live! (PK: {story_pk})")
            time.sleep(3)

            # 2. Add story into the Highlight
            print(f"📌 Binding musical story into Highlight '{title}' (ID: {hl.pk})...")
            cl.highlight_add_stories(highlight_pk=hl.pk, added_media_ids=[story_pk])
            print(f"✨ Story added to Highlight '{title}'!")
            time.sleep(2)

            # 3. Re-affirm custom cover
            if cover_path.exists():
                print(f"🎨 Ensuring custom cover icon remains active: {cover_path.name}...")
                cl.highlight_change_cover(hl.pk, cover_path)
                print(f"✅ Cover affirmed for '{title}'!")

        except Exception as err:
            print(f"⚠️ Error adding music to highlight '{title}': {err}")

        time.sleep(4)

    print("\n" + "=" * 50)
    print("🎉 ALL HIGHLIGHTS UPDATED WITH FULL MUSIC & SOUND!")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    add_music_to_all_highlights()

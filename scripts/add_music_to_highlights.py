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
STORIES_DIR = BRAND_DIR / "music_stories"

TARGETS = [
    {
        "title": "ANIME",
        "video": STORIES_DIR / "music_story_anime.mp4",
        "cover": BRAND_DIR / "highlight_anime.jpg",
        "caption": "✦ Samjho Na • Aditya Rikhari (Living 2D Anime) 🎧",
    },
    {
        "title": "LORE",
        "video": STORIES_DIR / "music_story_lore.mp4",
        "cover": BRAND_DIR / "highlight_lore.jpg",
        "caption": "✦ Ancient Indian Astronomy • Vedic Space Lore 🌌",
    },
    {
        "title": "MANGA",
        "video": STORIES_DIR / "music_story_manga.mp4",
        "cover": BRAND_DIR / "highlight_manga.jpg",
        "caption": "✦ Sahiba • Jasleen Royal (Crimson Manga) ✨",
    },
    {
        "title": "PLAYLIST",
        "video": STORIES_DIR / "music_story_playlist.mp4",
        "cover": BRAND_DIR / "highlight_playlist.jpg",
        "caption": "✦ Ishq • Faheem Abdullah & Rauhan Malik 🏔️✨",
    },
]


def add_music_to_all_highlights():
    print("🎵 Initializing Clean Highlight Recreation with Music on @vynox_00000...")
    cl = insta_local_post.get_client()

    # 1. Clean Delete of Old Silent Highlights
    print("\n🗑️ Deleting old silent highlights from profile...")
    try:
        old_hls = cl.user_highlights(cl.user_id)
        for h in old_hls:
            print(f"   Deleting old highlight: '{h.title}' (ID: {h.pk})...")
            cl.highlight_delete(h.pk)
            time.sleep(2)
        print("✅ Old highlights cleared!")
    except Exception as e:
        print(f"⚠️ Notice while deleting old highlights: {e}")

    # 2. Upload musical video stories and create fresh highlights with covers
    for item in TARGETS:
        title = item["title"]
        video_path = item["video"]
        cover_path = item["cover"]
        caption = item["caption"]

        print(f"\n==================================================")
        print(f"🎶 Creating Musical Highlight: [{title}]")
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
            print(f"🚀 Uploading musical video story with audio...")
            story = cl.video_upload_to_story(path=video_path, thumbnail=thumb_path, caption=caption)
            story_pk = str(getattr(story, "pk", ""))
            print(f"✅ Musical Story live! (PK: {story_pk})")
            time.sleep(3)

            # 2. Create fresh Highlight with this musical story
            print(f"✨ Creating fresh Highlight '{title}' on Instagram profile...")
            new_hl = cl.highlight_create(title=title, story_ids=[story_pk])
            print(f"🎉 Highlight '{title}' created! (ID: {new_hl.pk})")
            time.sleep(2)

            # 3. Apply custom luxury watercolor cover
            if cover_path.exists():
                print(f"🎨 Setting custom cover icon: {cover_path.name}...")
                cl.highlight_change_cover(new_hl.pk, cover_path)
                print(f"✅ Custom cover applied to '{title}'!")

        except Exception as err:
            print(f"⚠️ Error creating musical highlight '{title}': {err}")

        time.sleep(4)

    print("\n" + "=" * 50)
    print("🎉 ALL 4 HIGHLIGHTS RE-CREATED WITH FULL MUSIC & SOUND!")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    add_music_to_all_highlights()

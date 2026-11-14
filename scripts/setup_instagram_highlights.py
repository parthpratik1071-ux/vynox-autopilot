#!/usr/bin/env python3
"""
Automated Instagram Highlights & Studio Avatar Setup for @vynox_00000
Creates 4 aesthetic Story Highlights with custom luxury watercolor covers:
1. ANIME   -> projects/brand_identity/highlight_anime.jpg
2. LORE    -> projects/brand_identity/highlight_lore.jpg
3. MANGA   -> projects/brand_identity/highlight_manga.jpg
4. PLAYLIST-> projects/brand_identity/highlight_playlist.jpg
And updates profile avatar to studio_avatar.jpg.
"""

import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))

import insta_local_post

BRAND_DIR = BASE_DIR / "projects" / "brand_identity"

CATEGORIES = [
    {
        "title": "ANIME",
        "story_card": BASE_DIR / "projects/series-romantic-animations/08-samjho-na-proper-animation/output/story_card.jpg",
        "cover_icon": BRAND_DIR / "highlight_anime.jpg",
    },
    {
        "title": "LORE",
        "story_card": BASE_DIR / "projects/ancient-ujjain-astronomy/output/story_card.jpg",
        "cover_icon": BRAND_DIR / "highlight_lore.jpg",
    },
    {
        "title": "MANGA",
        "story_card": BASE_DIR / "projects/series-romantic-animations/07-sahiba-crimson-manga/output/story_card.jpg",
        "cover_icon": BRAND_DIR / "highlight_manga.jpg",
    },
    {
        "title": "PLAYLIST",
        "story_card": BASE_DIR / "projects/series-romantic-animations/09-ishq-faheem/output/story_card.jpg",
        "cover_icon": BRAND_DIR / "highlight_playlist.jpg",
    },
]


def setup_highlights():
    print("🚀 Initializing Instagram Highlights & Brand Setup for @vynox_00000...")
    cl = insta_local_post.get_client()

    # 1. Update Profile Picture Avatar
    avatar_path = BRAND_DIR / "studio_avatar.jpg"
    if avatar_path.exists():
        print(f"\n👤 Updating Profile Picture to Studio Avatar: {avatar_path.name}...")
        try:
            cl.account_change_picture(avatar_path)
            print("✅ Profile avatar updated successfully!")
        except Exception as e:
            print(f"⚠️ Profile avatar update notice: {e}")

    # 2. Check existing highlights
    print("\n🔍 Checking existing highlights on @vynox_00000...")
    existing = {}
    try:
        for h in cl.user_highlights(cl.user_id):
            existing[h.title.upper()] = h
            print(f"   Found existing highlight: '{h.title}' (ID: {h.pk})")
    except Exception as e:
        print(f"   Notice: {e}")

    # 3. Create or update each highlight category
    for cat in CATEGORIES:
        title = cat["title"]
        cover_icon = cat["cover_icon"]
        story_card = cat["story_card"]

        print(f"\n==================================================")
        print(f"🌟 Setting up Highlight: [{title}]")

        if title in existing:
            hl = existing[title]
            print(f"ℹ️ Highlight '{title}' already exists (ID: {hl.pk}). Updating cover...")
            try:
                cl.highlight_change_cover(hl.pk, cover_icon)
                print(f"✅ Cover updated for '{title}'!")
            except Exception as e:
                print(f"⚠️ Cover update notice: {e}")
            continue

        # Upload story card for this highlight
        story_pk = None
        if story_card.exists():
            print(f"📸 Uploading category story card: {story_card.name}...")
            try:
                story = cl.photo_upload_to_story(path=story_card, caption=f"✦ VYNOX {title} ✦")
                story_pk = str(getattr(story, "pk", ""))
                print(f"✅ Story published! (PK: {story_pk})")
                time.sleep(3)
            except Exception as e:
                print(f"⚠️ Story upload error: {e}")

        if not story_pk:
            # Fallback to active stories
            try:
                active_stories = cl.user_stories(cl.user_id)
                if active_stories:
                    story_pk = str(active_stories[0].pk)
                    print(f"ℹ️ Using active story PK: {story_pk}")
            except Exception:
                pass

        if not story_pk:
            print(f"❌ Cannot create highlight '{title}': no story available.")
            continue

        # Create Highlight
        print(f"✨ Creating Highlight '{title}' on Instagram profile...")
        try:
            new_hl = cl.highlight_create(title=title, story_ids=[story_pk])
            print(f"🎉 Highlight '{title}' created successfully! (ID: {new_hl.pk})")
            time.sleep(2)

            # Change cover to custom luxury icon
            if cover_icon.exists():
                print(f"🎨 Setting custom cover icon: {cover_icon.name}...")
                cl.highlight_change_cover(new_hl.pk, cover_icon)
                print(f"✅ Custom cover applied to '{title}'!")
        except Exception as e:
            print(f"⚠️ Error creating highlight '{title}': {e}")

        time.sleep(4)

    # 4. Verify Final State
    print("\n" + "=" * 50)
    print("📊 Verifying live highlights on @vynox_00000:")
    try:
        final_hls = cl.user_highlights(cl.user_id)
        for h in final_hls:
            print(f"   ✨ Highlight: {h.title} | ID: {h.pk} | Items: {h.media_count}")
        print(f"Total live highlights: {len(final_hls)}")
    except Exception as e:
        print(f"Verification notice: {e}")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    setup_highlights()

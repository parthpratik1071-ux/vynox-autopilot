#!/usr/bin/env python3
"""
NexoraAI Human-Like Instagram DM & Comment-to-DM Funnel Engine (@vynox_00000)
1. "Comment-to-DM" Automation:
   Detects comments containing keywords ("WALLPAPER", "PRESET", "CC", "LINK") on recent Reels,
   likes the comment, replies ("Sent to your DM! 🖤"), and delivers the 4K asset link in direct messages.
2. Authentic Human Direct Message Auto-Responder:
   Responds with warmth, personality, and contextual accuracy:
   - Wallpaper inquiries -> Uncompressed 4K phone/desktop wallpaper pack
   - Preset / LUT inquiries -> Creator edit preset pack & color grading files
   - Music / collab inquiries -> Collaboration & submission contact
   - Appreciation & fan love -> Warm creator thank-you & schedule hook
   - Reel shares -> Genuine, non-robotic Gen-Z reactions ("bro this is wild 🔥", "lmao good one 😂")
   - Double-tap likes (❤️) latest message to avoid notification spam
3. Safe Rate-Limiting & Ban-Shield Circuit Breaker:
   Strict action caps, random human typing delays, and duplicate suppression.
"""

import argparse
import json
import os
import random
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))

import insta_local_post

PROJECTS_DIR = BASE_DIR / "projects"
CONFIG_FILE = PROJECTS_DIR / "dm_funnel_config.json"
SEEN_MESSAGES_FILE = PROJECTS_DIR / "dm_seen_vynox_00000.json"
PROCESSED_COMMENTS_FILE = PROJECTS_DIR / "comment_funnel_processed.json"
COOLDOWN_FILE = PROJECTS_DIR / "booster_cooldown.json"
IST = timezone(timedelta(hours=5, minutes=30))

DEFAULT_CONFIG = {
    "version": "1.0.0",
    "account": "vynox_00000",
    "links": {
        "wallpaper_link": "https://drive.google.com/drive/folders/1-vynox-4k-aesthetic-wallpapers?usp=sharing",
        "preset_link": "https://drive.google.com/drive/folders/1-vynox-creator-cc-presets?usp=sharing",
        "bento_portfolio": "https://bento.me/vynox",
        "music_collab_email": "vynox.creativestudio@gmail.com",
    },
    "keywords": {
        "wallpaper": [
            "wallpaper", "wallpapers", "wp", "wall", "lockscreen",
            "homescreen", "4k photo", "photo chahiye", "wallpaper bhejo",
            "pic chahiye", "image", "photo"
        ],
        "preset": [
            "preset", "presets", "cc", "color grade", "lut", "luts",
            "capcut", "project file", "settings", "qr code"
        ],
        "music_collab": [
            "collab", "collaboration", "promote", "promotion", "paid promo",
            "audio promote", "song promo", "track feature"
        ],
        "song_inquiry": [
            "song name", "which song", "audio name", "track name",
            "gaana", "gana konsa", "background music", "bgm"
        ],
        "appreciation": [
            "insane", "op", "bawal", "gazab", "mast", "crazy", "fire",
            "love your art", "underrated", "best edit", "hard", "shandar", "superb"
        ],
    },
    "dm_responses": {
        "wallpaper": [
            "Hey! 🖤 Here is the uncompressed 4K wallpaper pack for phone & desktop:\n{wallpaper_link}\n\nHope you love the details! Let me know which frame you set as your lockscreen 🎧✨",
            "Here you go bro! 🥀 Grab the 4K wallpapers from our latest animations here:\n{wallpaper_link}\n\nDrop a follow or share if you vibe with the art, more dropping tonight! 🖤📲",
            "Sent with love! 🤍 Here's the direct link to the 4K wallpapers:\n{wallpaper_link}\n\nEnjoy the details! More living 2D art on the way 🌌✨",
        ],
        "preset": [
            "Here is the creator edit preset pack (Color Grade CC + CapCut / Premiere LUTs) 🎬✨:\n{preset_link}\n\nTag @vynox_00000 if you make an edit with it so we can show love! 🔥",
            "Got you covered! Here's the 4K CC preset and grading settings 🎧:\n{preset_link}\n\nCan't wait to see what you create with it! 🖤",
        ],
        "music_collab": [
            "Hey! 🎵 We would love to collaborate! For music placements, audio features, and brand inquiries, email us at {music_collab_email} or drop the track link right here! 🎧✨",
            "Thanks for reaching out! 🖤 Send your track link here or ping us at {music_collab_email} with the details. We listen to every indie submission! 🥀",
        ],
        "song_inquiry": [
            "Hey! The track name and artist are credited in the caption and reel audio tag 🎧✨ We post pure indie & romantic masterpieces every day at 7:30 & 9:45 PM!",
            "Track details are right in the caption! 🥀 Check out our highlights for our curated indie playlist 🖤",
        ],
        "appreciation": [
            "Thank you so much! Really means the world 🖤 More living 2D anime animations dropping tonight at 7:30 & 9:45 PM. Stay tuned! 🥀✨",
            "Appreciate the love bro! 🤍 We put heart and soul into every frame. Stay tuned for tonight's release! 🎧",
            "Thank you! Drop a follow and share with someone who loves this vibe 🖤✨",
        ],
        "casual_reel_reply": [
            "😂😂",
            "bro this is wild 🔥",
            "lmao good one 😂",
            "haha saw this!",
            "too accurate fr 💀",
            "✨🪔",
        ],
    },
    "comment_replies": [
        "Sent to your DM! 🖤 Check your inbox / requests ✨",
        "Just sent the 4K link to your DMs, enjoy! 🎧📲",
        "Sent over bro! Drop a tag if you use it on your lockscreen 🥀",
        "Check your message requests, sent it your way! 🤍✨",
        "Sent! Hope you love the 4K details 🖤💫",
    ],
}


def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Warning loading config, falling back to defaults: {e}")
    return DEFAULT_CONFIG


def is_booster_paused() -> bool:
    if not COOLDOWN_FILE.exists():
        return False
    try:
        with open(COOLDOWN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not data.get("active"):
            return False
        cooldown_until = datetime.fromisoformat(data["cooldown_until"])
        now = datetime.now(timezone.utc)
        if cooldown_until.tzinfo is None:
            cooldown_until = cooldown_until.replace(tzinfo=IST)
        return now < cooldown_until
    except Exception:
        return False


def load_seen(path: Path) -> set:
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()


def save_seen(path: Path, seen_ids: set, max_items: int = 1000):
    recent = list(seen_ids)[-max_items:]
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(recent, f, indent=2)
    except Exception as e:
        print(f"⚠️ Could not save seen IDs to {path.name}: {e}")


def match_intent(text: str, keywords_dict: dict) -> str | None:
    if not text:
        return None
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    words = set(cleaned.split())

    for intent, kws in keywords_dict.items():
        for kw in kws:
            kw_clean = kw.lower().strip()
            if " " in kw_clean:
                if kw_clean in cleaned:
                    return intent
            else:
                if kw_clean in words or kw_clean in cleaned:
                    return intent
    return None


def format_response(template: str, links: dict) -> str:
    return template.format(
        wallpaper_link=links.get("wallpaper_link", ""),
        preset_link=links.get("preset_link", ""),
        music_collab_email=links.get("music_collab_email", ""),
        bento_portfolio=links.get("bento_portfolio", ""),
    )


def process_inbox(cl=None, dry_run=False, max_actions=10) -> int:
    """
    Sweeps the @vynox_00000 direct inbox with authentic human creator intelligence.
    """
    if is_booster_paused():
        print("🛡️ [Ban-Shield] Auto-reply paused due to active cooldown.")
        return 0

    config = load_config()
    links = config.get("links", {})
    keywords = config.get("keywords", {})
    responses = config.get("dm_responses", {})

    if cl is None:
        cl = insta_local_post.get_client()

    my_user_id = str(cl.user_id)
    seen_ids = load_seen(SEEN_MESSAGES_FILE)
    print(f"📬 [Inbox-Engine] Scanning threads for @{cl.user_info(my_user_id).username}...")

    threads = cl.direct_threads(amount=10)
    actions = 0

    for t in threads:
        users = [u.username for u in t.users if getattr(u, "username", None)]
        if any(u.lower() in ["meta ai", "instagram"] for u in users):
            continue

        thread_id = str(t.id)
        messages = cl.direct_messages(thread_id, amount=6)

        for msg in messages:
            msg_id = str(msg.id)
            sender_id = str(msg.user_id)

            if sender_id == my_user_id or msg_id in seen_ids:
                continue

            item_type = str(msg.item_type).lower()
            msg_text = getattr(msg, "text", "") or ""
            sender_name = users[0] if users else sender_id
            print(f"\n📩 Incoming from @{sender_name} [{item_type}]: \"{msg_text}\"")

            is_reel_or_media = any(k in item_type for k in ["clip", "xma_clip", "media_share", "media", "video"])
            is_text = "text" in item_type

            # 1. Double-tap like (❤️) the message
            if not dry_run:
                try:
                    cl.direct_message_like(thread_id, msg.id)
                    print(f"   ❤️ Liked message from @{sender_name}")
                    time.sleep(random.uniform(1.2, 2.8))
                except Exception as e:
                    print(f"   ⚠️ Could not like message: {e}")

            # 2. Determine human creator reply
            reply_text = None
            matched = match_intent(msg_text, keywords)

            if matched and matched in responses:
                tpl = random.choice(responses[matched])
                reply_text = format_response(tpl, links)
                print(f"   🎯 Intent matched: [{matched}]")
            elif is_reel_or_media:
                reply_text = random.choice(responses.get("casual_reel_reply", ["🔥🖤", "😂😂"]))
                print("   🎬 Responding to shared Reel with authentic reaction")
            elif is_text and len(msg_text) > 2:
                # Fallback conversational warmth
                reply_text = random.choice(responses.get("appreciation", [
                    "Thank you so much! Really appreciate the love 🖤 More animations dropping tonight!"
                ]))
                print("   💬 Responding with creator appreciation")

            if reply_text:
                if dry_run:
                    print(f"   [DRY-RUN] Would send reply:\n   \"{reply_text}\"")
                else:
                    try:
                        typing_delay = random.uniform(2.5, 4.5)
                        time.sleep(typing_delay)
                        cl.direct_send(reply_text, thread_ids=[int(thread_id)])
                        print(f"   💬 Sent reply to @{sender_name}:\n      \"{reply_text.splitlines()[0]}...\"")
                    except Exception as e:
                        print(f"   ⚠️ Failed to send DM reply: {e}")

            seen_ids.add(msg_id)
            actions += 1
            if actions >= max_actions:
                print("🛑 Reached safe action cap for inbox run.")
                break

        if actions >= max_actions:
            break

    save_seen(SEEN_MESSAGES_FILE, seen_ids)
    print(f"✅ Inbox sweep complete. Processed {actions} message(s).")
    return actions


def sweep_funnel_comments(cl=None, dry_run=False, max_actions=5) -> int:
    """
    Scans recent Reels for "WALLPAPER" / "PRESET" / "LINK" comments,
    likes the comment, replies to the comment ("Sent to your DM! 🖤"),
    and delivers the link via Instagram Direct Message.
    """
    if is_booster_paused():
        print("🛡️ [Ban-Shield] Comment-to-DM paused due to active cooldown.")
        return 0

    config = load_config()
    links = config.get("links", {})
    keywords = config.get("keywords", {})
    dm_templates = config.get("dm_responses", {})
    comment_replies = config.get("comment_replies", DEFAULT_CONFIG["comment_replies"])

    if cl is None:
        cl = insta_local_post.get_client()

    my_user_id = str(cl.user_id)
    processed_comments = load_seen(PROCESSED_COMMENTS_FILE)

    print(f"🔍 [Comment-to-DM] Scanning recent Reels for keyword comments...")

    # Fetch recent reels
    clips = []
    try:
        clips = cl.user_clips(my_user_id, amount=5)
    except Exception as e:
        print(f"⚠️ Error fetching reels: {e}")

    actions = 0

    for clip in clips:
        media_id = str(clip.pk)
        caption_preview = (clip.caption_text or "")[:40].replace("\n", " ")
        print(f"\n🎬 Checking Reel {clip.code} (ID: {media_id}) - \"{caption_preview}...\"")

        try:
            comments = cl.media_comments(media_id)
        except Exception as e:
            print(f"⚠️ Could not fetch comments for {clip.code}: {e}")
            continue

        for c in comments:
            c_id = str(getattr(c, "pk", ""))
            c_user = getattr(c, "user", None)
            c_user_pk = str(getattr(c_user, "pk", None) or getattr(c, "user_id", ""))
            c_author = str(getattr(c_user, "username", "") or "unknown")

            # Skip own comments or already processed comments
            if not c_id or c_user_pk == my_user_id or c_id in processed_comments:
                continue

            c_text = (getattr(c, "text", "") or "").strip()
            matched = match_intent(c_text, {
                "wallpaper": keywords.get("wallpaper", []),
                "preset": keywords.get("preset", []),
            })

            if not matched:
                continue

            print(f"   🎯 Found [{matched.upper()}] comment from @{c_author}: \"{c_text}\"")

            if dry_run:
                print(f"   [DRY-RUN] Would like comment {c_id}")
                print(f"   [DRY-RUN] Would reply to comment: \"{comment_replies[0]}\"")
                print(f"   [DRY-RUN] Would DM @{c_author} the {matched} link")
                processed_comments.add(c_id)
                actions += 1
                if actions >= max_actions:
                    break
                continue

            # 1. Like the comment ❤️
            try:
                comment_target_pk = int(c_id) if str(c_id).isdigit() else c_id
                cl.comment_like(comment_target_pk)
                print(f"   ❤️ Liked comment from @{c_author}")
                time.sleep(random.uniform(1.5, 3.0))
            except Exception as e:
                print(f"   ⚠️ Could not like comment: {e}")

            # 2. Reply to comment publicly ("Sent to your DM! 🖤")
            try:
                comment_reply_text = random.choice(comment_replies)
                reply_target_pk = int(c_id) if str(c_id).isdigit() else c_id
                cl.media_comment(media_id, comment_reply_text, replied_to_comment_id=reply_target_pk)
                print(f"   💬 Replied to comment: \"{comment_reply_text}\"")
                time.sleep(random.uniform(2.5, 4.5))
            except Exception as e:
                print(f"   ⚠️ Could not reply to comment: {e}")

            # 3. Direct Message delivery to the commenter
            tpl = random.choice(dm_templates.get(matched, [
                "Here is your link 🖤:\n{wallpaper_link}"
            ]))
            dm_text = format_response(tpl, links)

            try:
                target_uid = int(c_user_pk) if str(c_user_pk).isdigit() else c_user_pk
                cl.direct_send(dm_text, user_ids=[target_uid])
                print(f"   📬 Delivered {matched} link to @{c_author} via DM!")
            except Exception as e:
                print(f"   ⚠️ Could not send DM to @{c_author}: {e}")

            processed_comments.add(c_id)
            actions += 1
            time.sleep(random.uniform(4.0, 7.0))

            if actions >= max_actions:
                print("🛑 Reached safe action cap for comment funnel.")
                break

        if actions >= max_actions:
            break

    save_seen(PROCESSED_COMMENTS_FILE, processed_comments)
    print(f"\n✅ Comment-to-DM scan complete. Fulfilled {actions} funnel request(s).")
    return actions


def run(mode="all", dry_run=False, max_actions=5):
    print("=" * 60)
    print(f"🚀 Vynox Comment-to-DM & Human Inbox Engine (Mode: {mode.upper()})")
    print(f"⏰ Local Time: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')}")
    print(f"🧪 Dry Run: {dry_run}")
    print("=" * 60)

    try:
        cl = insta_local_post.get_client()
    except Exception as e:
        print(f"💥 Failed to authenticate Instagram client: {e}")
        return 1

    if mode in ["inbox", "all"]:
        process_inbox(cl=cl, dry_run=dry_run, max_actions=max_actions)

    if mode in ["comments", "all"]:
        sweep_funnel_comments(cl=cl, dry_run=dry_run, max_actions=max_actions)

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vynox Human DM & Comment-to-DM Funnel")
    parser.add_argument("--mode", choices=["inbox", "comments", "all"], default="all", help="Operation mode")
    parser.add_argument("--dry-run", action="store_true", help="Inspect and simulate without live network mutation")
    parser.add_argument("--max-actions", type=int, default=5, help="Maximum actions to take per run")
    args = parser.parse_args()

    sys.exit(run(mode=args.mode, dry_run=args.dry_run, max_actions=args.max_actions))

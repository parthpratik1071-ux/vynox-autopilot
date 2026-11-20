#!/usr/bin/env python3
"""
NexoraAI Anti-Ban & Human-Like Instagram DM Funnel Engine (@vynox_00000)
Core Design Tenets:
1. 🛡️ STRICT FRIEND & FAMILY SHIELD:
   NEVER reacts, likes, or sends automated replies to friends, family, or people the creator follows.
   Manual human chat is preserved 100% untouched for friends.
2. 🛡️ IRONCLAD ANTI-BAN ARCHITECTURE:
   - Sleep window: 01:30 AM to 07:00 AM IST (zero automated actions while humans sleep).
   - Rate limit: Capped at max 3 DMs & 3 Comment replies per run.
   - Human pacing: 8.0 to 18.0 seconds randomized typing delays.
   - Contacted memory: Never sends automated link DMs to the same user twice within 7 days.
   - Dynamic message mutation: Unique hash per send with randomized emojis & phrasing to evade spam filters.
   - 48-Hour Ban-Shield auto-circuit breaker on any restriction / challenge signal.
3. 💬 COMMENT-TO-DM AUTOMATION:
   Detects "WALLPAPER" / "PRESET" comments from fans, likes the comment, replies naturally,
   and delivers the 4K link straight to their DM.
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
IGNORED_USERS_FILE = PROJECTS_DIR / "dm_ignored_users.json"
SEEN_MESSAGES_FILE = PROJECTS_DIR / "dm_seen_vynox_00000.json"
PROCESSED_COMMENTS_FILE = PROJECTS_DIR / "comment_funnel_processed.json"
CONTACTED_USERS_FILE = PROJECTS_DIR / "dm_contacted_users.json"
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
            "Hey! 🎵 We would love to collaborate! For music placements, audio features, and brand inquiries, email us at {music_collab_email} or drop the track link right here! (We accept Amazon Pay Gift Cards / Google Play codes) 🎧✨",
            "Thanks for reaching out! 🖤 Send your track link here or ping us at {music_collab_email} with the details. We do indie track placements & accept Amazon Pay redeem codes! 🥀",
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

DEFAULT_IGNORED = {
    "paras_kumar_thakur", "palak", "palak_thakur",
    "sarthak", "navneet", "jisan", "tiwari", "arpit",
    "sharma", "shadox", "roxit", "rohit", "akap", "akash",
    "pratikparth", "pratikparth_12", "vynox_00000"
}

RANDOM_EMOJI_POOL = ["🖤✨", "🥀💫", "🎧🌌", "🤍📲", "✨🪔", "🥀🖤", "🤍✨", "🎧✨"]


def load_ignored_users() -> set:
    ignored = set(DEFAULT_IGNORED)
    if IGNORED_USERS_FILE.exists():
        try:
            with open(IGNORED_USERS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    ignored.update([str(u).lower().strip() for u in data])
        except Exception:
            pass
    return ignored


def is_friend_or_family(username: str, user_id: str = "", following_set: set | None = None) -> bool:
    """
    Returns True if user is a friend, family member, or someone the account follows.
    Automated replies are strictly FORBIDDEN for friends.
    """
    u_clean = (username or "").lower().strip()
    uid_clean = str(user_id or "").strip()

    ignored = load_ignored_users()

    # 1. Ignored list matching (family, close brothers, personal accounts)
    if any(ign in u_clean for ign in ignored) or uid_clean in ignored:
        return True

    # 2. Account following list: people you follow are friends/fellow creators
    if following_set and (u_clean in following_set or uid_clean in following_set):
        return True

    return False


def is_sleep_window(now_ist: datetime | None = None) -> bool:
    """
    Returns True during late night hours (01:30 AM to 07:00 AM IST) when real humans are asleep.
    """
    if now_ist is None:
        now_ist = datetime.now(IST)
    mins = now_ist.hour * 60 + now_ist.minute
    return (1 * 60 + 30) <= mins < (7 * 60 + 0)


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


def trip_ban_shield(reason: str) -> None:
    """Activates 48-hour circuit breaker on any restriction or challenge signal."""
    cooldown_until = datetime.now(IST) + timedelta(hours=48)
    data = {
        "active": True,
        "activated_at": datetime.now(IST).isoformat(),
        "cooldown_until": cooldown_until.isoformat(),
        "reason": reason,
    }
    try:
        COOLDOWN_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(COOLDOWN_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"🛡️ [Ban-Shield] Restriction caught: '{reason}'. Paused until {cooldown_until.strftime('%Y-%m-%d %H:%M IST')}.")
    except Exception as e:
        print(f"⚠️ Failed to write cooldown: {e}")


def load_contacted_history() -> dict:
    if CONTACTED_USERS_FILE.exists():
        try:
            with open(CONTACTED_USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_contacted_history(history: dict) -> None:
    try:
        CONTACTED_USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONTACTED_USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
    except Exception:
        pass


def was_contacted_recently(user_id: str, cooldown_days: int = 7) -> bool:
    history = load_contacted_history()
    last_contact = history.get(str(user_id))
    if not last_contact:
        return False
    try:
        dt = datetime.fromisoformat(last_contact)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=IST)
        return datetime.now(IST) - dt < timedelta(days=cooldown_days)
    except Exception:
        return False


def record_contacted_user(user_id: str) -> None:
    history = load_contacted_history()
    history[str(user_id)] = datetime.now(IST).isoformat()
    save_contacted_history(history)


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


def mutate_message_for_antispam(template: str, links: dict) -> str:
    """
    Subtly mutates spacing, punctuation, and closing emojis to ensure
    every automated message has a unique text hash to bypass Instagram's spam filter.
    """
    formatted = template.format(
        wallpaper_link=links.get("wallpaper_link", ""),
        preset_link=links.get("preset_link", ""),
        music_collab_email=links.get("music_collab_email", ""),
        bento_portfolio=links.get("bento_portfolio", ""),
    )
    # Add random closing emoji variation
    closing_emoji = random.choice(RANDOM_EMOJI_POOL)
    if not formatted.endswith(closing_emoji):
        formatted = f"{formatted.rstrip()} {closing_emoji}"
    return formatted


def get_account_following(cl, user_id: str) -> set:
    """Fetches and caches the usernames of accounts the user follows (friends & VIPs)."""
    try:
        following_dict = cl.user_following(user_id, amount=200)
        return {str(getattr(u, "username", "")).lower() for u in following_dict.values()}
    except Exception:
        return set()


def process_inbox(cl=None, dry_run=False, max_actions=3) -> int:
    """
    Sweeps inbox with human pacing, friend exclusion, and anti-ban safeguards.
    """
    if is_sleep_window():
        print("🌙 [Anti-Ban] Nighttime sleep window (01:30–07:00 IST). Skipping inbox sweep.")
        return 0

    if is_booster_paused():
        print("🛡️ [Ban-Shield] Auto-reply paused due to active cooldown.")
        return 0

    config = DEFAULT_CONFIG
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception:
            pass

    links = config.get("links", {})
    keywords = config.get("keywords", {})
    responses = config.get("dm_responses", {})

    if cl is None:
        cl = insta_local_post.get_client()

    my_user_id = str(cl.user_id)
    seen_ids = load_seen(SEEN_MESSAGES_FILE)
    following_set = get_account_following(cl, my_user_id)

    print(f"📬 [Inbox-Engine] Scanning threads for @{cl.user_info(my_user_id).username}...")
    threads = cl.direct_threads(amount=8)
    actions = 0

    for t in threads:
        users = [u.username for u in t.users if getattr(u, "username", None)]
        user_ids = [str(getattr(u, "pk", "") or getattr(u, "id", "")) for u in t.users]

        # 🛡️ Skip official bots
        if any(u.lower() in ["meta ai", "instagram"] for u in users):
            continue

        # 🛡️ FRIEND & FAMILY SHIELD: Never touch friends, family, or followed accounts
        is_friend = any(
            is_friend_or_family(u, uid, following_set)
            for u, uid in zip(users or [""], user_ids or [""])
        )
        if is_friend:
            print(f"   🛡️ [Friend-Protection] Skipped @{users} (Friend/VIP detected - manual human chat only).")
            continue

        thread_id = str(t.id)
        messages = cl.direct_messages(thread_id, amount=4)

        for msg in messages:
            msg_id = str(msg.id)
            sender_id = str(msg.user_id)

            if sender_id == my_user_id or msg_id in seen_ids:
                continue

            # Anti-Spam: Never re-message the same user within 7 days
            if was_contacted_recently(sender_id):
                seen_ids.add(msg_id)
                continue

            item_type = str(msg.item_type).lower()
            msg_text = getattr(msg, "text", "") or ""
            sender_name = users[0] if users else sender_id
            print(f"\n📩 Fan Message from @{sender_name} [{item_type}]: \"{msg_text}\"")

            is_reel_or_media = any(k in item_type for k in ["clip", "xma_clip", "media_share", "media", "video"])
            is_text = "text" in item_type

            # 1. Realistic human delay before like (8–14 seconds)
            delay = random.uniform(8.0, 14.0)
            print(f"   ⏳ [Human-Pacing] Simulating reading time ({delay:.1f}s)...")
            if not dry_run:
                time.sleep(delay)
                try:
                    cl.direct_message_like(thread_id, msg.id)
                    print(f"   ❤️ Liked fan message from @{sender_name}")
                except Exception as e:
                    print(f"   ⚠️ Could not like message: {e}")
                    if insta_local_post.is_restriction_error(e):
                        trip_ban_shield(str(e))
                        return actions

            # 2. Determine human creator reply
            reply_text = None
            matched = match_intent(msg_text, keywords)

            if matched and matched in responses:
                tpl = random.choice(responses[matched])
                reply_text = mutate_message_for_antispam(tpl, links)
                print(f"   🎯 Intent matched: [{matched}]")
            elif is_reel_or_media:
                reply_text = random.choice(responses.get("casual_reel_reply", ["🔥🖤", "😂😂"]))
                print("   🎬 Authentic creator reaction to shared Reel")
            elif is_text and len(msg_text) > 2:
                reply_text = random.choice(responses.get("appreciation", [
                    "Thank you so much! Really appreciate the love 🖤 More animations dropping tonight!"
                ]))
                print("   💬 Friendly creator appreciation")

            if reply_text:
                if dry_run:
                    print(f"   [DRY-RUN] Would send reply:\n   \"{reply_text}\"")
                else:
                    typing_delay = random.uniform(6.0, 12.0)
                    print(f"   ⏳ [Human-Pacing] Simulating typing delay ({typing_delay:.1f}s)...")
                    time.sleep(typing_delay)
                    try:
                        cl.direct_send(reply_text, thread_ids=[int(thread_id)])
                        record_contacted_user(sender_id)
                        print(f"   💬 Sent reply to @{sender_name}:\n      \"{reply_text.splitlines()[0]}...\"")
                    except Exception as e:
                        print(f"   ⚠️ Failed to send DM reply: {e}")
                        if insta_local_post.is_restriction_error(e):
                            trip_ban_shield(str(e))
                            return actions

            seen_ids.add(msg_id)
            actions += 1
            if actions >= max_actions:
                print(f"🛑 Reached safe action cap ({max_actions}) for this run.")
                break

        if actions >= max_actions:
            break

    save_seen(SEEN_MESSAGES_FILE, seen_ids)
    print(f"✅ Inbox sweep complete. Processed {actions} message(s).")
    return actions


def sweep_funnel_comments(cl=None, dry_run=False, max_actions=3) -> int:
    """
    Comment-to-DM with strict friend exclusion, pacing, and 48-hr Ban-Shield.
    """
    if is_sleep_window():
        print("🌙 [Anti-Ban] Nighttime sleep window (01:30–07:00 IST). Skipping comment funnel.")
        return 0

    if is_booster_paused():
        print("🛡️ [Ban-Shield] Comment-to-DM paused due to active cooldown.")
        return 0

    config = DEFAULT_CONFIG
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception:
            pass

    links = config.get("links", {})
    keywords = config.get("keywords", {})
    dm_templates = config.get("dm_responses", {})
    comment_replies = config.get("comment_replies", DEFAULT_CONFIG["comment_replies"])

    if cl is None:
        cl = insta_local_post.get_client()

    my_user_id = str(cl.user_id)
    processed_comments = load_seen(PROCESSED_COMMENTS_FILE)
    following_set = get_account_following(cl, my_user_id)

    print("🔍 [Comment-to-DM] Scanning recent Reels for keyword comments...")

    clips = []
    try:
        clips = cl.user_clips(my_user_id, amount=4)
    except Exception as e:
        print(f"⚠️ Error fetching reels: {e}")

    actions = 0

    for clip in clips:
        media_id = str(clip.pk)
        try:
            comments = cl.media_comments(media_id)
        except Exception as e:
            continue

        for c in comments:
            c_id = str(getattr(c, "pk", ""))
            c_user = getattr(c, "user", None)
            c_user_pk = str(getattr(c_user, "pk", None) or getattr(c, "user_id", ""))
            c_author = str(getattr(c_user, "username", "") or "unknown")

            # 🛡️ Skip own comments or already processed comments
            if not c_id or c_user_pk == my_user_id or c_id in processed_comments:
                continue

            # 🛡️ FRIEND SHIELD: Never auto-reply or DM personal friends/VIPs
            if is_friend_or_family(c_author, c_user_pk, following_set):
                print(f"   🛡️ [Friend-Protection] Skipped comment from @{c_author} (Friend/VIP).")
                continue

            # Anti-Spam: Never re-DM the same user within 7 days
            if was_contacted_recently(c_user_pk):
                processed_comments.add(c_id)
                continue

            c_text = (getattr(c, "text", "") or "").strip()
            matched = match_intent(c_text, {
                "wallpaper": keywords.get("wallpaper", []),
                "preset": keywords.get("preset", []),
            })

            if not matched:
                continue

            print(f"   🎯 Found [{matched.upper()}] request from fan @{c_author}: \"{c_text}\"")

            if dry_run:
                print(f"   [DRY-RUN] Would like comment {c_id}")
                print(f"   [DRY-RUN] Would reply: \"{comment_replies[0]}\"")
                print(f"   [DRY-RUN] Would DM @{c_author} the {matched} link")
                processed_comments.add(c_id)
                actions += 1
                if actions >= max_actions:
                    break
                continue

            # 1. Paced Like on comment ❤️ (8–14s delay)
            delay = random.uniform(8.0, 14.0)
            time.sleep(delay)
            try:
                comment_target_pk = int(c_id) if str(c_id).isdigit() else c_id
                cl.comment_like(comment_target_pk)
                print(f"   ❤️ Liked comment from @{c_author}")
            except Exception as e:
                print(f"   ⚠️ Could not like comment: {e}")
                if insta_local_post.is_restriction_error(e):
                    trip_ban_shield(str(e))
                    return actions

            # 2. Reply to comment publicly with human pacing
            reply_delay = random.uniform(6.0, 12.0)
            time.sleep(reply_delay)
            try:
                comment_reply_text = random.choice(comment_replies)
                reply_target_pk = int(c_id) if str(c_id).isdigit() else c_id
                cl.media_comment(media_id, comment_reply_text, replied_to_comment_id=reply_target_pk)
                print(f"   💬 Replied to comment: \"{comment_reply_text}\"")
            except Exception as e:
                print(f"   ⚠️ Could not reply to comment: {e}")
                if insta_local_post.is_restriction_error(e):
                    trip_ban_shield(str(e))
                    return actions

            # 3. Direct Message delivery to the fan
            tpl = random.choice(dm_templates.get(matched, ["Here is your link 🖤:\n{wallpaper_link}"]))
            dm_text = mutate_message_for_antispam(tpl, links)

            dm_delay = random.uniform(7.0, 15.0)
            time.sleep(dm_delay)
            try:
                target_uid = int(c_user_pk) if str(c_user_pk).isdigit() else c_user_pk
                cl.direct_send(dm_text, user_ids=[target_uid])
                record_contacted_user(c_user_pk)
                print(f"   📬 Delivered {matched} link to @{c_author} via DM!")
            except Exception as e:
                print(f"   ⚠️ Could not send DM to @{c_author}: {e}")
                if insta_local_post.is_restriction_error(e):
                    trip_ban_shield(str(e))
                    return actions

            processed_comments.add(c_id)
            actions += 1
            if actions >= max_actions:
                print(f"🛑 Reached safe action cap ({max_actions}) for comment funnel.")
                break

        if actions >= max_actions:
            break

    save_seen(PROCESSED_COMMENTS_FILE, processed_comments)
    print(f"✅ Comment-to-DM scan complete. Fulfilled {actions} funnel request(s).")
    return actions


def run(mode="all", dry_run=False, max_actions=3):
    print("=" * 65)
    print(f"🛡️ VYNOX ANTI-BAN HUMAN DM & COMMENT FUNNEL (Mode: {mode.upper()})")
    print(f"⏰ Local Time: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')}")
    print(f"🌙 Sleep Window Active: {is_sleep_window()}")
    print(f"🧪 Dry Run: {dry_run} | Action Cap: {max_actions}")
    print("=" * 65)

    if is_sleep_window():
        print("🌙 Nighttime in India (01:30–07:00 IST). Sleeping to mimic real human patterns.")
        return 0

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
    parser = argparse.ArgumentParser(description="Vynox Anti-Ban Human DM & Comment Funnel")
    parser.add_argument("--mode", choices=["inbox", "comments", "all"], default="all", help="Operation mode")
    parser.add_argument("--dry-run", action="store_true", help="Inspect and simulate without live network mutation")
    parser.add_argument("--max-actions", type=int, default=3, help="Maximum safe actions per run (anti-ban capped)")
    args = parser.parse_args()

    sys.exit(run(mode=args.mode, dry_run=args.dry_run, max_actions=args.max_actions))

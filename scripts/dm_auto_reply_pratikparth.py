#!/usr/bin/env python3
"""
Automated Instagram Reel & Message Auto-Responder for @pratikparth_12
Automatically double-taps (❤️) and responds to friends sending Reels & messages.
Designed for 24/7 cloud execution via GitHub Actions (no laptop needed).
"""

import os
import sys
import json
import time
import random
from pathlib import Path
from instagrapi import Client

BASE_DIR = Path(__file__).resolve().parent.parent
SESSION_DIR = Path.home() / ".config" / "stickman_video_director"
SESSION_FILE = SESSION_DIR / "insta_session_pratikparth_12.json"
STATE_FILE = BASE_DIR / "projects" / "dm_seen_pratikparth.json"
STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

# Casual, natural reel reactions
REEL_REPLIES = [
    "😂😂",
    "bro this is wild 🔥",
    "lmao good one 😂",
    "haha saw this!",
    "too accurate fr 💀",
    "😂😂 literally",
    "bhai kya hai ye 😂🔥"
]

def load_seen():
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_seen(seen_ids):
    recent = list(seen_ids)[-1000:]
    with open(STATE_FILE, "w") as f:
        json.dump(recent, f, indent=2)

def get_client():
    cl = Client()
    cl.delay_range = [1, 3]

    # Check environment variable first (for GitHub Actions CI)
    env_session = os.environ.get("INSTA_SESSION_PRATIKPARTH_JSON")
    if env_session:
        print("🔑 Restoring session from environment variable...")
        try:
            data = json.loads(env_session)
            cl.set_settings(data)
            cl.init()
            return cl
        except Exception as e:
            print(f"⚠️ Could not load session from env var: {e}")

    # Fallback to local session file
    if SESSION_FILE.exists():
        print(f"🔑 Loading local session from: {SESSION_FILE}")
        cl.load_settings(SESSION_FILE)
        return cl

    raise FileNotFoundError(f"Session not found at {SESSION_FILE} and INSTA_SESSION_PRATIKPARTH_JSON is not set.")

def run_responder(like_only=False, dry_run=False):
    cl = get_client()
    my_user_id = str(cl.user_id)
    print(f"👤 Connected as: @{cl.user_info(my_user_id).username} (ID: {my_user_id})")

    seen_ids = load_seen()
    print(f"📂 Loaded {len(seen_ids)} previously processed message IDs.")

    threads = cl.direct_threads(amount=10)
    print(f"📬 Scanning {len(threads)} active message threads...")

    processed_count = 0
    max_actions = 12  # safe limit per run

    for t in threads:
        users = [u.username for u in t.users if getattr(u, 'username', None)]
        # Skip official meta bots
        if any(u.lower() in ["meta ai", "instagram"] for u in users):
            continue

        thread_id = str(t.id)
        messages = cl.direct_messages(thread_id, amount=5)

        for msg in messages:
            msg_id = str(msg.id)
            sender_id = str(msg.user_id)

            # Skip messages sent by yourself or already processed
            if sender_id == my_user_id or msg_id in seen_ids:
                continue

            item_type = str(msg.item_type).lower()
            if "action_log" in item_type:
                continue
            is_reel = any(k in item_type for k in ["clip", "xma_clip", "media_share", "media", "video"])
            is_text = "text" in item_type

            sender_name = users[0] if users else sender_id
            print(f"\n📩 New {item_type} from @{sender_name} (Msg ID: {msg_id})")

            if dry_run:
                print(f"   [DRY-RUN] Would double-tap ❤️ like and send reply")
                seen_ids.add(msg_id)
                continue

            # 1. Double-tap Like (❤️)
            try:
                cl.direct_message_like(thread_id, msg.id)
                print(f"   ❤️ Liked {item_type} from @{sender_name}")
                time.sleep(random.uniform(1.2, 2.8))
            except Exception as e:
                print(f"   ⚠️ Like failed: {e}")

            # 2. Reply to Reel share
            if is_reel and not like_only:
                reply_text = random.choice(REEL_REPLIES)
                try:
                    cl.direct_answer(thread_id, reply_text)
                    print(f"   💬 Replied: \"{reply_text}\"")
                    time.sleep(random.uniform(1.5, 3.2))
                except Exception as e:
                    print(f"   ⚠️ Reply failed: {e}")

            seen_ids.add(msg_id)
            processed_count += 1
            if processed_count >= max_actions:
                print("🛑 Reached safe action threshold for this check.")
                break

        if processed_count >= max_actions:
            break

    save_seen(seen_ids)
    print(f"\n✨ Inbox sweep finished. Processed {processed_count} new interactions.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Inspect without liking or replying")
    parser.add_argument("--like-only", action="store_true", help="Only double-tap like, don't send text reply")
    args = parser.parse_args()

    run_responder(like_only=args.like_only, dry_run=args.dry_run)

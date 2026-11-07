#!/usr/bin/env python3
"""
Automated Instagram DM Auto-Responder for @vynox_00000
Detects incoming Reels and messages, likes them (double-tap ❤️), and sends fun replies.
Can run locally, as a cron job, or in GitHub Actions (without laptop on).
"""

import os
import sys
import json
import time
import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))
import insta_local_post

STATE_FILE = BASE_DIR / "projects" / "dm_seen_messages.json"
STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

REEL_REPLIES = [
    "😂😂",
    "bro this is wild 🔥",
    "lmao good one 😂",
    "haha saw this!",
    "too accurate fr 💀",
    "✨🪔"
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
    # Keep only the last 500 IDs to avoid file bloat
    recent = list(seen_ids)[-500:]
    with open(STATE_FILE, "w") as f:
        json.dump(recent, f, indent=2)

def process_inbox(auto_reply_text=True, dry_run=False):
    print("🔄 Initializing Instagram client...")
    cl = insta_local_post.get_client()
    my_user_id = str(cl.user_id)
    print(f"👤 Active user: @{cl.user_info(my_user_id).username} (ID: {my_user_id})")

    seen_ids = load_seen()
    print(f"📂 Loaded {len(seen_ids)} previously seen message IDs.")

    threads = cl.direct_threads(amount=10)
    print(f"📬 Retrieved {len(threads)} recent threads.")

    action_count = 0
    max_actions = 10  # safety cap per run

    for t in threads:
        # Skip official bots
        users = [u.username for u in t.users if getattr(u, 'username', None)]
        if any(u.lower() in ["meta ai", "instagram"] for u in users):
            continue

        thread_id = str(t.id)
        messages = cl.direct_messages(thread_id, amount=5)

        for msg in messages:
            msg_id = str(msg.id)
            sender_id = str(msg.user_id)

            # Skip messages sent by ourselves or already processed
            if sender_id == my_user_id or msg_id in seen_ids:
                continue

            item_type = str(msg.item_type).lower()
            print(f"\n📩 New message in thread with {users}: Type '{item_type}', ID: {msg_id}")

            is_reel_or_media = any(k in item_type for k in ["clip", "xma_clip", "media_share", "media", "video"])
            is_text = "text" in item_type

            if dry_run:
                print(f"   [DRY-RUN] Would like & reply to message {msg_id}")
                seen_ids.add(msg_id)
                continue

            # 1. Like the message (Double-tap ❤️)
            try:
                cl.direct_message_like(thread_id, msg.id)
                print(f"   ❤️ Liked message {msg_id}")
                time.sleep(random.uniform(1.0, 2.5))
            except Exception as e:
                print(f"   ⚠️ Could not like message {msg_id}: {e}")

            # 2. Reply to Reel share
            if is_reel_or_media and auto_reply_text:
                reply = random.choice(REEL_REPLIES)
                try:
                    cl.direct_answer(thread_id, reply)
                    print(f"   💬 Sent reply: \"{reply}\"")
                    time.sleep(random.uniform(1.5, 3.0))
                except Exception as e:
                    print(f"   ⚠️ Could not send reply: {e}")

            seen_ids.add(msg_id)
            action_count += 1
            if action_count >= max_actions:
                print("🛑 Reached safe action cap for this run.")
                break

        if action_count >= max_actions:
            break

    save_seen(seen_ids)
    print(f"\n✅ Inbox sweep complete. Processed {action_count} new messages.")

if __name__ == "__main__":
    process_inbox(auto_reply_text=True, dry_run=False)

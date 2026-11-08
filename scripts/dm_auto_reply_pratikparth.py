#!/usr/bin/env python3
"""
NexoraAI-Powered Instagram DM Auto-Responder for @pratikparth_12 (Private & Personal)
Uses NexoraAI V14.2 Neural-Symbolic Semantic Classifier to understand Reels & Messages.
Priority: Authentic Gen-Z Hinglish and contextual emojis with human-like delays.
"""

import os
import sys
import json
import time
import random
from pathlib import Path
from instagrapi import Client

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))

from nexora_ai_dm_brain import nexora_brain

SESSION_DIR = Path.home() / ".config" / "stickman_video_director"
SESSION_FILE = SESSION_DIR / "insta_session_pratikparth_12.json"
STATE_FILE = BASE_DIR / "projects" / "dm_seen_pratikparth.json"
STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

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
    env_session = os.environ.get("INSTA_SESSION_PRATIKPARTH_JSON") or os.environ.get("INSTA_SESSION_PRATIKPARTH")
    if env_session:
        print("🔑 Restoring session from environment variable...")
        try:
            data = json.loads(env_session)
            cl.set_settings(data)
            cl.init()
            return cl
        except Exception:
            import base64
            try:
                decoded = base64.b64decode(env_session).decode("utf-8")
                data = json.loads(decoded)
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

    print("⚠️ No session found locally or in environment secrets.")
    return None

def run_responder(max_targets=5, dry_run=False, emoji_priority=True):
    cl = get_client()
    if cl is None:
        print("🛑 Exiting: Session not available.")
        sys.exit(0)

    my_user_id = str(cl.user_id)
    username = cl.user_info(my_user_id).username
    print(f"👤 Connected as: @{username} (ID: {my_user_id})")

    seen_ids = load_seen()
    print(f"📂 Loaded {len(seen_ids)} previously processed message IDs.")

    threads = cl.direct_threads(amount=10)
    print(f"📬 Scanning active message threads...")

    processed_count = 0

    for t in threads:
        users = [u.username for u in t.users if getattr(u, 'username', None)]
        if any(u.lower() in ["meta ai", "instagram"] for u in users):
            continue

        thread_id = str(t.id)
        messages = cl.direct_messages(thread_id, amount=3)

        for msg in messages:
            msg_id = str(msg.id)
            sender_id = str(msg.user_id)

            # Skip messages sent by yourself or already processed
            if sender_id == my_user_id or msg_id in seen_ids:
                continue

            item_type = str(msg.item_type).lower()
            if "action_log" in item_type:
                continue

            raw_xma = getattr(msg, "raw_xma", {}) or {}
            sender_name = users[0] if users else sender_id
            msg_text = getattr(msg, "text", "") or ""

            # 1. Nexora AI Reel Analysis
            reel_data = None
            if any(k in item_type for k in ["clip", "xma_clip", "media_share", "media", "video"]):
                reel_data = nexora_brain.analyze_reel(raw_xma, cl=cl)

            # 2. Nexora AI Intent & Response Selection
            reply_text = nexora_brain.generate_response(
                item_type=item_type,
                text=msg_text,
                reel_meta=reel_data,
                emoji_priority=emoji_priority
            )

            intent_label = reel_data.get("intent", "text_intent") if reel_data else "text_intent"
            print(f"\n📩 [{processed_count+1}/{max_targets}] New from @{sender_name} [{item_type}]:")
            if msg_text:
                print(f"   💬 Text: \"{msg_text}\"")
            if reel_data and reel_data.get("caption"):
                print(f"   🎬 Reel Caption: \"{reel_data['caption'][:60]}...\"")
            print(f"   🧠 [NexoraAI Intent]: {intent_label} -> Response: \"{reply_text}\"")

            if dry_run:
                print(f"   [DRY-RUN] Liked & replied.")
                seen_ids.add(msg_id)
                processed_count += 1
                if processed_count >= max_targets:
                    break
                continue

            # 3. Double-tap Like (❤️)
            try:
                cl.direct_message_like(thread_id, msg.id)
                print(f"   ❤️ Double-tap liked message from @{sender_name}")
                time.sleep(random.uniform(1.8, 3.2))
            except Exception as e:
                print(f"   ⚠️ Like failed: {e}")

            # 4. Send Nexora AI Response
            if reply_text:
                try:
                    cl.direct_answer(thread_id, reply_text)
                    print(f"   💬 Sent reply: {reply_text}")
                    time.sleep(random.uniform(2.5, 4.0))
                except Exception as e:
                    print(f"   ⚠️ Reply failed: {e}")

            seen_ids.add(msg_id)
            processed_count += 1
            if processed_count >= max_targets:
                print(f"🛑 Reached target of {max_targets} pending interactions.")
                break

        if processed_count >= max_targets:
            break

    save_seen(seen_ids)
    print(f"\n✨ NexoraAI Inbox sweep complete. Processed {processed_count} interactions.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Inspect without liking or replying")
    parser.add_argument("--count", type=int, default=5, help="Number of messages to reply to")
    parser.add_argument("--text-mode", action="store_true", help="Prefer text responses over emojis")
    args = parser.parse_args()

    run_responder(max_targets=args.count, dry_run=args.dry_run, emoji_priority=not args.text_mode)

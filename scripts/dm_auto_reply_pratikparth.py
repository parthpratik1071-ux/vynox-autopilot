#!/usr/bin/env python3
"""
NexoraAI-Powered Instagram DM Auto-Responder for @pratikparth_12 (Private & Personal)
Uses NexoraAI V14.2 Neural-Symbolic Semantic Classifier to understand Reels & Messages.
Designed to behave 100% like a REAL HUMAN USER:
- Simulates opening chat (direct_send_seen)
- Smart message batching (1 reply per conversation burst, no multi-reply spam)
- Real human "Like-Only" probability for casual reel dumps
- Realistic viewing & typing delays
- Anti-repetition memory per contact
- IST Sleep Cycle guard (3:00 AM - 7:00 AM IST)
"""

import os
import sys
import json
import time
import random
from datetime import datetime, timezone, timedelta
from pathlib import Path
from instagrapi import Client

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))

from nexora_ai_dm_brain import nexora_brain

SESSION_DIR = Path.home() / ".config" / "stickman_video_director"
SESSION_FILE = SESSION_DIR / "insta_session_pratikparth_12.json"
STATE_FILE = BASE_DIR / "projects" / "dm_seen_pratikparth.json"
HISTORY_FILE = BASE_DIR / "projects" / "dm_recent_replies.json"
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

def load_recent_replies():
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_recent_replies(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

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

def run_responder(max_targets=5, dry_run=False, emoji_priority=True, ignore_sleep=False):
    # 1. Real Human Sleep Cycle Check (India IST: UTC+5:30)
    IST = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(IST)
    if not ignore_sleep and (3 <= now_ist.hour < 7):
        print(f"🌙 [Real Human Sleep Cycle]: It is {now_ist.strftime('%I:%M %p')} IST.")
        print(f"   Friends expect @pratikparth_12 to be asleep. Skipping auto-reply until morning.")
        return

    cl = get_client()
    if cl is None:
        print("🛑 Exiting: Session not available.")
        sys.exit(0)

    my_user_id = str(cl.user_id)
    username = cl.user_info(my_user_id).username
    print(f"👤 Connected as: @{username} (ID: {my_user_id})")

    seen_ids = load_seen()
    recent_replies = load_recent_replies()
    print(f"📂 Loaded {len(seen_ids)} previously processed message IDs.")

    threads = cl.direct_threads(amount=10)
    print(f"📬 Scanning active message threads...")

    processed_conversations = 0

    for t in threads:
        users = [u.username for u in t.users if getattr(u, 'username', None)]
        if any(u.lower() in ["meta ai", "instagram"] for u in users):
            continue

        thread_id = str(t.id)
        messages = cl.direct_messages(thread_id, amount=10)

        # Filter unprocessed incoming messages from this friend
        unprocessed = [
            m for m in messages
            if str(m.user_id) != my_user_id
            and str(m.id) not in seen_ids
            and "action_log" not in str(m.item_type).lower()
        ]

        if not unprocessed:
            continue

        # Sort chronologically (oldest to newest)
        unprocessed.sort(key=lambda m: getattr(m, "timestamp", 0) or 0)
        sender_name = users[0] if users else str(unprocessed[0].user_id)
        print(f"\n📬 Detected {len(unprocessed)} new interaction(s) from @{sender_name}:")

        # Step 1: Human opens the chat (Mark thread seen)
        if not dry_run:
            try:
                cl.direct_send_seen(int(thread_id))
                print(f"   👀 [Human Action]: Marked thread seen for @{sender_name}")
            except Exception:
                pass
            time.sleep(random.uniform(1.8, 3.5))

        # Step 2: Double-tap like the incoming messages with natural human pauses
        for m in unprocessed:
            m_id = str(m.id)
            m_type = str(m.item_type).lower()
            m_text = getattr(m, "text", "") or ""
            if m_text:
                print(f"   💬 Incoming: \"{m_text}\"")
            else:
                print(f"   🎬 Incoming: [{m_type}]")

            # Skip double-tap liking system logs or call events
            if any(k in m_type for k in ["call", "event", "action_log"]):
                seen_ids.add(m_id)
                continue

            if not dry_run:
                try:
                    cl.direct_message_like(thread_id, m.id)
                    print(f"   ❤️ Double-tap liked message {m_id}")
                    time.sleep(random.uniform(1.2, 2.5))
                except Exception as e:
                    print(f"   ⚠️ Like failed: {e}")
            seen_ids.add(m_id)

        # Step 3: Determine the single cohesive human response for this conversation burst
        has_call_event = any("call" in str(m.item_type).lower() for m in unprocessed)
        text_msgs = [
            m for m in unprocessed
            if "text" in str(m.item_type).lower() and (getattr(m, "text", "") or "").strip()
        ]
        latest_msg = unprocessed[-1]

        # Prioritize replying to the text message if the friend typed something alongside a reel
        reply_target = text_msgs[-1] if text_msgs else latest_msg
        reply_item_type = str(reply_target.item_type).lower()
        reply_text_content = getattr(reply_target, "text", "") or ""

        # Natural human touch: if only reels/clips were sent, real humans often just like (❤️)
        only_reels = (not text_msgs) and (not has_call_event) and all(
            any(k in str(m.item_type).lower() for k in ["clip", "media", "video"])
            for m in unprocessed
        )

        should_send_text_reply = True
        if only_reels:
            # ~30% chance to only like (❤️) without text (very common among close friends)
            if random.random() < 0.30:
                should_send_text_reply = False
                print(f"   👤 [Human Choice]: Liked only (no text reply sent, natural human friend behavior).")

        if should_send_text_reply:
            user_history = recent_replies.get(sender_name, [])

            if has_call_event and not text_msgs:
                call_options = [
                    "Call kiya tha kya bhai? Bol kya hua",
                    "Bahar tha thoda isliye utha nahi paya, bol kya scene?",
                    "Missed call dekha bhai, sab theek na? 😂",
                    "Ruk free hoke call lagata hu 👍"
                ]
                reply_text = random.choice([c for c in call_options if c not in user_history] or call_options)
                intent_label = "missed_call_response"
            else:
                reel_data = None
                raw_xma = getattr(reply_target, "raw_xma", {}) or {}
                if any(k in reply_item_type for k in ["clip", "xma_clip", "media_share", "media", "video"]):
                    reel_data = nexora_brain.analyze_reel(raw_xma, cl=cl)

                reply_text = nexora_brain.generate_response(
                    item_type=reply_item_type,
                    text=reply_text_content,
                    reel_meta=reel_data,
                    emoji_priority=emoji_priority,
                    recent_history=user_history
                )
                intent_label = reel_data.get("intent", "conversational_text") if reel_data else "conversational_text"

            print(f"   🧠 [NexoraAI Intent]: {intent_label} -> Response: \"{reply_text}\"")

            if dry_run:
                print(f"   [DRY-RUN] Liked & drafted reply: \"{reply_text}\"")
            else:
                # Realistic typing / thinking delay (3.5 - 6.5s)
                type_delay = random.uniform(3.5, 6.5)
                time.sleep(type_delay)
                try:
                    cl.direct_answer(thread_id, reply_text)
                    print(f"   💬 Sent reply to @{sender_name}: {reply_text}")
                    # Update anti-repetition memory
                    user_history.append(reply_text)
                    recent_replies[sender_name] = user_history[-5:]
                except Exception as e:
                    print(f"   ⚠️ Reply failed: {e}")

        processed_conversations += 1
        if processed_conversations >= max_targets:
            print(f"🛑 Reached target of {max_targets} conversations.")
            break

        # Human delay between interacting with different friends
        time.sleep(random.uniform(2.5, 5.0))

    if not dry_run:
        save_seen(seen_ids)
        save_recent_replies(recent_replies)
        print(f"💾 Committed updated seen message IDs and conversation history.")
    else:
        print(f"ℹ️ [DRY-RUN]: State not committed to disk.")

    print(f"\n✨ NexoraAI Inbox sweep complete. Processed {processed_conversations} conversation(s).")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Inspect without liking or replying")
    parser.add_argument("--count", type=int, default=5, help="Number of conversations to reply to")
    parser.add_argument("--text-mode", action="store_true", help="Prefer text responses over emojis")
    parser.add_argument("--ignore-sleep", action="store_true", help="Bypass real human sleep cycle check")
    args = parser.parse_args()

    run_responder(
        max_targets=args.count,
        dry_run=args.dry_run,
        emoji_priority=not args.text_mode,
        ignore_sleep=args.ignore_sleep
    )

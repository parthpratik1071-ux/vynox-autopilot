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
- Continuous monitoring mode with configurable sweep loop
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
PROJECTS_DIR = BASE_DIR / "projects"
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

# Blacklisted / Excluded Accounts & Threads (Family, siblings, or accounts that should NEVER be touched)
IGNORED_USERS = {
    "paras_kumar_thakur",
    "palak",
    "palak_thakur"
}
IGNORED_THREAD_IDS = {
    "340282366841710301244276067887556527788"
}
IGNORED_FILE = PROJECTS_DIR / "dm_ignored_users.json"
if IGNORED_FILE.exists():
    try:
        with open(IGNORED_FILE, "r") as f:
            custom_ignored = json.load(f)
            IGNORED_USERS.update([u.lower().strip() for u in custom_ignored])
    except Exception:
        pass

# Own Accounts Exclusions (Prevents Pratik & Vynox from ever messaging each other)
MANAGED_ACCOUNTS = {"pratikparth_12", "vynox_00000", "35566427576", "16183885323"}

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
            return cl
        except Exception:
            import base64
            try:
                decoded = base64.b64decode(env_session).decode("utf-8")
                data = json.loads(decoded)
                cl.set_settings(data)
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

def run_responder_cycle(cl, max_targets=5, dry_run=False, emoji_priority=True, ignore_sleep=False, target_user=None):
    # 1. Real Human Sleep Cycle Check (India IST: UTC+5:30)
    IST = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(IST)
    if not ignore_sleep and (3 <= now_ist.hour < 7):
        print(f"🌙 [Real Human Sleep Cycle]: It is {now_ist.strftime('%I:%M %p')} IST.")
        print(f"   Friends expect @pratikparth_12 to be asleep. Skipping auto-reply until morning.")
        return 0

    my_user_id = str(cl.user_id)
    seen_ids = load_seen()
    recent_replies = load_recent_replies()

    threads = cl.direct_threads(amount=15)
    processed_conversations = 0

    for t in threads:
        thread_id = str(t.id)

        # Strict exclusion check for explicitly ignored thread IDs (e.g. Sister Palak)
        if thread_id in IGNORED_THREAD_IDS:
            continue

        users = [u.username for u in t.users if getattr(u, 'username', None)]
        user_ids = [str(getattr(u, 'pk', '') or getattr(u, 'id', '')) for u in t.users]

        if any(u.lower() in ["meta ai", "instagram"] for u in users):
            continue

        # Strict self-account exclusion: never message between user's own accounts
        if (
            any(u.lower() in MANAGED_ACCOUNTS for u in users)
            or any(uid in MANAGED_ACCOUNTS for uid in user_ids)
            or any(m in (t.thread_title or "").lower() for m in MANAGED_ACCOUNTS)
        ):
            continue

        if target_user and not any(target_user.lower() in u.lower() for u in users):
            continue

        # Strict exclusion check: never touch family or ignored users
        is_excluded = (
            any(u.lower() in IGNORED_USERS for u in users)
            or any(uid in IGNORED_USERS for uid in user_ids)
            or any(ign in (t.thread_title or "").lower() for ign in IGNORED_USERS)
        )
        if is_excluded:
            continue

        # 🛡️ Personal Account Strict Whitelist Guard (@pratikparth_12):
        # Never randomly message friends or open-sweep private inbox.
        # ONLY interact if the contact is explicitly in the approved Brothers inner-circle or specified target!
        is_allowed_brother = any(
            any(b in (u or "").lower() for b in ["sarthak", "navneet", "jisan", "tiwari", "arpit", "sharma", "shadox", "roxit", "rohit", "akap", "akash"])
            for u in users
        )
        if not is_allowed_brother and not (target_user and any(target_user.lower() in u.lower() for u in users)):
            continue

        messages = cl.direct_messages(thread_id, amount=10)

        # Filter unprocessed incoming messages from this friend
        unprocessed = [
            m for m in messages
            if str(m.user_id) != my_user_id
            and str(m.id) not in seen_ids
            and "action_log" not in str(m.item_type).lower()
        ]

        # 🛡️ Real Human Freshness Guard:
        # Never react or reply to old/stale messages from hours or days ago.
        # Only process interactions received within the last 45 minutes.
        now = datetime.now()
        MAX_AGE_SECONDS = 45 * 60
        fresh_messages = []
        for m in unprocessed:
            msg_time = getattr(m, "timestamp", None)
            if isinstance(msg_time, datetime):
                if msg_time.tzinfo is not None:
                    msg_time = msg_time.astimezone().replace(tzinfo=None)
                age = (now - msg_time).total_seconds()
                if age > MAX_AGE_SECONDS:
                    seen_ids.add(str(m.id))
                    continue
            fresh_messages.append(m)

        unprocessed = fresh_messages
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

        # Step 2: Mark messages seen, but like ONLY the latest reel/message (don't like all msgs)
        likeable_msgs = [
            m for m in unprocessed
            if not any(k in str(m.item_type).lower() for k in ["call", "event", "action_log"])
        ]
        target_to_like = likeable_msgs[-1] if likeable_msgs else None

        for m in unprocessed:
            m_id = str(m.id)
            m_type = str(m.item_type).lower()
            m_text = getattr(m, "text", "") or ""
            if m_text:
                print(f"   💬 Incoming: \"{m_text}\"")
            else:
                print(f"   🎬 Incoming: [{m_type}]")

            # Like ONLY the latest message/reel in the batch, not all messages
            if not dry_run and target_to_like and str(m.id) == str(target_to_like.id):
                try:
                    cl.direct_message_like(thread_id, m.id)
                    print(f"   ❤️ Double-tap liked latest message {m_id} (skipped older to avoid spam)")
                    time.sleep(random.uniform(1.2, 2.5))
                except Exception as e:
                    print(f"   ⚠️ Like failed: {e}")
            seen_ids.add(m_id)

        # Step 3: Determine single cohesive human response
        has_call_event = any("call" in str(m.item_type).lower() for m in unprocessed)
        text_msgs = [
            m for m in unprocessed
            if "text" in str(m.item_type).lower() and (getattr(m, "text", "") or "").strip()
        ]
        latest_msg = unprocessed[-1]

        reply_target = text_msgs[-1] if text_msgs else latest_msg
        reply_item_type = str(reply_target.item_type).lower()
        reply_text_content = getattr(reply_target, "text", "") or ""

        should_send_text_reply = True

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
                    user_history.append(reply_text)
                    recent_replies[sender_name] = user_history[-5:]
                except Exception as e:
                    print(f"   ⚠️ Reply failed: {e}")

        processed_conversations += 1
        if processed_conversations >= max_targets:
            print(f"🛑 Reached target of {max_targets} conversations for this sweep.")
            break

        time.sleep(random.uniform(2.5, 5.0))

    if not dry_run and processed_conversations > 0:
        save_seen(seen_ids)
        save_recent_replies(recent_replies)
        print(f"💾 Committed updated seen message IDs and conversation history to disk.")

    return processed_conversations

def run_continuous_monitor(max_targets=5, dry_run=False, emoji_priority=True, ignore_sleep=False, loop_minutes=0, target_user=None):
    cl = get_client()
    if cl is None:
        print("🛑 Exiting: Session not available or invalid credentials.")
        sys.exit(1)

    my_user_id = str(cl.user_id)
    username = cl.user_info(my_user_id).username
    print(f"👤 Connected as: @{username} (ID: {my_user_id})")

    start_time = time.time()
    loop_duration = loop_minutes * 60

    if loop_minutes > 0:
        print(f"🔄 Starting continuous inbox monitor (duration: {loop_minutes}m)...")
    else:
        print(f"📬 Starting single inbox sweep...")

    cycle = 1
    total_processed = 0

    while True:
        try:
            IST = timezone(timedelta(hours=5, minutes=30))
            now_str = datetime.now(IST).strftime('%I:%M:%S %p')
            print(f"\n--- [Sweep #{cycle} @ {now_str} IST] ---")
            processed = run_responder_cycle(
                cl,
                max_targets=max_targets,
                dry_run=dry_run,
                emoji_priority=emoji_priority,
                ignore_sleep=ignore_sleep,
                target_user=target_user
            )
            total_processed += processed
        except Exception as e:
            print(f"⚠️ Error during inbox sweep: {e}")

        elapsed = time.time() - start_time
        if loop_minutes <= 0 or elapsed >= loop_duration:
            print(f"\n🏁 Finished monitor session ({elapsed/60:.1f}m elapsed, {total_processed} conversations handled).")
            break

        sleep_sec = random.uniform(45, 65)
        rem_min = int((loop_duration - elapsed) / 60)
        print(f"⏳ Sleeping {sleep_sec:.0f}s before next inbox check ({rem_min}m remaining in session)...")
        time.sleep(sleep_sec)
        cycle += 1

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Inspect without liking or replying")
    parser.add_argument("--count", type=int, default=5, help="Max conversations per sweep")
    parser.add_argument("--text-mode", action="store_true", help="Prefer text responses over emojis")
    parser.add_argument("--ignore-sleep", action="store_true", help="Bypass real human sleep cycle check")
    parser.add_argument("--loop-minutes", type=int, default=0, help="Minutes to keep monitoring continuously")
    parser.add_argument("--target-user", type=str, default=None, help="Filter to a specific username")
    args = parser.parse_args()

    run_continuous_monitor(
        max_targets=args.count,
        dry_run=args.dry_run,
        emoji_priority=not args.text_mode,
        ignore_sleep=args.ignore_sleep,
        loop_minutes=args.loop_minutes,
        target_user=args.target_user
    )

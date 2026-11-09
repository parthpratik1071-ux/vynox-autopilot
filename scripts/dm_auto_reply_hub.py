#!/usr/bin/env python3
"""
NexoraAI Multi-Account Instagram DM Auto-Responder Hub
Handles ALL configured Instagram accounts simultaneously (e.g., @pratikparth_12, @vynox_00000, and new accounts):
- Auto-discovers local session files and environment secrets
- Employs NexoraAI V14.2 Neural Personality & Emotion Engine
- Marks thread seen (direct_send_seen)
- Likes ONLY the latest reel/message (avoids multi-like spam)
- Replies with authentic context-matched emojis and Gen-Z Hinglish
- Isolates seen state and anti-repetition memory per account
- Runs continuously 24/7 in GitHub Actions or locally
"""

import os
import sys
import json
import time
import random
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path
from instagrapi import Client

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))

from nexora_ai_dm_brain import nexora_brain
from emergency_alerter import alerter
from voice_engine import voice_engine
from reels_booster import reels_booster

SESSION_DIR = Path.home() / ".config" / "stickman_video_director"
SESSION_DIR.mkdir(parents=True, exist_ok=True)
PROJECTS_DIR = BASE_DIR / "projects"
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

# Blacklisted / Excluded Accounts & Threads (Family, siblings, or accounts that should NEVER be touched by auto-reply)
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

class AccountManager:
    """
    Manages authentication and state for a specific Instagram account.
    """
    def __init__(self, identifier: str, session_data: dict = None, session_file: Path = None):
        self.identifier = identifier
        self.session_data = session_data
        self.session_file = session_file
        self.cl = None
        self.user_id = None
        self.username = None

        # Per-account state files
        self.state_file = PROJECTS_DIR / f"dm_seen_{identifier}.json"
        self.history_file = PROJECTS_DIR / f"dm_recent_replies_{identifier}.json"

    def load_seen(self) -> set:
        if self.state_file.exists():
            try:
                with open(self.state_file, "r") as f:
                    return set(json.load(f))
            except Exception:
                return set()
        return set()

    def save_seen(self, seen_ids: set):
        recent = list(seen_ids)[-1000:]
        with open(self.state_file, "w") as f:
            json.dump(recent, f, indent=2)

    def load_history(self) -> dict:
        if self.history_file.exists():
            try:
                with open(self.history_file, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_history(self, history: dict):
        with open(self.history_file, "w") as f:
            json.dump(history, f, indent=2)

    def connect(self) -> bool:
        self.cl = Client()
        self.cl.delay_range = [1, 3]

        if self.session_data:
            try:
                self.cl.set_settings(self.session_data)
                self.user_id = str(self.cl.user_id)
                self.username = self.cl.user_info(self.user_id).username
                print(f"👤 Connected as: @{self.username} (ID: {self.user_id}) [via env session]")
                return True
            except Exception as e:
                print(f"⚠️ Failed to connect account {self.identifier} via env session: {e}")
                return False

        if self.session_file and self.session_file.exists():
            try:
                self.cl.load_settings(self.session_file)
                self.user_id = str(self.cl.user_id)
                self.username = self.cl.user_info(self.user_id).username
                print(f"👤 Connected as: @{self.username} (ID: {self.user_id}) [via {self.session_file.name}]")
                return True
            except Exception as e:
                print(f"⚠️ Failed to connect account {self.identifier} via file: {e}")
                return False

        return False

    def sweep_inbox(self, max_targets=5, dry_run=False, emoji_priority=True, ignore_sleep=False, target_user=None) -> int:
        if not self.cl:
            return 0

        # Check sleep cycle for personal accounts (3 AM - 7 AM IST)
        IST = timezone(timedelta(hours=5, minutes=30))
        now_ist = datetime.now(IST)
        if not ignore_sleep and (3 <= now_ist.hour < 7):
            print(f"🌙 [Real Human Sleep Cycle]: It is {now_ist.strftime('%I:%M %p')} IST.")
            print(f"   Friends expect @{self.username} to be asleep. Skipping auto-reply until morning.")
            return 0

        seen_ids = self.load_seen()
        recent_replies = self.load_history()

        # Own Accounts Exclusions (Prevents Pratik & Vynox from ever messaging each other)
        MANAGED_ACCOUNTS = {"pratikparth_12", "vynox_00000", "35566427576", "16183885323"}
        if self.username:
            MANAGED_ACCOUNTS.add(self.username.lower())
        if self.user_id:
            MANAGED_ACCOUNTS.add(str(self.user_id))

        threads = self.cl.direct_threads(amount=15)
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
            if "pratikparth" in (self.username or "").lower():
                is_allowed_brother = any(
                    any(b in (u or "").lower() for b in ["sarthak", "navneet", "jisan", "tiwari", "arpit", "sharma", "shadox", "roxit", "rohit", "akap", "akash"])
                    for u in users
                )
                if not is_allowed_brother and not (target_user and any(target_user.lower() in u.lower() for u in users)):
                    continue

            thread_id = str(t.id)
            messages = self.cl.direct_messages(thread_id, amount=10)

            unprocessed = [
                m for m in messages
                if str(m.user_id) != self.user_id
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
                        # Silently mark stale message as seen without any reaction or reply
                        seen_ids.add(str(m.id))
                        continue
                fresh_messages.append(m)

            unprocessed = fresh_messages
            if not unprocessed:
                continue

            unprocessed.sort(key=lambda m: getattr(m, "timestamp", 0) or 0)
            sender_name = users[0] if users else str(unprocessed[0].user_id)
            print(f"\n📬 [@{self.username}] Detected {len(unprocessed)} new interaction(s) from @{sender_name}:")

            # Emergency Alert Detection
            is_emergency = alerter.check_for_emergency(sender_name, unprocessed)
            if is_emergency:
                print(f"   🚨 [EMERGENCY DETECTED] Immediate alert logged & dispatched for @{sender_name}!")

            # 1. Human Action: Mark thread seen
            if not dry_run:
                try:
                    self.cl.direct_send_seen(int(thread_id))
                    print(f"   👀 [Human Action]: Marked thread seen for @{sender_name}")
                except Exception:
                    pass
                time.sleep(random.uniform(1.8, 3.2))

            # 2. Mark messages seen, but like ONLY the latest reel/message (anti-spam)
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

                # Like ONLY the latest message/reel in the burst
                if not dry_run and target_to_like and str(m.id) == str(target_to_like.id):
                    try:
                        self.cl.direct_message_like(thread_id, m.id)
                        print(f"   ❤️ Double-tap liked latest message {m_id} (skipped older to avoid spam)")
                        time.sleep(random.uniform(1.2, 2.5))
                    except Exception as e:
                        print(f"   ⚠️ Like failed: {e}")
                seen_ids.add(m_id)

            # 3. Determine single cohesive human response
            has_call_event = any("call" in str(m.item_type).lower() for m in unprocessed)
            text_msgs = [
                m for m in unprocessed
                if "text" in str(m.item_type).lower() and (getattr(m, "text", "") or "").strip()
            ]
            latest_msg = unprocessed[-1]

            if text_msgs:
                reply_target = text_msgs[-1]
                reply_item_type = "text"
                # Join all text messages in the burst so conversational context is fully understood
                reply_text_content = " ".join([getattr(m, "text", "").strip() for m in text_msgs if getattr(m, "text", "").strip()])
            else:
                reply_target = latest_msg
                reply_item_type = str(reply_target.item_type).lower()
                reply_text_content = getattr(reply_target, "text", "") or ""

            # Check for incoming voice note to transcribe
            if any(k in reply_item_type for k in ["voice", "audio"]):
                audio_url = None
                vm = getattr(reply_target, "voice_media", None)
                if vm and hasattr(vm, "media") and hasattr(vm.media, "audio"):
                    audio_url = getattr(vm.media.audio, "audio_src", None)
                if not audio_url:
                    raw_xma = getattr(reply_target, "raw_xma", {}) or {}
                    audio_url = raw_xma.get("audio_src") or raw_xma.get("url")

                if audio_url:
                    print(f"   🎙️ [Voice-Note] Transcribing incoming audio from @{sender_name}...")
                    transcribed = voice_engine.transcribe_audio(audio_url)
                    if transcribed:
                        reply_text_content = transcribed

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
                    reel_data = nexora_brain.analyze_reel(raw_xma, cl=self.cl)

                reply_text = nexora_brain.generate_response(
                    item_type=reply_item_type,
                    text=reply_text_content,
                    reel_meta=reel_data,
                    emoji_priority=emoji_priority,
                    recent_history=user_history,
                    sender_username=sender_name
                )
                intent_label = reel_data.get("intent", "conversational_text") if reel_data else "conversational_text"

            print(f"   🧠 [NexoraAI Intent]: {intent_label} -> Response: \"{reply_text}\"")

            if dry_run:
                print(f"   [DRY-RUN] Liked & drafted reply: \"{reply_text}\"")
            else:
                type_delay = random.uniform(3.5, 6.0)
                time.sleep(type_delay)

                # Check if we should reply with a spoken voice note
                should_voice_reply = (
                    any(k in reply_item_type for k in ["voice", "audio"])
                    or any(w in (reply_text_content or "").lower() for w in ["voice note", "bol ke bata", "voice bhej"])
                ) and not emoji_priority

                if should_voice_reply:
                    voice_file = voice_engine.generate_voice_note(reply_text)
                    if voice_file:
                        try:
                            self.cl.direct_send_voice(voice_file, thread_ids=[int(thread_id)])
                            print(f"   🎙️ [Voice-Reply] Sent native Instagram voice note to @{sender_name}!")
                        except Exception as e:
                            print(f"   ⚠️ Voice send failed, falling back to text: {e}")
                            self.cl.direct_send(reply_text, thread_ids=[int(thread_id)])
                            print(f"   💬 Sent text reply to @{sender_name}: {reply_text}")
                        if os.path.exists(voice_file):
                            os.unlink(voice_file)
                    else:
                        self.cl.direct_send(reply_text, thread_ids=[int(thread_id)])
                        print(f"   💬 Sent reply to @{sender_name}: {reply_text}")
                else:
                    try:
                        self.cl.direct_send(reply_text, thread_ids=[int(thread_id)])
                        print(f"   💬 Sent reply to @{sender_name}: {reply_text}")
                    except Exception as e:
                        print(f"   ⚠️ Reply failed: {e}")

                user_history.append(reply_text)
                recent_replies[sender_name] = user_history[-5:]

            processed_conversations += 1
            if processed_conversations >= max_targets:
                break

            time.sleep(random.uniform(2.5, 4.5))

        # Brand account algorithm booster check (e.g. @vynox_00000)
        if "vynox" in self.username.lower():
            reels_booster.boost_latest_reel(self.cl, dry_run=dry_run)

        if not dry_run and processed_conversations > 0:
            self.save_seen(seen_ids)
            self.save_history(recent_replies)
            print(f"💾 [@{self.username}] Committed updated state to disk.")

        return processed_conversations

def discover_accounts() -> list:
    """
    Discovers all configured Instagram accounts across environment variables and session files.
    """
    accounts = []

    # 1. Discover via environment variables
    env_mappings = [
        ("pratikparth_12", ["INSTA_SESSION_PRATIKPARTH_JSON", "INSTA_SESSION_PRATIKPARTH"]),
        ("vynox_00000", ["INSTA_SESSION_JSON", "INSTA_SESSION_VYNOX_JSON", "INSTA_SESSION"])
    ]

    for identifier, keys in env_mappings:
        for k in keys:
            val = os.environ.get(k)
            if val:
                try:
                    data = json.loads(val)
                    accounts.append(AccountManager(identifier, session_data=data))
                    break
                except Exception:
                    import base64
                    try:
                        decoded = base64.b64decode(val).decode("utf-8")
                        data = json.loads(decoded)
                        accounts.append(AccountManager(identifier, session_data=data))
                        break
                    except Exception:
                        pass

    # 2. Discover via local session files
    file_mappings = [
        ("pratikparth_12", SESSION_DIR / "insta_session_pratikparth_12.json"),
        ("vynox_00000", SESSION_DIR / "insta_session.json")
    ]

    existing_ids = {a.identifier for a in accounts}
    for identifier, file_path in file_mappings:
        if identifier not in existing_ids and file_path.exists():
            accounts.append(AccountManager(identifier, session_file=file_path))
            existing_ids.add(identifier)

    # 3. Dynamic scan for any other insta_session_*.json in session directory
    for f in SESSION_DIR.glob("insta_session_*.json"):
        ident = f.stem.replace("insta_session_", "")
        if ident not in existing_ids:
            accounts.append(AccountManager(ident, session_file=f))
            existing_ids.add(ident)

    return accounts

def add_new_account(username, password):
    """
    Logs in a brand new Instagram account, sets modern mobile device profile, and saves session.
    """
    print(f"🔄 Authenticating new account @{username}...")
    cl = Client()
    cl.delay_range = [1, 3]
    # Modern Pixel 8 Pro device profile
    cl.set_device({
        "app_version": "449.0.0.52.84",
        "android_version": 34,
        "android_release": "14",
        "dpi": "480dpi",
        "resolution": "1080x2400",
        "manufacturer": "Google",
        "device": "husky",
        "model": "Pixel 8 Pro",
        "cpu": "arm64-v8a",
        "version_code": "1079242191"
    })
    cl.set_user_agent("Instagram 449.0.0.52.84 Android (34/14; 480dpi; 1080x2400; Google; Pixel 8 Pro; husky; arm64-v8a; en_US; 1079242191)")

    try:
        cl.login(username, password)
        session_file = SESSION_DIR / f"insta_session_{username}.json"
        cl.dump_settings(session_file)
        session_file.chmod(0o600)
        print(f"✅ Successfully logged in and saved session to {session_file}")
        return True
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return False

def run_hub(max_targets=5, dry_run=False, emoji_priority=True, ignore_sleep=False, loop_minutes=0, target_user=None, account_filter=None, daemon=False):
    accounts = discover_accounts()
    if account_filter:
        accounts = [a for a in accounts if account_filter.lower() in a.identifier.lower()]

    if not accounts:
        print("🛑 No Instagram accounts found or configured.")
        sys.exit(1)

    print(f"🌐 [NexoraAI Hub] Initializing {len(accounts)} Instagram Account(s):")
    connected_accounts = []
    for acc in accounts:
        if acc.connect():
            connected_accounts.append(acc)

    if not connected_accounts:
        print("🛑 Failed to connect to any Instagram account.")
        sys.exit(1)

    start_time = time.time()
    loop_duration = loop_minutes * 60

    if daemon:
        print(f"\n🔄 [24/7 Daemon] Starting perpetual multi-account continuous monitor...")
    elif loop_minutes > 0:
        print(f"\n🔄 Starting multi-account continuous monitor (duration: {loop_minutes}m)...")
    else:
        print(f"\n📬 Starting single multi-account sweep...")

    cycle = 1
    total_processed = 0

    while True:
        IST = timezone(timedelta(hours=5, minutes=30))
        now_str = datetime.now(IST).strftime('%I:%M:%S %p')
        print(f"\n==================================================")
        print(f"--- [Multi-Account Sweep #{cycle} @ {now_str} IST] ---")
        print(f"==================================================")

        for acc in connected_accounts:
            try:
                processed = acc.sweep_inbox(
                    max_targets=max_targets,
                    dry_run=dry_run,
                    emoji_priority=emoji_priority,
                    ignore_sleep=ignore_sleep,
                    target_user=target_user
                )
                total_processed += processed
            except Exception as e:
                print(f"⚠️ Error sweeping @{acc.username}: {e}")

            time.sleep(random.uniform(2.0, 4.0))

        elapsed = time.time() - start_time
        if not daemon and (loop_minutes <= 0 or elapsed >= loop_duration):
            print(f"\n🏁 Finished multi-account session ({elapsed/60:.1f}m elapsed, {total_processed} conversations handled).")
            break

        sleep_sec = random.uniform(45, 65)
        if daemon:
            print(f"\n⏳ Sleeping {sleep_sec:.0f}s before next inbox check (24/7 perpetual daemon active)...")
        else:
            rem_min = int((loop_duration - elapsed) / 60)
            print(f"\n⏳ Sleeping {sleep_sec:.0f}s before next inbox check ({rem_min}m remaining in session)...")
        time.sleep(sleep_sec)
        cycle += 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Inspect without liking or replying")
    parser.add_argument("--count", type=int, default=5, help="Max conversations per account per sweep")
    parser.add_argument("--text-mode", action="store_true", help="Prefer text responses over emojis")
    parser.add_argument("--ignore-sleep", action="store_true", help="Bypass real human sleep cycle check")
    parser.add_argument("--loop-minutes", type=int, default=0, help="Minutes to keep monitoring continuously")
    parser.add_argument("--daemon", action="store_true", help="Run continuously forever in perpetual 24/7 background mode")
    parser.add_argument("--account", type=str, default=None, help="Specific account to run (e.g. pratikparth_12 or vynox_00000)")
    parser.add_argument("--target-user", type=str, default=None, help="Filter to a specific friend username")
    parser.add_argument("--add-account", type=str, default=None, help="Username of new account to add")
    parser.add_argument("--password", type=str, default=None, help="Password of new account to add")
    args = parser.parse_args()

    if args.add_account:
        if not args.password:
            print("❌ --password required when using --add-account")
            sys.exit(1)
        add_new_account(args.add_account, args.password)
        sys.exit(0)

    run_hub(
        max_targets=args.count,
        dry_run=args.dry_run,
        emoji_priority=not args.text_mode,
        ignore_sleep=args.ignore_sleep,
        loop_minutes=args.loop_minutes,
        target_user=args.target_user,
        account_filter=args.account,
        daemon=args.daemon
    )


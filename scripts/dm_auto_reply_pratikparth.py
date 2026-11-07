#!/usr/bin/env python3
"""
Context & Emotion-Aware Instagram DM Responder for @pratikparth_12 (Private & Personal)
Priority: Maximum emoji replies for fast, authentic Gen-Z friend vibes.
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

def get_emotion_reply(item_type, text=None, raw_xma=None, is_placeholder=False):
    """
    Intelligently analyzes the context, mood, and content of incoming messages and reels.
    Returns emoji-first authentic responses.
    """
    if is_placeholder:
        return random.choice(["😂💀", "💀🤷‍♂️", "😂😂"])

    text_lower = (text or "").lower().strip()

    # 1. Text Messages (Emoji priority)
    if "text" in item_type and text_lower:
        if any(w in text_lower for w in ["diwali", "deepavali"]):
            return random.choice(["✨🪔❤️", "🪔✨", "✨🙏"])
        if any(w in text_lower for w in ["call", "phone", "uthana", "utha", "urgent"]):
            return random.choice(["📞 5 min bhai", "ruk call karta hu 👍", "📞👍"])
        if any(w in text_lower for w in ["kaisa hai", "kya haal", "sab sahi", "wassup", "sup"]):
            return random.choice(["ekdum badiya bhai 👍🔥", "mast bhai tu bata 🙌", "all good 👍"])
        if any(w in text_lower for w in ["marna mat", "jane de", "mat kar", "haha", "lmao", "lol", "xd", "😂", "💀"]):
            return random.choice(["😂😂💀", "😭😭😂", "💀👍", "😂💀"])
        if any(w in text_lower for w in ["thanks", "thank you", "thx"]):
            return random.choice(["❤️🙌", "🙌👍", "❤️"])
        return random.choice(["👍😂", "🙌🔥", "👍"])

    # 2. Reel / Video Clip (Emoji priority)
    reel_creator = ""
    if raw_xma and "xma_clip" in raw_xma:
        clips = raw_xma["xma_clip"]
        if clips and isinstance(clips, list):
            reel_creator = (clips[0].get("header_title_text") or clips[0].get("username") or "").lower()

    # Animals / Pets
    if any(k in reel_creator for k in ["cat", "dog", "kitten", "puppy", "paw", "animal", "pet"]):
        return random.choice(["🥺❤️", "😭❤️", "😂❤️", "🐱❤️"])

    # Cricket / Sports
    if any(k in reel_creator for k in ["cricket", "cric", "ipl", "virat", "rohit", "sports", "football"]):
        return random.choice(["🔥🏏", "🐐🔥", "🔥🔥"])

    # Gym / Motivation
    if any(k in reel_creator for k in ["gym", "fitness", "workout", "grind", "motivation"]):
        return random.choice(["💪🔥", "💀💪", "🔥💪"])

    # Memes / Relatable / Comedy (Sheetalbeingreal, etc.)
    if any(k in reel_creator for k in ["sheetal", "meme", "dank", "sarcasm", "shitpost", "troll", "bakchodi", "desi"]):
        return random.choice(["😂😂💀", "😭😭😂", "💀💀", "😂😂", "🔥💀"])

    # Default Reel emoji reactions
    return random.choice(["😂😂💀", "😭😭😂", "💀💀", "😂😂", "🔥💀"])

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

    env_session = os.environ.get("INSTA_SESSION_PRATIKPARTH_JSON")
    if env_session:
        try:
            data = json.loads(env_session)
            cl.set_settings(data)
            cl.init()
            return cl
        except Exception:
            import base64
            try:
                decoded = base64.b64decode(env_session).decode()
                data = json.loads(decoded)
                cl.set_settings(data)
                cl.init()
                return cl
            except Exception as e:
                print(f"⚠️ Could not load session from env var: {e}")

    if SESSION_FILE.exists():
        print(f"🔑 Loading local session from: {SESSION_FILE}")
        cl.load_settings(SESSION_FILE)
        return cl

    raise FileNotFoundError(f"Session not found at {SESSION_FILE} and INSTA_SESSION_PRATIKPARTH_JSON is not set.")

def run_responder(max_targets=5, dry_run=False):
    cl = get_client()
    my_user_id = str(cl.user_id)
    print(f"👤 Connected to: @{cl.user_info(my_user_id).username} (ID: {my_user_id})")

    seen_ids = load_seen()
    print(f"📂 Loaded {len(seen_ids)} previously processed message IDs.")

    threads = cl.direct_threads(amount=10)
    print(f"📬 Scanning active threads for pending messages...")

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

            if sender_id == my_user_id or msg_id in seen_ids:
                continue

            item_type = str(msg.item_type).lower()
            if "action_log" in item_type:
                continue

            is_placeholder = False
            raw_xma = getattr(msg, "raw_xma", {}) or {}
            if raw_xma and "xma_clip" in raw_xma:
                for c in raw_xma.get("xma_clip", []):
                    if c.get("ig_template_type") == "placeholder" or c.get("title_text") == "Message unavailable":
                        is_placeholder = True
                        break

            sender_name = users[0] if users else sender_id
            msg_text = getattr(msg, "text", "") or ""

            # Pick emoji response
            reply_text = get_emotion_reply(item_type, text=msg_text, raw_xma=raw_xma, is_placeholder=is_placeholder)

            print(f"\n📩 [{processed_count+1}/{max_targets}] Pending message from @{sender_name} ({item_type}):")
            if msg_text:
                print(f"   Text: \"{msg_text}\"")
            print(f"   Picked Emoji Reply: {reply_text}")

            if dry_run:
                print(f"   [DRY-RUN] Liked & replied.")
                seen_ids.add(msg_id)
                processed_count += 1
                if processed_count >= max_targets:
                    break
                continue

            # 1. Double-tap Like (❤️)
            try:
                cl.direct_message_like(thread_id, msg.id)
                print(f"   ❤️ Double-tap liked message from @{sender_name}")
                time.sleep(random.uniform(1.8, 3.2))
            except Exception as e:
                print(f"   ⚠️ Like failed: {e}")

            # 2. Send Emoji Reply
            try:
                cl.direct_answer(thread_id, reply_text)
                print(f"   💬 Sent emoji reply: {reply_text}")
                time.sleep(random.uniform(2.5, 4.0))
            except Exception as e:
                print(f"   ⚠️ Reply failed: {e}")

            seen_ids.add(msg_id)
            processed_count += 1
            if processed_count >= max_targets:
                print(f"🛑 Reached target of {max_targets} pending messages.")
                break

        if processed_count >= max_targets:
            break

    save_seen(seen_ids)
    print(f"\n🎉 Successfully processed {processed_count} pending messages!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Inspect without liking or replying")
    parser.add_argument("--count", type=int, default=5, help="Number of messages to reply to")
    args = parser.parse_args()

    run_responder(max_targets=args.count, dry_run=args.dry_run)

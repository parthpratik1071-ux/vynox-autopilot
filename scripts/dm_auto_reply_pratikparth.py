#!/usr/bin/env python3
"""
Context & Emotion-Aware Instagram DM Responder for @pratikparth_12 (Private & Personal)
Understands emotional tone of reels and text messages to reply like a real friend.
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

def get_emotion_reply(item_type, text=None, raw_xma=None):
    """
    Intelligently analyzes the context, mood, and content of incoming messages and reels.
    Returns natural, authentic Hinglish replies tailored for close friends.
    """
    text_lower = (text or "").lower().strip()

    # 1. Contextual Text Messages
    if "text" in item_type and text_lower:
        if any(w in text_lower for w in ["diwali", "deepavali"]):
            return random.choice([
                "Same to you bhai! ✨🪔 Tere aur poori family ko Happy Diwali!",
                "Happy Diwali bhai! 🪔 Khushiyan aur mithai bhar bhar ke mile tujhe! ✨",
                "Shubh Deepavali bhai! ✨🪔 Mast celebrate kar!"
            ])
        if any(w in text_lower for w in ["call", "phone", "uthana", "utha", "urgent"]):
            return random.choice([
                "Thoda busy tha bhai, abhi thodi der me call karta hu 👍",
                "Haan ruk bhai, abhi free hoke turant lagata hu phone",
                "Dekha message, 10 min me call karta hu bhai"
            ])
        if any(w in text_lower for w in ["kaisa hai", "kya haal", "sab sahi", "wassup", "sup", "how are you"]):
            return random.choice([
                "Sab badhiya bhai! Tu bata kya chal raha hai aaj kal?",
                "Ekdum mast bhai, tu suna kya scene hai?",
                "All good bhai! Tu kaisa hai?"
            ])
        if any(w in text_lower for w in ["kahan hai", "kidhar hai", "where are you", "kaha hai"]):
            return random.choice([
                "Bas yahi hu bhai, bol kya scene hai?",
                "Ghar pe hi hu bhai, bata kya hua?",
                "Yahi aas paas hi hu bhai, bol"
            ])
        if any(w in text_lower for w in ["plan", "scene", "chale", "chalte", "bahar", "milte", "kal"]):
            return random.choice([
                "Bata kab aur kahan ka scene ban raha hai?",
                "Haan bhai chalte hai, time aur jagah bata",
                "Bata kya plan hai? Done karte hai"
            ])
        if any(w in text_lower for w in ["sun", "bhai", "bro", "oi", "oye", "oyee"]):
            return random.choice([
                "Haan bol bhai, sab theek?",
                "Haan bol bhai kya hua?",
                "Bol na bhai, sun raha hu"
            ])
        if any(w in text_lower for w in ["haha", "lmao", "lol", "xd", "😂", "💀", "rofl"]):
            return random.choice([
                "Bhai alag hi bakchodi hai 😂",
                "Mast tha na ye 😂",
                "Hass hass ke bura haal ho gaya 😂💀"
            ])
        if any(w in text_lower for w in ["thanks", "thank you", "thx", "shukriya"]):
            return random.choice([
                "Arre welcome bhai! Anytime 🙌",
                "Mention not bhai ❤️",
                "Arre koi na bhai apna hi scene hai 👍"
            ])
        # Default natural acknowledgments
        return random.choice([
            "Sahi hai bhai 👍",
            "Haan bhai samjha",
            "Badiya 👍",
            "Done bhai"
        ])

    # 2. Contextual Reel / Video Clip
    reel_creator = ""
    if raw_xma and "xma_clip" in raw_xma:
        clips = raw_xma["xma_clip"]
        if clips and isinstance(clips, list):
            reel_creator = (clips[0].get("header_title_text") or clips[0].get("username") or "").lower()

    # Cute Animals / Pets
    if any(k in reel_creator for k in ["cat", "dog", "kitten", "puppy", "paw", "animal", "pet"]):
        return random.choice([
            "Aww so cute yaar 😭❤️",
            "Cat/dog reels are pure therapy fr 🥺❤️",
            "Kitna cute hai ye yaar 😂❤️",
            "Bhai ye video kitni pyari hai yaar 🥺❤️"
        ])

    # Cricket / Sports / Hype
    if any(k in reel_creator for k in ["cricket", "cric", "ipl", "virat", "rohit", "sports", "football"]):
        return random.choice([
            "Bhai absolute goosebumps 🔥🏏",
            "GOAT behavior fr 🐐🔥",
            "Khatarnak moment tha ye bhai 🔥",
            "Kya player hai yaar alag hi level 🏏🔥"
        ])

    # Gym / Fitness / Grind
    if any(k in reel_creator for k in ["gym", "fitness", "workout", "grind", "motivation"]):
        return random.choice([
            "Motivation mil gayi, kal se pakka grind shuru 💪🔥",
            "Us bhai us, bas regularity chahiye ab 💀💪",
            "Form ekdum peak pe hai bhai 💪🔥"
        ])

    # Memes / Dank / Comedy / Sarcasm
    if any(k in reel_creator for k in ["meme", "dank", "sarcasm", "shitpost", "troll", "bakchodi", "desi", "btech"]):
        return random.choice([
            "Bhai ye to direct narak leke jayega 💀💀",
            "I should not be laughing at this 😭💀",
            "Literally us moment ho gaya ye to 😭😂",
            "Bhai hass hass ke pagal ho gaya 😂💀",
            "Too accurate bhai kahan se dhoondte ho aisi reels 😂"
        ])

    # Default relatable friend reaction
    return random.choice([
        "Bhai literally ye kya tha 😂💀",
        "Lmao too accurate bhai 😭",
        "Mast reel thi ye fr 😂🔥",
        "Hahah epic bhai 😂",
        "Bhai ye sach me bohot sahi tha 😂🔥"
    ])

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
        print("🔑 Restoring session from environment variable...")
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

def run_responder(dry_run=False):
    cl = get_client()
    my_user_id = str(cl.user_id)
    print(f"👤 Connected to private account: @{cl.user_info(my_user_id).username} (ID: {my_user_id})")

    seen_ids = load_seen()
    print(f"📂 Loaded {len(seen_ids)} previously processed message IDs.")

    threads = cl.direct_threads(amount=10)
    print(f"📬 Scanning {len(threads)} active message threads...")

    processed_count = 0
    max_actions = 10  # safe limit per sweep

    for t in threads:
        users = [u.username for u in t.users if getattr(u, 'username', None)]
        if any(u.lower() in ["meta ai", "instagram"] for u in users):
            continue

        thread_id = str(t.id)
        messages = cl.direct_messages(thread_id, amount=5)

        for msg in messages:
            msg_id = str(msg.id)
            sender_id = str(msg.user_id)

            if sender_id == my_user_id or msg_id in seen_ids:
                continue

            item_type = str(msg.item_type).lower()
            if "action_log" in item_type:
                continue

            is_reel = any(k in item_type for k in ["clip", "xma_clip", "media_share", "media", "video"])
            is_text = "text" in item_type

            sender_name = users[0] if users else sender_id
            msg_text = getattr(msg, "text", "") or ""
            raw_xma = getattr(msg, "raw_xma", {}) or {}

            # Generate emotionally intelligent response
            reply_text = get_emotion_reply(item_type, text=msg_text, raw_xma=raw_xma)

            print(f"\n📩 Incoming from @{sender_name} [{item_type}]: \"{msg_text}\"")
            print(f"   💡 Emotional Response Picked: \"{reply_text}\"")

            if dry_run:
                print(f"   [DRY-RUN] Would double-tap ❤️ like and send reply")
                seen_ids.add(msg_id)
                continue

            # 1. Double-tap Like (❤️)
            try:
                cl.direct_message_like(thread_id, msg.id)
                print(f"   ❤️ Liked message from @{sender_name}")
                time.sleep(random.uniform(1.5, 3.0))
            except Exception as e:
                print(f"   ⚠️ Like failed: {e}")

            # 2. Send intelligent reply
            if reply_text:
                try:
                    cl.direct_answer(thread_id, reply_text)
                    print(f"   💬 Sent reply to @{sender_name}: \"{reply_text}\"")
                    time.sleep(random.uniform(2.0, 4.0))
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
    print(f"\n✨ Inbox sweep complete. Processed {processed_count} messages with contextual emotional intelligence.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Inspect without liking or replying")
    args = parser.parse_args()

    run_responder(dry_run=args.dry_run)

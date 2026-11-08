#!/usr/bin/env python3
"""
Advanced Context & Deep Emotion Engine for @pratikparth_12 (Private & Personal)
Analyzes shared reel captions, hashtags, creator context, and message semantics.
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
SESSION_DIR = Path.home() / ".config" / "stickman_video_director"
SESSION_FILE = SESSION_DIR / "insta_session_pratikparth_12.json"
STATE_FILE = BASE_DIR / "projects" / "dm_seen_pratikparth.json"
STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

def deep_analyze_reel(cl, raw_xma):
    """
    Fetches the actual caption, hashtags, and creator of the shared reel for 1000x deeper context.
    """
    creator = ""
    caption = ""
    hashtags = []
    is_placeholder = False

    if raw_xma and "xma_clip" in raw_xma:
        clips = raw_xma["xma_clip"]
        if clips and isinstance(clips, list):
            clip = clips[0]
            if clip.get("ig_template_type") == "placeholder" or clip.get("title_text") == "Message unavailable":
                return {"is_placeholder": True, "creator": "", "caption": "", "hashtags": []}

            creator = (clip.get("header_title_text") or clip.get("username") or "").lower()

            # Attempt fetching live reel caption from media_id
            ref_str = clip.get("serialized_content_ref")
            if ref_str:
                try:
                    ref_data = json.loads(ref_str)
                    media_id = ref_data.get("fetch_params", {}).get("media_igid")
                    if media_id:
                        info = cl.media_info(int(media_id))
                        caption = (info.caption_text or "").lower()
                        hashtags = [w.lower() for w in caption.split() if w.startswith("#")]
                except Exception:
                    pass

    return {
        "is_placeholder": is_placeholder,
        "creator": creator,
        "caption": caption,
        "hashtags": hashtags
    }

def get_deep_emotion_reply(item_type, text=None, reel_data=None):
    """
    Selects the most natural, contextually accurate emoji/Hinglish reply.
    """
    if reel_data and reel_data.get("is_placeholder"):
        return random.choice(["😂💀", "💀🤷‍♂️", "😂😂"])

    text_lower = (text or "").lower().strip()

    # ==========================================
    # 1. TEXT MESSAGES (Intent & Sentiment)
    # ==========================================
    if "text" in item_type and text_lower:
        # Festive / Diwali
        if any(w in text_lower for w in ["diwali", "deepavali", "patakhe", "mithai"]):
            return random.choice(["✨🪔❤️", "🪔✨ Happy Diwali bhai!", "✨🙏 Same to you bhai! 🪔"])

        # Urgent / Phone calls
        if any(w in text_lower for w in ["call", "phone", "uthana", "utha", "urgent"]):
            return random.choice(["📞 5 min me call karta hu", "ruk bhai free hoke call lagata hu 👍", "📞👍"])

        # Check-in / How are you
        if any(w in text_lower for w in ["kaisa hai", "kya haal", "sab sahi", "wassup", "sup"]):
            return random.choice(["ekdum mast bhai tu bata 🙌🔥", "sab badhiya bhai! 👍", "all good bhai tu suna?"])

        # Banter / "Jane de marna mat" / Laughter
        if any(w in text_lower for w in ["marna mat", "jane de", "mat kar", "haha", "lmao", "lol", "xd", "😂", "💀"]):
            return random.choice(["😂😂💀", "😭😭😂", "💀👍", "😂💀"])

        # Location / Hangout
        if any(w in text_lower for w in ["kahan hai", "kidhar hai", "scene", "plan", "chale"]):
            return random.choice(["bata kya plan hai? chalte hai 👍", "Ghar pe hi hu bhai, bol kya scene hai?", "Done bhai time bata"])

        # Gratitude
        if any(w in text_lower for w in ["thanks", "thank you", "thx"]):
            return random.choice(["❤️🙌", "anytime bhai ❤️", "mention not bhai 👍"])

        # Default natural acknowledgments
        return random.choice(["👍😂", "🙌🔥", "👍", "sahi hai bhai 👍"])

    # ==========================================
    # 2. SHARED REELS (Deep Caption & Creator Context)
    # ==========================================
    context_blob = ""
    if reel_data:
        context_blob = f"{reel_data.get('creator', '')} {reel_data.get('caption', '')} {' '.join(reel_data.get('hashtags', []))}".lower()

    # Diwali / Rangoli / Festive Reels
    if any(k in context_blob for k in ["rangoli", "diwali", "deepavali", "diwalivibes", "festive"]):
        return random.choice(["✨🪔❤️", "mast banaya hai yaar ✨🪔", "bohot pyara hai ✨❤️", "🪔✨"])

    # Cute Animals / Cats / Dogs / Pets
    if any(k in context_blob for k in ["cat", "dog", "kitten", "puppy", "paw", "animal", "pet", "cute"]):
        return random.choice(["🥺❤️", "so cute yaar 😭❤️", "cat/dog reels are therapy fr 🥺❤️", "😂❤️"])

    # Moms / Parents / Relatable Family
    if any(k in context_blob for k in ["mummy", "mom", "papa", "dad", "ghar wale", "parivar", "family"]):
        return random.choice(["😂😂💀", "literally mummy log aise hi karti hai 😭😂", "too accurate bhai 😭💀", "😂😂"])

    # College / Exams / Backlogs / Studies
    if any(k in context_blob for k in ["exam", "college", "btech", "backlog", "sem", "padhai", "study", "student"]):
        return random.choice(["us bhai us 😭💀", "literally me fr 😭😂", "dard bhai dard 💀💀", "😭😭"])

    # Cricket / Sports / Matches
    if any(k in context_blob for k in ["cricket", "cric", "ipl", "virat", "kohli", "rohit", "six", "wicket", "football"]):
        return random.choice(["🔥🏏", "GOAT behavior fr 🐐🔥", "khatarnak bhai 🔥", "absolute goosebumps 🔥🏏"])

    # Gym / Workout / Motivation
    if any(k in context_blob for k in ["gym", "fitness", "workout", "grind", "motivation", "bodybuilder"]):
        return random.choice(["💪🔥", "motivation peak pe hai bhai 💪", "kal se pakka grind shuru 💪💀", "🔥💪"])

    # Pranks / Drama / Breakup
    if any(k in context_blob for k in ["prank", "breakup", "lafda", "kalesh"]):
        return random.choice(["😂😂💀", "bhai ye prank to alag level tha 💀💀", "kalesh alag hi hai 😂", "😭😭😂"])

    # Dank Memes / High Comedy / Relatable
    if any(k in context_blob for k in ["meme", "dank", "sarcasm", "shitpost", "troll", "bakchodi", "desi", "sheetal"]):
        return random.choice(["😂😂💀", "😭😭😂", "💀💀", "bhai ye to direct narak leke jayega 💀", "kahan se dhoondte ho aisi reels 😂🔥"])

    # Default versatile friend reaction
    return random.choice(["😂😂💀", "😭😭😂", "💀💀", "mast reel thi ye fr 😂🔥", "😂😂"])

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

    print("⚠️ No session found locally or in INSTA_SESSION_PRATIKPARTH_JSON.")
    print("👉 Please add the secret in your repository: https://github.com/parthpratik1071-ux/vynox-autopilot/settings/secrets/actions")
    return None

def run_responder(max_targets=5, dry_run=False):
    cl = get_client()
    if cl is None:
        print("⚠️ Exiting cleanly without error. Add INSTA_SESSION_PRATIKPARTH_JSON secret to enable 24/7 cloud auto-responses.")
        sys.exit(0)

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

            raw_xma = getattr(msg, "raw_xma", {}) or {}
            sender_name = users[0] if users else sender_id
            msg_text = getattr(msg, "text", "") or ""

            # Deep analysis of reel content
            reel_data = None
            if "clip" in item_type or "media" in item_type:
                reel_data = deep_analyze_reel(cl, raw_xma)

            # Deep Emotion Reaction Selection
            reply_text = get_deep_emotion_reply(item_type, text=msg_text, reel_data=reel_data)

            print(f"\n📩 [{processed_count+1}/{max_targets}] Message from @{sender_name} ({item_type}):")
            if msg_text:
                print(f"   Text: \"{msg_text}\"")
            if reel_data and reel_data.get("caption"):
                print(f"   Reel Caption: \"{reel_data['caption'][:60]}...\"")
            print(f"   💡 Intelligent Reply: {reply_text}")

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

            # 2. Send Intelligent Emoji Reply
            try:
                cl.direct_answer(thread_id, reply_text)
                print(f"   💬 Sent reply: {reply_text}")
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
    print(f"\n🎉 Successfully processed {processed_count} messages with 1000x Deep Emotion Engine!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Inspect without liking or replying")
    parser.add_argument("--count", type=int, default=5, help="Number of messages to reply to")
    args = parser.parse_args()

    run_responder(max_targets=args.count, dry_run=args.dry_run)

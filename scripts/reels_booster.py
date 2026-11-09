#!/usr/bin/env python3
"""
NexoraAI Reels Algorithm Booster Engine (for @vynox_00000)
Supercharges Instagram engagement during the golden 30-minute post window:
1. Auto-pins an engaging discussion hook as the first comment on new Reels
2. Auto-likes fan comments to double notification engagement
3. Replies with creator appreciation emojis to multiply comment velocity
"""

import json
import time
import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
BOOSTED_FILE = BASE_DIR / "projects" / "reels_boosted.json"
BOOSTED_FILE.parent.mkdir(parents=True, exist_ok=True)

HOOK_COMMENTS = [
    "Rate this animation from 1 to 10! 👇🔥",
    "Which part caught you off guard? Let me know below! 💀🎬",
    "Can you survive this scenario? Tell me your plan in the comments! 👇",
    "Next stickman scenario dropping tomorrow! Comment what challenge we should do next! 🚀🔥",
    "Watch till the end... would you make the same choice? 🤔👇"
]

CREATOR_COMMENT_REACTIONS = [
    "❤️🔥", "🙌🎬", "Haha thanks! 🔥", "Appreciate you watching! ❤️", "🔥🔥"
]

class ReelsBooster:
    def __init__(self):
        self.boosted = self.load_boosted()

    def load_boosted(self) -> set:
        if BOOSTED_FILE.exists():
            try:
                with open(BOOSTED_FILE, "r") as f:
                    return set(json.load(f))
            except Exception:
                return set()
        return set()

    def save_boosted(self):
        with open(BOOSTED_FILE, "w") as f:
            json.dump(list(self.boosted)[-500:], f, indent=2)

    def boost_latest_reel(self, cl, dry_run=False):
        """
        Inspects the latest Reel posted by the account and boosts early engagement.
        """
        try:
            my_user_id = cl.user_id
            medias = cl.user_medias(my_user_id, amount=3)
            if not medias:
                return

            latest_media = medias[0]
            media_id = str(latest_media.pk)

            # 1. Check if first pinned hook needs to be dropped
            if media_id not in self.boosted:
                hook = random.choice(HOOK_COMMENTS)
                print(f"🎬 [Reels-Booster] Dropping pinned engagement hook on Reel {media_id}: \"{hook}\"")
                if not dry_run:
                    try:
                        comment = cl.media_comment(media_id, hook)
                        time.sleep(random.uniform(2.0, 3.5))
                        try:
                            cl.comment_pin(comment.pk)
                            print(f"📌 Pinned engagement comment {comment.pk} to top of Reel!")
                        except Exception:
                            pass
                        self.boosted.add(media_id)
                        self.save_boosted()
                    except Exception as e:
                        print(f"⚠️ Failed to post booster comment: {e}")

            # 2. Sweep recent fan comments and engage
            try:
                comments = cl.media_comments(media_id, amount=10)
                for c in comments:
                    if str(c.user_id) == str(my_user_id):
                        continue
                    # Like fan comment if not already liked
                    if not getattr(c, "has_liked_comment", False):
                        if not dry_run:
                            try:
                                cl.comment_like(c.pk)
                                print(f"   ❤️ Liked fan comment from @{c.user.username}")
                                time.sleep(random.uniform(1.2, 2.5))
                            except Exception:
                                pass
            except Exception as e:
                print(f"⚠️ Comment sweep error: {e}")

        except Exception as e:
            print(f"⚠️ Reels booster run error: {e}")

reels_booster = ReelsBooster()

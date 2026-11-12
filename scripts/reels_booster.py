#!/usr/bin/env python3
"""
Vynox Reels Engagement Booster Engine (standalone, @vynox_00000 only)
Safe, low-frequency post-upload engagement helper:
1. Drops and pins one niche discussion hook on a newly published Reel (< 24h old)
2. Persists boosted Reel IDs to `projects/reels_boosted.json` to prevent duplicate comments
3. Likes a small batch of recent fan comments with human-like pacing and sleep-hour guards
"""

import argparse
import json
import random
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
BOOSTED_FILE = BASE_DIR / "projects" / "reels_boosted.json"
BOOSTED_FILE.parent.mkdir(parents=True, exist_ok=True)
IST = timezone(timedelta(hours=5, minutes=30))

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

try:
    from scripts import insta_local_post
except ImportError:
    if str(BASE_DIR / "scripts") not in sys.path:
        sys.path.insert(0, str(BASE_DIR / "scripts"))
    import insta_local_post

_is_restriction_error = insta_local_post.is_restriction_error

HOOK_COMMENTS = [
    "Which line hit the hardest? Drop it below! 🖤✨",
    "Tag someone who needs to see this edit tonight 🥀💫",
    "Which song should we animate next? Comment your track! 🎧👇",
    "Late-night feels hit different... rate this edit 1–10 🌙🔥",
    "Save this Reel for your late-night playlist ✨🎧",
]


def _comment_author(comment) -> str:
    """Safely extracts the comment author's username or falls back to user_id."""
    user = getattr(comment, "user", None)
    username = getattr(user, "username", None) if user is not None else None
    return str(username or getattr(comment, "user_id", "unknown"))


def _media_age_hours(media) -> float | None:
    """Returns the age of an Instagram media item in hours, or None if unavailable."""
    taken_at = getattr(media, "taken_at", None)
    if not isinstance(taken_at, datetime):
        return None
    if taken_at.tzinfo is None:
        taken_at = taken_at.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - taken_at.astimezone(timezone.utc)).total_seconds() / 3600.0


class ReelsBooster:
    """Manages one-time engagement hooks and throttled comment likes for @vynox_00000."""

    def __init__(self, boosted_file: Path = BOOSTED_FILE):
        self.boosted_file = boosted_file
        self.boosted = self.load_boosted()

    def load_boosted(self) -> set[str]:
        if self.boosted_file.exists():
            try:
                with open(self.boosted_file, "r") as f:
                    return {str(item) for item in json.load(f)}
            except Exception:
                return set()
        return set()

    def save_boosted(self):
        self.boosted_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.boosted_file, "w") as f:
            json.dump(sorted(self.boosted)[-500:], f, indent=2)
            f.write("\n")

    def boost_latest_reel(self, cl, dry_run: bool = False, max_likes: int = 5, ignore_sleep: bool = False) -> bool:
        """
        Inspects the latest Reel on @vynox_00000, posts at most one pinned hook
        for newly posted Reels (<24h), and likes up to `max_likes` fan comments.
        Returns True if the check completed cleanly, False if aborted on restriction/error.
        """
        now_ist = datetime.now(IST)
        if not ignore_sleep and (3 <= now_ist.hour < 7):
            print(f"🌙 [Reels-Booster] Sleep window ({now_ist.strftime('%H:%M')} IST). Skipping engagement.")
            return True

        try:
            my_user_id = cl.user_id
            medias = cl.user_medias(my_user_id, amount=1)
            if not medias:
                print("ℹ️ [Reels-Booster] No medias found on account.")
                return True

            latest_media = medias[0]
            media_id = str(latest_media.pk)
            age_hours = _media_age_hours(latest_media)

            # 1. Drop one pinned hook comment only if never boosted and posted within 24h
            if media_id not in self.boosted:
                if age_hours is not None and age_hours > 24.0:
                    print(f"⏭️ [Reels-Booster] Latest Reel {media_id} is {age_hours:.1f}h old (>24h); marking seen without commenting.")
                    if not dry_run:
                        self.boosted.add(media_id)
                        self.save_boosted()
                else:
                    hook = random.choice(HOOK_COMMENTS)
                    print(f"🎬 [Reels-Booster] Dropping pinned engagement hook on Reel {media_id}: \"{hook}\"")
                    if not dry_run:
                        try:
                            comment = cl.media_comment(media_id, hook)
                            time.sleep(random.uniform(3.0, 6.0))
                            try:
                                cl.comment_pin(comment.pk)
                                print(f"📌 Pinned engagement comment {comment.pk} to top of Reel!")
                            except Exception:
                                pass
                            self.boosted.add(media_id)
                            self.save_boosted()
                        except Exception as e:
                            print(f"⚠️ Failed to post booster comment: {e}")
                            if _is_restriction_error(e):
                                print("🛑 [Reels-Booster] Stopping immediately due to account restriction/challenge signal.")
                                return False
            else:
                print(f"✅ [Reels-Booster] Reel {media_id} already has a boosted hook.")

            # 2. Sweep recent fan comments and like up to max_likes with conservative jitter
            if max_likes <= 0:
                return True

            comments = cl.media_comments(media_id, amount=10)
            likes_done = 0
            for c in comments:
                if likes_done >= max_likes:
                    break
                if str(c.user_id) == str(my_user_id):
                    continue
                if getattr(c, "has_liked_comment", False):
                    continue
                if dry_run:
                    print(f"   [DRY-RUN] Would like comment from @{_comment_author(c)}")
                    likes_done += 1
                    continue
                try:
                    cl.comment_like(c.pk)
                    likes_done += 1
                    print(f"   ❤️ Liked fan comment from @{_comment_author(c)} ({likes_done}/{max_likes})")
                    time.sleep(random.uniform(3.5, 7.5))
                except Exception as e:
                    print(f"⚠️ Comment like skipped: {e}")
                    if _is_restriction_error(e):
                        print("🛑 [Reels-Booster] Stopping comment sweep due to account restriction/challenge signal.")
                        return False

            return True
        except Exception as e:
            print(f"⚠️ Reels booster run error: {e}")
            return not _is_restriction_error(e)


reels_booster = ReelsBooster()


def main():
    parser = argparse.ArgumentParser(description="Standalone Vynox Reels Engagement Booster (@vynox_00000 only)")
    parser.add_argument("--dry-run", action="store_true", help="Inspect without commenting or liking")
    parser.add_argument("--max-likes", type=int, default=5, help="Max fan comments to like per run (default: 5)")
    parser.add_argument("--ignore-sleep", action="store_true", help="Run even during 3 AM - 7 AM IST sleep hours")
    args = parser.parse_args()

    cl = insta_local_post.get_client()
    ok = reels_booster.boost_latest_reel(
        cl,
        dry_run=args.dry_run,
        max_likes=max(0, args.max_likes),
        ignore_sleep=args.ignore_sleep,
    )
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()

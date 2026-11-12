#!/usr/bin/env python3
"""
Vynox Reels Viral Intelligence & Engagement Booster (@vynox_00000 only)
Safe, low-frequency post-upload growth & protection engine:
1. Context-aware hook generator (Gemini Flash when GEMINI_API_KEY is set, with mood-matched fallback)
2. 48-hour auto-circuit-breaker Ban Shield (`projects/booster_cooldown.json`) on any challenge/restriction
3. Viral velocity telemetry & fan song-request mining (`projects/reel_analytics.json`, `projects/fan_requests.json`)
4. Zero-repeat hook guard (`projects/reels_boosted.json`) and throttled comment likes with IST sleep window
"""

import argparse
import json
import os
import random
import sys
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECTS_DIR = BASE_DIR / "projects"
BOOSTED_FILE = PROJECTS_DIR / "reels_boosted.json"
COOLDOWN_FILE = PROJECTS_DIR / "booster_cooldown.json"
ANALYTICS_FILE = PROJECTS_DIR / "reel_analytics.json"
FAN_REQUESTS_FILE = PROJECTS_DIR / "fan_requests.json"
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

MOOD_HOOKS = {
    "crimson_manga": (
        {"sahiba", "saree", "payal", "manga", "bindi", "crimson", "gajra"},
        [
            "That black-and-crimson energy hits differently... which frame stopped you? 🩸🖤",
            "Who has this exact look in your head right now? Drop a 🥀 below",
            "Saree drape + silver payal details — rate this manga frame 1–10 🩸✨",
        ],
    ),
    "science_history": (
        {"astronomy", "ujjain", "aryabhata", "nasa", "mariana", "science", "trench", "विज्ञान", "खगोलीय"},
        [
            "Did you already know this fact before watching? Drop 🔥 or 🤯 below!",
            "Which mind-blowing science/history topic should we animate next? 👇🌌",
            "1500+ years ahead of its time — what stunned you most here? 🔭✨",
        ],
    ),
    "romantic_lofi": (
        {"anuv", "choo lo", "kashish", "husn", "baarishein", "kasoor", "indie", "lofi", "aditya", "love"},
        [
            "Which lyric line hits the deepest at 2 AM? Drop it below 🌙🎧",
            "Tag someone you'd send this track to without saying a word 🥀✨",
            "Which indie song should we turn into 2D art next? Comment your pick! 🎶👇",
        ],
    ),
}

DEFAULT_HOOKS = [
    "Which frame hit the hardest? Drop it below! 🖤✨",
    "Tag someone who needs to see this edit tonight 🥀💫",
    "What story or song should we animate next? Comment below! 🎧👇",
]

REQUEST_KEYWORDS = ("next", "song", "track", "animate", "part 2", "please", "pls", "banao", "karo", "upload", "?")


def _load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return default


def _save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _load_gemini_key() -> str:
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if key:
        return key
    env_file = BASE_DIR / ".env"
    if not env_file.exists():
        return ""
    for line in env_file.read_text(errors="ignore").splitlines():
        clean = line.strip().removeprefix("export ").strip()
        if clean.startswith("GEMINI_API_KEY="):
            return clean.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


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


def detect_niche(caption: str) -> str:
    """Classifies a Reel's visual/song niche from its caption text."""
    lower = (caption or "").lower()
    for niche, (keywords, _) in MOOD_HOOKS.items():
        if any(kw in lower for kw in keywords):
            return niche
    return "general"


def generate_smart_hook(caption: str, use_ai: bool = True) -> tuple[str, str]:
    """
    Generates one short context-aware pinned comment tailored to the Reel's caption.
    Returns (hook_text, source_label).
    """
    niche = detect_niche(caption)
    api_key = _load_gemini_key() if use_ai else ""
    if api_key and caption.strip():
        prompt = (
            "Write ONE ultra-short, natural Instagram Reel pinned comment (max 95 chars, 1-2 emojis) "
            "from the creator @vynox_00000 to spark real fan replies about this Reel. "
            "Never beg for follows/likes, no hashtags, keep the vibe authentic to the caption:\n\n"
            f"{caption[:500]}"
        )
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        payload = json.dumps({
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.8, "maxOutputTokens": 60},
        }).encode()
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=6) as resp:
                body = json.loads(resp.read().decode())
                text = body["candidates"][0]["content"]["parts"][0]["text"].strip().strip('"').splitlines()[0]
                if 8 <= len(text) <= 130:
                    return text, f"gemini:{niche}"
        except Exception:
            pass

    pool = MOOD_HOOKS[niche][1] if niche in MOOD_HOOKS else DEFAULT_HOOKS
    return random.choice(pool), f"template:{niche}"


def extract_fan_requests(comments, own_user_id: str) -> list[dict]:
    """Extracts non-spam fan song/topic requests from fetched Reel comments."""
    requests = []
    for c in comments:
        if str(getattr(c, "user_id", "")) == str(own_user_id):
            continue
        text = (getattr(c, "text", "") or "").strip()
        if len(text) < 5:
            continue
        lower = text.lower()
        if any(kw in lower for kw in REQUEST_KEYWORDS):
            requests.append({
                "comment_id": str(getattr(c, "pk", "")),
                "author": _comment_author(c),
                "text": text[:200],
            })
    return requests


class ReelsBooster:
    """Manages smart one-time hooks, viral radar metrics, fan mining, and Ban Shield cooldown."""

    def __init__(
        self,
        boosted_file: Path = BOOSTED_FILE,
        cooldown_file: Path = COOLDOWN_FILE,
        analytics_file: Path = ANALYTICS_FILE,
        requests_file: Path = FAN_REQUESTS_FILE,
    ):
        self.boosted_file = boosted_file
        self.cooldown_file = cooldown_file
        self.analytics_file = analytics_file
        self.requests_file = requests_file
        self.boosted = self.load_boosted()

    def load_boosted(self) -> set[str]:
        data = _load_json(self.boosted_file, [])
        return {str(item) for item in data} if isinstance(data, list) else set()

    def save_boosted(self):
        _save_json(self.boosted_file, sorted(self.boosted)[-500:])

    def get_cooldown_until(self) -> datetime | None:
        data = _load_json(self.cooldown_file, {})
        raw = data.get("cooldown_until") if isinstance(data, dict) else None
        if not raw:
            return None
        try:
            dt = datetime.fromisoformat(raw)
            return dt if dt > datetime.now(IST) else None
        except Exception:
            return None

    def activate_cooldown(self, hours: int = 48, reason: str = "") -> datetime:
        until = datetime.now(IST) + timedelta(hours=hours)
        _save_json(self.cooldown_file, {
            "active": True,
            "activated_at": datetime.now(IST).isoformat(),
            "cooldown_until": until.isoformat(),
            "reason": reason[:300],
        })
        return until

    def clear_cooldown(self):
        if self.cooldown_file.exists():
            self.cooldown_file.unlink()

    def is_cooldown_active(self) -> bool:
        """Checks whether Ban Shield is active and logs remaining cooldown hours."""
        active_cd = self.get_cooldown_until()
        if not active_cd:
            return False
        rem_h = (active_cd - datetime.now(IST)).total_seconds() / 3600.0
        print(f"🛡️ [Ban-Shield] Active until {active_cd.strftime('%Y-%m-%d %H:%M IST')} ({rem_h:.1f}h remaining). Skipping Instagram calls.")
        return True

    def _trip_shield_if_restricted(self, exc: Exception, context: str, dry_run: bool = False) -> bool:
        """Activates 48h cooldown if `exc` indicates a restriction/challenge; returns True if tripped."""
        if not _is_restriction_error(exc):
            return False
        if not dry_run:
            until = self.activate_cooldown(48, f"{context}: {exc}")
            print(f"🛡️ [Ban-Shield] Restriction signal in {context}; paused until {until.strftime('%Y-%m-%d %H:%M IST')}.")
        return True

    def _record_radar_and_requests(self, media, niche: str, comments, own_user_id: str, hook_source: str = ""):
        media_id = str(media.pk)
        views = int(getattr(media, "play_count", None) or getattr(media, "view_count", None) or 0)
        likes = int(getattr(media, "like_count", None) or 0)
        comment_count = int(getattr(media, "comment_count", None) or 0)
        eng_rate = round(((likes + comment_count) / views) * 100, 2) if views > 0 else 0.0
        tier = "🔥 Breakout" if (views >= 5000 or eng_rate >= 8.0) else ("⚡ Rising" if views >= 500 else "🌱 Warming Up")

        analytics = _load_json(self.analytics_file, {})
        if not isinstance(analytics, dict):
            analytics = {}
        entry = {
            "code": getattr(media, "code", ""),
            "niche": niche,
            "views": views,
            "likes": likes,
            "comments": comment_count,
            "engagement_rate_pct": eng_rate,
            "viral_tier": tier,
            "updated_at": datetime.now(IST).isoformat(),
        }
        if hook_source:
            entry["hook_source"] = hook_source
        analytics[media_id] = entry
        _save_json(self.analytics_file, analytics)
        print(f"📡 [Viral-Radar] {tier} | views={views:,} likes={likes:,} comments={comment_count} ({eng_rate}% eng, niche={niche})")

        new_reqs = extract_fan_requests(comments, own_user_id)
        if not new_reqs:
            return
        existing = _load_json(self.requests_file, [])
        if not isinstance(existing, list):
            existing = []
        seen_ids = {str(r.get("comment_id")) for r in existing if isinstance(r, dict)}
        added = 0
        for r in new_reqs:
            if r["comment_id"] not in seen_ids:
                r["media_id"] = media_id
                r["captured_at"] = datetime.now(IST).isoformat()
                existing.append(r)
                seen_ids.add(r["comment_id"])
                added += 1
        if added:
            _save_json(self.requests_file, existing[-100:])
            print(f"💡 [Fan-Miner] Captured {added} new fan song/topic request(s) -> {self.requests_file.name}")

    def boost_latest_reel(self, cl, dry_run: bool = False, max_likes: int = 5, ignore_sleep: bool = False) -> bool:
        """
        Inspects the latest Reel on @vynox_00000, posts one context-aware pinned hook
        for newly posted Reels (<24h), updates Viral Radar + fan request mining,
        and likes up to `max_likes` fan comments. Returns False on restriction/challenge.
        """
        if self.is_cooldown_active():
            return True

        now_ist = datetime.now(IST)
        if not ignore_sleep and (3 <= now_ist.hour < 7):
            print(f"🌙 [Reels-Booster] Sleep window ({now_ist.strftime('%H:%M')} IST). Skipping engagement.")
            return True

        try:
            my_user_id = str(cl.user_id)
            medias = cl.user_medias(my_user_id, amount=1)
            if not medias:
                print("ℹ️ [Reels-Booster] No medias found on account.")
                return True

            latest_media = medias[0]
            media_id = str(latest_media.pk)
            caption = getattr(latest_media, "caption_text", "") or ""
            niche = detect_niche(caption)
            age_hours = _media_age_hours(latest_media)
            hook_source = ""

            # 1. Drop one context-aware pinned hook comment only if unseen and <24h old
            if media_id not in self.boosted:
                if age_hours is not None and age_hours > 24.0:
                    print(f"⏭️ [Reels-Booster] Latest Reel {media_id} is {age_hours:.1f}h old (>24h); marking seen without commenting.")
                    if not dry_run:
                        self.boosted.add(media_id)
                        self.save_boosted()
                else:
                    hook, hook_source = generate_smart_hook(caption, use_ai=True)
                    print(f"🎬 [Reels-Booster] [{hook_source}] Hook for Reel {media_id}: \"{hook}\"")
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
                            if self._trip_shield_if_restricted(e, "media_comment", dry_run=dry_run):
                                return False
            else:
                print(f"✅ [Reels-Booster] Reel {media_id} already has a boosted hook.")

            # 2. Fetch up to 10 comments once: drives both Viral Radar mining & throttled likes
            comments = cl.media_comments(media_id, amount=10)
            if not dry_run:
                self._record_radar_and_requests(latest_media, niche, comments, my_user_id, hook_source)

            likes_done = 0
            for c in comments:
                if likes_done >= max_likes:
                    break
                if str(c.user_id) == my_user_id or getattr(c, "has_liked_comment", False):
                    continue
                author = _comment_author(c)
                if dry_run:
                    print(f"   [DRY-RUN] Would like comment from @{author}")
                    likes_done += 1
                    continue
                try:
                    cl.comment_like(c.pk)
                    likes_done += 1
                    print(f"   ❤️ Liked fan comment from @{author} ({likes_done}/{max_likes})")
                    time.sleep(random.uniform(3.5, 7.5))
                except Exception as e:
                    print(f"⚠️ Comment like skipped: {e}")
                    if self._trip_shield_if_restricted(e, "comment_like", dry_run=dry_run):
                        return False

            return True
        except Exception as e:
            print(f"⚠️ Reels booster run error: {e}")
            return not self._trip_shield_if_restricted(e, "boost_loop", dry_run=dry_run)


reels_booster = ReelsBooster()


def print_status_board():
    """Prints a rich offline studio status board without making any Instagram calls."""
    queue_files = sorted((PROJECTS_DIR / "queue").glob("*.json"))
    archive_files = sorted((PROJECTS_DIR / "archive").glob("*.json"))
    boosted = reels_booster.load_boosted()
    cd = reels_booster.get_cooldown_until()
    analytics = _load_json(ANALYTICS_FILE, {})
    requests = _load_json(FAN_REQUESTS_FILE, [])

    print("\n" + "=" * 56)
    print("🚀 VYNOX REELS MISSION CONTROL (Offline Status)")
    print("=" * 56)
    print(f"🛡️ Ban Shield     : {'ACTIVE until ' + cd.strftime('%Y-%m-%d %H:%M IST') if cd else 'Standby (Ready)'}")
    print(f"📦 Queued Reels   : {len(queue_files)} ({', '.join(p.name for p in queue_files) or 'empty'})")
    print(f"🎬 Archived Reels : {len(archive_files)} | Boosted Guard IDs: {len(boosted)}")
    print(f"🤖 Gemini Hooks   : {'Enabled' if _load_gemini_key() else 'Mood-Template Mode (no GEMINI_API_KEY)'}")
    if isinstance(analytics, dict) and analytics:
        print("\n📡 Viral Radar (Tracked Reels):")
        for mid, row in list(analytics.items())[-5:]:
            print(f"   • {mid} [{row.get('niche', '?')}] {row.get('viral_tier', '')} | views={row.get('views', 0):,} likes={row.get('likes', 0):,} ({row.get('engagement_rate_pct', 0)}%)")
    if isinstance(requests, list) and requests:
        print(f"\n💡 Fan Song/Topic Requests ({len(requests)} captured):")
        for req in requests[-5:]:
            print(f"   • @{req.get('author')}: \"{req.get('text')}\"")
    print("=" * 56 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Standalone Vynox Viral Intelligence & Reels Booster (@vynox_00000)")
    parser.add_argument("--dry-run", action="store_true", help="Inspect without commenting, liking, or saving cooldowns")
    parser.add_argument("--max-likes", type=int, default=5, help="Max fan comments to like per run (default: 5)")
    parser.add_argument("--ignore-sleep", action="store_true", help="Run even during 3 AM - 7 AM IST sleep hours")
    parser.add_argument("--status", action="store_true", help="Show offline Viral Radar, queue, requests, and Ban Shield state")
    parser.add_argument("--clear-cooldown", action="store_true", help="Clear active Ban Shield cooldown after verifying account")
    args = parser.parse_args()

    if args.clear_cooldown:
        reels_booster.clear_cooldown()
        print("🔓 [Ban-Shield] Cooldown cleared.")

    if args.status:
        print_status_board()
        return

    if reels_booster.is_cooldown_active():
        return

    try:
        cl = insta_local_post.get_client()
    except Exception as e:
        print(f"⚠️ Instagram client init failed: {e}")
        reels_booster._trip_shield_if_restricted(e, "client_init", dry_run=args.dry_run)
        sys.exit(1)

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

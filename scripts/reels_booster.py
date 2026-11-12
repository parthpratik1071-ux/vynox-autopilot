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
import html
import json
import os
import random
import re
import sys
import textwrap
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
LEADERBOARD_FILE = PROJECTS_DIR / "hook_leaderboard.json"
COCKPIT_HTML_FILE = PROJECTS_DIR / "vynox_cockpit.html"
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


def _top_winning_hooks(leaderboard_file: Path = LEADERBOARD_FILE, limit: int = 3) -> list[dict]:
    """Returns top-scoring hooks ordered by average engagement rate."""
    board = _load_json(leaderboard_file, {})
    if not isinstance(board, dict):
        return []
    ranked = [v for v in board.values() if isinstance(v, dict) and v.get("best_hook")]
    ranked.sort(key=lambda r: (r.get("avg_engagement_pct", 0.0), r.get("best_views", 0)), reverse=True)
    return ranked[:limit]


def generate_smart_hook(caption: str, use_ai: bool = True, leaderboard_file: Path = LEADERBOARD_FILE) -> tuple[str, str]:
    """
    Generates one short context-aware pinned comment tailored to the Reel's caption,
    informed by top-performing hooks on `hook_leaderboard.json`.
    Returns (hook_text, source_label).
    """
    niche = detect_niche(caption)
    winners = [w for w in _top_winning_hooks(leaderboard_file) if w.get("niche") in (niche, "general")]
    winner_hint = f"\nHighest-converting past example: {winners[0]['best_hook']}" if winners else ""

    api_key = _load_gemini_key() if use_ai else ""
    if api_key and caption.strip():
        prompt = (
            "Write ONE ultra-short, natural Instagram Reel pinned comment (max 95 chars, 1-2 emojis) "
            "from the creator @vynox_00000 to spark real fan replies about this Reel. "
            "Never beg for follows/likes, no hashtags, keep the vibe authentic to the caption:"
            f"{winner_hint}\n\n{caption[:500]}"
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
    if winners and random.random() < 0.75 and winners[0]["best_hook"] in pool:
        return winners[0]["best_hook"], f"winner:{niche}"
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
        leaderboard_file: Path = LEADERBOARD_FILE,
    ):
        self.boosted_file = boosted_file
        self.cooldown_file = cooldown_file
        self.analytics_file = analytics_file
        self.requests_file = requests_file
        self.leaderboard_file = leaderboard_file
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

    def _update_leaderboard(self, strategy_key: str, niche: str, hook_text: str, eng_rate: float, views: int):
        if not strategy_key:
            return
        board = _load_json(self.leaderboard_file, {})
        if not isinstance(board, dict):
            board = {}
        rec = board.get(strategy_key, {"niche": niche, "runs": 0, "avg_engagement_pct": 0.0, "best_views": 0, "best_hook": ""})
        runs = int(rec.get("runs", 0))
        prev_avg = float(rec.get("avg_engagement_pct", 0.0))
        rec["niche"] = niche
        rec["runs"] = runs + 1
        rec["avg_engagement_pct"] = round(((prev_avg * runs) + eng_rate) / (runs + 1), 2)
        if views >= int(rec.get("best_views", 0)) or not rec.get("best_hook"):
            rec["best_views"] = views
            if hook_text:
                rec["best_hook"] = hook_text
        rec["updated_at"] = datetime.now(IST).isoformat()
        board[strategy_key] = rec
        _save_json(self.leaderboard_file, board)

    def _record_radar_and_requests(self, media, niche: str, comments, own_user_id: str, hook_source: str = "", hook_text: str = ""):
        media_id = str(media.pk)
        views = int(getattr(media, "play_count", None) or getattr(media, "view_count", None) or 0)
        likes = int(getattr(media, "like_count", None) or 0)
        comment_count = int(getattr(media, "comment_count", None) or 0)
        eng_rate = round(((likes + comment_count) / views) * 100, 2) if views > 0 else 0.0
        tier = "🔥 Breakout" if (views >= 5000 or eng_rate >= 8.0) else ("⚡ Rising" if views >= 500 else "🌱 Warming Up")

        analytics = _load_json(self.analytics_file, {})
        if not isinstance(analytics, dict):
            analytics = {}
        prev = analytics.get(media_id, {}) if isinstance(analytics.get(media_id), dict) else {}
        eff_source = hook_source or prev.get("hook_source", "")
        eff_hook = hook_text or prev.get("hook_text", "")
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
        if eff_source:
            entry["hook_source"] = eff_source
        if eff_hook:
            entry["hook_text"] = eff_hook
        analytics[media_id] = entry
        _save_json(self.analytics_file, analytics)
        self._update_leaderboard(eff_source, niche, eff_hook, eng_rate, views)
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
            hook_text = ""

            # 1. Drop one context-aware pinned hook comment only if unseen and <24h old
            if media_id not in self.boosted:
                if age_hours is not None and age_hours > 24.0:
                    print(f"⏭️ [Reels-Booster] Latest Reel {media_id} is {age_hours:.1f}h old (>24h); marking seen without commenting.")
                    if not dry_run:
                        self.boosted.add(media_id)
                        self.save_boosted()
                else:
                    hook_text, hook_source = generate_smart_hook(caption, use_ai=True, leaderboard_file=self.leaderboard_file)
                    print(f"🎬 [Reels-Booster] [{hook_source}] Hook for Reel {media_id}: \"{hook_text}\"")
                    if not dry_run:
                        try:
                            comment = cl.media_comment(media_id, hook_text)
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
                self._record_radar_and_requests(latest_media, niche, comments, my_user_id, hook_source, hook_text)

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


def _pick_font(size: int, bold: bool = False):
    """Selects a crisp TrueType font if installed, falling back to Pillow default."""
    from PIL import ImageFont

    candidates = [
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf" if bold else "/usr/share/fonts/truetype/ubuntu/Ubuntu-M.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def generate_story_card(cover_path: Path, title: str, out_path: Path | None = None, handle: str = "@vynox_00000") -> Path:
    """Renders a 1080x1920 glassmorphic Story promo card from a Reel cover image."""
    from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

    cover = Image.open(cover_path).convert("RGB")
    W, H = 1080, 1920

    # Blurred ambient cover backdrop + dark moody vignette
    scale = max(W / cover.width, H / cover.height)
    bg = cover.resize((int(cover.width * scale), int(cover.height * scale)), Image.Resampling.LANCZOS)
    left, top = (bg.width - W) // 2, (bg.height - H) // 2
    bg = bg.crop((left, top, left + W, top + H)).filter(ImageFilter.GaussianBlur(radius=42))
    bg = ImageEnhance.Brightness(bg).enhance(0.32).convert("RGBA")

    # Center rounded poster frame
    card_w, card_h = 840, 1180
    card_x, card_y = (W - card_w) // 2, 290
    c_scale = max(card_w / cover.width, card_h / cover.height)
    fg = cover.resize((int(cover.width * c_scale), int(cover.height * c_scale)), Image.Resampling.LANCZOS)
    fl, ft = (fg.width - card_w) // 2, (fg.height - card_h) // 2
    fg = fg.crop((fl, ft, fl + card_w, ft + card_h)).convert("RGBA")

    mask = Image.new("L", (card_w, card_h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, card_w, card_h), radius=48, fill=255)
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        (card_x - 8, card_y + 18, card_x + card_w + 8, card_y + card_h + 26), radius=52, fill=(0, 0, 0, 165)
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=26))
    bg = Image.alpha_composite(bg, shadow)
    bg.paste(fg, (card_x, card_y), mask)

    draw = ImageDraw.Draw(bg)
    draw.rounded_rectangle((card_x, card_y, card_x + card_w, card_y + card_h), radius=48, outline=(255, 255, 255, 70), width=3)

    # Top glowing badge
    badge_w, badge_h = 340, 62
    bx, by = (W - badge_w) // 2, 165
    draw.rounded_rectangle((bx, by, bx + badge_w, by + badge_h), radius=31, fill=(195, 24, 52, 235), outline=(255, 190, 200, 180), width=2)
    f_badge = _pick_font(30, bold=True)
    draw.text((W // 2, by + badge_h // 2), "NEW REEL LIVE", fill=(255, 255, 255, 255), font=f_badge, anchor="mm")

    # Bottom typography & CTA pill
    clean_title = re.sub(r"[^\x20-\x7E]+", " ", title or "New Visual Story").strip() or "New Visual Story"
    lines = textwrap.wrap(clean_title, width=26)[:2]
    f_title = _pick_font(54, bold=True)
    ty = 1545
    for line in lines:
        draw.text((W // 2, ty), line, fill=(248, 248, 252, 255), font=f_title, anchor="mm")
        ty += 68

    f_sub = _pick_font(34, bold=False)
    draw.text((W // 2, 1745), f"WATCH FULL EDIT  |  {handle.upper()}", fill=(225, 210, 220, 235), font=f_sub, anchor="mm")

    dest = out_path or (cover_path.parent / "story_card.jpg")
    bg.convert("RGB").save(dest, quality=94)
    return dest


def preview_queue():
    """Audits all queued Reels offline with viral readiness and smart hook previews."""
    queue_files = sorted((PROJECTS_DIR / "queue").glob("*.json"))
    print("\n" + "=" * 62)
    print(f"🎬 QUEUE VIRAL PRE-FLIGHT ({len(queue_files)} staged Reels)")
    print("=" * 62)
    for idx, qf in enumerate(queue_files, 1):
        data = _load_json(qf, {})
        cap = data.get("caption", "")
        niche = detect_niche(cap)
        hook, src = generate_smart_hook(cap, use_ai=False)
        hashtags = len(re.findall(r"#\w+", cap))
        vp = BASE_DIR / str(data.get("video_path", "")).split("stickman-video-director/")[-1]
        cp = BASE_DIR / str(data.get("cover_path", "")).split("stickman-video-director/")[-1]
        size_mb = (vp.stat().st_size / (1024 * 1024)) if vp.exists() else 0.0
        print(f"{idx}. {qf.name} | niche={niche} | {size_mb:.1f} MB | tags={hashtags} | cover={'OK' if cp.exists() else 'MISSING'}")
        print(f"   Hook Preview [{src}]: \"{hook}\"")
    print("=" * 62 + "\n")


def generate_cockpit_html(out_path: Path = COCKPIT_HTML_FILE) -> Path:
    """Builds a self-contained Neon Cyber Cockpit dashboard at `projects/vynox_cockpit.html`."""
    queue_files = sorted((PROJECTS_DIR / "queue").glob("*.json"))
    archive_files = sorted((PROJECTS_DIR / "archive").glob("*.json"), reverse=True)
    cd = reels_booster.get_cooldown_until()
    analytics = _load_json(ANALYTICS_FILE, {})
    requests = _load_json(FAN_REQUESTS_FILE, [])
    board = _load_json(LEADERBOARD_FILE, {})

    q_cards = []
    for qf in queue_files:
        d = _load_json(qf, {})
        cap = d.get("caption", "")
        hook, _ = generate_smart_hook(cap, use_ai=False)
        q_cards.append(
            f"<div class='card'><div class='tag'>{html.escape(detect_niche(cap))}</div>"
            f"<h3>{html.escape(d.get('title', qf.name))}</h3>"
            f"<p class='muted'>{html.escape(qf.name)} · {d.get('duration', '?')}s</p>"
            f"<div class='hook'>Pinned Hook: {html.escape(hook)}</div></div>"
        )

    a_rows = []
    for af in archive_files[:8]:
        d = _load_json(af, {})
        if d.get("status") == "deleted_from_instagram":
            continue
        mid = str(d.get("media_id", ""))
        m_stats = analytics.get(mid, {}) if isinstance(analytics, dict) else {}
        tier = m_stats.get("viral_tier", "Archived")
        url = d.get("reel_url", "#")
        a_rows.append(
            f"<tr><td>{html.escape(d.get('title', af.name)[:42])}</td>"
            f"<td>{html.escape(str(tier))}</td>"
            f"<td><a href='{html.escape(url)}' target='_blank'>Open Reel ↗</a></td></tr>"
        )

    req_items = "".join(
        f"<li><strong>@{html.escape(str(r.get('author', '?')))}</strong>: {html.escape(str(r.get('text', '')))}</li>"
        for r in (requests[-8:] if isinstance(requests, list) else [])
    ) or "<li class='muted'>No fan song requests captured yet.</li>"

    lb_items = "".join(
        f"<li><code>{html.escape(k)}</code> · {v.get('avg_engagement_pct', 0)}% eng · \"{html.escape(str(v.get('best_hook', ''))[:70])}\"</li>"
        for k, v in (board.items() if isinstance(board, dict) else [])
    ) or "<li class='muted'>Leaderboard populates as Viral Radar sweeps live Reels.</li>"

    shield_badge = (
        f"<span class='pill warn'>Ban Shield Active until {html.escape(cd.strftime('%d %b %H:%M IST'))}</span>"
        if cd else "<span class='pill ok'>Ban Shield Standby · Ready</span>"
    )
    graph_mode = "Official Graph API" if (os.environ.get("INSTA_GRAPH_ACCESS_TOKEN") and os.environ.get("INSTA_IG_USER_ID")) else "Session API (instagrapi)"

    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Vynox Studio Cockpit</title>
<style>
body{{margin:0;background:#090b12;color:#e9ecf5;font-family:Inter,system-ui,sans-serif;padding:32px}}
.wrap{{max-width:1080px;margin:0 auto}} .top{{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;margin-bottom:24px}}
h1{{margin:0;font-size:28px;letter-spacing:-.5px}} .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:16px;margin-bottom:24px}}
.card{{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1);border-radius:16px;padding:18px}}
.tag{{display:inline-block;font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#ff7b93;background:rgba(220,38,70,.16);padding:4px 10px;border-radius:99px}}
.pill{{padding:6px 14px;border-radius:99px;font-size:13px;font-weight:600}} .ok{{background:rgba(16,185,129,.18);color:#6ee7b7}} .warn{{background:rgba(245,158,11,.2);color:#fcd34d}}
.muted{{color:#94a3b8;font-size:13px}} .hook{{margin-top:10px;padding:10px;border-radius:10px;background:rgba(255,255,255,.03);font-size:13px;color:#cbd5e1}}
table{{width:100%;border-collapse:collapse}} td{{padding:10px 6px;border-bottom:1px solid rgba(255,255,255,.08);font-size:14px}} a{{color:#60a5fa;text-decoration:none}}
ul{{margin:8px 0 0;padding-left:18px;line-height:1.7;font-size:14px}}
</style></head><body><div class="wrap">
<div class="top"><div><h1>Vynox Autopilot Studio Cockpit</h1><div class="muted">Transport: {html.escape(graph_mode)} · Queued: {len(queue_files)} · Archived: {len(archive_files)}</div></div>{shield_badge}</div>
<h2>Queued Next</h2><div class="grid">{''.join(q_cards) or '<div class="card muted">Queue empty</div>'}</div>
<div class="grid"><div class="card"><h3>Winning Hook Leaderboard</h3><ul>{lb_items}</ul></div><div class="card"><h3>Fan Song & Topic Requests</h3><ul>{req_items}</ul></div></div>
<div class="card"><h3>Recent Published Reels</h3><table>{''.join(a_rows)}</table></div>
</div></body></html>"""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(doc)
    return out_path


def print_status_board():
    """Prints a rich offline studio status board without making any Instagram calls."""
    queue_files = sorted((PROJECTS_DIR / "queue").glob("*.json"))
    archive_files = sorted((PROJECTS_DIR / "archive").glob("*.json"))
    boosted = reels_booster.load_boosted()
    cd = reels_booster.get_cooldown_until()
    analytics = _load_json(ANALYTICS_FILE, {})
    requests = _load_json(FAN_REQUESTS_FILE, [])
    board = _load_json(LEADERBOARD_FILE, {})

    print("\n" + "=" * 56)
    print("🚀 VYNOX REELS MISSION CONTROL (Offline Status)")
    print("=" * 56)
    print(f"🛡️ Ban Shield     : {'ACTIVE until ' + cd.strftime('%Y-%m-%d %H:%M IST') if cd else 'Standby (Ready)'}")
    print(f"📦 Queued Reels   : {len(queue_files)} ({', '.join(p.name for p in queue_files) or 'empty'})")
    print(f"🎬 Archived Reels : {len(archive_files)} | Boosted Guard IDs: {len(boosted)}")
    print(f"🤖 Gemini Hooks   : {'Enabled' if _load_gemini_key() else 'Mood-Template Mode (no GEMINI_API_KEY)'}")
    print(f"🏆 Hook Strategies: {len(board) if isinstance(board, dict) else 0} tracked")
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
    parser.add_argument("--preview-queue", action="store_true", help="Audit staged queued Reels offline and preview generated hooks")
    parser.add_argument("--story-card", nargs="?", const="queue_0", help="Generate a 1080x1920 Story promo card from a cover or queue JSON")
    parser.add_argument("--cockpit", action="store_true", help="Generate interactive HTML studio cockpit at projects/vynox_cockpit.html")
    parser.add_argument("--clear-cooldown", action="store_true", help="Clear active Ban Shield cooldown after verifying account")
    args = parser.parse_args()

    if args.clear_cooldown:
        reels_booster.clear_cooldown()
        print("🔓 [Ban-Shield] Cooldown cleared.")

    if args.status:
        print_status_board()
        return

    if args.preview_queue:
        preview_queue()
        return

    if args.cockpit:
        path = generate_cockpit_html()
        print(f"🖥️ Generated Vynox Cyber Cockpit: {path}")
        return

    if args.story_card:
        if args.story_card == "queue_0":
            qfiles = sorted((PROJECTS_DIR / "queue").glob("*.json"))
            if not qfiles:
                print("❌ Queue is empty; pass a cover image or Reel JSON path.")
                sys.exit(1)
            meta = _load_json(qfiles[0], {})
            cover_p = BASE_DIR / str(meta.get("cover_path", "")).split("stickman-video-director/")[-1]
            title = meta.get("title", qfiles[0].stem)
        elif args.story_card.endswith(".json"):
            meta = _load_json(Path(args.story_card), {})
            cover_p = BASE_DIR / str(meta.get("cover_path", "")).split("stickman-video-director/")[-1]
            title = meta.get("title", Path(args.story_card).stem)
        else:
            cover_p = Path(args.story_card)
            title = cover_p.parent.parent.name.replace("-", " ").title()
        out = generate_story_card(cover_p, title)
        print(f"🎨 Generated 1080x1920 Story Promo Card: {out}")
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

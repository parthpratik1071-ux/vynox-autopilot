#!/usr/bin/env python3
"""
Automated Daily Reel Dispatcher
Reads the next scheduled video from `projects/queue/`, posts it to Instagram,
and archives the record.
"""

import os
import sys
import json
import shutil
import datetime
import argparse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
QUEUE_DIR = BASE_DIR / "projects" / "queue"
ARCHIVE_DIR = BASE_DIR / "projects" / "archive"
LOG_FILE = BASE_DIR / "projects" / "daily_dispatcher.log"

IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))

if str(BASE_DIR / "scripts") not in sys.path:
    sys.path.insert(0, str(BASE_DIR / "scripts"))
import insta_local_post
import duplicate_guard
import youtube_uploader

def log(msg):
    timestamp = datetime.datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {msg}"
    print(formatted)
    with open(LOG_FILE, "a") as f:
        f.write(formatted + "\n")

def parse_dt(dt_str):
    if not dt_str:
        return None
    try:
        return datetime.datetime.fromisoformat(dt_str)
    except Exception:
        return None

def _sync_local_state_to_remote():
    """Commits and pushes queue/archive state after a local dispatch so CI stays synchronized."""
    import subprocess

    targets = ["projects/queue/", "projects/archive/", "projects/daily_dispatcher.log"]
    for extra in ("projects/duplicate_registry.json", "projects/vynox_cockpit.html"):
        if (BASE_DIR / extra).exists():
            targets.append(extra)

    try:
        subprocess.run(["git", "add", *targets], cwd=str(BASE_DIR), check=False, capture_output=True)
        diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=str(BASE_DIR), check=False)
        if diff.returncode == 0:
            return
        subprocess.run(
            ["git", "commit", "-m", "chore: auto-sync Reel dispatch state [skip ci]"],
            cwd=str(BASE_DIR),
            check=True,
            capture_output=True,
        )
        subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "main"], cwd=str(BASE_DIR), check=False, capture_output=True)
        res = subprocess.run(["git", "push", "origin", "main"], cwd=str(BASE_DIR), check=False, capture_output=True)
        if res.returncode == 0:
            log("☁️ Synced queue and archive state to origin/main.")
        else:
            log("⚠️ Local dispatch committed; git push skipped/failed.")
    except Exception as e:
        log(f"⚠️ Remote state sync skipped: {e}")


def dispatch_next(force=False):
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Synchronize with remote repository to prevent duplicate dispatches
    try:
        import subprocess
        subprocess.run(["git", "pull", "--rebase", "origin", "main"], cwd=str(BASE_DIR), capture_output=True, timeout=15)
    except Exception as e:
        log(f"⚠️ Git sync skipped: {e}")

    now = datetime.datetime.now(IST)
    today_str = now.date().isoformat()

    queue_files = sorted(list(QUEUE_DIR.glob("*.json")))
    if not queue_files:
        log("⚠️ No queued Reels found in projects/queue/! Queue is empty.")
        return True

    is_ci = os.environ.get("GITHUB_ACTIONS") == "true"

    # 2. Pre-Flight Authentication Health Check before touching queue
    auth_ok, auth_code, client_or_err = insta_local_post.check_auth_health()
    if not auth_ok:
        log(f"⏸️ AUTHENTICATION HEALTH CHECK FAILED: {auth_code}")
        log(f"   Reason: {client_or_err}")
        log(f"🛡️ PRESERVING QUEUE: All {len(queue_files)} queued Reels remain staged untouched (Next: {queue_files[0].name}).")

        insta_local_post.write_auth_status(
            status="PAUSED_AUTH_REQUIRED",
            code=auth_code,
            detail=f"{client_or_err} (Queue preserved: {len(queue_files)} reels waiting)",
        )

        step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
        if step_summary:
            try:
                with open(step_summary, "a", encoding="utf-8") as f:
                    f.write("\n### ⚠️ Vynox Autopilot: Instagram Authentication Required\n\n")
                    f.write(f"- **Issue:** `{auth_code}`\n")
                    f.write(f"- **Detail:** {client_or_err}\n")
                    f.write(f"- **Queue Status:** 🛡️ **Preserved** ({len(queue_files)} Reels waiting, next: `{queue_files[0].name}`)\n")
                    f.write("- **Publishing:** Automatically paused until fresh authentication is provided.\n\n")
                    f.write("#### Quick Resolution Steps:\n")
                    f.write("1. On your trusted local machine, run:\n")
                    f.write("   ```bash\n   python3 scripts/vynox_update_bio_and_dispatch.py --bio-only\n   ```\n")
                    f.write("2. Copy the exported session into GitHub Repository Secret **`INSTA_SESSION_JSON`**.\n")
                    f.write("3. The queue will automatically resume publishing on the very next scheduled slot!\n")
            except Exception:
                pass

        try:
            from emergency_alerter import EmergencyAlerter
            alerter = EmergencyAlerter()
            if alerter.bot_token or alerter.webhook_url:
                alerter.send_alert(
                    "vynox_autopilot",
                    f"Auth Required: {auth_code}",
                    f"Session expired in GitHub Actions. 🛡️ Queue preserved ({len(queue_files)} reels waiting)."
                )
        except Exception:
            pass

        if not is_ci:
            _sync_local_state_to_remote()
        return False

    cl = client_or_err

    if not force:
        # Check valid posts published today (ignoring deleted posts)
        today_posts = []
        for p in ARCHIVE_DIR.glob(f"{today_str}*.json"):
            try:
                with open(p, "r") as f:
                    data = json.load(f)
                if data.get("status") != "deleted_from_instagram":
                    today_posts.append(data)
            except Exception:
                pass

        # Calculate time in minutes from midnight (IST)
        mins_now = now.hour * 60 + now.minute
        slot1_start = 19 * 60 + 15   # 19:15 IST (7:15 PM)
        slot1_end = 20 * 60 + 45     # 20:45 IST (8:45 PM)
        slot2_start = 21 * 60 + 30   # 21:30 IST (9:30 PM)
        slot2_end = 23 * 60 + 15     # 23:15 IST (11:15 PM)

        if slot1_start <= mins_now <= slot1_end:
            # Slot 1: Evening Wind-Down
            slot1_posted = any(
                (parse_dt(p.get("published_at")) and 19 <= parse_dt(p.get("published_at")).hour < 21)
                for p in today_posts
            )
            if slot1_posted:
                log(f"✅ Evening Slot 1 Reel already published today ({today_str}). Next slot is Late-Night Peak at 9:45 PM IST.")
                return True
            log(f"🎯 Slot 1 (Evening 7:30 PM IST Window) active ({now.strftime('%H:%M')} IST). Proceeding to dispatch...")
        elif slot2_start <= mins_now <= slot2_end:
            # Slot 2: Late-Night Viral Peak
            slot2_posted = any(
                (parse_dt(p.get("published_at")) and parse_dt(p.get("published_at")).hour >= 21)
                for p in today_posts
            )
            if slot2_posted:
                log(f"✅ Late-Night Slot 2 Reel already published today ({today_str}). Daily quota fulfilled!")
                return True
            log(f"🎯 Slot 2 (Late-Night 9:45 PM IST Peak Window) active ({now.strftime('%H:%M')} IST). Proceeding to dispatch...")
        else:
            log(
                f"⏳ Current time ({now.strftime('%H:%M')} IST) is outside peak audience publishing windows "
                f"(Slot 1: 19:15–20:45 IST | Slot 2: 21:30–23:15 IST). Aborting off-hours dispatch to protect organic reach."
            )
            return False

    next_file = queue_files[0]
    log(f"📦 Processing queue item: {next_file.name}")

    with open(next_file, "r") as f:
        data = json.load(f)

    def resolve_path(p):
        if not p:
            return None
        po = Path(p)
        if po.is_absolute() and po.exists():
            return po
        # Check relative to BASE_DIR or strip local prefix
        p_str = str(p).split("stickman-video-director/")[-1]
        cand = BASE_DIR / p_str
        if cand.exists():
            return cand
        return po

    video_path = resolve_path(data.get("video_path"))
    cover_path = resolve_path(data.get("cover_path"))
    caption = data.get("caption", "")

    if not video_path or not video_path.exists():
        log(f"❌ Video file does not exist: {video_path}")
        raise FileNotFoundError(f"Video file does not exist: {video_path}")

    log(f"🎬 Uploading video: {video_path}")

    # Zero-Repeat Check: Never re-publish an already posted video or caption headline
    is_dup, dup_reason = duplicate_guard.is_duplicate_video(video_path, caption)
    if is_dup and not force:
        log(f"🛑 ZERO-REPEAT GUARD: {dup_reason}. Skipping upload to prevent duplicate post.")
        archive_dest = ARCHIVE_DIR / f"{now.date().isoformat()}_{next_file.name}"
        with open(archive_dest, "w") as f:
            data["status"] = "skipped_duplicate"
            data["reason"] = dup_reason
            json.dump(data, f, indent=2)
        next_file.unlink()
        return True

    if cl is None:
        cl = insta_local_post.get_client()

    # Safety duplicate guard: Check if identical caption was already posted in latest medias
    if not force:
        try:
            recent_medias = cl.user_medias(cl.user_id, amount=10)
            first_sentence = caption.split('\n')[0].strip()
            for rm in recent_medias:
                rm_cap = (rm.caption_text or '').strip()
                if first_sentence and first_sentence in rm_cap:
                    log(f"⚠️ Live Instagram duplicate detected: '{first_sentence[:40]}...' already exists as https://www.instagram.com/reel/{rm.code}/. Skipping upload.")
                    # Archive and remove from queue to avoid repeated triggers
                    archive_dest = ARCHIVE_DIR / f"{now.date().isoformat()}_{next_file.name}"
                    with open(archive_dest, "w") as f:
                        data["status"] = "skipped_duplicate"
                        data["duplicate_of"] = f"https://www.instagram.com/reel/{rm.code}/"
                        json.dump(data, f, indent=2)
                    next_file.unlink()
                    return True
        except Exception as e:
            log(f"⚠️ Duplicate check warning: {e}")

    media = insta_local_post.upload_reel(
        cl,
        video_path=video_path,
        caption=caption,
        thumbnail_path=cover_path
    )

    reel_url = f"https://www.instagram.com/reel/{media.code}/"
    log(f"✅ Reel posted successfully: {reel_url}")

    data["published_at"] = datetime.datetime.now(IST).isoformat()
    data["reel_url"] = reel_url
    data["media_id"] = media.pk

    # Optional cross-post to YouTube Shorts if credentials are configured
    try:
        yt_ok, yt_code, yt_info = youtube_uploader.check_auth_health()
        if yt_ok:
            log(f"📺 Cross-posting to YouTube Shorts ({yt_info})...")
            yt_res = youtube_uploader.upload_short(
                video_path=video_path,
                title=data.get("title", ""),
                song_title=data.get("song_title", ""),
                artist=data.get("artist", ""),
                description=caption,
                privacy_status="public",
            )
            data["youtube_short_id"] = yt_res.get("id")
            data["youtube_short_url"] = f"https://youtube.com/shorts/{yt_res.get('id')}"
            log(f"✅ YouTube Short published: {data['youtube_short_url']}")
        else:
            log(f"ℹ️ YouTube Shorts cross-posting skipped ({yt_code})")
    except Exception as yt_err:
        log(f"⚠️ YouTube cross-posting warning: {yt_err}")

    # Move to archive
    archive_dest = ARCHIVE_DIR / f"{now.date().isoformat()}_{next_file.name}"
    with open(archive_dest, "w") as f:
        json.dump(data, f, indent=2)

    duplicate_guard.register_video(
        title=data.get("title", ""),
        video_path=video_path,
        caption=caption,
        status="published_to_instagram"
    )
    next_file.unlink()
    insta_local_post.write_auth_status("HEALTHY", auth_code, f"Published {media.code} successfully")

    log(f"📁 Archived record to: {archive_dest.name}")
    remaining = len(list(QUEUE_DIR.glob("*.json")))
    log(f"📊 Remaining queued items: {remaining}")
    if not is_ci:
        _sync_local_state_to_remote()
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vynox Daily Reel Dispatcher")
    parser.add_argument("--force", action="store_true", help="Force dispatch regardless of time or today's quota")
    args = parser.parse_args()

    try:
        dispatch_next(force=args.force)
    except Exception as e:
        log(f"💥 Error during daily dispatch: {e}")
        sys.exit(1)

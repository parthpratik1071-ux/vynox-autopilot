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

    if not force and not is_ci:
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

        # Check slot fulfillment (Slot 1: Afternoon 2:00 PM IST | Slot 2: Evening 7:00 PM IST)
        if now.hour >= 18:
            evening_posted = any(
                (parse_dt(p.get("published_at")) and parse_dt(p.get("published_at")).hour >= 18)
                for p in today_posts
            )
            if evening_posted:
                log(f"✅ Evening Reel already published today ({today_str}). Daily quota fulfilled!")
                return True
        elif now.hour < 13:
            log(f"⏳ Current time ({now.strftime('%H:%M')}) is before afternoon slot (14:00 IST). Waiting.")
            return False
        else:
            # Afternoon slot
            afternoon_posted = any(
                (parse_dt(p.get("published_at")) and parse_dt(p.get("published_at")).hour < 18)
                for p in today_posts
            )
            if afternoon_posted:
                log(f"✅ Afternoon Reel already published today ({today_str}). Next slot at 7:00 PM IST.")
                return True
    elif is_ci:
        log(f"🤖 Scheduled GitHub Actions trigger detected ({now.strftime('%H:%M')} IST). Proceeding to dispatch next queued reel...")

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
    
    # Import and run our local instagram poster
    sys.path.insert(0, str(BASE_DIR / "scripts"))
    import insta_local_post

    cl = insta_local_post.get_client()

    # Safety duplicate guard: Check if identical caption was already posted in latest medias
    if not force:
        try:
            recent_medias = cl.user_medias(cl.user_id, amount=3)
            first_sentence = caption.split('\n')[0].strip()
            for rm in recent_medias:
                rm_cap = (rm.caption_text or '').strip()
                if first_sentence and first_sentence in rm_cap:
                    log(f"⚠️ Duplicate detected: '{first_sentence[:40]}...' already exists as https://www.instagram.com/reel/{rm.code}/. Skipping upload.")
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

    # Move to archive
    archive_dest = ARCHIVE_DIR / f"{now.date().isoformat()}_{next_file.name}"
    with open(archive_dest, "w") as f:
        json.dump(data, f, indent=2)
    next_file.unlink()

    log(f"📁 Archived record to: {archive_dest.name}")
    remaining = len(list(QUEUE_DIR.glob("*.json")))
    log(f"📊 Remaining queued items: {remaining}")
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

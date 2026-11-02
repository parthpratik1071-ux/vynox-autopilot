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

BASE_DIR = Path("/home/pratik/stickman-video-director")
QUEUE_DIR = BASE_DIR / "projects" / "queue"
ARCHIVE_DIR = BASE_DIR / "projects" / "archive"
LOG_FILE = BASE_DIR / "projects" / "daily_dispatcher.log"

def log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {msg}"
    print(formatted)
    with open(LOG_FILE, "a") as f:
        f.write(formatted + "\n")

def dispatch_next(force=False):
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    today_str = datetime.date.today().isoformat()
    now = datetime.datetime.now()

    # Check if a post was already made today
    already_published = any(f.name.startswith(today_str) for f in ARCHIVE_DIR.glob("*.json"))
    if already_published and not force:
        log(f"✅ Already published a Reel today ({today_str}). Quota fulfilled. Next post scheduled for tomorrow at 7:00 PM.")
        return True

    # If triggered via startup/catch-up before 19:00, wait until scheduled time
    if now.hour < 19 and not force:
        log(f"⏳ Current time ({now.strftime('%H:%M')}) is before 7:00 PM IST. Queued post will release at 19:00.")
        return False

    queue_files = sorted(list(QUEUE_DIR.glob("*.json")))
    if not queue_files:
        log("⚠️ No queued Reels found in projects/queue/! Queue is empty.")
        return False

    next_file = queue_files[0]
    log(f"📦 Processing queue item: {next_file.name}")

    with open(next_file, "r") as f:
        data = json.load(f)

    video_path = data.get("video_path")
    cover_path = data.get("cover_path")
    caption = data.get("caption", "")

    if not video_path or not os.path.exists(video_path):
        log(f"❌ Video file does not exist: {video_path}")
        return False

    log(f"🎬 Uploading video: {video_path}")
    
    # Import and run our local instagram poster
    sys.path.insert(0, str(BASE_DIR / "scripts"))
    import insta_local_post

    cl = insta_local_post.get_client()
    media = insta_local_post.upload_reel(
        cl,
        video_path=video_path,
        caption=caption,
        thumbnail_path=cover_path
    )

    reel_url = f"https://www.instagram.com/reel/{media.code}/"
    log(f"✅ Reel posted successfully: {reel_url}")

    data["published_at"] = datetime.datetime.now().isoformat()
    data["reel_url"] = reel_url
    data["media_id"] = media.pk

    # Move to archive
    archive_dest = ARCHIVE_DIR / f"{datetime.date.today().isoformat()}_{next_file.name}"
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

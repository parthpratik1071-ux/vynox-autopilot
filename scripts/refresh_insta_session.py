#!/usr/bin/env python3
"""
Interactive Instagram Session Refresher for @vynox_00000.
Run this AFTER resolving the Instagram challenge on your phone.
It will:
1. Log in with fresh credentials
2. Save the new session
3. Export base64 for GitHub Secrets
4. Clear the Ban-Shield cooldown
5. Test the session with a simple API call
"""

import base64
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))

from instagrapi import Client

SESSION_DIR = Path.home() / ".config" / "stickman_video_director"
SESSION_FILE = SESSION_DIR / "insta_session.json"
COOLDOWN_FILE = BASE_DIR / "projects" / "booster_cooldown.json"
IST = timezone(timedelta(hours=5, minutes=30))

USERNAME = "vynox_00000"


def main():
    print("🔄 Instagram Session Refresher for @vynox_00000")
    print("=" * 50)
    print()
    print("⚠️  IMPORTANT: Before running this, make sure you have:")
    print("   1. Opened Instagram app on your phone")
    print("   2. Resolved any verification/challenge prompt")
    print("   3. Confirmed you can browse normally in the app")
    print()

    password = input("Enter Instagram password for @vynox_00000: ").strip()
    if not password:
        print("❌ Password cannot be empty.")
        return

    print(f"\n🔑 Logging in as @{USERNAME}...")
    cl = Client()
    cl.delay_range = [2, 5]

    try:
        cl.login(USERNAME, password)
        info = cl.account_info()
        print(f"✅ Login successful!")
        print(f"   Username: @{info.username}")
        print(f"   Followers: {info.follower_count}")
        print(f"   Posts: {info.media_count}")
    except Exception as e:
        print(f"❌ Login failed: {e}")
        print("\nTroubleshooting:")
        print("  - Make sure you resolved the challenge on your phone FIRST")
        print("  - Wait 5-10 minutes after resolving before running this")
        print("  - Try logging in from the Instagram app first")
        return

    # Save session
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    settings = cl.get_settings()
    with open(SESSION_FILE, "w") as f:
        json.dump(settings, f, indent=2, default=str)
    print(f"\n💾 Session saved to: {SESSION_FILE}")

    # Export base64 for GitHub Secrets
    with open(SESSION_FILE, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    
    b64_file = SESSION_DIR / "insta_session_b64.txt"
    with open(b64_file, "w") as f:
        f.write(b64)
    print(f"📋 Base64 session exported to: {b64_file}")
    print(f"   Copy this to GitHub Secret 'INSTA_SESSION_JSON'")

    # Clear Ban-Shield cooldown
    if COOLDOWN_FILE.exists():
        cooldown_data = {"active": False, "cleared_at": datetime.now(IST).isoformat(), "reason": "Manual session refresh"}
        with open(COOLDOWN_FILE, "w") as f:
            json.dump(cooldown_data, f, indent=2)
        print(f"\n🛡️ Ban-Shield cooldown CLEARED ✅")
    
    # Test with a simple API call
    print("\n🧪 Testing session with API calls...")
    try:
        clips = cl.user_clips(cl.user_id, amount=1)
        if clips:
            latest = clips[0]
            print(f"   Latest reel: {latest.pk} ({latest.play_count} views)")
        print("✅ Session is fully operational!")
    except Exception as e:
        print(f"⚠️ Test failed: {e}")
        print("   Session saved but may need challenge resolution first")

    print("\n" + "=" * 50)
    print("📋 NEXT STEPS:")
    print(f"   1. Copy base64 from {b64_file}")
    print("   2. Update GitHub Secret 'INSTA_SESSION_JSON'")
    print("   3. The crontab will auto-dispatch tonight's reels!")
    print("=" * 50)


if __name__ == "__main__":
    main()
